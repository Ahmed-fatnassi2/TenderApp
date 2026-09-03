# routes/it_notification_routes.py
from flask import Blueprint, request, jsonify, session
from models.user import User
from database import db
from services.it_notification_service import ITNotificationService
import logging

it_notification_bp = Blueprint('it_notification', __name__, url_prefix='/api/it-notifications')
logger = logging.getLogger(__name__)

@it_notification_bp.route('/send-test', methods=['POST'])
def send_test_notification():
    """Send a test IT notification to the current user"""
    try:
        # Get user ID from header or session
        user_id = request.headers.get('X-User-ID') or session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not user.preferences:
            return jsonify({'error': 'No preferences found'}), 400
        
        service = ITNotificationService()
        
        # Force send immediately
        logger.info(f"📧 Sending test IT notification to user {user.id}")
        success = service.send_daily_digest_for_user(user)
        
        return jsonify({
            'success': success,
            'message': 'Test IT notification sent' if success else 'Failed to send test notification',
            'user_email': user.email
        })
        
    except Exception as e:
        logger.error(f"Error sending test IT notification: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@it_notification_bp.route('/force-send/<int:user_id>', methods=['POST'])
def force_send(user_id):
    """Force send a notification to a specific user (admin only)"""
    try:
        admin_id = session.get('user_id') or request.headers.get('X-User-ID')
        if not admin_id:
            return jsonify({'error': 'Not authenticated'}), 401
        
        admin = User.query.get(admin_id)
        if not admin or not admin.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        service = ITNotificationService()
        success = service.send_daily_digest_for_user(user)
        
        return jsonify({
            'success': success,
            'message': f'Notification sent to user {user_id}' if success else 'Failed to send',
            'user': user.email
        })
        
    except Exception as e:
        logger.error(f"Error forcing send: {e}")
        return jsonify({'error': str(e)}), 500

@it_notification_bp.route('/send-all', methods=['POST'])
def send_to_all_users():
    """Send IT notifications to all users"""
    try:
        # Check if admin
        user_id = session.get('user_id') or request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user = User.query.get(user_id)
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        from services.it_scheduler import send_it_digest_for_all_users
        send_it_digest_for_all_users()
        
        return jsonify({
            'success': True,
            'message': 'IT notifications sent to all users'
        })
        
    except Exception as e:
        logger.error(f"Error sending to all users: {e}")
        return jsonify({'error': str(e)}), 500



@it_notification_bp.route('/debug-send', methods=['GET'])
def debug_send():
    """Debug endpoint to test email sending"""
    try:
        user_id = request.headers.get('X-User-ID') or session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Not authenticated'}), 401
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Test email service directly
        from services.email_service import EmailService
        email_service = EmailService()
        
        test_html = """
        <h1>Test Email</h1>
        <p>This is a test email from TenderApp.</p>
        <p>If you see this, the email service is working correctly.</p>
        """
        
        print(f"📧 Testing email to: {user.email}")
        success = email_service.send_email(
            to_email=user.email,
            subject="🧪 TenderApp Test Email",
            html_content=test_html,
            plain_text="Test email from TenderApp"
        )
        
        return jsonify({
            'success': success,
            'message': 'Test email sent' if success else 'Failed to send test email',
            'user_email': user.email,
            'smtp_user': email_service.smtp_user,
            'smtp_host': email_service.smtp_host,
            'smtp_port': email_service.smtp_port,
            'from_email': email_service.from_email
        })
        
    except Exception as e:
        logger.error(f"Debug send error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500