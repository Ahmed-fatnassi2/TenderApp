# routes/smart_construction_routes.py
from flask import Blueprint, request, jsonify
from services.smart_construction_agent import SmartConstructionAgent
import logging

logger = logging.getLogger(__name__)

smart_bp = Blueprint('smart_construction', __name__, url_prefix='/api/smart-construction')

_agent = None

def get_agent():
    global _agent
    if _agent is None:
        _agent = SmartConstructionAgent()
    return _agent

@smart_bp.route('/search', methods=['POST'])
def search():
    try:
        data = request.get_json()
        query = data.get('query', '')
        top_k = data.get('top_k', 10)
        
        if not query:
            return jsonify({'success': False, 'error': 'Query required'}), 400
        
        agent = get_agent()
        results = agent.search_tenders(query, top_k)
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@smart_bp.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({'success': False, 'error': 'Message required'}), 400
        
        agent = get_agent()
        response = agent.chat(message)
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@smart_bp.route('/analyze/<reference>', methods=['GET'])
def analyze(reference):
    try:
        agent = get_agent()
        result = agent._analyze_tender(reference)
        
        return jsonify({
            'success': True,
            'analysis': result
        })
        
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500