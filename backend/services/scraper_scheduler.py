# # services/scraper_scheduler.py - FIXED

# import schedule
# import time
# import threading
# import logging
# from datetime import datetime

# logger = logging.getLogger(__name__)

# scraper_scheduler_thread = None
# _app = None
# _scraper_running = False

# def run_scrape_and_index():
#     """Call the existing scrape_all_and_index route"""
#     global _app
    
#     if not _app:
#         print("❌ Scraper scheduler not initialized")
#         return
    
#     # ✅ FIX: Use app.app_context() not app.context()
#     with _app.app_context():
#         try:
#             print("=" * 60)
#             print(f"🔄 [SCRAPER SCHEDULER] Running scrape and index at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
#             # Import and call the existing route function directly
#             from routes.scraper_routes import scrape_all_and_index
            
#             # Call the function that your button uses
#             result = scrape_all_and_index()
            
#             # Print result (it returns a Flask Response object)
#             if result and hasattr(result, 'status_code'):
#                 if result.status_code == 200:
#                     try:
#                         import json
#                         data = json.loads(result.get_data(as_text=True))
#                         if data.get('success'):
#                             print(f"✅ Scrape and index completed: {data.get('message')}")
#                         else:
#                             print(f"❌ Scrape and index failed: {data.get('error')}")
#                     except:
#                         print(f"✅ Scrape and index completed (status: {result.status_code})")
#                 else:
#                     print(f"❌ Scrape and index failed with status: {result.status_code}")
#             else:
#                 print(f"✅ Scrape and index triggered")
            
#             print("=" * 60)
            
#         except Exception as e:
#             print(f"❌ [SCRAPER SCHEDULER] Error in scrape and index: {e}")
#             import traceback
#             traceback.print_exc()

# def run_delete_expired():
#     """Call the existing delete_expired_tenders route"""
#     global _app
    
#     if not _app:
#         print("❌ Scraper scheduler not initialized")
#         return
    
#     # ✅ FIX: Use app.app_context() not app.context()
#     with _app.app_context():
#         try:
#             print("=" * 60)
#             print(f"🗑️ [SCRAPER SCHEDULER] Running delete expired at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
#             # Import and call the existing route function directly
#             from routes.scraper_routes import delete_expired_tenders
            
#             # Call the function that your button uses
#             result = delete_expired_tenders()
            
#             # Print result
#             if result and hasattr(result, 'status_code'):
#                 if result.status_code == 200:
#                     try:
#                         import json
#                         data = json.loads(result.get_data(as_text=True))
#                         if data.get('success'):
#                             deleted_count = data.get('data', {}).get('deleted_count', 0)
#                             print(f"✅ Delete expired completed: {deleted_count} tenders deleted")
#                         else:
#                             print(f"❌ Delete expired failed: {data.get('error')}")
#                     except:
#                         print(f"✅ Delete expired completed (status: {result.status_code})")
#                 else:
#                     print(f"❌ Delete expired failed with status: {result.status_code}")
#             else:
#                 print(f"✅ Delete expired triggered")
            
#             print("=" * 60)
            
#         except Exception as e:
#             print(f"❌ [SCRAPER SCHEDULER] Error in delete expired: {e}")
#             import traceback
#             traceback.print_exc()

# def start_scraper_scheduler(app):
#     """Start the scraper scheduler in a background thread"""
#     global scraper_scheduler_thread, _app, _scraper_running
    
#     if _scraper_running:
#         print("⚠️ Scraper scheduler already running")
#         return scraper_scheduler_thread
    
#     # Store app reference
#     _app = app
    
#     # Clear any existing schedules
#     schedule.clear()
    
#     # Production times (uncomment for production)
#     # schedule.every().day.at("02:00").do(run_scrape_and_index)
#     # schedule.every().day.at("03:00").do(run_delete_expired)
    
#     # 🔧 TEST TIMES - Change to your current time + 2-3 minutes
#     # Example: If it's 15:30 now, set to 15:33 and 15:36
#     schedule.every().day.at("03:34").do(run_scrape_and_index)   # TEST
#     schedule.every().day.at("03:37").do(run_delete_expired)     # TEST
    
#     print("=" * 60)
#     print("⏰ SCRAPER SCHEDULER CONFIGURED:")
#     print("  - 14:33: Scrape and Index (TEST)")
#     print("  - 14:36: Delete Expired Tenders (TEST)")
#     print("=" * 60)
    
