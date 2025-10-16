from django.apps import AppConfig
import threading

class KampalaPharmaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'kampala_pharma'
    
    def ready(self):
        # Import admin configuration when the app is ready
        try:
            from . import admin
        except ImportError:
            pass
            
        # Start database maintenance thread
        # Only in main process, not in runserver reloader thread
        import os
        if not os.environ.get('RUN_MAIN') == 'true':
            try:
                from . import db_maintenance
                db_maintenance.start_maintenance()
            except Exception as e:
                # Just log any errors, don't prevent app startup
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to start database maintenance: {e}")
