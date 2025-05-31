from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    # Main website URLs
    path('', views.home, name='home'),
    path('about/', views.about_us, name='about_us'),
    path('projects/', views.projects, name='projects'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('contact/', views.contact_us, name='contact_us'),
    path('contact-ajax/', views.contact_ajax, name='contact_ajax'),
    path('api/search-projects/', views.search_projects, name='search_projects'),
    
    # Core API endpoints
    path('api/projects/', api_views.api_projects, name='api_projects'),
    path('api/projects/<int:project_id>/', api_views.api_project_detail, name='api_project_detail'),
    path('api/contact/', api_views.api_contact_submit, name='api_contact_submit'),
    path('api/newsletter/', api_views.api_newsletter_subscribe, name='api_newsletter_subscribe'),
    path('api/company-info/', api_views.api_company_info, name='api_company_info'),
    
    # Advanced API endpoints
    path('api/search-advanced/', api_views.api_advanced_search, name='api_advanced_search'),
    path('api/statistics/', api_views.api_statistics, name='api_statistics'),
    path('api/analytics/track/', api_views.api_track_analytics, name='api_track_analytics'),
    
    # Additional API endpoints
    path('api/featured-projects/', api_views.api_featured_projects, name='api_featured_projects'),
    path('api/project-types/', api_views.api_project_types, name='api_project_types'),
    path('api/locations/', api_views.api_locations, name='api_locations'),
    path('api/quick-inquiry/', api_views.api_quick_inquiry, name='api_quick_inquiry'),
    path('api/similar-projects/<int:project_id>/', api_views.api_similar_projects, name='api_similar_projects'),
    path('api/price-estimate/', api_views.api_price_estimate, name='api_price_estimate'),
    path('api/health/', api_views.api_health_check, name='api_health_check'),
]