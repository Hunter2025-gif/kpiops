from django.urls import path
from . import views
from . import timeline_views

app_name = 'reports'

urlpatterns = [
    path('timeline/', timeline_views.timeline_list_view, name='timeline_list'),
    path('timeline/<int:bmr_id>/', timeline_views.enhanced_timeline_view, name='timeline_detail'),
    path('timeline/export/csv/', timeline_views.export_timeline_csv, name='export_timeline_csv'),
    path('timeline/export/excel/', timeline_views.export_timeline_excel, name='export_timeline_excel'),
    path('comments/', views.comments_report_view, name='comments_report'),
    path('comments/export/csv/', views.export_comments_csv, name='export_comments_csv'),
    path('comments/export/word/', views.export_comments_word, name='export_comments_word'),
    path('comments/export/excel/', views.export_comments_excel, name='export_comments_excel'),
    path('comments/bmr/<int:bmr_id>/', views.bmr_comments_detail, name='bmr_comments_detail'),
    path('enhanced-timeline/<int:bmr_id>/', timeline_views.enhanced_timeline_view, name='enhanced_timeline'),
]
