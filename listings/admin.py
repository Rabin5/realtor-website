# listings/admin.py - FIXED VERSION
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponse
import csv


from .models import (
    Listing,
    ListingImage,
    AgentProfile,
    ContactInquiry,
    Contact,
    BuyerPreference,
    SiteSetting,
    HeroSection,
    SectionContent,
    Testimonial,
    FAQ,
    Page,
    PropertyInterest,
    Review,
)

# ----------------------
# Helper utilities
# ----------------------

def export_listings_csv(modeladmin, request, queryset):
    """Admin action: export selected listings as CSV"""
    field_names = [
        'id', 'title', 'price', 'status', 'source', 'api_id',
        'address', 'city', 'state', 'zip_code', 'beds', 'baths', 'sq_ft',
        'featured', 'created_at', 'updated_at'
    ]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=listings.csv'

    writer = csv.writer(response)
    writer.writerow(field_names)
    for obj in queryset:
        writer.writerow([getattr(obj, f) for f in field_names])

    return response

export_listings_csv.short_description = "Export selected listings to CSV"

# ----------------------
# Inlines
# ----------------------
class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1
    fields = ('preview', 'image', 'caption', 'order', 'created_at')
    readonly_fields = ('preview', 'created_at')

    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:64px;border-radius:4px;"/>', obj.image.url)
        return "-"
    preview.short_description = 'Preview'

# ----------------------
# Listing Admin
# ----------------------
@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'city', 'price', 'status', 'source', 'featured', 'created_at', 'main_image_preview'
    )
    list_display_links = ('title',)
    list_filter = ('status', 'featured', 'source', 'city')
    search_fields = ('title', 'description', 'address', 'city', 'api_id')
    readonly_fields = ('created_at', 'updated_at', 'get_additional_images_count')
    inlines = (ListingImageInline,)
    actions = (export_listings_csv, 'mark_active', 'mark_sold')
    ordering = ('-created_at',)
    list_per_page = 25

    def main_image_preview(self, obj):
        url = obj.get_first_image()
        if url:
            return format_html('<img src="{}" style="height:80px; border-radius:6px;"/>', url)
        return "-"
    main_image_preview.short_description = 'Image'

    def get_additional_images_count(self, obj):
        return obj.get_additional_images_count()
    get_additional_images_count.short_description = 'Additional images'

    # Simple bulk actions
    def mark_active(self, request, queryset):
        updated = queryset.update(status='active')
        self.message_user(request, f"{updated} listing(s) marked as active.")
    mark_active.short_description = 'Mark selected listings as Active'

    def mark_sold(self, request, queryset):
        updated = queryset.update(status='sold')
        self.message_user(request, f"{updated} listing(s) marked as Sold.")
    mark_sold.short_description = 'Mark selected listings as Sold'

# ----------------------
# AgentProfile Admin
# ----------------------
@admin.register(AgentProfile)
class AgentProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'phone', 'email', 'rating', 'is_active', 'display_order', 'photo_preview')
    list_editable = ('is_active', 'display_order')
    search_fields = ('name', 'email', 'phone')
    readonly_fields = ('photo_preview',)
    fieldsets = (
        (None, {'fields': ('user', 'name', 'title', 'photo', 'photo_preview')}),
        ('Stats', {'fields': ('rating', 'review_count', 'properties_sold', 'client_satisfaction', 'years_experience')}),
        ('Contact & Description', {'fields': ('phone', 'email', 'description', 'areas_of_expertise', 'why_choose')}),
        ('Visibility', {'fields': ('is_active', 'display_order')}),
    )

    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" style="height:80px;border-radius:50%;"/>', obj.photo.url)
        return "-"
    photo_preview.short_description = 'Photo'

    # Provide a compact representation of areas
    def get_areas_short(self, obj):
        return ', '.join(obj.get_areas_of_expertise_list()[:5])
    get_areas_short.short_description = 'Top areas'

# ----------------------
# Content / Site settings Admins
# ----------------------

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'value_short', 'image_preview', 'updated_at')
    search_fields = ('key', 'value')
    readonly_fields = ('image_preview', 'updated_at')

    def value_short(self, obj):
        return (obj.value[:75] + '...') if obj.value and len(obj.value) > 75 else obj.value
    value_short.short_description = 'Value'

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:48px;"/>', obj.image.url)
        return '-'
    image_preview.short_description = 'Image'