#     # Run once immediately for testing
#     print("🧪 Running initial test...")
#     run_scrape_and_index()
    
#     def run_scheduler():
#         global _scraper_running
#         _scraper_running = True
#         print("✅ Scraper scheduler thread started - checking every 30 seconds")
#         while _scraper_running:
#             try:
#                 schedule.run_pending()
#                 time.sleep(30)
#             except Exception as e:
#                 print(f"Scraper scheduler error: {e}")
#                 time.sleep(30)
    
#     scraper_scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
#     scraper_scheduler_thread.start()
#     print("✅ Scraper scheduler running in background")
#     print("=" * 60)
    
#     return scraper_scheduler_thread

# def stop_scraper_scheduler():
#     """Stop the scraper scheduler"""
#     global scraper_scheduler_thread, _scraper_running
#     if scraper_scheduler_thread:
#         print("🛑 Stopping scraper scheduler...")
#         _scraper_running = False
#         scraper_scheduler_thread = None
#         schedule.clear()
        



# services/scraper_scheduler.py - UPDATED with delete expired

import schedule
import time
import threading
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

scraper_scheduler_thread = None
_app = None
_scraper_running = False

def run_scrape_and_index():
    """Call the existing scrape_all_and_index route"""
    global _app
    
    if not _app:
        print("❌ Scraper scheduler not initialized")
        return
    
    with _app.app_context():
        try:
            print("=" * 60)
            print(f"🔄 [SCRAPER SCHEDULER] Running scrape and index at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            from routes.scraper_routes import scrape_all_and_index
            
            result = scrape_all_and_index()
            
            if result and hasattr(result, 'status_code'):
                if result.status_code == 200:
                    try:
                        import json
                        data = json.loads(result.get_data(as_text=True))
                        if data.get('success'):
                            print(f"✅ Scrape and index completed: {data.get('message')}")
                        else:
                            print(f"❌ Scrape and index failed: {data.get('error')}")
                    except:
                        print(f"✅ Scrape and index completed (status: {result.status_code})")
                else:
                    print(f"❌ Scrape and index failed with status: {result.status_code}")
            else:
                print(f"✅ Scrape and index triggered")
            
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ [SCRAPER SCHEDULER] Error in scrape and index: {e}")
            import traceback
            traceback.print_exc()

def run_check_expired():
    """Call the existing check_expired_deadlines route"""
    global _app
    
    if not _app:
        print("❌ Scraper scheduler not initialized")
        return
    
    with _app.app_context():
        try:
            print("=" * 60)
            print(f"🔍 [SCRAPER SCHEDULER] Checking expired deadlines at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            from routes.scraper_routes import check_expired_deadlines
            
            result = check_expired_deadlines()
            
            if result and hasattr(result, 'status_code'):
                if result.status_code == 200:
                    try:
                        import json
                        data = json.loads(result.get_data(as_text=True))
                        if data.get('success'):
                            expired_count = data.get('data', {}).get('expired_count', 0)
                            print(f"✅ Check expired completed: {expired_count} expired tenders found")
                        else:
                            print(f"❌ Check expired failed: {data.get('error')}")
                    except:
                        print(f"✅ Check expired completed (status: {result.status_code})")
                else:
                    print(f"❌ Check expired failed with status: {result.status_code}")
            else:
                print(f"✅ Check expired triggered")
            
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ [SCRAPER SCHEDULER] Error in check expired: {e}")
            import traceback
            traceback.print_exc()

def run_delete_expired():
    """Call the existing delete_expired_tenders route - same as the button"""
    global _app
    
    if not _app:
        print("❌ Scraper scheduler not initialized")
        return
    
    with _app.app_context():
        try:
            print("=" * 60)
            print(f"🗑️ [SCRAPER SCHEDULER] Running delete expired at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Import and call the EXACT SAME function as the button
            from routes.scraper_routes import delete_expired_tenders
            
            # This is the same function your dashboard button calls
            result = delete_expired_tenders()
            
            if result and hasattr(result, 'status_code'):
                if result.status_code == 200:
                    print(f"✅ Delete expired completed successfully")
                else:
                    print(f"❌ Delete expired failed with status: {result.status_code}")
            else:
                print(f"✅ Delete expired triggered")
            
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ [SCRAPER SCHEDULER] Error in delete expired: {e}")
            import traceback
            traceback.print_exc()

# def start_scraper_scheduler(app):
#     """Start the scraper scheduler in a background thread"""
#     global scraper_scheduler_thread, _app, _scraper_running
    
#     if _scraper_running:
#         print("⚠️ Scraper scheduler already running")
#         return scraper_scheduler_thread
    
#     _app = app
    
#     schedule.clear()
    
#     # 🔧 TEST TIMES - Change to your current time + a few minutes
#     # Example: If it's 15:45 now:
#     schedule.every().day.at("10:33").do(run_scrape_and_index)      # Run at 03:45
#     schedule.every().day.at("11:40").do(run_check_expired)         # Run at 03:47
#     schedule.every().day.at("11:41").do(run_delete_expired)        # Run at 03:49
    
#     # For production, uncomment these:
#     # schedule.every().day.at("02:00").do(run_scrape_and_index)
#     # schedule.every().day.at("02:30").do(run_check_expired)
#     # schedule.every().day.at("03:00").do(run_delete_expired)
    
#     print("=" * 60)
#     print("⏰ SCRAPER SCHEDULER CONFIGURED (TEST MODE):")
#     print("  - 03:45: Scrape and Index")
#     print("  - 03:47: Check Expired Deadlines")
#     print("  - 03:49: Delete Expired Tenders")
#     print("=" * 60)
    
#     # Run once immediately for testing
#     print("🧪 Running initial test...")
#     run_scrape_and_index()
#     run_check_expired()
#     run_delete_expired()
    
#     def run_scheduler():
#         global _scraper_running
#         _scraper_running = True
#         print("✅ Scraper scheduler thread started - checking every 30 seconds")
#         while _scraper_running:
#             try:
#                 schedule.run_pending()
#                 time.sleep(30)
#             except Exception as e:
#                 print(f"Scraper scheduler error: {e}")
#                 time.sleep(30)
    
#     scraper_scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
#     scraper_scheduler_thread.start()
#     print("✅ Scraper scheduler running in background")
#     print("=" * 60)
    
#     return scraper_scheduler_thread
# services/scraper_scheduler.py


def start_scraper_scheduler(app):
    """Start the scraper scheduler in a background thread"""
    global scraper_scheduler_thread, _app, _scraper_running
    
    if _scraper_running:
        print("⚠️ Scraper scheduler already running")
        return scraper_scheduler_thread
    
    _app = app
    
    schedule.clear()
    
    # ✅ PRODUCTION TIMES - Only these should run
    schedule.every().day.at("07:00").do(run_scrape_and_index)
    schedule.every().day.at("07:30").do(run_check_expired)
    schedule.every().day.at("07:32").do(run_delete_expired)
    
    # ❌ REMOVE ALL TEST TIMES
    # schedule.every().day.at("11:47").do(run_check_expired)
    # schedule.every().day.at("11:48").do(run_delete_expired)
    
    print("=" * 60)
    print("⏰ SCRAPER SCHEDULER CONFIGURED:")
    print("  - 07:00 AM: Scrape and Index")
    print("  - 07:28 AM: Check Expired Deadlines")
    print("  - 07:30 AM: Delete Expired Tenders")
    print("=" * 60)
    
    # ❌ REMOVE initial test runs
    # print("🧪 Running initial test...")
    # run_scrape_and_index()
    # run_check_expired()
    # run_delete_expired()
    
    def run_scheduler():
        global _scraper_running
        _scraper_running = True
        print("✅ Scraper scheduler thread started - waiting for scheduled times")
        while _scraper_running:
            try:
                schedule.run_pending()
                time.sleep(30)
            except Exception as e:
                print(f"Scraper scheduler error: {e}")
                time.sleep(30)
    
    scraper_scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scraper_scheduler_thread.start()
    print("✅ Scraper scheduler running in background")
    print("=" * 60)
    
    return scraper_scheduler_thread
def stop_scraper_scheduler():
    """Stop the scraper scheduler"""
    global scraper_scheduler_thread, _scraper_running
    if scraper_scheduler_thread:
        print("🛑 Stopping scraper scheduler...")
        _scraper_running = False
        scraper_scheduler_thread = None
        schedule.clear()