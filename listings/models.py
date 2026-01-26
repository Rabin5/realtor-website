from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
from django.contrib.auth.models import User
# listings/models.py
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid




class Listing(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('sold', 'Sold'),
    ]
    
    SOURCE_CHOICES = [
        ('manual', 'Manual Entry'),
        ('api', 'API Import'),
    ]
    
    # Source tracking
    source = models.CharField(
        max_length=20, 
        choices=SOURCE_CHOICES, 
        default='manual'
    )
    api_id = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        help_text="External API ID"
    )
    
    # Basic Information
    title = models.CharField(max_length=200, default="New Property Listing")
    description = models.TextField(default="Property description")
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # Location
    address = models.CharField(max_length=255, default="123 Main Street")
    city = models.CharField(max_length=100, default="Killeen")
    state = models.CharField(max_length=50, default='TX')
    zip_code = models.CharField(max_length=10, blank=True, default="76541")
    
    # Property Details - ADD DEFAULTS TO THESE FIELDS
    beds = models.IntegerField(default=3)
    baths = models.DecimalField(max_digits=3, decimal_places=1, default=2.0)  # Added default
    sq_ft = models.IntegerField(null=True, blank=True, default=1500)
    
    # Media
    main_image = models.ImageField(upload_to='properties/main/', null=True, blank=True)
    
    # Status and Features
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    featured = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - ${self.price}"
    
    def get_first_image(self):
        if self.main_image:
            return self.main_image.url
        first_additional = self.additional_images.first()
        if first_additional:
            return first_additional.image.url
        return None
    
    def get_additional_images_count(self):
        return self.additional_images.count()


