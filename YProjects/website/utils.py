from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from .models import Contact, CompanyInfo
import logging
import os
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.cache import cache
import hashlib
import pickle
from typing import Any, Optional

logger = logging.getLogger(__name__)

def send_contact_notification(contact_id):
    """Send email notification when new contact is received"""
    try:
        contact = Contact.objects.get(id=contact_id)
        company_info = CompanyInfo.objects.first()
        
        # Email to admin
        subject = f'New Contact Inquiry from {contact.name}'
        
        # Create HTML email content
        html_message = render_to_string('emails/contact_notification.html', {
            'contact': contact,
            'company_info': company_info,
        })
        plain_message = strip_tags(html_message)
        
        # Send to admin email
        admin_email = company_info.email if company_info else settings.DEFAULT_FROM_EMAIL
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[admin_email],
            html_message=html_message,
            fail_silently=False,
        )
        
        # Send auto-reply to customer
        customer_subject = 'Thank you for contacting Harsha Designers'
        customer_html = render_to_string('emails/contact_auto_reply.html', {
            'contact': contact,
            'company_info': company_info,
        })
        customer_plain = strip_tags(customer_html)
        
        send_mail(
            subject=customer_subject,
            message=customer_plain,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[contact.email],
            html_message=customer_html,
            fail_silently=False,
        )
        
        return True
    except Exception as e:
        logger.error(f'Error sending contact notification: {str(e)}')
        return False

