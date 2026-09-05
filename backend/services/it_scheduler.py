# # services/it_scheduler.py
# import schedule
# import time
# import threading
# import logging
# from datetime import datetime
# import os

# logger = logging.getLogger(__name__)

# it_scheduler_thread = None
# _app = None
# _scheduler_running = False

# def init_scheduler(app):
#     """Initialize scheduler with Flask app"""
#     global _app
#     _app = app
#     logger.info("✅ Scheduler initialized with app context")
#     print("✅ Scheduler initialized with app context")

# def send_it_digest_for_all_users():
#     """Send IT digest to all users with notifications enabled"""
#     global _app
    
#     if not _app:
#         logger.error("❌ Scheduler not initialized - call init_scheduler(app) first")
#         print("❌ Scheduler not initialized")
#         return
    
#     try:
#         with _app.app_context():
#             from database import db
#             from models.user import User
#             from models.user_preferences import UserPreferences
#             from services.it_notification_service import ITNotificationService
            
#             print("=" * 60)
#             print(f"📧 [SCHEDULER] send_it_digest_for_all_users STARTED at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
#             # Get all users with notifications enabled
#             users = User.query.join(User.preferences).filter(
#                 UserPreferences.notifications_enabled == True
#             ).all()
            
#             print(f"📧 [SCHEDULER] Found {len(users)} users with notifications enabled")
            
#             if not users:
#                 logger.info("No users with notifications enabled")
#                 print("No users with notifications enabled")
#                 return
            
#             service = ITNotificationService()
#             success_count = 0
            
#             for user in users:
#                 try:
#                     print(f"📧 [SCHEDULER] Processing user {user.id} - {user.email}")
#                     print(f"📧 [SCHEDULER]   User object type: {type(user)}")
#                     print(f"📧 [SCHEDULER]   Has preferences: {hasattr(user, 'preferences')}")
#                     print(f"📧 [SCHEDULER]   preferences: {user.preferences}")
                    
#                     if user.preferences:
#                         print(f"📧 [SCHEDULER]   notifications_enabled: {user.preferences.notifications_enabled}")
#                         print(f"📧 [SCHEDULER]   send_time: {user.preferences.send_time}")
#                         print(f"📧 [SCHEDULER]   last_sent_at: {user.preferences.last_sent_at}")
                    
#                     # Check if already sent today
#                     if user.preferences and user.preferences.last_sent_at:
#                         today = datetime.now().date()
#                         last_sent = user.preferences.last_sent_at.date()
#                         if last_sent == today:
#                             logger.info(f"Already sent today to user {user.id}, skipping")
#                             print(f"📧 [SCHEDULER] Already sent today to user {user.id}, skipping")
#                             continue
                    
#                     print(f"📧 [SCHEDULER] Calling service.send_daily_digest_for_user...")
                    
#                     # Call the method and capture the result
#                     result = service.send_daily_digest_for_user(user)
                    
#                     print(f"📧 [SCHEDULER] Result: {result}")
                    
#                     if result:
#                         success_count += 1
#                         print(f"✅ Sent to user {user.id} ({user.email})")
#                     else:
#                         print(f"❌ Failed to send to user {user.id} ({user.email})")
                        
#                 except Exception as e:
#                     logger.error(f"Error sending to user {user.id}: {e}")
#                     print(f"❌ Error sending to user {user.id}: {e}")
#                     import traceback
#                     traceback.print_exc()
            
#             logger.info(f"✅ IT digest sent to {success_count}/{len(users)} users")
#             print(f"✅ IT digest sent to {success_count}/{len(users)} users")
#             print("=" * 60)
            
#     except Exception as e:
#         logger.error(f"❌ Error sending IT digest: {e}")
#         print(f"❌ Error sending IT digest: {e}")
#         import traceback
#         traceback.print_exc()

# def check_user_send_times():
#     """Check if any user has a matching send_time"""
#     global _app
    
#     if not _app:
#         logger.error("❌ Scheduler not initialized")
#         print("❌ Scheduler not initialized")
#         return
    
#     try:
#         with _app.app_context():
#             from models.user import User
#             from models.user_preferences import UserPreferences
            
#             current_time = datetime.now().strftime('%H:%M')
            
#             # Print every minute so we can see it's working
#             print(f"⏰ Scheduler checking time: {current_time}")
            
