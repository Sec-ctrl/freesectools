from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from forms import LoginForm  # Import the LoginForm
from models import User
import bleach

auth_bp = Blueprint('auth', __name__)  # Ensure the blueprint is named 'auth'

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Sanitize input
        username = bleach.clean(form.username.data)
        password = bleach.clean(form.password.data)
        
        # Retrieve the user by username
        user_data = User.get_user_by_username(username)
        if user_data and User.verify_password(user_data[2], password):  # user_data[2] is the stored password
            user = User(user_data[0], user_data[1], user_data[3])  # user_data[0] is id, [1] is username, [3] is role
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('blogs.blogs'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))
