# services/scheduler_manager.py
import threading
import time
import logging
from datetime import datetime
from flask import Flask

logger = logging.getLogger(__name__)

class SchedulerManager:
    """Manages the IT scheduler across Flask reloads"""
    
    _instance = None
    _lock = threading.Lock()
    _thread = None
    _running = False
    _app = None
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(SchedulerManager, cls).__new__(cls)
        return cls._instance
    
    def init_app(self, app: Flask):
        """Initialize with Flask app"""
        self._app = app
        # Also initialize the it_scheduler module
        from services.it_scheduler import init_scheduler
        init_scheduler(app)
        logger.info("✅ SchedulerManager initialized with app")
        print("✅ SchedulerManager initialized with app")
    
    def start(self):
        """Start the scheduler in a background thread"""
        if self._running:
            logger.info("⚠️ Scheduler already running")
            return
        
        if not self._app:
            logger.error("❌ SchedulerManager not initialized with app")
            print("❌ SchedulerManager not initialized with app")
            return
        
        logger.info("🚀 Starting IT scheduler...")
        self._running = True
        
        def run_scheduler():
            import schedule
            from services.it_scheduler import check_user_send_times, send_it_digest_for_all_users
            
            # Clear any existing schedules
            schedule.clear()
            
            # Schedule for specific times
            schedule.every().day.at("08:00").do(send_it_digest_for_all_users)
            schedule.every().day.at("09:00").do(send_it_digest_for_all_users)
            
            # Check every minute for user-specific times
            schedule.every(1).minutes.do(check_user_send_times)
            
            print("=" * 60)
            print("⏰ IT SCHEDULER RUNNING:")
            print("  - 08:00 AM (daily)")
            print("  - 09:00 AM (daily)")
            print("  - Every minute (user-specific times)")
            print("=" * 60)
            
            # Run initial test
            print("🧪 Running initial test digest...")
            send_it_digest_for_all_users()
            
            print("✅ Scheduler thread active - checking every 30 seconds")
            
            while self._running:
                try:
                    schedule.run_pending()
                    time.sleep(30)
                except Exception as e:
                    print(f"Scheduler error: {e}")
                    time.sleep(30)
        
        self._thread = threading.Thread(target=run_scheduler, daemon=True)
        self._thread.start()
        print("✅ IT scheduler thread started")
    
    def stop(self):
        """Stop the scheduler"""
        self._running = False
        if self._thread:
            print("🛑 Stopping IT scheduler...")
            self._thread = None

# Create a global instance
scheduler_manager = SchedulerManager()