#             # Check if any user has this send_time
#             users = User.query.join(User.preferences).filter(
#                 UserPreferences.notifications_enabled == True,
#                 UserPreferences.send_time == current_time
#             ).all()
            
#             if users:
#                 print(f"🎯 Found {len(users)} user(s) with send_time {current_time}")
#                 send_it_digest_for_all_users()
            
#     except Exception as e:
#         print(f"Error checking user times: {e}")
#         import traceback
#         traceback.print_exc()

# def start_it_scheduler(app):
#     """Start the scheduler in a background thread"""
#     global it_scheduler_thread, _app, _scheduler_running
    
#     if _scheduler_running:
#         logger.info("⚠️ Scheduler already running")
#         return it_scheduler_thread
    
#     # Store app reference
#     _app = app
    
#     # Clear any existing schedules
#     schedule.clear()
    
#     # Schedule for specific times
#     schedule.every().day.at("08:00").do(send_it_digest_for_all_users)
#     schedule.every().day.at("09:00").do(send_it_digest_for_all_users)
    
#     # Also check every minute for user-specific times
#     schedule.every(1).minutes.do(check_user_send_times)
    
#     # Log using print so it always shows
#     print("=" * 60)
#     print("⏰ IT SCHEDULER CONFIGURED:")
#     print("  - 08:00 AM (daily)")
#     print("  - 09:00 AM (daily)")
#     print("  - Every minute (user-specific times)")
#     print("=" * 60)
    
#     # Run once immediately for testing
#     print("🧪 Running initial test digest...")
#     send_it_digest_for_all_users()
    
#     def run_scheduler():
#         global _scheduler_running
#         _scheduler_running = True
#         print("✅ Scheduler thread started - checking every 30 seconds")
#         while _scheduler_running:
#             try:
#                 schedule.run_pending()
#                 time.sleep(30)
#             except Exception as e:
#                 print(f"Scheduler error: {e}")
#                 time.sleep(30)
    
#     it_scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
#     it_scheduler_thread.start()
#     print("✅ IT scheduler running in background")
#     print("=" * 60)
    
#     return it_scheduler_thread

# def stop_it_scheduler():
#     """Stop the scheduler"""
#     global it_scheduler_thread, _scheduler_running
#     if it_scheduler_thread:
#         print("🛑 Stopping IT scheduler...")
#         _scheduler_running = False
#         it_scheduler_thread = None
#         schedule.clear()





# services/it_scheduler.py

# services/it_scheduler.py - FINAL FIXED VERSION

import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import os

logger = logging.getLogger(__name__)

it_scheduler = None
_app = None

def is_main_process():
    """Check if we're running in the main Flask process (not the reloader)"""
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        return False
    return True

def init_scheduler(app):
    """Initialize scheduler with Flask app"""
    global _app
    _app = app
    logger.info("✅ Scheduler initialized with app context")
    print("✅ Scheduler initialized with app context")

