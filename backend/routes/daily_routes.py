# routes/daily_routes.py
from flask import Blueprint, request, jsonify
from services.daily_tender_service import DailyTenderService
import logging

daily_bp = Blueprint('daily', __name__, url_prefix='/api/daily')
logger = logging.getLogger(__name__)

@daily_bp.route('/send-digest', methods=['POST'])
def send_daily_digest():
    """Manually trigger daily digest"""
    try:
        service = DailyTenderService()
        success = service.send_daily_digest()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Daily digest sent successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to send daily digest'
            }), 500
            
    except Exception as e:
        logger.error(f"Error in daily digest endpoint: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@daily_bp.route('/test-digest', methods=['GET'])
def test_daily_digest():
    """Test the daily digest with preview"""
    try:
        service = DailyTenderService()
        tenders = service.get_new_tenders_last_24h()
        
        return jsonify({
            'success': True,
            'tenders_found': len(tenders),
            'tenders': tenders[:10]  # Show first 10
        })
        
    except Exception as e:
        logger.error(f"Error testing daily digest: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500