def send_newsletter_welcome(email):
    """Send welcome email to newsletter subscriber"""
    try:
        company_info = CompanyInfo.objects.first()
        
        subject = 'Welcome to Harsha Designers Newsletter'
        html_message = render_to_string('emails/newsletter_welcome.html', {
            'email': email,
            'company_info': company_info,
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return True
    except Exception as e:
        logger.error(f'Error sending newsletter welcome: {str(e)}')
        return False

def optimize_image(image_field, max_size=(1920, 1080), quality=85):
    """Optimize uploaded images to reduce file size"""
    try:
        img = Image.open(image_field)
        
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')
        
        # Resize if larger than max_size
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save optimized image
        output = BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)
        
        return ContentFile(output.read())
    except Exception as e:
        logger.error(f'Error optimizing image: {str(e)}')
        return image_field

def generate_seo_meta(title, description, project=None):
    """Generate SEO meta tags for pages"""
    meta_data = {
        'title': title,
        'description': description,
        'keywords': 'real estate, properties, bangalore, harsha designers',
        'og_title': title,
        'og_description': description,
        'og_type': 'website',
        'twitter_card': 'summary_large_image',
    }
    
    if project:
        meta_data['keywords'] += f', {project.project_type}, {project.location}'
        if project.image:
            meta_data['og_image'] = project.image.url
    
    return meta_data

def create_sitemap_data():
    """Generate sitemap data for SEO"""
    from .models import Project
    from django.urls import reverse
    
    urls = []
    
    # Static pages
    static_pages = [
        {'loc': '/', 'priority': '1.0', 'changefreq': 'weekly'},
        {'loc': '/about/', 'priority': '0.8', 'changefreq': 'monthly'},
        {'loc': '/projects/', 'priority': '0.9', 'changefreq': 'weekly'},
        {'loc': '/contact/', 'priority': '0.7', 'changefreq': 'monthly'},
    ]
    
    urls.extend(static_pages)
    
    # Project pages
    projects = Project.objects.all()
    for project in projects:
        urls.append({
            'loc': f'/projects/{project.id}/',
            'priority': '0.8',
            'changefreq': 'monthly',
            'lastmod': project.updated_at.strftime('%Y-%m-%d') if hasattr(project, 'updated_at') else None
        })
    
    return urls

def backup_database():
    """Create database backup (for SQLite)"""
    import shutil
    from datetime import datetime
    
    try:
        db_path = settings.DATABASES['default']['NAME']
        backup_dir = settings.BASE_DIR / 'backups'
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = backup_dir / f'db_backup_{timestamp}.sqlite3'
        
        shutil.copy2(db_path, backup_path)
        
        # Keep only last 10 backups
        backups = sorted(backup_dir.glob('db_backup_*.sqlite3'))
        if len(backups) > 10:
            for old_backup in backups[:-10]:
                old_backup.unlink()
        
        logger.info(f'Database backup created: {backup_path}')
        return str(backup_path)
    except Exception as e:
        logger.error(f'Error creating database backup: {str(e)}')
        return None

def get_popular_projects(limit=6):
    """Get popular projects based on inquiries"""
    from django.db.models import Count
    from .models import Project
    
    popular_projects = Project.objects.annotate(
        inquiry_count=Count('contact_inquiries')
    ).order_by('-inquiry_count', '-is_featured')[:limit]
    
    return popular_projects

def calculate_project_stats():
    """Calculate various project statistics"""
    from .models import Project, Contact
    from django.db.models import Count, Q
    
    stats = {
        'total_projects': Project.objects.count(),
        'featured_projects': Project.objects.filter(is_featured=True).count(),
        'completed_projects': Project.objects.filter(status='completed').count(),
        'ongoing_projects': Project.objects.filter(status='ongoing').count(),
        'upcoming_projects': Project.objects.filter(status='upcoming').count(),
        'total_inquiries': Contact.objects.count(),
        'unread_inquiries': Contact.objects.filter(is_read=False).count(),
    }
    
    # Project type breakdown
    project_types = Project.objects.values('project_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    stats['project_types'] = {pt['project_type']: pt['count'] for pt in project_types}
    
    return stats

def get_cache_key(prefix: str, *args, **kwargs) -> str:
    """Generate a consistent cache key"""
    key_data = f"{prefix}:{':'.join(map(str, args))}"
    if kwargs:
        key_data += f":{hashlib.md5(str(sorted(kwargs.items())).encode()).hexdigest()}"
    return key_data

def cached_query(cache_key: str, timeout: int = 3600):
    """Decorator for caching expensive database queries"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                # Try to get from cache first
                result = cache.get(cache_key)
                if result is not None:
                    return pickle.loads(result)
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                cache.set(cache_key, pickle.dumps(result), timeout)
                return result
            except Exception as e:
                logger.warning(f"Cache operation failed: {e}")
                return func(*args, **kwargs)
        return wrapper
    return decorator

class ProjectCache:
    """Centralized caching for project-related data"""
    
    @staticmethod
    def get_featured_projects():
        cache_key = get_cache_key('featured_projects')
        cached = cache.get(cache_key)
        if cached:
            return cached
            
        from .models import Project
        projects = list(Project.objects.filter(
            is_featured=True, 
            status='active'
        ).select_related().order_by('-created_at')[:6])
        
        cache.set(cache_key, projects, 1800)  # 30 minutes
        return projects
    
    @staticmethod
    def get_project_stats():
        cache_key = get_cache_key('project_stats')
        cached = cache.get(cache_key)
        if cached:
            return cached
            
        stats = calculate_project_stats()
        cache.set(cache_key, stats, 3600)  # 1 hour
        return stats
    
    @staticmethod
    def invalidate_project_cache():
        """Clear all project-related cache"""
        cache_keys = [
            get_cache_key('featured_projects'),
            get_cache_key('project_stats'),
            get_cache_key('recent_projects'),
        ]
        cache.delete_many(cache_keys)

def rate_limit_check(key: str, limit: int = 60, window: int = 3600) -> bool:
    """Simple rate limiting using cache"""
    current = cache.get(key, 0)
    if current >= limit:
        return False
    
    cache.set(key, current + 1, window)
    return True

def get_client_ip(request) -> str:
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class BackgroundTaskManager:
    """Simple background task manager using database flags"""
    
    @staticmethod
    def schedule_email_batch():
        """Schedule batch email sending"""
        from .models import Newsletter
        
        # Mark pending newsletters for processing
        pending_count = Newsletter.objects.filter(
            is_active=True,
            email_sent=False
        ).update(processing=True)
        
        logger.info(f"Scheduled {pending_count} emails for batch processing")
        return pending_count
    
    @staticmethod
    def process_image_optimization():
        """Schedule image optimization for new uploads"""
        from .models import Project
        
        # Find projects with unoptimized images
        projects = Project.objects.filter(
            image__isnull=False,
            image_optimized=False
        )[:10]  # Process 10 at a time
        
        for project in projects:
            try:
                optimize_project_image(project)
                project.image_optimized = True
                project.save(update_fields=['image_optimized'])
            except Exception as e:
                logger.error(f"Image optimization failed for project {project.id}: {e}")
        
        return len(projects)
    
    @staticmethod
    def cleanup_old_contacts():
        """Clean up old contact entries"""
        from .models import Contact
        from django.utils import timezone
        from datetime import timedelta
        
        # Delete contacts older than 2 years
        cutoff_date = timezone.now() - timedelta(days=730)
        deleted_count = Contact.objects.filter(
            created_at__lt=cutoff_date,
            status='resolved'
        ).delete()[0]
        
        logger.info(f"Cleaned up {deleted_count} old contact entries")
        return deleted_count

def generate_sitemap_data():
    """Generate sitemap data for SEO"""
    from .models import Project
    from django.urls import reverse
    from django.utils import timezone
    
    urls = []
    
    # Static pages
    static_pages = [
        {'url': '/', 'priority': 1.0, 'changefreq': 'daily'},
        {'url': '/about/', 'priority': 0.8, 'changefreq': 'monthly'},
        {'url': '/projects/', 'priority': 0.9, 'changefreq': 'daily'},
        {'url': '/contact/', 'priority': 0.7, 'changefreq': 'monthly'},
    ]
    
    for page in static_pages:
        urls.append({
            'loc': page['url'],
            'lastmod': timezone.now(),
            'priority': page['priority'],
            'changefreq': page['changefreq']
        })
    
    # Project pages
    projects = Project.objects.filter(status='active')
    for project in projects:
        urls.append({
            'loc': f'/projects/{project.id}/',
            'lastmod': project.updated_at,
            'priority': 0.8,
            'changefreq': 'weekly'
        })
    
    return urls

def export_data_to_csv(model_name: str, filters: dict = None):
    """Export model data to CSV format"""
    import csv
    from io import StringIO
    from django.apps import apps
    
    try:
        model = apps.get_model('website', model_name)
        queryset = model.objects.all()
        
        if filters:
            queryset = queryset.filter(**filters)
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write headers
        fields = [field.name for field in model._meta.fields]
        writer.writerow(fields)
        
        # Write data
        for obj in queryset:
            row = []
            for field in fields:
                value = getattr(obj, field)
                if hasattr(value, 'strftime'):  # Date/DateTime field
                    value = value.strftime('%Y-%m-%d %H:%M:%S')
                row.append(str(value) if value is not None else '')
            writer.writerow(row)
        
        return output.getvalue()
    
    except Exception as e:
        logger.error(f"CSV export failed: {e}")
        return None