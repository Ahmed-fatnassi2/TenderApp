# routes/oidc_routes.py - COMPLETE WORKING VERSION

from flask import Blueprint, request, jsonify, redirect, url_for, session, current_app
from services.oidc_service import oauth, create_or_update_user, login_required, get_current_user
import logging
import os

# Use '/auth' prefix so all routes are under /auth
oidc_bp = Blueprint('oidc_auth', __name__, url_prefix='/auth')
logger = logging.getLogger(__name__)

@oidc_bp.route('/oidc/test', methods=['GET'])
def oidc_test():
    """Test if OIDC blueprint is working"""
    return jsonify({
        'status': 'OK',
        'message': 'OIDC blueprint is working!',
        'oauth_initialized': oauth is not None
    })

@oidc_bp.route('/oidc/login', methods=['GET'])
def oidc_login():
    """Redirect to OIDC provider login page"""
    try:
        provider = request.args.get('provider', 'google')
        redirect_uri = url_for('oidc_auth.oidc_callback', _external=True)
        
        logger.info(f"🔐 OIDC Login with provider: {provider}")
        logger.info(f"📡 Redirect URI: {redirect_uri}")
        
        if oauth is None:
            return jsonify({'error': 'OAuth not initialized'}), 500
        
        session['oidc_provider'] = provider
        
        if provider == 'google':
            return oauth.google.authorize_redirect(redirect_uri)
        elif provider == 'keycloak':
            return oauth.keycloak.authorize_redirect(redirect_uri)
        elif provider == 'auth0':
            return oauth.auth0.authorize_redirect(redirect_uri)
        else:
            return jsonify({'error': f'Provider {provider} not supported'}), 400
    except Exception as e:
        logger.error(f"OIDC Login error: {e}")
        return jsonify({'error': str(e)}), 500

@oidc_bp.route('/oidc/callback', methods=['GET'])
def oidc_callback():
    """Handle OIDC callback after provider authentication"""
    try:
        provider = session.get('oidc_provider', 'google')
        logger.info(f"🔐 OIDC Callback from provider: {provider}")
        
        if oauth is None:
            return jsonify({'error': 'OAuth not initialized'}), 500
        
        if provider == 'google':
            client = oauth.google
        elif provider == 'keycloak':
            client = oauth.keycloak
        elif provider == 'auth0':
            client = oauth.auth0
        else:
            return jsonify({'error': 'Unknown provider'}), 400
        
        token = client.authorize_access_token()
        logger.info(f"✅ OIDC Token received")
        
        user_info = token.get('userinfo')
        
        if not user_info:
            userinfo_endpoint = token.get('userinfo_endpoint')
            if userinfo_endpoint:
                import requests
                headers = {'Authorization': f"Bearer {token.get('access_token')}"}
                response = requests.get(userinfo_endpoint, headers=headers)
                if response.status_code == 200:
                    user_info = response.json()
        
        if not user_info:
            return jsonify({'error': 'Could not get user info'}), 400
        
        session['access_token'] = token.get('access_token')
        session['id_token'] = token.get('id_token')
        session['refresh_token'] = token.get('refresh_token')
        
        user_info['provider'] = provider
        user = create_or_update_user(user_info)
        
        if user:
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['user_name'] = user.username
            session['is_authenticated'] = True
            
            logger.info(f"✅ OIDC User authenticated: {user.email}")
            
            frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
            return redirect(f"{frontend_url}/?login=success")
        else:
            return jsonify({'error': 'Failed to create user'}), 500
            
    except Exception as e:
        logger.error(f"OIDC callback error: {e}")
        return jsonify({'error': str(e)}), 500

@oidc_bp.route('/oidc/logout', methods=['GET'])
def oidc_logout():
    """OIDC Logout"""
    session.clear()
    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
    return redirect(f"{frontend_url}/?logout=success")

# routes/oidc_routes.py - Fix the /oidc/user endpoint

@oidc_bp.route('/oidc/user', methods=['GET'])
def oidc_current_user():
    """Get current OIDC authenticated user"""
    try:
        user = get_current_user()
        if user:
            return jsonify({
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'first_name': user.first_name or '',
                'last_name': user.last_name or '',
                'is_active': user.is_active,
                'is_admin': user.is_admin,
                'created_at': user.created_at.isoformat() if user.created_at else None
            })
        return jsonify({'error': 'Not authenticated'}), 401
    except Exception as e:
        logger.error(f"Error in oidc_current_user: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@oidc_bp.route('/oidc/status', methods=['GET'])
def oidc_auth_status():
    """Check OIDC authentication status"""
    user = get_current_user()
    return jsonify({
        'authenticated': user is not None,
        'user': {
            'id': user.id,
            'email': user.email,
            'username': user.username
        } if user else None
    })