"""
Scheduled tasks for database maintenance
"""
import time
import logging
import threading
from django.core import management
from django.db import connection
from django.conf import settings

logger = logging.getLogger(__name__)

class DatabaseMaintenanceThread(threading.Thread):
    """
    Thread to periodically check database health and perform maintenance
    """
    def __init__(self, check_interval=3600):  # Default: check every hour
        self.check_interval = check_interval
        self.stop_event = threading.Event()
        super().__init__(daemon=True)  # Daemon thread to auto-terminate on app shutdown
        
    def run(self):
        """Main thread loop that runs maintenance checks"""
        logger.info("Database maintenance thread started")
        
        while not self.stop_event.is_set():
            try:
                # Close any idle connections
                connection.close_if_unusable_or_obsolete()
                
                # Run integrity check
                self._run_integrity_check()
                
                # Sleep until next check (can be interrupted by stop event)
                self.stop_event.wait(self.check_interval)
            except Exception as e:
                logger.error(f"Error in database maintenance thread: {e}")
                # Sleep for a bit before retrying after an error
                time.sleep(60)
                
    def stop(self):
        """Stop the maintenance thread"""
        self.stop_event.set()
        
    def _run_integrity_check(self):
        """Run integrity check on the database"""
        try:
            # Use Django's management command system to run our check
            management.call_command('fix_db_locks', check_only=True)
            logger.info("Database integrity check completed")
        except Exception as e:
            logger.error(f"Database integrity check failed: {e}")

# Create the maintenance thread
maintenance_thread = None

def start_maintenance():
    """Start the database maintenance thread if enabled"""
    global maintenance_thread
    
    # Only start if in DEBUG mode or specifically enabled
    if getattr(settings, 'DB_MAINTENANCE_ENABLED', settings.DEBUG):
        maintenance_thread = DatabaseMaintenanceThread()
        maintenance_thread.start()
        logger.info("Database maintenance scheduler started")
        
def stop_maintenance():
    """Stop the database maintenance thread if running"""
    global maintenance_thread
    
    if maintenance_thread and maintenance_thread.is_alive():
        maintenance_thread.stop()
        maintenance_thread.join(timeout=5)
        logger.info("Database maintenance scheduler stopped")