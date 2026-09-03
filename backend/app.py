# # app/__init__.py
# from flask import Flask, jsonify, request
# from flask_cors import CORS
# from dotenv import load_dotenv
# import os

# load_dotenv()

# from database import db, migrate
# from models import Tender, User
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
#     app.config['SESSION_COOKIE_SECURE'] = False  # Set to False for development
#     app.config['SESSION_COOKIE_HTTPONLY'] = True
#     app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
#     # Initialize extensions with app
#     db.init_app(app)
#     migrate.init_app(app, db)
    
#     # --- SINGLE CORS CONFIGURATION ---
#     CORS(app, 
#          supports_credentials=True,
#          origins=['http://localhost:3000', 'http://127.0.0.1:3000', 
#                   'http://localhost:5173', 'http://127.0.0.1:5173'],
#          methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
#          allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
#          expose_headers=['Content-Type', 'Authorization'],
#          max_age=600)
    
#     # Register blueprints
#     app.register_blueprint(auth_bp)
#     app.register_blueprint(openrag_bp)
#     app.register_blueprint(agent_bp)
    
#     # --- Health Routes ---
#     @app.route('/api/health')
#     def health():
#         return jsonify({
#             'status': 'healthy',
#             'database': 'PostgreSQL' if 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI'] else 'Unknown',
#             'message': 'Connected to PostgreSQL!'
#         })
    
#     # --- Tender Routes ---
#     @app.route('/api/tenders', methods=['GET'])
#     def get_tenders():
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
    
#     @app.route('/api/tenders/scrape', methods=['POST'])
#     def scrape_tenders():
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
    
#     @app.route('/api/tenders/<string:reference>', methods=['GET'])
#     def get_tender_by_reference(reference):
#         tender = Tender.query.filter_by(reference=reference).first()
#         if tender:
#             return jsonify(tender.to_dict())
#         return jsonify({'error': 'Tender not found'}), 404
    
#     @app.route('/api/tenders/<int:tender_id>', methods=['DELETE'])
#     def delete_tender(tender_id):
#         tender = Tender.query.get(tender_id)
#         if tender:
#             db.session.delete(tender)
#             db.session.commit()
#             return jsonify({'message': 'Tender deleted'})
#         return jsonify({'error': 'Tender not found'}), 404
    
#     @app.route('/api/tenders/count', methods=['GET'])
#     def count_tenders():
#         count = Tender.query.count()
#         return jsonify({'total': count})
    
#     return app

# # Create app instance
# app = create_app()

# if __name__ == "__main__":
#     print("🚀 Starting Flask server on http://localhost:5000")
#     app.run(debug=True, host="0.0.0.0", port=5000)


# app.py (in the root of your backend)
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_session import Session
from dotenv import load_dotenv
import os

load_dotenv()

