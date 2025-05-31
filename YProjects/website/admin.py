from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Project, Banner, Contact, AboutUs, CompanyInfo, ProjectImage, Newsletter, SEOSettings

class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ['image', 'caption', 'order']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'location', 'price', 'project_type', 'status', 'is_featured', 'image_preview', 'created_at']
    list_filter = ['is_featured', 'project_type', 'status', 'created_at']
    search_fields = ['title', 'location', 'description']
    list_editable = ['is_featured', 'price', 'status']
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    actions = ['make_featured', 'remove_featured']
    inlines = [ProjectImageInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'location', 'image')
        }),
        ('Property Details', {
            'fields': ('project_type', 'status', 'price', 'area_sqft', 'bedrooms', 'bathrooms', 'parking')
        }),
        ('Features', {
            'fields': ('amenities', 'is_featured')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 5px;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = "Preview"
    
    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, f"{queryset.count()} projects marked as featured.")
    make_featured.short_description = "Mark selected projects as featured"
    
    def remove_featured(self, request, queryset):
        queryset.update(is_featured=False)
        self.message_user(request, f"{queryset.count()} projects removed from featured.")
    remove_featured.short_description = "Remove selected projects from featured"

@admin.register(ProjectImage)
class ProjectImageAdmin(admin.ModelAdmin):
    list_display = ['project', 'caption', 'order', 'image_preview', 'created_at']
    list_filter = ['project', 'created_at']
    search_fields = ['project__title', 'caption']
    list_editable = ['order']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 5px;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = "Preview"

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'subtitle', 'is_active', 'order', 'image_preview', 'created_at']
    list_filter = ['is_active', 'created_at']
    list_editable = ['is_active', 'order']
    ordering = ['order']
    fieldsets = (
        ('Content', {
            'fields': ('title', 'subtitle', 'image')
        }),
        ('Link Settings', {
            'fields': ('link_url', 'button_text')
        }),
        ('Display Settings', {
            'fields': ('is_active', 'order')
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="80" height="40" style="border-radius: 5px;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = "Preview"

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'mobile', 'inquiry_type', 'project_interest', 'is_read', 'created_at', 'view_message']
    list_filter = ['is_read', 'inquiry_type', 'created_at', 'project_interest']
    search_fields = ['name', 'email', 'mobile']
    list_editable = ['is_read']
    readonly_fields = ['created_at', 'name', 'email', 'mobile', 'message', 'inquiry_type']
    date_hierarchy = 'created_at'
    actions = ['mark_as_read', 'mark_as_unread']
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'mobile', 'created_at')
        }),
        ('Inquiry Details', {
            'fields': ('inquiry_type', 'project_interest', 'message')
        }),
        ('Response Management', {
            'fields': ('is_read', 'responded_at', 'response_notes')
        }),
    )
    
    def view_message(self, obj):
        if obj.message:
            return format_html('<span title="{}">{}</span>', 
                             obj.message, 
                             obj.message[:50] + "..." if len(obj.message) > 50 else obj.message)
        return "No message"
    view_message.short_description = "Message"
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f"{queryset.count()} contacts marked as read.")
    mark_as_read.short_description = "Mark selected contacts as read"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
        self.message_user(request, f"{queryset.count()} contacts marked as unread.")
    mark_as_unread.short_description = "Mark selected contacts as unread"

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'subscribed_at', 'is_active']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email']
    list_editable = ['is_active']
    readonly_fields = ['subscribed_at']
    actions = ['activate_subscribers', 'deactivate_subscribers']
    
    def activate_subscribers(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} subscribers activated.")
    activate_subscribers.short_description = "Activate selected subscribers"
    
    def deactivate_subscribers(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} subscribers deactivated.")
    deactivate_subscribers.short_description = "Deactivate selected subscribers"

@admin.register(AboutUs)
class AboutUsAdmin(admin.ModelAdmin):
    list_display = ['title', 'subtitle', 'happy_families', 'completed_projects', 'landmarks', 'years_experience', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'subtitle', 'description')
        }),
        ('Company Vision & Mission', {
            'fields': ('mission', 'vision')
        }),
        ('Statistics', {
            'fields': ('happy_families', 'completed_projects', 'landmarks', 'years_experience')
        }),
        ('Media', {
            'fields': ('about_image',)
        }),
    )
    
    def has_add_permission(self, request):
        return not AboutUs.objects.exists()

@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'email', 'phone', 'location']
    fieldsets = (
        ('Company Details', {
            'fields': ('company_name', 'tagline', 'email', 'phone', 'phone2', 'location', 'address', 'working_hours')
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'instagram_url', 'twitter_url', 'youtube_url', 'linkedin_url', 'whatsapp_number')
        }),
        ('Media & Maps', {
            'fields': ('logo', 'google_maps_embed')
        }),
    )
    
    def has_add_permission(self, request):
        return not CompanyInfo.objects.exists()

@admin.register(SEOSettings)
class SEOSettingsAdmin(admin.ModelAdmin):
    list_display = ['page_name', 'meta_title', 'meta_description']
    search_fields = ['page_name', 'meta_title']
    fieldsets = (
        ('Page Information', {
            'fields': ('page_name',)
        }),
        ('Meta Tags', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords')
        }),
        ('Open Graph', {
            'fields': ('og_title', 'og_description', 'og_image')
        }),
    )

# Customize Admin Site
admin.site.site_header = "Harsha Designers Admin Panel"
admin.site.site_title = "Harsha Designers Admin"
admin.site.index_title = "Welcome to Harsha Designers Administration"
