from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from website.models import Contact, Newsletter, Project, ProjectImage
import os

class Command(BaseCommand):
    help = 'Generate various reports for the website'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type',
            type=str,
            choices=['contacts', 'projects', 'newsletter', 'cleanup', 'analytics'],
            default='contacts',
            help='Type of report to generate'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to look back for data'
        )

    def handle(self, *args, **options):
        report_type = options['type']
        days_back = options['days']
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days_back)

        self.stdout.write(
            self.style.SUCCESS(f'\n=== {report_type.upper()} REPORT ===')
        )
        self.stdout.write(f'Period: {start_date.date()} to {end_date.date()}\n')

        if report_type == 'contacts':
            self.generate_contacts_report(start_date, end_date)
        elif report_type == 'projects':
            self.generate_projects_report()
        elif report_type == 'newsletter':
            self.generate_newsletter_report(start_date, end_date)
        elif report_type == 'cleanup':
            self.generate_cleanup_report()
        elif report_type == 'analytics':
            self.generate_analytics_report(start_date, end_date)

    def generate_contacts_report(self, start_date, end_date):
        """Generate contacts report"""
        contacts = Contact.objects.filter(
            created_at__range=[start_date, end_date]
        )
        
        total_contacts = contacts.count()
        responded_contacts = contacts.filter(is_responded=True).count()
        
        # Group by inquiry type
        inquiry_types = contacts.values('inquiry_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Group by date
        daily_contacts = contacts.extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(count=Count('id')).order_by('day')
        
        self.stdout.write(f'Total Contacts: {total_contacts}')
        self.stdout.write(f'Responded: {responded_contacts} ({(responded_contacts/total_contacts*100) if total_contacts > 0 else 0:.1f}%)')
        self.stdout.write(f'Pending: {total_contacts - responded_contacts}')
        
        self.stdout.write('\nInquiry Types:')
        for inquiry in inquiry_types:
            self.stdout.write(f'  {inquiry["inquiry_type"]}: {inquiry["count"]}')
        
        self.stdout.write('\nDaily Breakdown:')
        for day in daily_contacts:
            self.stdout.write(f'  {day["day"]}: {day["count"]} contacts')

    def generate_projects_report(self):
        """Generate projects report"""
        total_projects = Project.objects.count()
        featured_projects = Project.objects.filter(is_featured=True).count()
        
        # Group by project type
        project_types = Project.objects.values('project_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Group by status
        status_breakdown = Project.objects.values('status').annotate(
            count=Count('id')
        ).order_by('-count')
        
        self.stdout.write(f'Total Projects: {total_projects}')
        self.stdout.write(f'Featured Projects: {featured_projects}')
        
        self.stdout.write('\nProject Types:')
        for ptype in project_types:
            self.stdout.write(f'  {ptype["project_type"]}: {ptype["count"]}')
        
        self.stdout.write('\nStatus Breakdown:')
        for status in status_breakdown:
            self.stdout.write(f'  {status["status"]}: {status["count"]}')

    def generate_newsletter_report(self, start_date, end_date):
        """Generate newsletter report"""
        subscribers = Newsletter.objects.filter(
            subscribed_at__range=[start_date, end_date]
        )
        
        total_new_subscribers = subscribers.count()
        total_subscribers = Newsletter.objects.count()
        
        # Daily breakdown
        daily_subs = subscribers.extra(
            select={'day': 'date(subscribed_at)'}
        ).values('day').annotate(count=Count('id')).order_by('day')
        
        self.stdout.write(f'New Subscribers: {total_new_subscribers}')
        self.stdout.write(f'Total Subscribers: {total_subscribers}')
        
        self.stdout.write('\nDaily Breakdown:')
        for day in daily_subs:
            self.stdout.write(f'  {day["day"]}: {day["count"]} new subscribers')

    def generate_cleanup_report(self):
        """Generate cleanup suggestions"""
        # Find projects without images
        projects_no_images = Project.objects.filter(
            Q(image__isnull=True) | Q(image='')
        ).count()
        
        # Find project images without files
        missing_images = []
        for img in ProjectImage.objects.all():
            if img.image and not os.path.exists(img.image.path):
                missing_images.append(img.id)
        
        # Find contacts older than 1 year without response
        old_contacts = Contact.objects.filter(
            created_at__lt=timezone.now() - timedelta(days=365),
            is_responded=False
        ).count()
        
        self.stdout.write(f'Projects without images: {projects_no_images}')
        self.stdout.write(f'Missing image files: {len(missing_images)}')
        self.stdout.write(f'Old unresponded contacts: {old_contacts}')
        
        if missing_images:
            self.stdout.write('\nMissing image IDs:')
            for img_id in missing_images[:10]:  # Show first 10
                self.stdout.write(f'  ProjectImage ID: {img_id}')

    def generate_analytics_report(self, start_date, end_date):
        """Generate analytics overview"""
        # Recent activity summary
        new_contacts = Contact.objects.filter(
            created_at__range=[start_date, end_date]
        ).count()
        
        new_subscribers = Newsletter.objects.filter(
            subscribed_at__range=[start_date, end_date]
        ).count()
        
        # Popular project types from contacts
        popular_projects = Contact.objects.filter(
            project_interest__isnull=False,
            created_at__range=[start_date, end_date]
        ).values(
            'project_interest__project_type'
        ).annotate(
            count=Count('id')
        ).order_by('-count')
        
        self.stdout.write('ANALYTICS SUMMARY')
        self.stdout.write(f'New Contacts: {new_contacts}')
        self.stdout.write(f'New Subscribers: {new_subscribers}')
        
        self.stdout.write('\nMost Inquired Project Types:')
        for project in popular_projects:
            ptype = project['project_interest__project_type'] or 'Unknown'
            self.stdout.write(f'  {ptype}: {project["count"]} inquiries')
        
        # Conversion rate
        total_projects = Project.objects.count()
        if total_projects > 0:
            inquiry_to_project_ratio = new_contacts / total_projects
            self.stdout.write(f'\nInquiry to Project Ratio: {inquiry_to_project_ratio:.2f}')