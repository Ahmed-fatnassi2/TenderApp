# routes/auth_routes.py - COMPLETE FIXED VERSION
from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from models.user import User
import re
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400
        
        # Find user by email
        user = User.query.filter_by(email=data['email']).first()
        
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check password
        if not check_password_hash(user.hashed_password, data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check if user is active
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 403
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # ============ CREATE SESSION ============
        # This is the key part - create the session!
        session['user_id'] = user.id
        session['username'] = user.username
        session['is_admin'] = user.is_admin
        session['is_authenticated'] = True
        
        print(f"✅ LOGIN SUCCESS: User {user.username} (ID: {user.id})")
        print(f"📋 Session created: {dict(session)}")
        
        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/auth/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['firstName', 'lastName', 'email', 'password', 'username']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate email format
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_pattern, data['email']):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password strength
        if len(data['password']) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # Check if user already exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already taken'}), 400
        
        # Create new user
        new_user = User(
            username=data['username'],
            email=data['email'],
            hashed_password=generate_password_hash(data['password']),
            first_name=data['firstName'],
            last_name=data['lastName'],
            is_active=True,
            is_admin=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Create session
        session['user_id'] = new_user.id
        session['username'] = new_user.username
        session['is_admin'] = new_user.is_admin
        session['is_authenticated'] = True
        
        return jsonify({
            'message': 'User created successfully',
            'user': new_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/auth/logout', methods=['POST', 'OPTIONS'])
def logout():
    if request.method == 'OPTIONS':
        return '', 200
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_bp.route('/auth/current-user', methods=['GET', 'OPTIONS'])
def get_current_user():
    if request.method == 'OPTIONS':
        return '', 200
    
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': user.to_dict()}), 200