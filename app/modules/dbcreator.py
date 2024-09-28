import sqlite3

# Connect to the SQLite database (creates it if it doesn't exist)
conn = sqlite3.connect('blogs_advanced.db')

# Create a cursor object
cursor = conn.cursor()

# Create the authors table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS authors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        bio TEXT
    )
''')

# Create the categories table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
''')

# Create the posts table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        summary TEXT NOT NULL,
        content TEXT NOT NULL,
        image TEXT NOT NULL,
        date TEXT NOT NULL,
        author_id INTEGER NOT NULL,
        category_id INTEGER NOT NULL,
        FOREIGN KEY (author_id) REFERENCES authors (id),
        FOREIGN KEY (category_id) REFERENCES categories (id)
    )
''')

# Create the tags table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
''')

# Create the post_tags table (many-to-many relationship)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS post_tags (
        post_id INTEGER NOT NULL,
        tag_id INTEGER NOT NULL,
        FOREIGN KEY (post_id) REFERENCES posts (id),
        FOREIGN KEY (tag_id) REFERENCES tags (id),
        PRIMARY KEY (post_id, tag_id)
    )
''')

# Insert sample authors
cursor.executemany('''
    INSERT INTO authors (name, bio)
    VALUES (?, ?)
''', [
    ("John Doe", "Cybersecurity expert and writer."),
    ("Jane Smith", "Software engineer and tech blogger.")
])

# Insert sample categories
cursor.executemany('''
    INSERT INTO categories (name)
    VALUES (?)
''', [
    ("Cybersecurity",),
    ("Programming",),
    ("Tech News",)
])

# Insert sample posts
cursor.executemany('''
    INSERT INTO posts (title, summary, content, image, date, author_id, category_id)
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', [
    ("Introduction to Cybersecurity", "A brief overview of cybersecurity concepts.", "Full content of the post.", "images/featured1.jpg", "August 1, 2024", 1, 1),
    ("Advanced Python Techniques", "Tips and tricks for advanced Python programming.", "Full content of the post.", "images/featured2.png", "August 5, 2024", 2, 2),
])

# Insert sample tags
cursor.executemany('''
    INSERT INTO tags (name)
    VALUES (?)
''', [
    ("Python",),
    ("Security",),
    ("Programming",),
    ("Nmap",),
    ("Exploit",),
    ("SQL",),
    ("Tutorial",),
    ("Whois",),
    ("Infosec",)

])

# Insert sample post_tags relationships
cursor.executemany('''
    INSERT INTO post_tags (post_id, tag_id)
    VALUES (?, ?)
''', [
    (1, 2),  # "Introduction to Cybersecurity" has tag "Security"
    (2, 1),  # "Advanced Python Techniques" has tag "Python"
    (2, 3),  # "Advanced Python Techniques" has tag "Programming"
])

# Commit changes and close the connection
conn.commit()
conn.close()

print("Advanced database schema created and sample data inserted successfully.")
