from .tender import Tender
from .user import User
from .user_preferences import UserPreferences
__all__ = ['Tender', 'User', 'UserPreferences']

# # app/__init__.py
# from flask import Flask, jsonify, request
# from flask_cors import CORS
# from dotenv import load_dotenv
# import os

# load_dotenv()

# from database import db, migrate
# # Import directly from files instead of using __init__.py
# from models.tender import Tender
# from models.user import User
# from services import TUNEPSListingScraper
# from services.openrag_client import OpenRAGClient
# from routes.openrag_routes import openrag_bp
# from routes.agent_routes import agent_bp
# from routes.auth_routes import auth_bp

# def create_app():
#     app = Flask(__name__)
    
#     # Configuration
#     app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
#     app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#     app.config['SESSION_TYPE'] = 'filesystem'
#     app.config['SESSION_PERMANENT'] = False
#     app.config['SESSION_USE_SIGNER'] = True
#     app.config['SESSION_COOKIE_SECURE'] = False
#     app.config['SESSION_COOKIE_HTTPONLY'] = True
#     app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
#     # Initialize extensions with app
#     db.init_app(app)
#     migrate.init_app(app, db)
    
#     # --- CORS Configuration ---
#     CORS(app, 
#          supports_credentials=True,
#          origins=['http://localhost:3000', 'http://127.0.0.1:3000', 
#                   'http://localhost:5173', 'http://127.0.0.1:5173'],
#          methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
#          allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
#          expose_headers=['Content-Type', 'Authorization'],
#          max_age=600)
    
#     # --- Global before_request handler for CORS ---
#     @app.before_request
#     def handle_preflight():
#         if request.method == "OPTIONS":
#             response = app.make_default_options_response()
#             response.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
#             response.headers["Access-Control-Allow-Credentials"] = "true"
#             response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
#             response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
#             return response
    
#     # Register blueprints
#     app.register_blueprint(auth_bp, url_prefix='/api')
#     app.register_blueprint(openrag_bp, url_prefix='/api')
#     app.register_blueprint(agent_bp, url_prefix='/api')
    
#     # --- Health Routes ---
#     @app.route('/api/health', methods=['GET', 'OPTIONS'])
#     def health():
#         if request.method == 'OPTIONS':
#             return '', 200
#         return jsonify({
#             'status': 'healthy',
#             'database': 'PostgreSQL' if 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI'] else 'Unknown',
#             'message': 'Connected to PostgreSQL!'
#         })
    
#     # --- Tender Routes ---
#     @app.route('/api/tenders', methods=['GET', 'OPTIONS'])
#     def get_tenders():
#         if request.method == 'OPTIONS':
#             return '', 200
#         try:
#             page = request.args.get('page', 1, type=int)
#             per_page = request.args.get('per_page', 10000, type=int)
            
#             page = max(1, page)
#             per_page = max(1, per_page)
            
#             query = Tender.query.order_by(Tender.scraped_at.desc())
#             total = query.count()
            
#             tenders = query.offset((page - 1) * per_page).limit(per_page).all()
            
#             return jsonify({
#                 'success': True,
#                 'data': [t.to_dict() for t in tenders],
#                 'pagination': {
#                     'page': page,
#                     'per_page': per_page,
#                     'total': total,
#                     'total_pages': (total + per_page - 1) // per_page
#                 }
#             })
#         except Exception as e:
#             return jsonify({'success': False, 'error': str(e)}), 500
    
#     @app.route('/api/tenders/scrape', methods=['POST', 'OPTIONS'])
#     def scrape_tenders():
#         if request.method == 'OPTIONS':
#             return '', 200
#         try:
#             scraper = TUNEPSListingScraper()
#             result = scraper.scrape_and_save(db, Tender)
#             return jsonify({
#                 'success': True,
#                 'message': f"Added {result['new']} new tenders",
#                 'data': result
#             })
#         except Exception as e:
#             return jsonify({'success': False, 'error': str(e)}), 500
    
#     @app.route('/api/tenders/<string:reference>', methods=['GET', 'OPTIONS'])
#     def get_tender_by_reference(reference):
#         if request.method == 'OPTIONS':
#             return '', 200
#         tender = Tender.query.filter_by(reference=reference).first()
#         if tender:
#             return jsonify(tender.to_dict())
#         return jsonify({'error': 'Tender not found'}), 404
    
#     @app.route('/api/tenders/<int:tender_id>', methods=['DELETE', 'OPTIONS'])
#     def delete_tender(tender_id):
#         if request.method == 'OPTIONS':
#             return '', 200
#         tender = Tender.query.get(tender_id)
#         if tender:
#             db.session.delete(tender)
#             db.session.commit()
#             return jsonify({'message': 'Tender deleted'})
#         return jsonify({'error': 'Tender not found'}), 404
    
#     @app.route('/api/tenders/count', methods=['GET', 'OPTIONS'])
#     def count_tenders():
#         if request.method == 'OPTIONS':
#             return '', 200
#         count = Tender.query.count()
#         return jsonify({'total': count})
    
#     return app

# # Create app instance
# app = create_app()

# if __name__ == "__main__":
#     print("🚀 Starting Flask server on http://localhost:5000")
#     app.run(debug=True, host="0.0.0.0", port=5000)