import sqlite3
from flask import Blueprint, render_template, request, abort, flash, redirect, url_for, make_response, g
from werkzeug.utils import secure_filename
from forms import BlogForm
import os
from flask_login import login_required, current_user
import bleach

blogs_bp = Blueprint('blogs', __name__)

UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_TAGS = ['p', 'strong', 'em', 'ul', 'li', 'br']

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@blogs_bp.route('/blogs/new', methods=['GET', 'POST'])
@login_required
def add_blog():
    api_key = '7dowqsizhjpg0668xmzqpw2d4c8by4dam96yft0stapvilcc'
    
    # Check if the current user is an admin
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('blogs.blogs'))

    form = BlogForm()

    # Fetch categories to populate the dropdown
    conn = sqlite3.connect('blogs_advanced.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM categories')
    categories = cursor.fetchall()
    conn.close()

    # Update the form's category field choices
    form.category.choices = [(category[0], category[1]) for category in categories]

    if form.validate_on_submit():
        title = form.title.data
        summary = form.summary.data
        content = form.content.data
        category_id = form.category.data

        # Handle file upload
        file = form.image.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            image_path = os.path.join('images', filename)
        else:
            image_path = 'images/default.jpg'  # Default image if none is uploaded

        # Insert the new blog post into the database
        conn = sqlite3.connect('blogs_advanced.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO posts (title, summary, content, image, date, author_id, category_id)
            VALUES (?, ?, ?, ?, datetime('now'), ?, ?)
        ''', (title, summary, content, image_path, current_user.id, category_id))
        conn.commit()
        conn.close()

        flash('Blog post added successfully!', 'success')
        return redirect(url_for('blogs.blogs'))

    # Apply relaxed CSP with 'unsafe-inline' only for this page
    response = make_response(render_template('/blogs/add_blog.html', form=form, api_key=api_key))
    response.headers['Content-Security-Policy'] = (
        f"default-src 'none'; "
        f"script-src 'self' *.tinymce.com *.tiny.cloud; "
        f"connect-src 'self' *.tinymce.com *.tiny.cloud blob:; "
        f"img-src 'self' *.tinymce.com *.tiny.cloud data: blob:; "
        f"style-src 'self' 'unsafe-inline' *.tinymce.com *.tiny.cloud; "
        f"font-src 'self' *.tinymce.com *.tiny.cloud;"
    )

    return response

# Function to sanitize HTML
def sanitize_html(content):
    return bleach.clean(content, tags=ALLOWED_TAGS, strip=True)

@blogs_bp.route('/blogs')
def blogs():
    # Get search and category filter parameters from the URL
    search_query = request.args.get('search', '')
    category_filter = request.args.get('category', '')

    # Connect to the SQLite database
    with sqlite3.connect('blogs_advanced.db') as conn:
        cursor = conn.cursor()

        # Base query to fetch blog posts with parameter placeholders
        query = '''
            SELECT posts.id, posts.title, posts.summary, posts.image, posts.date, authors.name, categories.name
            FROM posts
            JOIN authors ON posts.author_id = authors.id
            JOIN categories ON posts.category_id = categories.id
        '''

        # List to hold the query conditions and parameters
        query_conditions = []
        query_params = []

        # Add search condition with parameterized query
        if search_query:
            query_conditions.append("(posts.title LIKE ? OR posts.summary LIKE ?)")
            query_params.extend([f"%{search_query}%", f"%{search_query}%"])

        # Add category condition with parameterized query
        if category_filter:
            query_conditions.append("categories.name = ?")
            query_params.append(category_filter)

        # Combine conditions into the SQL query if they exist
        if query_conditions:
            query += " WHERE " + " AND ".join(query_conditions)

        # Execute the query with parameters
        cursor.execute(query, query_params)
        rows = cursor.fetchall()

        # Convert rows to a list of dictionaries
        blog_posts = [
            {
                'id': row[0],
                'title': row[1],
                'summary': sanitize_html(row[2]),  # Sanitize HTML for safety
                'image': row[3],
                'date': row[4],
                'author': row[5],
                'category': row[6]
            }
            for row in rows
        ]

        # Fetch all categories for the filter dropdown
        cursor.execute('SELECT name FROM categories')
        categories = [row[0] for row in cursor.fetchall()]

    # Render the template with blog data and filters
    return render_template('/blogs/blogs.html', title='Blogs', blog_posts=blog_posts, categories=categories, search_query=search_query, selected_category=category_filter)

@blogs_bp.route('/blogs/<int:blog_id>')
def blog_detail(blog_id):
    # Connect to the SQLite database
    conn = sqlite3.connect('blogs_advanced.db')
    cursor = conn.cursor()

    # Fetch the specific blog post by ID using a parameterized query
    cursor.execute('''
        SELECT posts.id, posts.title, posts.content, posts.image, posts.date, authors.name, categories.name
        FROM posts
        JOIN authors ON posts.author_id = authors.id
        JOIN categories ON posts.category_id = categories.id
        WHERE posts.id = ?
    ''', (blog_id,))
    row = cursor.fetchone()

    # If the blog post does not exist, return a 404 error
    if row is None:
        abort(404)

    # Convert row to a dictionary
    blog_post = {
        'id': row[0],
        'title': row[1],
        'content': row[2],
        'image': row[3],
        'date': row[4],
        'author': row[5],
        'category': row[6]
    }

    # Close the database 
    conn.close()

    # Render the template for the individual blog post
    return render_template('/blogs/blog_detail.html', title=blog_post['title'], blog_post=blog_post)

@blogs_bp.route('/blogs/edit/<int:blog_id>', methods=['GET', 'POST'])
@login_required
def edit_blog(blog_id):
    api_key = '7dowqsizhjpg0668xmzqpw2d4c8by4dam96yft0stapvilcc'
    
    # Only allow admins to edit
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('blogs.blogs'))

    # Connect to the SQLite database
    conn = sqlite3.connect('blogs_advanced.db')
    cursor = conn.cursor()

    # Retrieve the blog post by ID
    cursor.execute('SELECT id, title, summary, content, image, category_id FROM posts WHERE id = ?', (blog_id,))
    blog_data = cursor.fetchone()

    # If no blog data found, return an error
    if not blog_data:
        flash('Blog post not found.', 'danger')
        conn.close()
        return redirect(url_for('blogs.select_blog_to_edit'))

    # Create a form and pre-populate with the current data
    form = BlogForm()

    # Fetch categories to populate the dropdown
    cursor.execute('SELECT id, name FROM categories')
    categories = cursor.fetchall()
    form.category.choices = [(category[0], category[1]) for category in categories]

    if request.method == 'POST' and form.validate_on_submit():
        title = form.title.data
        summary = form.summary.data
        content = form.content.data
        category_id = form.category.data

        # Handle file upload for image update
        file = form.image.data
        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            image_path = os.path.join('images', filename)
        else:
            image_path = blog_data[4]  # Use the existing image if no new image is uploaded

        # Update the blog post in the database
        cursor.execute('''
            UPDATE posts
            SET title = ?, summary = ?, content = ?, image = ?, category_id = ?
            WHERE id = ?
        ''', (title, summary, content, image_path, category_id, blog_id))
        conn.commit()
        conn.close()

        flash('Blog post updated successfully!', 'success')
        return redirect(url_for('blogs.blog_detail', blog_id=blog_id))

    # Pre-fill the form fields with the existing blog data
    form.title.data = blog_data[1]
    form.summary.data = blog_data[2]
    form.content.data = blog_data[3]
    form.category.data = blog_data[5]

    conn.close()

    # Apply relaxed CSP with 'unsafe-inline' only for this page
    response = make_response(render_template('/blogs/edit_blog.html', form=form, blog_id=blog_id, api_key=api_key))
    response.headers['Content-Security-Policy'] = (
        f"default-src 'none'; "
        f"script-src 'self' *.tinymce.com *.tiny.cloud https://cdn.jsdelivr.net; "
        f"connect-src 'self' *.tinymce.com *.tiny.cloud blob: https://cdn.jsdelivr.net; "
        f"img-src 'self' *.tinymce.com *.tiny.cloud data: blob: https://cdn.jsdelivr.net; "
        f"style-src 'self' 'unsafe-inline' *.tinymce.com *.tiny.cloud https://cdn.jsdelivr.net; "
        f"font-src 'self' *.tinymce.com *.tiny.cloud;"
    )


    return render_template('/blogs/edit_blog.html', form=form, blog_id=blog_id, api_key=api_key)

@blogs_bp.route('/blogs/edit', methods=['GET'])
@login_required
def select_blog_to_edit():
    # Only allow admins to access the edit selection page
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('blogs.blogs'))

    # Connect to the SQLite database
    conn = sqlite3.connect('blogs_advanced.db')
    cursor = conn.cursor()

    # Retrieve all blog posts
    cursor.execute('''
        SELECT id, title, summary, date 
        FROM posts
        ORDER BY date DESC
    ''')
    rows = cursor.fetchall()

    # Convert rows to a list of dictionaries
    blog_posts = []
    for row in rows:
        # Ensure each element in the row is not None before adding it
        if len(row) == 4 and all(row):
            blog_posts.append({
                'id': row[0],
                'title': row[1],
                'summary': row[2],
                'date': row[3]
            })
    conn.close()

    # Render the template for selecting a blog to edit
    return render_template('/blogs/select_blog_to_edit.html', blog_posts=blog_posts)