@admin.register(HeroSection)
class HeroSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'button_text', 'is_active', 'order', 'background_preview')
    list_editable = ('is_active', 'order')
    readonly_fields = ('background_preview',)

    def background_preview(self, obj):
        if obj.background_image:
            return format_html('<img src="{}" style="height:64px; object-fit:cover;"/>', obj.background_image.url)
        return '-'
    background_preview.short_description = 'Background'

@admin.register(SectionContent)
class SectionContentAdmin(admin.ModelAdmin):
    list_display = ('section', 'title', 'is_active', 'updated_at')
    search_fields = ('section', 'title', 'content')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:48px;"/>', obj.image.url)
        return '-'
    image_preview.short_description = 'Image'

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'company', 'rating', 'is_active', 'order', 'created_at')
    list_editable = ('is_active', 'order')
    readonly_fields = ('avatar_preview',)

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" style="height:48px;border-radius:50%;"/>', obj.avatar.url)
        return '-'
    avatar_preview.short_description = 'Avatar'

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('question', 'answer')

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('page', 'title', 'updated_at')
    readonly_fields = ('header_preview', 'updated_at')

    def header_preview(self, obj):
        if obj.header_image:
            return format_html('<img src="{}" style="height:48px;object-fit:cover;"/>', obj.header_image.url)
        return '-'
    header_preview.short_description = 'Header'

# ----------------------
# Contact & BuyerPreference Admins
# ----------------------
@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'listing', 'email', 'phone', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('created_at',)

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'property_id', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('created_at',)

@admin.register(BuyerPreference)
class BuyerPreferenceAdmin(admin.ModelAdmin):
    list_display = ('property_type', 'budget', 'location', 'bedrooms', 'submitted_at')
    search_fields = ('property_type', 'location')

# ----------------------
# PropertyInterest Admin
# ----------------------
@admin.register(PropertyInterest)
class PropertyInterestAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'interest_type', 'property_type', 'status', 'created_at_short']
    list_filter = ['interest_type', 'property_type', 'status', 'created_at']
    search_fields = ['name', 'email', 'phone']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Contact Info', {
            'fields': ('name', 'email', 'phone', 'message')
        }),
        ('Property Details', {
            'fields': ('interest_type', 'property_type', 'timeline')
        }),
        ('Buyer Info', {
            'fields': ('budget', 'pre_approved', 'bedrooms'),
            'classes': ('collapse',),
        }),
        ('Seller Info', {
            'fields': ('property_value', 'agent_experience', 'property_condition'),
            'classes': ('collapse',),
        }),
        ('Management', {
            'fields': ('status', 'priority', 'notes', 'assigned_to', 'follow_up_date')
        }),
    )
    
    # Custom display methods
    def interest_type(self, obj):
        return obj.get_interest_type_display()
    interest_type.short_description = 'Interest Type'
    interest_type.admin_order_field = 'interest_type'
    
    def property_type(self, obj):
        return obj.get_property_type_display()
    property_type.short_description = 'Property Type'
    property_type.admin_order_field = 'property_type'
    
    def created_at_short(self, obj):
        return obj.created_at.strftime("%Y-%m-%d")
    created_at_short.short_description = 'Created'
    created_at_short.admin_order_field = 'created_at'
    
    ordering = ['-created_at']

# listings/admin.py

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'rating', 'category', 'is_approved', 'featured', 'created_at')
    list_filter = ('is_approved', 'featured', 'category', 'rating', 'created_at')
    search_fields = ('name', 'email', 'comment', 'location')
    list_editable = ('is_approved', 'featured', 'rating')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Reviewer Information', {
            'fields': ('name', 'email', 'location', 'avatar_url', 'user')
        }),
        ('Review Content', {
            'fields': ('rating', 'category', 'comment', 'property_related')
        }),
        ('Administration', {
            'fields': ('is_approved', 'featured', 'helpful_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_reviews', 'feature_reviews', 'unfeature_reviews']
    
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, f"{queryset.count()} reviews approved.")
    approve_reviews.short_description = "Approve selected reviews"
    
    def feature_reviews(self, request, queryset):
        queryset.update(featured=True)
        self.message_user(request, f"{queryset.count()} reviews featured.")
    feature_reviews.short_description = "Feature selected reviews"
    
    def unfeature_reviews(self, request, queryset):
        queryset.update(featured=False)
        self.message_user(request, f"{queryset.count()} reviews unfeatured.")
    unfeature_reviews.short_description = "Remove from featured"

# Admin site branding
# ----------------------
admin.site.site_header = 'Veterans Realty Admin'
admin.site.site_title = 'Veterans Realty CMS'
admin.site.index_title = 'Content & Listings Administration'


