# routes/preferences_routes.py
from flask import Blueprint, request, jsonify, session
from models.user import User
from models.user_preferences import UserPreferences
from database import db
from services.notification_service import NotificationService
import logging

preferences_bp = Blueprint('preferences', __name__, url_prefix='/api/preferences')
logger = logging.getLogger(__name__)

def get_user_id():
    """Get user ID from request headers or query params"""
    # First try to get from header
    user_id = request.headers.get('X-User-ID')
    if user_id:
        return user_id
    
    # Then try from query params
    user_id = request.args.get('user_id')
    if user_id:
        return user_id
    
    # Finally try from session (for backward compatibility)
    user_id = session.get('user_id')
    return user_id

@preferences_bp.route('/', methods=['GET'])
def get_preferences():
    """Get current user's preferences"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # ✅ FIX: Use 'preferences' not 'user_preferences'
        prefs = user.preferences
        if not prefs:
            prefs = UserPreferences(user_id=user_id)
            db.session.add(prefs)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'preferences': prefs.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error getting preferences: {e}")
        return jsonify({'error': str(e)}), 500

@preferences_bp.route('/', methods=['PUT'])
def update_preferences():
    """Update user preferences"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # ✅ FIX: Use 'preferences' not 'user_preferences'
        prefs = user.preferences
        if not prefs:
            prefs = UserPreferences(user_id=user_id)
            db.session.add(prefs)
        
        # Update fields
        if 'notifications_enabled' in data:
            prefs.notifications_enabled = data['notifications_enabled']
        if 'frequency' in data:
            prefs.frequency = data['frequency']
        if 'send_time' in data:
            prefs.send_time = data['send_time']
        if 'custom_prompt' in data:
            prefs.custom_prompt = data['custom_prompt']
        if 'search_terms' in data:
            if isinstance(data['search_terms'], list):
                prefs.search_terms = prefs._join_list(data['search_terms'])
            else:
                prefs.search_terms = data['search_terms']
        if 'categories' in data:
            if isinstance(data['categories'], list):
                prefs.categories = prefs._join_list(data['categories'])
            else:
                prefs.categories = data['categories']
        if 'regions' in data:
            if isinstance(data['regions'], list):
                prefs.regions = prefs._join_list(data['regions'])
            else:
                prefs.regions = data['regions']
        if 'buyers' in data:
            if isinstance(data['buyers'], list):
                prefs.buyers = prefs._join_list(data['buyers'])
            else:
                prefs.buyers = data['buyers']
        if 'sources' in data:
            if isinstance(data['sources'], list):
                prefs.sources = prefs._join_list(data['sources'])
            else:
                prefs.sources = data['sources']
        if 'min_budget' in data:
            prefs.min_budget = data['min_budget']
        if 'max_budget' in data:
            prefs.max_budget = data['max_budget']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Preferences updated successfully',
            'preferences': prefs.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error updating preferences: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@preferences_bp.route('/test', methods=['POST'])
def test_preferences():
    """Test search with current preferences"""
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        from services.notification_service import NotificationService
        service = NotificationService()
        
        # ✅ FIX: Use 'preferences' not 'user_preferences'
        prefs = user.preferences
        if not prefs:
            prefs = UserPreferences(user_id=user_id)
            db.session.add(prefs)
            db.session.commit()
        
        # Search for tenders
        tenders = service.search_tenders_for_user(user)
        
        return jsonify({
            'success': True,
            'tenders_found': len(tenders),
            'tenders': tenders[:10]
        })
        
    except Exception as e:
        logger.error(f"Error testing preferences: {e}")
        return jsonify({'error': str(e)}), 500