# # services/oidc_service.py - COMPLETE FIXED VERSION

# import os
# import json
# import requests
# from flask import session, redirect, url_for, request, jsonify
# from authlib.integrations.flask_client import OAuth
# from functools import wraps
# from models.user import User
# from database import db
# from datetime import datetime
# import logging

# logger = logging.getLogger(__name__)

# # Global OAuth instance
# oauth = OAuth()  # ← Create the OAuth instance here

# def init_oidc(app):
#     """Initialize OIDC with the Flask app"""
#     global oauth
    
#     logger.info("🔐 Initializing OIDC...")
    
#     # Check which provider to use
#     provider = os.getenv('OIDC_PROVIDER', 'google')
#     logger.info(f"📋 OIDC Provider: {provider}")
    
#     if provider == 'google':
#         client_id = os.getenv('GOOGLE_CLIENT_ID')
#         client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        
#         if not client_id or not client_secret:
#             logger.error("❌ Google Client ID or Secret not configured!")
#             logger.error(f"GOOGLE_CLIENT_ID: {'SET' if client_id else 'MISSING'}")
#             logger.error(f"GOOGLE_CLIENT_SECRET: {'SET' if client_secret else 'MISSING'}")
#             raise ValueError("Google Client ID and Secret are required")
        
#         logger.info(f"✅ Google Client ID: {client_id[:20]}...")
#         logger.info(f"✅ Google Client Secret: {'*' * 10}")
        
#         # Initialize OAuth with the app
#         oauth.init_app(app)
        
#         # Register Google OAuth
#         oauth.register(
#             name='google',
#             client_id=client_id,
#             client_secret=client_secret,
#             server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
#             client_kwargs={
#                 'scope': 'openid email profile'
#             }
#         )
#         logger.info("✅ Google OIDC registered successfully")
        
#     elif provider == 'keycloak':
#         # ... similar for keycloak ...
#         pass
#     elif provider == 'auth0':
#         # ... similar for auth0 ...
#         pass
#     else:
#         logger.error(f"❌ Unknown provider: {provider}")
#         raise ValueError(f"Unknown OIDC provider: {provider}")
    
#     logger.info("✅ OIDC initialization complete")
#     return oauth

# def login_required(f):
#     """Decorator to require login for routes"""
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if not session.get('user_id'):
#             return redirect(url_for('oidc_auth.oidc_login'))
#         return f(*args, **kwargs)
#     return decorated_function

# def get_current_user():
#     """Get current user from session"""
#     user_id = session.get('user_id')
#     if user_id:
#         return User.query.get(user_id)
#     return None

# def create_or_update_user(user_info):
#     """Create or update user from OIDC user info"""
#     email = user_info.get('email')
#     if not email:
#         logger.error("❌ No email in user info")
#         return None
    
#     # Check if user exists
#     user = User.query.filter_by(email=email).first()
    
#     if not user:
#         # Create new user
#         name = user_info.get('name', email.split('@')[0])
#         # Use name as username (make unique if needed)
#         username = name.lower().replace(' ', '_')
#         base_username = username
#         counter = 1
#         while User.query.filter_by(username=username).first():
#             username = f"{base_username}{counter}"
#             counter += 1
        
#         # Split name into first and last
#         name_parts = name.split(' ', 1)
#         first_name = name_parts[0]
#         last_name = name_parts[1] if len(name_parts) > 1 else ''
        
#         user = User(
#             email=email,
#             username=username,
#             first_name=first_name,
#             last_name=last_name,
#             is_active=True,
#             is_admin=False,
#             created_at=datetime.utcnow(),
#             updated_at=datetime.utcnow()
#         )
#         db.session.add(user)
#         db.session.commit()
#         logger.info(f"✅ New OIDC user created: {user.email} (ID: {user.id})")
#     else:
#         # Update existing user
#         user.last_login = datetime.utcnow()
#         user.updated_at = datetime.utcnow()
#         # Update name if provided and fields are empty
#         if user_info.get('name') and not user.first_name:
#             name_parts = user_info.get('name').split(' ', 1)
#             user.first_name = name_parts[0]
#             user.last_name = name_parts[1] if len(name_parts) > 1 else ''
#         db.session.commit()
#         logger.info(f"✅ OIDC user updated: {user.email} (ID: {user.id})")
    
#     return user





# services/oidc_service.py - UPDATED (no full_name)

