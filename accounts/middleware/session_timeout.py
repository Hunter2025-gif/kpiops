import time
from django.conf import settings
from django.contrib import auth
from django.contrib.auth import logout
from django.utils.deprecation import MiddlewareMixin

class SessionTimeoutMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Skip for non-authenticated users
        if not request.user.is_authenticated:
            return None
            
        # Skip for AJAX requests
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return None
        
        # Get current time and last activity time
        current_time = time.time()
        last_activity = request.session.get('last_activity')
        
        # Set default session timeout (12 hours = 43200 seconds)
        session_timeout = getattr(settings, 'SESSION_TIMEOUT', 43200)
        
        # Update last activity time
        request.session['last_activity'] = current_time
        
        # If no last activity or session expired, ignore
        if not last_activity:
            return None
            
        # Check if session has expired
        if current_time - last_activity > session_timeout:
            # Logout user and display message
            auth.logout(request)
            # Let the logout view handle the redirect
            
        return None
