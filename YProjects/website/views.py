from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
import json
from .models import Project, Banner, Contact, AboutUs, CompanyInfo

# Cache the home page for 15 minutes
@cache_page(60 * 15)
def home(request):
    """Home page with all sections"""
    banners = Banner.objects.filter(is_active=True).order_by('order')
    projects = Project.objects.filter(is_featured=True)[:6]
    about_us = AboutUs.objects.first()
    company_info = CompanyInfo.objects.first()
    
    context = {
        'banners': banners,
        'projects': projects,
        'about_us': about_us,
        'company_info': company_info,
        'page_title': 'Home'
    }
    return render(request, 'website/home.html', context)

def about_us(request):
    """About Us page"""
    about_us = AboutUs.objects.first()
    company_info = CompanyInfo.objects.first()
    
    context = {
        'about_us': about_us,
        'company_info': company_info,
        'page_title': 'About Us'
    }
    return render(request, 'website/about.html', context)

def projects(request):
    """Our Projects page with filtering and pagination"""
    project_type = request.GET.get('type', '')
    search_query = request.GET.get('search', '')
    
    all_projects = Project.objects.all()
    
    # Filter by project type
    if project_type:
        all_projects = all_projects.filter(project_type__icontains=project_type)
    
    # Search functionality
    if search_query:
        all_projects = all_projects.filter(
            Q(title__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(all_projects, 9)  # Show 9 projects per page
    page_number = request.GET.get('page')
    projects_page = paginator.get_page(page_number)
    
    # Get unique project types for filter dropdown
    project_types = Project.objects.values_list('project_type', flat=True).distinct()
    
    company_info = CompanyInfo.objects.first()
    
    context = {
        'projects': projects_page,
        'project_types': project_types,
        'current_type': project_type,
        'search_query': search_query,
        'company_info': company_info,
        'page_title': 'Our Projects'
    }
    return render(request, 'website/projects.html', context)

def project_detail(request, project_id):
    """Individual project detail page"""
    project = get_object_or_404(Project, id=project_id)
    related_projects = Project.objects.filter(
        project_type=project.project_type
    ).exclude(id=project.id)[:3]
    
    company_info = CompanyInfo.objects.first()
    
    context = {
        'project': project,
        'related_projects': related_projects,
        'company_info': company_info,
        'page_title': project.title
    }
    return render(request, 'website/project_detail.html', context)

def contact_us(request):
    """Contact Us page"""
    company_info = CompanyInfo.objects.first()
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        mobile = request.POST.get('mobile', '').strip()
        message = request.POST.get('message', '').strip()
        
        # Validation
        errors = []
        if not name:
            errors.append('Name is required.')
        if not email:
            errors.append('Email is required.')
        if not mobile:
            errors.append('Mobile number is required.')
        elif len(mobile) < 10:
            errors.append('Please enter a valid mobile number.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            try:
                Contact.objects.create(
                    name=name,
                    email=email,
                    mobile=mobile,
                    message=message
                )
                messages.success(request, 'Thank you for your inquiry! We will get back to you soon.')
                return redirect('contact_us')
            except Exception as e:
                messages.error(request, 'An error occurred while submitting your inquiry. Please try again.')
    
    context = {
        'company_info': company_info,
        'page_title': 'Contact Us'
    }
    return render(request, 'website/contact.html', context)

@csrf_exempt
def contact_ajax(request):
    """Handle AJAX contact form submission"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name', '').strip()
            email = data.get('email', '').strip()
            mobile = data.get('mobile', '').strip()
            message = data.get('message', '').strip()
            
            # Validation
            if not name:
                return JsonResponse({'status': 'error', 'message': 'Name is required.'})
            if not email:
                return JsonResponse({'status': 'error', 'message': 'Email is required.'})
            if not mobile:
                return JsonResponse({'status': 'error', 'message': 'Mobile number is required.'})
            if len(mobile) < 10:
                return JsonResponse({'status': 'error', 'message': 'Please enter a valid mobile number.'})
            
            Contact.objects.create(
                name=name,
                email=email,
                mobile=mobile,
                message=message
            )
            return JsonResponse({'status': 'success', 'message': 'Thank you for your inquiry! We will get back to you soon.'})
            
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid data format.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'An error occurred. Please try again.'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

def search_projects(request):
    """AJAX search for projects"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    projects = Project.objects.filter(
        Q(title__icontains=query) |
        Q(location__icontains=query) |
        Q(project_type__icontains=query)
    )[:10]
    
    results = []
    for project in projects:
        results.append({
            'id': project.id,
            'title': project.title,
            'location': project.location,
            'price': project.price,
            'image_url': project.image.url if project.image else '',
            'project_type': project.project_type
        })
    
    return JsonResponse({'results': results})

# Class-based views for better structure
class ProjectListView(ListView):
    model = Project
    template_name = 'website/projects.html'
    context_object_name = 'projects'
    paginate_by = 9
    
    def get_queryset(self):
        queryset = Project.objects.all()
        project_type = self.request.GET.get('type')
        search_query = self.request.GET.get('search')
        
        if project_type:
            queryset = queryset.filter(project_type__icontains=project_type)
        
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(location__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['project_types'] = Project.objects.values_list('project_type', flat=True).distinct()
        context['current_type'] = self.request.GET.get('type', '')
        context['search_query'] = self.request.GET.get('search', '')
        context['company_info'] = CompanyInfo.objects.first()
        context['page_title'] = 'Our Projects'
        return context
