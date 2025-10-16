from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

# Customize the admin site
admin.site.site_header = "Kampala Pharmaceutical Industries"
admin.site.site_title = "KPI Operations Admin"
admin.site.index_title = "Operations Management System"

# Override the default admin site URLs
class CustomAdminSite(admin.AdminSite):
    site_header = "Kampala Pharmaceutical Industries"
    site_title = "KPI Operations Admin"
    index_title = "Operations Management System"
    
    def each_context(self, request):
        context = super().each_context(request)
        # Add custom context for the admin interface
        context.update({
            'site_url': '/',  # This makes "View site" link point to the root URL (dashboard)
            'has_permission': request.user.is_active,
        })
        return context

# You can replace the default admin site if needed
# admin_site = CustomAdminSite(name='custom_admin')