import os
import json
import requests
from flask import session, redirect, url_for, request, jsonify
from authlib.integrations.flask_client import OAuth
from functools import wraps
from models.user import User
from database import db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Global OAuth instance
oauth = OAuth()

def init_oidc(app):
    """Initialize OIDC with the Flask app"""
    global oauth
    
    logger.info("🔐 Initializing OIDC...")
    
    # Check which provider to use
    provider = os.getenv('OIDC_PROVIDER', 'google')
    logger.info(f"📋 OIDC Provider: {provider}")
    
    if provider == 'google':
        client_id = os.getenv('GOOGLE_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            logger.error("❌ Google Client ID or Secret not configured!")
            raise ValueError("Google Client ID and Secret are required")
        
        logger.info(f"✅ Google Client ID: {client_id[:20]}...")
        
        # Initialize OAuth with the app
        oauth.init_app(app)
        
        # Register Google OAuth
        oauth.register(
            name='google',
            client_id=client_id,
            client_secret=client_secret,
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={
                'scope': 'openid email profile'
            }
        )
        logger.info("✅ Google OIDC registered successfully")
        
    elif provider == 'keycloak':
        keycloak_url = os.getenv('KEYCLOAK_URL', 'http://localhost:8080')
        keycloak_realm = os.getenv('KEYCLOAK_REALM', 'tenderapp')
        client_id = os.getenv('KEYCLOAK_CLIENT_ID')
        client_secret = os.getenv('KEYCLOAK_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            logger.error("❌ Keycloak Client ID or Secret not configured!")
            raise ValueError("Keycloak Client ID and Secret are required")
        
        oauth.init_app(app)
        
        oauth.register(
            name='keycloak',
            client_id=client_id,
            client_secret=client_secret,
            server_metadata_url=f'{keycloak_url}/realms/{keycloak_realm}/.well-known/openid-configuration',
            client_kwargs={
                'scope': 'openid email profile'
            }
        )
        logger.info("✅ Keycloak OIDC registered successfully")
        
    elif provider == 'auth0':
        auth0_domain = os.getenv('AUTH0_DOMAIN')
        client_id = os.getenv('AUTH0_CLIENT_ID')
        client_secret = os.getenv('AUTH0_CLIENT_SECRET')
        
        if not auth0_domain or not client_id or not client_secret:
            logger.error("❌ Auth0 configuration missing!")
            raise ValueError("Auth0 Domain, Client ID, and Secret are required")
        
        oauth.init_app(app)
        
        oauth.register(
            name='auth0',
            client_id=client_id,
            client_secret=client_secret,
            server_metadata_url=f'https://{auth0_domain}/.well-known/openid-configuration',
            client_kwargs={
                'scope': 'openid email profile'
            }
        )
        logger.info("✅ Auth0 OIDC registered successfully")
        
    else:
        logger.error(f"❌ Unknown provider: {provider}")
        raise ValueError(f"Unknown OIDC provider: {provider}")
    
    logger.info("✅ OIDC initialization complete")
    return oauth

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('oidc_auth.oidc_login'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get current user from session"""
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None

def create_or_update_user(user_info):
    """Create or update user from OIDC user info - using only existing fields"""
    email = user_info.get('email')
    if not email:
        logger.error("❌ No email in user info")
        return None
    
    # Check if user exists
    user = User.query.filter_by(email=email).first()
    
    if not user:
        # Create new user
        name = user_info.get('name', email.split('@')[0])
        
        # Generate username from name or email
        username = name.lower().replace(' ', '_') if name else email.split('@')[0]
        base_username = username
        counter = 1
        while User.query.filter_by(username=username).first():
            username = f"{base_username}{counter}"
            counter += 1
        
        # Split name into first and last
        name_parts = name.split(' ', 1) if name else [email.split('@')[0], '']
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        # Create user with only existing fields
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
            is_admin=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(user)
        db.session.commit()
        logger.info(f"✅ New OIDC user created: {user.email} (ID: {user.id})")
    else:
        # Update existing user
        user.last_login = datetime.utcnow()
        user.updated_at = datetime.utcnow()
        
        # Update name if provided and fields are empty
        name = user_info.get('name')
        if name and (not user.first_name or not user.last_name):
            name_parts = name.split(' ', 1)
            user.first_name = name_parts[0]
            user.last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        db.session.commit()
        logger.info(f"✅ OIDC user updated: {user.email} (ID: {user.id})")
    
    return user