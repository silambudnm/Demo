from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from website.models import Project, Banner, Contact, AboutUs, CompanyInfo
import random

class Command(BaseCommand):
    help = 'Populate database with sample data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--projects',
            type=int,
            default=10,
            help='Number of sample projects to create',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to populate database...'))
        
        # Create sample projects
        project_titles = [
            'Luxury Villa Paradise', 'Green Valley Apartments', 'Sunrise Heights',
            'Royal Gardens', 'City Center Plaza', 'Waterfront Homes',
            'Mountain View Villas', 'Urban Living Complex', 'Golden Heights',
            'Peaceful Meadows', 'Elite Residency', 'Dream Homes'
        ]
        
        locations = [
            'Electronic City', 'Whitefield', 'Koramangala', 'HSR Layout',
            'Marathahalli', 'Banashankari', 'Jayanagar', 'Indiranagar',
            'BTM Layout', 'Sarjapur Road'
        ]
        
        project_types = ['apartments', 'villas', 'plots', 'commercial', 'luxury']
        
        for i in range(options['projects']):
            title = random.choice(project_titles) + f" Phase {i+1}"
            Project.objects.get_or_create(
                title=title,
                defaults={
                    'description': f'Premium {random.choice(project_types)} project with modern amenities and excellent connectivity.',
                    'location': random.choice(locations),
                    'price': f'₹{random.randint(30, 150)} Lakhs',
                    'project_type': random.choice(project_types),
                    'area_sqft': f'{random.randint(800, 3000)} sq ft',
                    'bedrooms': f'{random.randint(1, 4)} BHK',
                    'bathrooms': str(random.randint(1, 3)),
                    'parking': f'{random.randint(1, 2)} Car',
                    'amenities': 'Swimming Pool, Gym, Garden, Security, Power Backup',
                    'is_featured': random.choice([True, False]),
                }
            )
        
        # Create or update AboutUs
        AboutUs.objects.get_or_create(
            defaults={
                'title': 'About Harsha Designers',
                'subtitle': 'Best Designers in India',
                'description': 'We are a leading real estate company with over 10 years of experience in creating dream homes.',
                'mission': 'To provide quality homes at affordable prices.',
                'vision': 'To be the most trusted real estate brand in India.',
                'happy_families': 500,
                'completed_projects': 50,
                'landmarks': 25,
                'years_experience': 10,
            }
        )
        
        # Create or update CompanyInfo
        CompanyInfo.objects.get_or_create(
            defaults={
                'company_name': 'Harsha Designers',
                'tagline': 'Building Dreams, Creating Homes',
                'email': 'info.harshadesigners@mail.com',
                'phone': '8012961197',
                'location': 'Bangalore',
                'address': 'Electronic City, Bangalore, Karnataka',
                'working_hours': 'Mon-Sat: 9:00 AM - 6:00 PM',
                'whatsapp_number': '918012961197',
            }
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {options["projects"]} sample projects and updated company information'
            )
        )