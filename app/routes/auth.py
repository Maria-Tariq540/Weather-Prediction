"""
Authentication Routes
Handles user registration, login, and logout.
"""
from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, current_user
from app import db
from app.models.user import User
from app.utils.decorators import login_required_api

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/signup', methods=['POST'])
def signup():
    """
    User registration endpoint.
    
    Request JSON:
        - username: str
        - email: str
        - password: str
    
    Returns:
        JSON response with user data or error
    """
    data = request.get_json()
    
    # Validate input
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not username or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400
    
    if len(username) < 3:
        return jsonify({'error': 'Username must be at least 3 characters'}), 400
    
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create new user
    try:
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Log in the user
        login_user(user)
        
        return jsonify({
            'success': True,
            'message': 'Account created successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create account: {str(e)}'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    User login endpoint.
    
    Request JSON:
        - username: str (username or email)
        - password: str
    
    Returns:
        JSON response with user data or error
    """
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400
    
    # Find user by username or email
    user = User.query.filter(
        (User.username == username) | (User.email == username.lower())
    ).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    # Log in the user
    login_user(user, remember=True)
    
    return jsonify({
        'success': True,
        'message': 'Logged in successfully',
        'user': user.to_dict()
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@login_required_api
def logout():
    """
    User logout endpoint.
    
    Returns:
        JSON response confirming logout
    """
    logout_user()
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    }), 200


@auth_bp.route('/user', methods=['GET'])
@login_required_api
def get_current_user():
    """
    Get current logged-in user information.
    
    Returns:
        JSON response with user data
    """
    return jsonify({
        'success': True,
        'user': current_user.to_dict()
    }), 200


@auth_bp.route('/check', methods=['GET'])
def check_auth():
    """
    Check if user is authenticated.
    
    Returns:
        JSON response with authentication status
    """
    return jsonify({
        'authenticated': current_user.is_authenticated,
        'user': current_user.to_dict() if current_user.is_authenticated else None
    }), 200