from database import db, migrate
from models.tender import Tender
from models.user import User
from services import TUNEPSListingScraper
from services.openrag_client import OpenRAGClient
from routes.openrag_routes import openrag_bp
from routes.agent_routes import agent_bp
from routes.auth_routes import auth_bp
from routes.scraper_routes import scraper_bp
from routes.smart_construction_routes import smart_bp
from routes.admin_routes import admin_bp
# app.py - Add this line
from routes.daily_routes import daily_bp
# from services.scheduler import start_scheduler
# from services.scheduler import start_scheduler, stop_scheduler
from routes.oidc_routes import oidc_bp
from services.oidc_service import init_oidc
from routes.preferences_routes import preferences_bp
from routes.it_notification_routes import it_notification_bp
# from services.it_scheduler import start_it_scheduler, stop_it_scheduler
from services.it_scheduler import start_it_scheduler, stop_it_scheduler, init_scheduler
from services.scheduler_manager import scheduler_manager
from services.scraper_scheduler import start_scraper_scheduler, stop_scraper_scheduler
import atexit
# Create Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.register_blueprint(scraper_bp)
app.register_blueprint(smart_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(daily_bp)
app.register_blueprint(preferences_bp)
app.register_blueprint(it_notification_bp)
init_oidc(app)

db.init_app(app)
migrate.init_app(app, db)
Session(app)

# --- CORS Configuration ---
CORS(app, 
     supports_credentials=True,
     origins=['http://localhost:3000', 'http://127.0.0.1:3000', 
              'http://localhost:5173', 'http://127.0.0.1:5173',
              'http://localhost:5000', 'http://127.0.0.1:5000'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization', 'X-Requested-With', 'X-User-ID'],
     expose_headers=['Content-Type', 'Authorization', 'X-User-ID'],
     max_age=600)



try:
    init_oidc(app)
    print("✅ OIDC initialized successfully")
except Exception as e:
    print(f"❌ OIDC initialization failed: {e}")

# Register blueprints
app.register_blueprint(oidc_bp)


# --- Global before_request handler for CORS ---
# @app.before_request
# def handle_preflight():
#     if request.method == "OPTIONS":
#         response = app.make_default_options_response()
#         response.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
#         response.headers["Access-Control-Allow-Credentials"] = "true"
#         response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
#         response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
#         return response
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = app.make_default_options_response()
        response.headers["Access-Control-Allow-Origin"] = "http://localhost:5173"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, X-User-ID"  # ✅ Added X-User-ID
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        return response
# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(openrag_bp) 
app.register_blueprint(agent_bp) 

# --- Health Routes ---
@app.route('/api/health', methods=['GET', 'OPTIONS'])
def health():
    if request.method == 'OPTIONS':
        return '', 200
    return jsonify({
        'status': 'healthy',
        'database': 'PostgreSQL' if 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI'] else 'Unknown',
        'message': 'Connected to PostgreSQL!'
    })

# --- Tender Routes ---
@app.route('/api/tenders', methods=['GET', 'OPTIONS'])
def get_tenders():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10000, type=int)
        
        page = max(1, page)
        per_page = max(1, per_page)
        
        query = Tender.query.order_by(Tender.scraped_at.desc())
        total = query.count()
        
        tenders = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return jsonify({
            'success': True,
            'data': [t.to_dict() for t in tenders],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': (total + per_page - 1) // per_page
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tenders/scrape', methods=['POST', 'OPTIONS'])
def scrape_tenders():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        scraper = TUNEPSListingScraper()
        result = scraper.scrape_and_save(db, Tender)
        return jsonify({
            'success': True,
            'message': f"Added {result['new']} new tenders",
            'data': result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tenders/<string:reference>', methods=['GET', 'OPTIONS'])
def get_tender_by_reference(reference):
    if request.method == 'OPTIONS':
        return '', 200
    tender = Tender.query.filter_by(reference=reference).first()
    if tender:
        return jsonify(tender.to_dict())
    return jsonify({'error': 'Tender not found'}), 404

@app.route('/api/tenders/<int:tender_id>', methods=['DELETE', 'OPTIONS'])
def delete_tender(tender_id):
    if request.method == 'OPTIONS':
        return '', 200
    tender = Tender.query.get(tender_id)
    if tender:
        db.session.delete(tender)
        db.session.commit()
        return jsonify({'message': 'Tender deleted'})
    return jsonify({'error': 'Tender not found'}), 404

@app.route('/api/tenders/count', methods=['GET', 'OPTIONS'])
def count_tenders():
    if request.method == 'OPTIONS':
        return '', 200
    count = Tender.query.count()
    return jsonify({'total': count})


# ===== START DAILY SCHEDULER =====
# # Only start scheduler in the main process (not the debug reloader)
# if not os.environ.get('WERKZEUG_RUN_MAIN'):
#     print("⏰ Starting daily tender scheduler...")
#     scheduler_thread = start_scheduler()
#     atexit.register(stop_scheduler)
#     print("✅ Daily tender scheduler started - will send at 08:00 AM")
# # ===== END SCHEDULER =====



if not os.environ.get('WERKZEUG_RUN_MAIN'):
    print("⏰ Starting IT tender scheduler...")
    from services.it_scheduler import start_it_scheduler, stop_it_scheduler
    it_scheduler_thread = start_it_scheduler(app)
    atexit.register(stop_it_scheduler)
    print("✅ IT tender scheduler started")



# ===== START SCRAPER SCHEDULER =====
if not os.environ.get('WERKZEUG_RUN_MAIN'):
    print("⏰ Starting scraper scheduler...")
    scraper_scheduler_thread = start_scraper_scheduler(app)
    atexit.register(stop_scraper_scheduler)
    print("✅ Scraper scheduler started - will run at 02:00 and 03:00 AM")
# ===== END SCRAPER SCHEDULER =====




if __name__ == "__main__":
    print("🚀 Starting Flask server on http://localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)