def send_it_digest_for_users_at_time(target_time=None):
    """Send IT digest to users whose preferred time matches the given time"""
    global _app
    
    if not _app:
        logger.error("❌ Scheduler not initialized")
        print("❌ Scheduler not initialized")
        return
    
    try:
        with _app.app_context():
            from database import db
            from models.user import User
            from models.user_preferences import UserPreferences
            from services.it_notification_service import ITNotificationService
            
            # Use current time if no target_time provided
            if not target_time:
                target_time = datetime.now().strftime('%H:%M')
            
            print("=" * 60)
            print(f"📧 [SCHEDULER] Checking for users with send_time: {target_time}")
            print(f"📧 [SCHEDULER] Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Get users with this specific send_time
            users = User.query.join(User.preferences).filter(
                UserPreferences.notifications_enabled == True,
                UserPreferences.send_time == target_time
            ).all()
            
            print(f"📧 [SCHEDULER] Found {len(users)} user(s) with send_time {target_time}")
            
            # Debug: Show all users and their times
            all_users = User.query.join(User.preferences).filter(
                UserPreferences.notifications_enabled == True
            ).all()
            print(f"📧 [SCHEDULER] All enabled users: {[(u.id, u.email, u.preferences.send_time) for u in all_users]}")
            
            if not users:
                print(f"📧 [SCHEDULER] No users scheduled for {target_time}")
                return
            
            service = ITNotificationService()
            success_count = 0
            
            for user in users:
                try:
                    user_id = user.id
                    
                    print(f"📧 [SCHEDULER] Processing user {user.id} - {user.email}")
                    print(f"📧 [SCHEDULER]   Preferences: {user.preferences}")
                    print(f"📧 [SCHEDULER]   Send time: {user.preferences.send_time}")
                    print(f"📧 [SCHEDULER]   last_sent_at: {user.preferences.last_sent_at}")
                    
                    # 🔥 CRITICAL FIX: Check last_sent_at BEFORE anything else
                    if user.preferences and user.preferences.last_sent_at:
                        today = datetime.now().date()
                        last_sent_date = user.preferences.last_sent_at.date()
                        if last_sent_date == today:
                            print(f"⏭️ [SCHEDULER] User {user_id} already received email today at {user.preferences.last_sent_at.strftime('%H:%M:%S')}, SKIPPING")
                            continue
                    
                    # 🔥 CRITICAL FIX: Update last_sent_at BEFORE sending
                    if user.preferences:
                        user.preferences.last_sent_at = datetime.now()
                        db.session.commit()
                        print(f"✅ [SCHEDULER] Updated last_sent_at to {user.preferences.last_sent_at} for user {user_id}")
                    
                    # Send the email
                    print(f"📧 [SCHEDULER] Sending email to user {user_id}...")
                    result = service.send_daily_digest_for_user(user)
                    
                    if result:
                        success_count += 1
                        print(f"✅ Sent to user {user.id} ({user.email}) at {target_time}")
                    else:
                        print(f"❌ Failed to send to user {user.id} ({user.email})")
                        # Rollback if send failed
                        db.session.rollback()
                        
                except Exception as e:
                    logger.error(f"Error sending to user {user.id}: {e}")
                    print(f"❌ Error sending to user {user.id}: {e}")
                    import traceback
                    traceback.print_exc()
            
            logger.info(f"✅ IT digest sent to {success_count}/{len(users)} users at {target_time}")
            print(f"✅ IT digest sent to {success_count}/{len(users)} users at {target_time}")
            print("=" * 60)
            
    except Exception as e:
        logger.error(f"❌ Error sending IT digest: {e}")
        print(f"❌ Error sending IT digest: {e}")
        import traceback
        traceback.print_exc()

def check_and_send_for_all_users():
    """Check all users and send to those whose time matches now"""
    current_time = datetime.now().strftime('%H:%M')
    print(f"⏰ [SCHEDULER] Checking at {current_time}")
    send_it_digest_for_users_at_time(current_time)

def start_it_scheduler(app):
    """Start the scheduler using APScheduler"""
    global it_scheduler, _app
    
    # Only run in the main process, not the reloader process
    if not is_main_process():
        print("⏰ [SCHEDULER] Skipping scheduler start in reloader process")
        return None
    
    if it_scheduler and it_scheduler.running:
        logger.info("⚠️ Scheduler already running")
        return it_scheduler
    
    _app = app
    
    # Create scheduler
    it_scheduler = BackgroundScheduler()
    
    # Run every 30 seconds
    it_scheduler.add_job(
        check_and_send_for_all_users,
        trigger=CronTrigger(second='0,30'),  # Run at 0 and 30 seconds of every minute
        id='check_users',
        replace_existing=True
    )
    
    print("=" * 60)
    print("⏰ IT SCHEDULER CONFIGURED (APScheduler):")
    print("  - Every 30 seconds: Check user preferences")
    print("  - Users control their own send time")
    print("  - Running in main process only")
    print("  - Duplicate prevention: last_sent_at check BEFORE sending")
    print("=" * 60)
    
    it_scheduler.start()
    print("✅ IT scheduler running in background")
    print("=" * 60)
    
    # ❌ NO immediate check - let the scheduler handle it
    print("🧪 Scheduler will start checking at the next :00 or :30 second")
    
    return it_scheduler

def stop_it_scheduler():
    """Stop the scheduler"""
    global it_scheduler
    if it_scheduler and it_scheduler.running:
        print("🛑 Stopping IT scheduler...")
        it_scheduler.shutdown()
        it_scheduler = None 