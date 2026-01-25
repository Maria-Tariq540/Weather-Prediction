"""
Main Routes
Handles HTML page rendering for the frontend.
"""
from flask import Blueprint, render_template
from flask_login import current_user

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Landing page with weather search."""
    return render_template('index.html')


@main_bp.route('/login')
def login_page():
    """Login page."""
    if current_user.is_authenticated:
        return render_template('dashboard.html')
    return render_template('login.html')


@main_bp.route('/signup')
def signup_page():
    """Signup page."""
    if current_user.is_authenticated:
        return render_template('dashboard.html')
    return render_template('signup.html')


@main_bp.route('/dashboard')
def dashboard():
    """User dashboard (requires login)."""
    return render_template('dashboard.html')
