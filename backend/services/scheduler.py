# import schedule
# import time
# import threading
# import logging
# from datetime import datetime
# from services.daily_tender_service import DailyTenderService

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# scheduler_thread = None

# def send_daily_digest():
#     """Send daily digest of new tenders"""
#     try:
#         logger.info(f"📧 Sending daily digest - {datetime.now()}")
#         service = DailyTenderService()
#         result = service.send_daily_digest()
#         if result:
#             logger.info("✅ Daily digest sent successfully")
#         else:
#             logger.error("❌ Failed to send daily digest")
#     except Exception as e:
#         logger.error(f"❌ Error sending daily digest: {e}")

# def start_scheduler():
#     """Start the scheduler in a background thread"""
#     global scheduler_thread
    
#     # Clear any existing schedules
#     schedule.clear()
    
#     # Schedule for 8 AM Tunisian time
#     schedule.every().day.at("08:00").do(send_daily_digest)
    
#     # FOR TESTING ONLY - remove this line in production
#     # schedule.every().day.at("10:48").do(send_daily_digest)
    
#     logger.info("⏰ Daily scheduler configured - will run at 08:00 AM Tunisian time")
    
#     # Run once immediately for testing
#     logger.info("🧪 Running initial test digest...")
#     send_daily_digest()
    
#     def run_scheduler():
#         while True:
#             schedule.run_pending()
#             time.sleep(30)
    
#     scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
#     scheduler_thread.start()
#     logger.info("✅ Scheduler running in background")
    
#     return scheduler_thread

# def stop_scheduler():
#     """Stop the scheduler"""
#     global scheduler_thread
#     if scheduler_thread:
#         logger.info("🛑 Stopping scheduler...")
#         scheduler_thread = None
#         schedule.clear()

# if __name__ == "__main__":
#     start_scheduler()
#     try:
#         while True:
#             time.sleep(60)
#     except KeyboardInterrupt:
#         logger.info("🛑 Scheduler stopped")