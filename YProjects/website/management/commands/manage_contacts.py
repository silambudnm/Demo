from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from website.models import Contact, Newsletter
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Manage contacts: cleanup old entries, export data, send notifications'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Remove contacts older than 6 months',
        )
        parser.add_argument(
            '--export',
            action='store_true',
            help='Export recent contacts to CSV',
        )
        parser.add_argument(
            '--notify-unread',
            action='store_true',
            help='Send notification about unread contacts',
        )

    def handle(self, *args, **options):
        if options['cleanup']:
            self.cleanup_old_contacts()
        
        if options['export']:
            self.export_contacts()
        
        if options['notify_unread']:
            self.notify_unread_contacts()

    def cleanup_old_contacts(self):
        six_months_ago = timezone.now() - timedelta(days=180)
        old_contacts = Contact.objects.filter(created_at__lt=six_months_ago, is_read=True)
        count = old_contacts.count()
        old_contacts.delete()
        self.stdout.write(
            self.style.SUCCESS(f'Cleaned up {count} old contact entries')
        )

    def export_contacts(self):
        import csv
        from django.http import HttpResponse
        
        contacts = Contact.objects.all().order_by('-created_at')
        
        filename = f'contacts_export_{timezone.now().strftime("%Y%m%d")}.csv'
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Name', 'Email', 'Mobile', 'Inquiry Type', 'Project', 'Message', 'Created', 'Read'])
            
            for contact in contacts:
                writer.writerow([
                    contact.name,
                    contact.email,
                    contact.mobile,
                    contact.get_inquiry_type_display(),
                    contact.project_interest.title if contact.project_interest else '',
                    contact.message,
                    contact.created_at.strftime('%Y-%m-%d %H:%M'),
                    'Yes' if contact.is_read else 'No'
                ])
        
        self.stdout.write(
            self.style.SUCCESS(f'Exported {contacts.count()} contacts to {filename}')
        )

    def notify_unread_contacts(self):
        unread_count = Contact.objects.filter(is_read=False).count()
        
        if unread_count > 0:
            self.stdout.write(
                self.style.WARNING(f'You have {unread_count} unread contact inquiries!')
            )
            
            # List recent unread contacts
            recent_unread = Contact.objects.filter(
                is_read=False,
                created_at__gte=timezone.now() - timedelta(days=7)
            ).order_by('-created_at')
            
            self.stdout.write('\nRecent unread contacts:')
            for contact in recent_unread:
                self.stdout.write(f'- {contact.name} ({contact.email}) - {contact.created_at.strftime("%Y-%m-%d %H:%M")}')
        else:
            self.stdout.write(
                self.style.SUCCESS('All contacts have been read!')
            )