from django.db import models
from django.core.validators import RegexValidator
from django.urls import reverse
from django.utils import timezone
from PIL import Image
import os

class Project(models.Model):
    PROPERTY_TYPES = [
        ('apartments', '2/3 BHK Apartments'),
        ('villas', 'Villas'),
        ('plots', 'Plots'),
        ('commercial', 'Commercial'),
        ('luxury', 'Luxury Homes'),
    ]
    
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('sold_out', 'Sold Out'),
    ]
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()
    location = models.CharField(max_length=200)
    price = models.CharField(max_length=100)
    image = models.ImageField(upload_to='projects/')
    project_type = models.CharField(max_length=100, choices=PROPERTY_TYPES, default='apartments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    area_sqft = models.CharField(max_length=50, blank=True)
    bedrooms = models.CharField(max_length=20, blank=True)
    bathrooms = models.CharField(max_length=20, blank=True)
    parking = models.CharField(max_length=20, blank=True)
    amenities = models.TextField(blank=True, help_text="Comma-separated list of amenities")
    is_featured = models.BooleanField(default=False)
    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
        
        super().save(*args, **kwargs)
        
        # Resize image if too large
        if self.image:
            img = Image.open(self.image.path)
            if img.height > 800 or img.width > 1200:
                output_size = (1200, 800)
                img.thumbnail(output_size)
                img.save(self.image.path)
    
    def get_absolute_url(self):
        return reverse('project_detail', kwargs={'project_id': self.pk})
    
    def get_amenities_list(self):
        return [amenity.strip() for amenity in self.amenities.split(',') if amenity.strip()]
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']

class ProjectImage(models.Model):
    project = models.ForeignKey(Project, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='projects/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']

class Banner(models.Model):
    title = models.CharField(max_length=200, blank=True)
    subtitle = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to='banners/')
    link_url = models.URLField(blank=True)
    button_text = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Resize banner image
        if self.image:
            img = Image.open(self.image.path)
            if img.height > 600 or img.width > 1920:
                output_size = (1920, 600)
                img.thumbnail(output_size)
                img.save(self.image.path)
    
    def __str__(self):
        return self.title or f"Banner {self.id}"
    
    class Meta:
        ordering = ['order']

class Contact(models.Model):
    INQUIRY_TYPES = [
        ('general', 'General Inquiry'),
        ('project', 'Project Information'),
        ('callback', 'Request Callback'),
        ('visit', 'Site Visit'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    mobile = models.CharField(validators=[phone_regex], max_length=17)
    inquiry_type = models.CharField(max_length=20, choices=INQUIRY_TYPES, default='general')
    project_interest = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    responded_at = models.DateTimeField(null=True, blank=True)
    response_notes = models.TextField(blank=True)
    
    def mark_as_read(self):
        self.is_read = True
        self.save()
    
    def __str__(self):
        return f"{self.name} - {self.mobile}"
    
    class Meta:
        ordering = ['-created_at']

class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.email

class AboutUs(models.Model):
    title = models.CharField(max_length=200, default="About Harsha Designers")
    subtitle = models.CharField(max_length=200, default="Best Designers in India")
    description = models.TextField()
    mission = models.TextField(blank=True)
    vision = models.TextField(blank=True)
    happy_families = models.IntegerField(default=30)
    completed_projects = models.IntegerField(default=30)
    landmarks = models.IntegerField(default=30)
    years_experience = models.IntegerField(default=10)
    about_image = models.ImageField(upload_to='about/', blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "About Us"
        verbose_name_plural = "About Us"

class CompanyInfo(models.Model):
    company_name = models.CharField(max_length=200, default="Harsha Designers")
    tagline = models.CharField(max_length=200, blank=True)
    email = models.EmailField(default="info.harshadesigners@mail.com")
    phone = models.CharField(max_length=20, default="8012961197")
    phone2 = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=100, default="Bangalore")
    address = models.TextField(blank=True)
    working_hours = models.CharField(max_length=100, default="Mon-Sat: 9:00 AM - 6:00 PM")
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    logo = models.ImageField(upload_to='company/', blank=True)
    google_maps_embed = models.TextField(blank=True)
    whatsapp_number = models.CharField(max_length=20, blank=True)
    
    def __str__(self):
        return self.company_name
    
    class Meta:
        verbose_name = "Company Information"
        verbose_name_plural = "Company Information"

class SEOSettings(models.Model):
    page_name = models.CharField(max_length=50, unique=True)
    meta_title = models.CharField(max_length=60)
    meta_description = models.CharField(max_length=160)
    meta_keywords = models.CharField(max_length=255, blank=True)
    og_title = models.CharField(max_length=60, blank=True)
    og_description = models.CharField(max_length=160, blank=True)
    og_image = models.ImageField(upload_to='seo/', blank=True)
    
    def __str__(self):
        return f"SEO for {self.page_name}"
    
    class Meta:
        verbose_name = "SEO Setting"
        verbose_name_plural = "SEO Settings"
