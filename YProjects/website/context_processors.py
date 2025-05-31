from .models import CompanyInfo, AboutUs, Project

def company_context(request):
    """Context processor to add company information to all templates"""
    company_info = CompanyInfo.objects.first()
    about_us = AboutUs.objects.first()
    
    # Get featured projects count for header/footer
    featured_projects_count = Project.objects.filter(is_featured=True).count()
    total_projects_count = Project.objects.count()
    
    context = {
        'company_info': company_info,
        'about_us': about_us,
        'featured_projects_count': featured_projects_count,
        'total_projects_count': total_projects_count,
    }
    
    # Add social media links if company info exists
    if company_info:
        context.update({
            'social_links': {
                'facebook': company_info.facebook_url,
                'instagram': company_info.instagram_url,
                'twitter': company_info.twitter_url,
                'youtube': company_info.youtube_url,
                'linkedin': company_info.linkedin_url,
            }
        })
    
    return context