class ListingImage(models.Model):
    listing = models.ForeignKey(
        Listing, 
        on_delete=models.CASCADE, 
        related_name='additional_images'
    )
    image = models.ImageField(upload_to='properties/additional/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['order', 'created_at']
    
    def __str__(self):
        return f"Image for {self.listing.title}"
      

class AgentProfile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    name = models.CharField(max_length=100, default="Raja Ram Gautam")
    title = models.CharField(max_length=100, default="Senior Real Estate Specialist")
    photo = models.ImageField(upload_to='agents/', null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.7)
    review_count = models.IntegerField(default=128)
    
    # Stats
    properties_sold = models.CharField(max_length=50, default="500+")
    client_satisfaction = models.CharField(max_length=50, default="98%")
    years_experience = models.CharField(max_length=50, default="15+")
    
    # Contact
    phone = models.CharField(max_length=20, default="(555) 123-4567")
    email = models.EmailField(default="raja@veteransrealty.com")
    
    # Description and details
    description = models.TextField(
        default="Welcome to Veterans Realty, where your home journey begins with confidence and trust. Our lead realtor is one of the most talented, well-experienced, and highly professional agents in the Central Texas area."
    )
    areas_of_expertise = models.TextField(
        default="Residential Home Sales and Purchases\nVA and FHA Loan Support\nMilitary Relocation Assistance (Fort Cavazos Area)\nInvestment and Rental Properties\nNew Construction & First-Time Home Buyers",
        help_text="Enter each area of expertise on a new line"
    )
    why_choose = models.TextField(
        default="Highly Experienced: Proven track record of successful home sales and purchases.\nProfessional & Reliable: Trusted by clients for his honesty and clear communication.\nLocal Market Expert: Deep knowledge of Fort Cavazos, Killeen, Harker Heights, and Copperas Cove.\nMilitary Friendly: Dedicated to supporting our service members and their families.",
        help_text="Enter each reason on a new line, format: Title: Description"
    )
    
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = "Agent Profile"
        verbose_name_plural = "Agent Profiles"
    
    def __str__(self):
        return self.name
    
    def get_areas_of_expertise_list(self):
        """Convert text area to list of items"""
        if self.areas_of_expertise:
            return [item.strip() for item in self.areas_of_expertise.split('\n') if item.strip()]
        return []
    
    def get_why_choose_list(self):
        """Convert text area to list of items with title and description"""
        items = []
        if self.why_choose:
            for item in self.why_choose.split('\n'):
                if ':' in item:
                    title, description = item.split(':', 1)
                    items.append({
                        'title': title.strip(),
                        'description': description.strip()
                    })
                else:
                    items.append({
                        'title': item.strip(),
                        'description': ''
                    })
        return items
    
    def get_star_rating(self):
        """Generate star rating HTML"""
        full_stars = int(self.rating)
        half_star = self.rating - full_stars >= 0.5
        empty_stars = 5 - full_stars - (1 if half_star else 0)
        
        stars = []
        stars.extend(['fas fa-star'] * full_stars)
        if half_star:
            stars.append('fas fa-star-half-alt')
        stars.extend(['far fa-star'] * empty_stars)
        
        return stars
    
    def get_first_name(self):
        """Extract first name from full name"""
        return self.name.split()[0] if self.name else "Agent"
# listings/models.py




class ContactInquiry(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'Inquiry from {self.name} about {self.listing}'


class Contact(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    message = models.TextField()
    property_id = models.IntegerField(null=True, blank=True)  # optional link to property
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.email}) - property {self.property_id or 'general'}"


# models.py
class BuyerPreference(models.Model):
    property_type = models.CharField(max_length=50)
    budget = models.CharField(max_length=50)
    location = models.CharField(max_length=50)
    bedrooms = models.CharField(max_length=50)
    submitted_at = models.DateTimeField(auto_now_add=True)




# listings/models.py

# Override storage to organize uploaded files
class PageContentStorage(FileSystemStorage):
    def get_available_name(self, name, max_length=None):
        # Remove existing file if it exists
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name

page_storage = PageContentStorage()

class SiteSetting(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField(blank=True)
    image = models.ImageField(
        upload_to='site-settings/', 
        storage=page_storage,
        null=True, 
        blank=True
    )
    description = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.key
    
    class Meta:
        verbose_name = "Site Setting"
        verbose_name_plural = "Site Settings"

class HeroSection(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.TextField(blank=True)
    background_image = models.ImageField(
        upload_to='hero/',
        storage=page_storage,
        help_text="Recommended size: 1920x800px"
    )
    button_text = models.CharField(max_length=50, default="Browse Properties")
    button_link = models.CharField(max_length=100, default="/properties/")
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order', '-is_active']
        verbose_name = "Hero Section"
        verbose_name_plural = "Hero Sections"
    
    def __str__(self):
        return f"Hero: {self.title}"

class SectionContent(models.Model):
    SECTION_CHOICES = [
        ('about', 'About Section'),
        ('services', 'Services Section'),
        ('testimonials', 'Testimonials'),
        ('cta', 'Call to Action'),
        ('features', 'Features'),
        ('contact_info', 'Contact Information'),
    ]
    
    section = models.CharField(max_length=50, choices=SECTION_CHOICES, unique=True)
    title = models.CharField(max_length=200, blank=True)
    content = models.TextField(blank=True)
    image = models.ImageField(
        upload_to='section-content/',
        storage=page_storage,
        null=True, 
        blank=True
    )
    button_text = models.CharField(max_length=50, blank=True)
    button_link = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Section Content"
        verbose_name_plural = "Section Contents"
    
    def __str__(self):
        return self.get_section_display()

class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=100, blank=True)
    content = models.TextField()
    avatar = models.ImageField(
        upload_to='testimonials/',
        storage=page_storage,
        null=True, 
        blank=True
    )
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=5)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "Testimonial"
        verbose_name_plural = "Testimonials"
    
    def __str__(self):
        return f"Testimonial from {self.name}"

class FAQ(models.Model):
    question = models.CharField(max_length=200)
    answer = models.TextField()
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order']
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"
    
    def __str__(self):
        return self.question

class Page(models.Model):
    PAGE_CHOICES = [
        ('home', 'Home Page'),
        ('about', 'About Page'),
        ('contact', 'Contact Page'),
        ('properties', 'Properties Page'),
    ]
    
    page = models.CharField(max_length=50, choices=PAGE_CHOICES, unique=True)
    title = models.CharField(max_length=200)
    meta_description = models.TextField(blank=True)
    header_image = models.ImageField(
        upload_to='page-headers/',
        storage=page_storage,
        null=True, 
        blank=True
    )
    content = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Page Content"
        verbose_name_plural = "Page Contents"
    
    def __str__(self):
        return self.get_page_display()

# listings/models.py - Update your PropertyInterest model
# listings/models.py - Make sure your PropertyInterest model has all fields


class PropertyInterest(models.Model):
    # ============ DEFINE ALL CHOICES FIRST ============
    INTEREST_TYPE_CHOICES = [
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
    ]
    
    PROPERTY_TYPE_CHOICES = [
        ('house', 'House'),
        ('apartment', 'Apartment'),
        ('condo', 'Condo'),
        ('land', 'Land'),
        ('commercial', 'Commercial'),
    ]
    
    TIMELINE_CHOICES = [
        ('immediately', 'Immediately'),
        ('1-3 months', '1-3 Months'),
        ('3-6 months', '3-6 Months'),
        ('6+ months', '6+ Months'),
        ('just exploring', 'Just Exploring Options'),
    ]
    
    BUDGET_CHOICES = [
        ('under-250k', 'Under $250,000'),
        ('250k-500k', '$250,000 - $500,000'),
        ('500k-1m', '$500,000 - $1 Million'),
        ('1m-2m', '$1 Million - $2 Million'),
        ('over-2m', 'Over $2 Million'),
    ]
    
    PROPERTY_VALUE_CHOICES = [
        ('under-250k', 'Under $250,000'),
        ('250k-500k', '$250,000 - $500,000'),
        ('500k-1m', '$500,000 - $1 Million'),
        ('1m-2m', '$1 Million - $2 Million'),
        ('over-2m', 'Over $2 Million'),
    ]
    
    AGENT_EXPERIENCE_CHOICES = [
        ('yes-currently', 'Yes, Currently Working With One'),
        ('yes-past', 'Yes, In The Past'),
        ('no', 'No, This Is My First Time'),
    ]
    
    PROPERTY_CONDITION_CHOICES = [
        ('excellent', 'Excellent - Recently Renovated'),
        ('good', 'Good - Well Maintained'),
        ('average', 'Average - Needs Some Updates'),
        ('needs-work', 'Needs Work - Significant Updates Required'),
    ]
    
    PRE_APPROVED_CHOICES = [
        ('yes', 'Yes'),
        ('no', 'No'),
        ('working-on-it', 'Working On It'),
        ('cash-buyer', 'Cash Buyer'),
    ]
    
    BEDROOMS_CHOICES = [
        ('studio', 'Studio'),
        ('1', '1 Bedroom'),
        ('2', '2 Bedrooms'),
        ('3', '3 Bedrooms'),
        ('4+', '4+ Bedrooms'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('in_progress', 'In Progress'),
        ('qualified', 'Qualified'),
        ('closed', 'Closed'),
        ('rejected', 'Rejected'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    # ============ MODEL FIELDS ============
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    interest_type = models.CharField(max_length=20, choices=INTEREST_TYPE_CHOICES)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES)
    timeline = models.CharField(max_length=20, choices=TIMELINE_CHOICES)
    
    # For buyers
    budget = models.CharField(max_length=20, choices=BUDGET_CHOICES, blank=True)
    pre_approved = models.CharField(max_length=20, choices=PRE_APPROVED_CHOICES, blank=True)
    bedrooms = models.CharField(max_length=10, choices=BEDROOMS_CHOICES, blank=True)
    
    # For sellers
    property_value = models.CharField(max_length=20, choices=PROPERTY_VALUE_CHOICES, blank=True)
    agent_experience = models.CharField(max_length=20, choices=AGENT_EXPERIENCE_CHOICES, blank=True)
    property_condition = models.CharField(max_length=20, choices=PROPERTY_CONDITION_CHOICES, blank=True)
    
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # New management fields
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    notes = models.TextField(blank=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                    related_name='assigned_interests')
    contacted_date = models.DateTimeField(null=True, blank=True)
    follow_up_date = models.DateTimeField(null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_interest_type_display()}"
    
    # Helper methods
    def is_buyer(self):
        return self.interest_type == 'buyer'
    
    def is_seller(self):
        return self.interest_type == 'seller'
    
    def mark_as_contacted(self):
        """Mark this interest as contacted"""
        self.status = 'contacted'
        self.contacted_date = timezone.now()
        self.save()
    
    def get_display_info(self):
        """Get display information for templates"""
        info = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'interest_type': self.get_interest_type_display(),
            'property_type': self.get_property_type_display(),
            'timeline': self.get_timeline_display(),
            'status': self.get_status_display(),
            'priority': self.get_priority_display(),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M'),
            'is_buyer': self.is_buyer(),
            'is_seller': self.is_seller(),
        }
        
        if self.is_buyer():
            info.update({
                'budget': self.get_budget_display() if self.budget else 'Not specified',
                'pre_approved': self.get_pre_approved_display() if self.pre_approved else 'Not specified',
                'bedrooms': self.get_bedrooms_display() if self.bedrooms else 'Not specified',
            })
        else:
            info.update({
                'property_value': self.get_property_value_display() if self.property_value else 'Not specified',
                'agent_experience': self.get_agent_experience_display() if self.agent_experience else 'Not specified',
                'property_condition': self.get_property_condition_display() if self.property_condition else 'Not specified',
            })
        
        return info 



class Review(models.Model):
    REVIEW_CATEGORIES = [
        ('buying', 'Buying Experience'),
        ('selling', 'Selling Experience'),
        ('military', 'Military Relocation'),
        ('first_time', 'First-Time Home Buyer'),
        ('investment', 'Investment Property'),
        ('general', 'General Experience'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5
    )
    category = models.CharField(max_length=50, choices=REVIEW_CATEGORIES, default='general')
    comment = models.TextField()
    location = models.CharField(max_length=100, blank=True, null=True)
    avatar_url = models.URLField(blank=True, null=True)
    property_related = models.CharField(max_length=200, blank=True, null=True, help_text="Property or service mentioned in review")
    
    # Admin control
    is_approved = models.BooleanField(default=False)
    featured = models.BooleanField(default=False)
    helpful_count = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # User relation (optional)
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='reviews'
    )
    
    class Meta:
        ordering = ['-created_at', '-featured']
        verbose_name = "Client Review"
        verbose_name_plural = "Client Reviews"
    
    def __str__(self):
        return f"{self.name} - {self.rating} stars"
    
    def get_stars(self):
        """Generate star rating HTML"""
        full_stars = self.rating
        half_star = False
        empty_stars = 5 - full_stars
        
        stars_html = ''
        for i in range(full_stars):
            stars_html += '<i class="fas fa-star"></i>'
        if half_star:
            stars_html += '<i class="fas fa-star-half-alt"></i>'
        for i in range(empty_stars):
            stars_html += '<i class="far fa-star"></i>'
        return stars_html
    
    def get_avatar(self):
        """Get avatar URL or generate a default"""
        if self.avatar_url:
            return self.avatar_url
        # Generate random avatar based on name
        seed = abs(hash(self.name)) % 100
        gender = 'women' if seed % 2 == 0 else 'men'
        return f"https://randomuser.me/api/portraits/{gender}/{seed}.jpg"
    
    def get_display_date(self):
        """Format date for display"""
        return self.created_at.strftime("%B %Y")
    
    def get_category_display_name(self):
        """Get category display name"""
        return dict(self.REVIEW_CATEGORIES).get(self.category, 'General Experience')