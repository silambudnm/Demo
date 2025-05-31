from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Min, Max, Count, Avg
from django.utils import timezone
import json
import logging
from .models import Project, Contact, Newsletter, AboutUs, CompanyInfo

@csrf_exempt
@require_http_methods(["GET"])
def api_projects(request):
    """API endpoint to get projects with filtering and pagination"""
    try:
        # Get query parameters
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        project_type = request.GET.get('type')
        location = request.GET.get('location')
        featured_only = request.GET.get('featured') == 'true'
        search = request.GET.get('search')
        
        # Build queryset
        projects = Project.objects.all()
        
        if project_type:
            projects = projects.filter(project_type=project_type)
        
        if location:
            projects = projects.filter(location__icontains=location)
            
        if featured_only:
            projects = projects.filter(is_featured=True)
            
        if search:
            projects = projects.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search) |
                Q(location__icontains=search)
            )
        
        projects = projects.order_by('-created_at')
        
        # Pagination
        paginator = Paginator(projects, per_page)
        page_obj = paginator.get_page(page)
        
        # Serialize data
        projects_data = []
        for project in page_obj:
            project_data = {
                'id': project.id,
                'title': project.title,
                'description': project.description,
                'location': project.location,
                'price': project.price,
                'project_type': project.project_type,
                'area_sqft': project.area_sqft,
                'bedrooms': project.bedrooms,
                'bathrooms': project.bathrooms,
                'parking': project.parking,
                'amenities': project.get_amenities_list(),
                'is_featured': project.is_featured,
                'status': project.status,
                'image_url': project.image.url if project.image else None,
                'created_at': project.created_at.isoformat(),
            }
            projects_data.append(project_data)
        
        return JsonResponse({
            'success': True,
            'data': projects_data,
            'pagination': {
                'current_page': page_obj.number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'has_next': page_obj.has_next(),
                'has_previous': page_obj.has_previous(),
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def api_contact_submit(request):
    """API endpoint to submit contact form"""
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['name', 'email', 'mobile', 'message']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({
                    'success': False,
                    'error': f'{field} is required'
                }, status=400)
        
        # Create contact
        contact = Contact.objects.create(
            name=data['name'],
            email=data['email'],
            mobile=data['mobile'],
            message=data['message'],
            inquiry_type=data.get('inquiry_type', 'general'),
            project_interest_id=data.get('project_id') if data.get('project_id') else None,
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Contact form submitted successfully',
            'contact_id': contact.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def api_newsletter_subscribe(request):
    """API endpoint to subscribe to newsletter"""
    try:
        data = json.loads(request.body)
        email = data.get('email')
        
        if not email:
            return JsonResponse({
                'success': False,
                'error': 'Email is required'
            }, status=400)
        
        # Check if already subscribed
        if Newsletter.objects.filter(email=email).exists():
            return JsonResponse({
                'success': False,
                'error': 'Email already subscribed'
            }, status=400)
        
        # Create subscription
        Newsletter.objects.create(email=email)
        
        return JsonResponse({
            'success': True,
            'message': 'Successfully subscribed to newsletter'
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@csrf_exempt
@require_http_methods(["GET"])
def api_company_info(request):
    """API endpoint to get company information"""
    try:
        company_info = CompanyInfo.objects.first()
        about_us = AboutUs.objects.first()
        
        data = {}
        
        if company_info:
            data['company'] = {
                'name': company_info.company_name,
                'tagline': company_info.tagline,
                'email': company_info.email,
                'phone': company_info.phone,
                'location': company_info.location,
                'address': company_info.address,
                'working_hours': company_info.working_hours,
                'whatsapp_number': company_info.whatsapp_number,
                'social_media': {
                    'facebook': company_info.facebook_url,
                    'instagram': company_info.instagram_url,
                    'youtube': company_info.youtube_url,
                    'twitter': company_info.twitter_url,
                }
            }
        
        if about_us:
            data['about'] = {
                'title': about_us.title,
                'subtitle': about_us.subtitle,
                'description': about_us.description,
                'mission': about_us.mission,
                'vision': about_us.vision,
                'stats': {
                    'happy_families': about_us.happy_families,
                    'completed_projects': about_us.completed_projects,
                    'landmarks': about_us.landmarks,
                    'years_experience': about_us.years_experience,
                }
            }
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@csrf_exempt
@require_http_methods(["GET"])
def api_project_detail(request, project_id):
    """API endpoint to get detailed project information"""
    try:
        project = Project.objects.get(id=project_id)
        
        # Get related projects
        related_projects = Project.objects.filter(
            project_type=project.project_type
        ).exclude(id=project.id)[:3]
        
        project_data = {
            'id': project.id,
            'title': project.title,
            'description': project.description,
            'location': project.location,
            'price': project.price,
            'project_type': project.project_type,
            'area_sqft': project.area_sqft,
            'bedrooms': project.bedrooms,
            'bathrooms': project.bathrooms,
            'parking': project.parking,
            'amenities': project.get_amenities_list(),
            'is_featured': project.is_featured,
            'status': project.status,
            'image_url': project.image.url if project.image else None,
            'images': [
                {
                    'url': img.image.url,
                    'caption': img.caption
                } for img in project.images.all()
            ],
            'meta_title': project.meta_title,
            'meta_description': project.meta_description,
            'created_at': project.created_at.isoformat(),
            'related_projects': [
                {
                    'id': rp.id,
                    'title': rp.title,
                    'location': rp.location,
                    'price': rp.price,
                    'image_url': rp.image.url if rp.image else None,
                } for rp in related_projects
            ]
        }
        
        return JsonResponse({
            'success': True,
            'data': project_data
        })
        
    except Project.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Project not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@csrf_exempt
@require_http_methods(["GET"])
def api_advanced_search(request):
    """Advanced search API with multiple filters and sorting"""
    try:
        # Get search parameters
        query = request.GET.get('q', '')
        min_price = request.GET.get('min_price')
        max_price = request.GET.get('max_price')
        project_type = request.GET.get('project_type')
        location = request.GET.get('location')
        min_bedrooms = request.GET.get('min_bedrooms')
        max_bedrooms = request.GET.get('max_bedrooms')
        amenities = request.GET.getlist('amenities')
        sort_by = request.GET.get('sort', 'created_at')
        sort_order = request.GET.get('order', 'desc')
        page = int(request.GET.get('page', 1))
        per_page = min(int(request.GET.get('per_page', 12)), 50)  # Max 50 per page
        
        # Start with all projects
        projects = Project.objects.all()
        
        # Apply filters
        if query:
            projects = projects.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(location__icontains=query) |
                Q(amenities__icontains=query)
            )
        
        if min_price:
            projects = projects.filter(price__gte=float(min_price))
        
        if max_price:
            projects = projects.filter(price__lte=float(max_price))
            
        if project_type:
            projects = projects.filter(project_type=project_type)
            
        if location:
            projects = projects.filter(location__icontains=location)
            
        if min_bedrooms:
            projects = projects.filter(bedrooms__gte=int(min_bedrooms))
            
        if max_bedrooms:
            projects = projects.filter(bedrooms__lte=int(max_bedrooms))
            
        if amenities:
            for amenity in amenities:
                projects = projects.filter(amenities__icontains=amenity)
        
        # Apply sorting
        valid_sort_fields = ['created_at', 'price', 'title', 'bedrooms', 'area_sqft']
        if sort_by in valid_sort_fields:
            if sort_order == 'desc':
                projects = projects.order_by(f'-{sort_by}')
            else:
                projects = projects.order_by(sort_by)
        else:
            projects = projects.order_by('-created_at')
        
        # Pagination
        paginator = Paginator(projects, per_page)
        page_obj = paginator.get_page(page)
        
        # Serialize results
        results = []
        for project in page_obj:
            results.append({
                'id': project.id,
                'title': project.title,
                'description': project.description[:200] + '...' if len(project.description) > 200 else project.description,
                'location': project.location,
                'price': project.price,
                'project_type': project.project_type,
                'bedrooms': project.bedrooms,
                'bathrooms': project.bathrooms,
                'area_sqft': project.area_sqft,
                'amenities': project.get_amenities_list()[:5],  # First 5 amenities
                'image_url': project.image.url if project.image else None,
                'is_featured': project.is_featured,
                'status': project.status,
            })
        
        # Get filter options for frontend
        filter_options = {
            'project_types': list(Project.objects.values_list('project_type', flat=True).distinct()),
            'locations': list(Project.objects.values_list('location', flat=True).distinct()),
            'price_range': {
                'min': Project.objects.aggregate(min_price=Min('price'))['min_price'] or 0,
                'max': Project.objects.aggregate(max_price=Max('price'))['max_price'] or 0,
            },
            'bedroom_range': {
                'min': Project.objects.aggregate(min_br=Min('bedrooms'))['min_br'] or 0,
                'max': Project.objects.aggregate(max_br=Max('bedrooms'))['max_br'] or 0,
            }
        }
        
        return JsonResponse({
            'success': True,
            'data': {
                'results': results,
                'pagination': {
                    'current_page': page_obj.number,
                    'total_pages': paginator.num_pages,
                    'total_items': paginator.count,
                    'has_next': page_obj.has_next(),
                    'has_previous': page_obj.has_previous(),
                    'per_page': per_page,
                },
                'filters': filter_options,
                'applied_filters': {
                    'query': query,
                    'min_price': min_price,
                    'max_price': max_price,
                    'project_type': project_type,
                    'location': location,
                    'min_bedrooms': min_bedrooms,
                    'max_bedrooms': max_bedrooms,
                    'amenities': amenities,
                    'sort_by': sort_by,
                    'sort_order': sort_order,
                }
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@csrf_exempt
@require_http_methods(["GET"])
def api_statistics(request):
    """API endpoint for dashboard statistics"""
    try:
        from .utils import calculate_project_stats
        from django.db.models import Count, Avg
        from django.utils import timezone
        from datetime import timedelta
        
        # Basic stats
        stats = calculate_project_stats()
        
        # Recent activity (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_contacts = Contact.objects.filter(created_at__gte=thirty_days_ago).count()
        recent_newsletters = Newsletter.objects.filter(subscribed_at__gte=thirty_days_ago).count()
        
        # Popular locations
        popular_locations = Project.objects.values('location').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        # Average project price by type
        price_by_type = Project.objects.values('project_type').annotate(
            avg_price=Avg('price'),
            count=Count('id')
        ).order_by('-avg_price')
        
        # Monthly contact trends (last 6 months)
        monthly_contacts = []
        for i in range(6):
            month_start = timezone.now().replace(day=1) - timedelta(days=30*i)
            month_end = (month_start + timedelta(days=32)).replace(day=1)
            count = Contact.objects.filter(
                created_at__gte=month_start,
                created_at__lt=month_end
            ).count()
            monthly_contacts.append({
                'month': month_start.strftime('%Y-%m'),
                'count': count
            })
        
        return JsonResponse({
            'success': True,
            'data': {
                'overview': stats,
                'recent_activity': {
                    'contacts_30_days': recent_contacts,
                    'newsletter_subs_30_days': recent_newsletters,
                },
                'popular_locations': list(popular_locations),
                'price_by_type': list(price_by_type),
                'monthly_trends': monthly_contacts[::-1],  # Reverse to show oldest first
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def api_track_analytics(request):
    """Track user interactions for analytics"""
    try:
        data = json.loads(request.body)
        event_type = data.get('event_type')
        event_data = data.get('event_data', {})
        
        # You can expand this to save to a proper analytics model
        # For now, we'll just log the events
        import logging
        logger = logging.getLogger('analytics')
        
        analytics_data = {
            'timestamp': timezone.now().isoformat(),
            'event_type': event_type,
            'event_data': event_data,
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'ip_address': request.META.get('REMOTE_ADDR', ''),
        }
        
        logger.info(f"Analytics Event: {analytics_data}")
        
        return JsonResponse({
            'success': True,
            'message': 'Event tracked successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@csrf_exempt
@require_http_methods(["GET"])
def api_featured_projects(request):
    """Get featured projects for homepage"""
    try:
        featured_projects = Project.objects.filter(is_featured=True)[:6]
        
        projects_data = []
        for project in featured_projects:
            projects_data.append({
                'id': project.id,
                'title': project.title,
                'location': project.location,
                'price': project.price,
                'project_type': project.project_type,
                'bedrooms': project.bedrooms,
                'area_sqft': project.area_sqft,
                'image_url': project.image.url if project.image else None,
                'status': project.status,
            })
        
        return JsonResponse({
            'success': True,
            'data': projects_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@csrf_exempt
@require_http_methods(["GET"])
def api_project_types(request):
    """Get available project types with counts"""
    try:
        project_types = Project.objects.values('project_type').annotate(
            count=Count('id'),
            avg_price=Avg('price')
        ).order_by('project_type')
        
        return JsonResponse({
            'success': True,
            'data': list(project_types)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@csrf_exempt
@require_http_methods(["GET"])
def api_locations(request):
    """Get available locations with project counts"""
    try:
        locations = Project.objects.values('location').annotate(
            count=Count('id'),
            avg_price=Avg('price'),
            min_price=Min('price'),
            max_price=Max('price')
        ).order_by('location')
        
        return JsonResponse({
            'success': True,
            'data': list(locations)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def api_quick_inquiry(request):
    """Quick inquiry form for specific projects"""
    try:
        data = json.loads(request.body)
        
        required_fields = ['name', 'phone', 'project_id']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({
                    'success': False,
                    'error': f'{field} is required'
                }, status=400)
        
        # Verify project exists
        try:
            project = Project.objects.get(id=data['project_id'])
        except Project.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Project not found'
            }, status=404)
        
        # Create contact with quick inquiry type
        contact = Contact.objects.create(
            name=data['name'],
            email=data.get('email', ''),
            mobile=data['phone'],
            message=f"Quick inquiry for {project.title}. {data.get('message', '')}",
            inquiry_type='quick_inquiry',
            project_interest=project,
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Quick inquiry submitted successfully',
            'contact_id': contact.id
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@csrf_exempt
@require_http_methods(["GET"])
def api_similar_projects(request, project_id):
    """Get similar projects based on location and type"""
    try:
        project = Project.objects.get(id=project_id)
        
        # Find similar projects
        similar_projects = Project.objects.filter(
            Q(location__icontains=project.location.split(',')[0]) |  # Same city
            Q(project_type=project.project_type)
        ).exclude(id=project.id).order_by('-is_featured', '-created_at')[:6]
        
        projects_data = []
        for proj in similar_projects:
            projects_data.append({
                'id': proj.id,
                'title': proj.title,
                'location': proj.location,
                'price': proj.price,
                'project_type': proj.project_type,
                'bedrooms': proj.bedrooms,
                'image_url': proj.image.url if proj.image else None,
                'similarity_score': (
                    (2 if proj.project_type == project.project_type else 0) +
                    (1 if project.location.split(',')[0] in proj.location else 0)
                )
            })
        
        # Sort by similarity score
        projects_data.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return JsonResponse({
            'success': True,
            'data': projects_data
        })
        
    except Project.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Project not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@csrf_exempt
@require_http_methods(["POST"])
def api_price_estimate(request):
    """Get price estimate based on requirements"""
    try:
        data = json.loads(request.body)
        
        bedrooms = data.get('bedrooms')
        area_sqft = data.get('area_sqft')
        location = data.get('location')
        project_type = data.get('project_type')
        
        # Build filter for similar projects
        filters = Q()
        if bedrooms:
            filters &= Q(bedrooms=bedrooms)
        if project_type:
            filters &= Q(project_type=project_type)
        if location:
            filters &= Q(location__icontains=location)
        
        similar_projects = Project.objects.filter(filters)
        
        if similar_projects.exists():
            stats = similar_projects.aggregate(
                avg_price=Avg('price'),
                min_price=Min('price'),
                max_price=Max('price'),
                count=Count('id')
            )
            
            # Calculate price per sqft if area provided
            price_per_sqft = None
            if area_sqft and stats['avg_price']:
                avg_area = similar_projects.aggregate(avg_area=Avg('area_sqft'))['avg_area']
                if avg_area:
                    price_per_sqft = stats['avg_price'] / avg_area
                    estimated_price = price_per_sqft * float(area_sqft)
                    stats['estimated_price'] = estimated_price
                    stats['price_per_sqft'] = price_per_sqft
            
            return JsonResponse({
                'success': True,
                'data': {
                    'estimate': stats,
                    'similar_projects_count': stats['count'],
                    'criteria': {
                        'bedrooms': bedrooms,
                        'area_sqft': area_sqft,
                        'location': location,
                        'project_type': project_type,
                    }
                }
            })
        else:
            return JsonResponse({
                'success': True,
                'data': {
                    'estimate': None,
                    'message': 'No similar projects found for accurate estimation',
                    'criteria': {
                        'bedrooms': bedrooms,
                        'area_sqft': area_sqft,
                        'location': location,
                        'project_type': project_type,
                    }
                }
            })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@csrf_exempt
@require_http_methods(["GET"])
def api_health_check(request):
    """API health check endpoint"""
    try:
        from django.db import connection
        
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Get basic counts
        project_count = Project.objects.count()
        contact_count = Contact.objects.count()
        
        return JsonResponse({
            'success': True,
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'data': {
                'database': 'connected',
                'projects_count': project_count,
                'contacts_count': contact_count,
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'status': 'unhealthy',
            'error': str(e)
        }, status=500)