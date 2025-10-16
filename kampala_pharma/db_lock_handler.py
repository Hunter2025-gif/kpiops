"""
Database Lock Recovery Management
This module provides utilities to handle SQLite database locks
"""
import os
import sqlite3
import time
import logging
from django.conf import settings
from django.db import connection, transaction

logger = logging.getLogger(__name__)

def check_db_locked():
    """
    Check if the database is currently locked
    Returns True if locked, False otherwise
    """
    try:
        # Try to get a write lock on the database
        with sqlite3.connect(settings.DATABASES['default']['NAME'], timeout=0.5) as conn:
            conn.execute("BEGIN IMMEDIATE")
            # If we get here, the database is not locked by another process
            return False
    except sqlite3.OperationalError:
        # Database is locked
        return True
        
def fix_database_lock():
    """
    Attempt to fix a database lock issue by closing all connections
    and optimizing the database
    """
    try:
        # Close all Django connections
        connection.close()
        
        # Connect with a higher timeout to wait for any locks to clear
        with sqlite3.connect(settings.DATABASES['default']['NAME'], timeout=10) as conn:
            # Force PRAGMA settings that help with locks
            conn.execute("PRAGMA busy_timeout = 5000")
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA synchronous = NORMAL")
            
            # Optimize database (skipping PRAGMA optimize which might not be available)
            conn.execute("VACUUM")
            
        return True
    except Exception as e:
        logger.error(f"Error fixing database lock: {e}")
        return False

def is_database_healthy():
    """
    Check if the database is in a healthy state
    Returns True if healthy, False otherwise
    """
    try:
        with sqlite3.connect(settings.DATABASES['default']['NAME'], timeout=1) as conn:
            # Check if we can perform a simple query
            conn.execute("SELECT 1")
            # Check for integrity
            pragma_result = conn.execute("PRAGMA integrity_check").fetchone()[0]
            return pragma_result == "ok"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False