# routes/admin_routes.py - COMPLETE FIXED VERSION
from flask import Blueprint, request, jsonify, session
from database import db
from models.user import User
from models.tender import Tender
import logging

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')
logger = logging.getLogger(__name__)

# Helper function to check if user is admin - accepts user_id parameter
def check_admin_access(user_id=None):
    """Check if a user is admin"""
    try:
        # If user_id not provided, try to get from session or request
        if not user_id:
            # Try query parameter
            user_id = request.args.get('user_id', type=int)
        
        # If still no user_id, try session
        if not user_id:
            user_id = session.get('user_id')
        
        if not user_id:
            return False, "Not logged in"
        
        user = User.query.get(user_id)
        if not user:
            return False, "User not found"
        
        return user.is_admin, None
    except Exception as e:
        logger.error(f"Error checking admin: {e}")
        return False, str(e)

@admin_bp.route('/users', methods=['GET'])
def get_users():
    """Get all users (admin only)"""
    # Get user_id from query parameter
    user_id = request.args.get('user_id', type=int)
    
    # Check if user is admin
    is_admin, error = check_admin_access(user_id)
    
    if not is_admin:
        return jsonify({'success': False, 'error': 'Unauthorized. Admin access required.'}), 403
    
    try:
        users = User.query.all()
        return jsonify({
            'success': True,
            'count': len(users),
            'users': [u.to_dict() for u in users]
        })
    except Exception as e:
        logger.error(f"Error getting users: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user (admin only)"""
    # Get admin user_id from query parameter
    admin_user_id = request.args.get('admin_id', type=int)
    
    is_admin, error = check_admin_access(admin_user_id)
    
    if not is_admin:
        return jsonify({'success': False, 'error': 'Unauthorized. Admin access required.'}), 403
    
    # Prevent admin from deleting themselves
    if user_id == admin_user_id:
        return jsonify({'success': False, 'error': 'Cannot delete your own account'}), 400
    
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'User {user.username} deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting user: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>/make-admin', methods=['POST'])
def make_admin(user_id):
    """Make a user an admin (admin only)"""
    admin_user_id = request.args.get('admin_id', type=int)
    
    is_admin, error = check_admin_access(admin_user_id)
    
    if not is_admin:
        return jsonify({'success': False, 'error': 'Unauthorized. Admin access required.'}), 403
    
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        user.is_admin = True
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{user.username} is now an admin',
            'user': user.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error making admin: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>/remove-admin', methods=['POST'])
def remove_admin(user_id):
    """Remove admin status from a user (admin only)"""
    admin_user_id = request.args.get('admin_id', type=int)
    
    is_admin, error = check_admin_access(admin_user_id)
    
    if not is_admin:
        return jsonify({'success': False, 'error': 'Unauthorized. Admin access required.'}), 403
    
    if user_id == admin_user_id:
        return jsonify({'success': False, 'error': 'Cannot remove your own admin status'}), 400
    
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        user.is_admin = False
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{user.username} is no longer an admin',
            'user': user.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error removing admin: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>/toggle-active', methods=['POST'])
def toggle_user_active(user_id):
    """Activate or deactivate a user (admin only)"""
    admin_user_id = request.args.get('admin_id', type=int)
    
    is_admin, error = check_admin_access(admin_user_id)
    
    if not is_admin:
        return jsonify({'success': False, 'error': 'Unauthorized. Admin access required.'}), 403
    
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        user.is_active = not user.is_active
        db.session.commit()
        
        status = "activated" if user.is_active else "deactivated"
        return jsonify({
            'success': True,
            'message': f'User {user.username} {status}',
            'user': user.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error toggling user: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/stats', methods=['GET'])
def get_admin_stats():
    """Get admin dashboard statistics"""
    admin_user_id = request.args.get('admin_id', type=int)
    
    is_admin, error = check_admin_access(admin_user_id)
    
    if not is_admin:
        return jsonify({'success': False, 'error': 'Unauthorized. Admin access required.'}), 403
    
    try:
        total_users = User.query.count()
        total_tenders = Tender.query.count()
        admin_count = User.query.filter_by(is_admin=True).count()
        active_users = User.query.filter_by(is_active=True).count()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_users': total_users,
                'admin_count': admin_count,
                'active_users': active_users,
                'total_tenders': total_tenders,
                'sources': {}
            }
        })
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/check', methods=['GET'])
def check_admin():
    """Check if current user is admin"""
    try:
        # Get user_id from query parameter
        user_id = request.args.get('user_id', type=int)
        
        if not user_id:
            return jsonify({
                'success': True,
                'is_admin': False,
                'is_authenticated': False,
                'message': 'Not logged in'
            })
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'success': True,
                'is_admin': False,
                'is_authenticated': False,
                'message': 'User not found'
            })
        
        return jsonify({
            'success': True,
            'is_admin': user.is_admin,
            'is_authenticated': True,
            'username': user.username,
            'user_id': user.id
        })
        
    except Exception as e:
        logger.error(f"Error checking admin: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/session-debug', methods=['GET'])
def session_debug():
    """Debug endpoint to check session"""
    return jsonify({
        'session': dict(session),
        'user_id': session.get('user_id'),
        'is_admin': session.get('is_admin'),
        'is_authenticated': session.get('is_authenticated'),
        'session_keys': list(session.keys())
    })

@admin_bp.route('/force-session/<int:user_id>', methods=['POST'])
def force_session(user_id):
    """Force create a session for a user (debug only)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        session.clear()
        session['user_id'] = user.id
        session['username'] = user.username
        session['is_admin'] = user.is_admin
        session['is_authenticated'] = True
        
        return jsonify({
            'success': True,
            'message': f'Session created for {user.username}',
            'session': dict(session)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500