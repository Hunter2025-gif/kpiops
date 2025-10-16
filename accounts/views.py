from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django.db.utils import OperationalError
from django.db import connection
import sqlite3
import time

# Import the database lock handler
from kampala_pharma.db_lock_handler import fix_database_lock, check_db_locked

@csrf_protect
def user_login(request):
    """User login view for operators and staff"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # Close any existing connections before login to prevent locks
                connection.close()
                
                try:
                    login(request, user)
                    messages.success(request, f'Welcome, {user.get_full_name() or user.username}!')
                    
                    # Use centralized dashboard routing
                    return redirect('dashboards:dashboard_home')
                except OperationalError as e:
                    if "database is locked" in str(e):
                        # Try to fix the database lock
                        if fix_database_lock():
                            messages.warning(request, "Database lock detected and fixed. Please try logging in again.")
                        else:
                            messages.error(request, "Database is currently locked. Please try again in a few moments.")
                    else:
                        messages.error(request, f"Login error: {str(e)}")
            else:
                messages.error(request, 'Invalid username or password.')
        except OperationalError as e:
            if "database is locked" in str(e):
                # Try to fix the database lock
                if fix_database_lock():
                    messages.warning(request, "Database lock detected and fixed. Please try logging in again.")
                else:
                    messages.error(request, "Database is currently locked. Please try again in a few moments.")
            else:
                messages.error(request, f"Login error: {str(e)}")
    
    # Check if database is currently locked and show message if needed
    if check_db_locked():
        messages.warning(request, "System is currently busy. If login fails, please try again in a few moments.")
    
    return render(request, 'accounts/login.html')

def user_logout(request):
    """User logout view"""
    logout(request)
    return redirect('accounts:login')

@login_required
def user_profile(request):
    """User profile view"""
    return render(request, 'accounts/profile.html', {'user': request.user})
