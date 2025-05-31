from django.core.management.base import BaseCommand
import requests
import json
from django.conf import settings

class Command(BaseCommand):
    help = 'Test API endpoints'
    
    def add_arguments(self, parser):
        parser.add_argument('--host', default='http://localhost:8000', help='Host URL')
        parser.add_argument('--endpoint', help='Specific endpoint to test')
    
    def handle(self, *args, **options):
        host = options['host']
        endpoint = options.get('endpoint')
        
        endpoints = {
            'projects': '/api/projects/',
            'featured': '/api/featured-projects/',
            'statistics': '/api/statistics/',
            'health': '/api/health/',
            'company': '/api/company-info/',
            'types': '/api/project-types/',
            'locations': '/api/locations/',
        }
        
        if endpoint:
            if endpoint in endpoints:
                self.test_endpoint(host, endpoints[endpoint], endpoint)
            else:
                self.stdout.write(f"Unknown endpoint: {endpoint}")
                self.stdout.write(f"Available endpoints: {', '.join(endpoints.keys())}")
        else:
            for name, url in endpoints.items():
                self.test_endpoint(host, url, name)
    
    def test_endpoint(self, host, endpoint, name):
        try:
            response = requests.get(f"{host}{endpoint}")
            if response.status_code == 200:
                self.stdout.write(
                    self.style.SUCCESS(f"✓ {name}: {response.status_code}")
                )
                if name == 'health':
                    data = response.json()
                    self.stdout.write(f"  Status: {data.get('status')}")
            else:
                self.stdout.write(
                    self.style.ERROR(f"✗ {name}: {response.status_code}")
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"✗ {name}: Connection error - {str(e)}")
            )