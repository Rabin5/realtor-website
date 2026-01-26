# Standard library imports
import json
import math
import os

# Third-party imports
import requests
from formtools.wizard.views import SessionWizardView
from twilio.rest import Client

# Django imports
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.mail import BadHeaderError, send_mail
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from django.http import (Http404, HttpResponse, HttpResponseForbidden,
                         JsonResponse)
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

# Local imports
from .forms import (ContactForm, ListingSearchForm, ReviewForm, Step1Form,
                    Step2Form, Step3Form, Step4Form)
from .models import (AgentProfile, Listing, PropertyInterest, Review,
                     SectionContent, User)


# ============ HOME VIEW ============
def home(request):
    """Home page view with featured listings and reviews"""
    # Get 4 featured or active listings (prioritize featured ones)
    # featured_listings = Listing.objects.filter(
    #     status='active', 
    #     featured=True
    # ).order_by('-created_at')[:4]
    featured_listings = Listing.objects.filter(
        status='active'
    ).order_by('-created_at')[:4]
    print(featured_listings)
    # If we don't have 4 featured listings, fill with recent active listings
    if featured_listings.count() < 4:
        remaining_count = 4 - featured_listings.count()
        recent_listings = Listing.objects.filter(
            status='active'
        ).exclude(
            id__in=featured_listings.values_list('id', flat=True)
        ).order_by('-created_at')[:remaining_count]
        listings = list(featured_listings) + list(recent_listings)
    else:
        listings = featured_listings
    
    # Get the first active agent profile
    agent_profile = AgentProfile.objects.filter(is_active=True).first()
    
    # Get section content for the home page
    section_content = {
        'agent': SectionContent.objects.filter(section='about', is_active=True).first()
    }
    
    # PDF Files information
    pdf_files = [
        {
            'name': 'TREC License Information',
            'static_path': 'listings/pdfs/CN 1-5.pdf',
            'size': '150 KB',
        },
        {
            'name': 'Brokerage Services Information',
            'static_path': 'listings/pdfs/Information_about_Brokerage_Services__Buyer_Tenant____2_25-2 (1).pdf',
            'size': '180 KB',
        }
    ]
    
    # Get featured reviews
    featured_reviews = Review.objects.filter(
        is_approved=True, 
        featured=True
    ).order_by('-created_at')[:4]
    
    # Get review statistics
    review_stats = Review.objects.filter(is_approved=True).aggregate(
        avg_rating=Avg('rating'),
        total_reviews=Count('id')
    )

    context = {
        'listings': featured_listings,
        'agent_profile': agent_profile,
        'section_content': section_content,
        'pdf_files': pdf_files,
        'featured_reviews': featured_reviews,
        'review_stats': review_stats,

    }
    print(featured_listings)
    return render(request, 'listings/info.html', context)


# ============ CONTACT VIEW ============
@csrf_exempt
def contact_view(request):
    """
    Combined view that handles both GET and POST requests for contact form.
    GET: Renders the contact form page
    POST: Processes form submission and sends emails
    """
    
    if request.method == 'GET':
        return render(request, 'listings/contact.html')
    
    elif request.method == 'POST':
        try:
            # Check content type to handle both JSON and form data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                # Handle form-encoded data
                data = request.POST
            
            # Get form data
            name = data.get('name')
            email = data.get('email')
            message = data.get('message')
            send_copy = data.get('send_copy', False)
            
            # Validate required fields
            if not all([name, email, message]):
                return JsonResponse({
                    'success': False, 
                    'message': 'Please fill in all required fields.'
                }, status=400)
            
            # Validate email format
            if '@' not in email or '.' not in email:
                return JsonResponse({
                    'success': False, 
                    'message': 'Please enter a valid email address.'
                }, status=400)
            
            # Email content for admin
            admin_subject = f"New Contact Form Submission from {name}"
            admin_message_content = f"""
            New Contact Form Submission:
            
            Name: {name}
            Email: {email}
            Message: {message}
            
            Received from website contact form.
            
            ---
            Dream Homes Real Estate
            """
            
            # Send email to admin
            try:
                send_mail(
                    admin_subject,
                    admin_message_content,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.CONTACT_EMAIL],  # Your admin email
                    fail_silently=False,
                )
                
                # Send copy to user if requested
                if send_copy:
                    user_subject = "Copy of Your Message - Dream Homes Real Estate"
                    user_message_content = f"""
                    Dear {name},
                    
                    Thank you for contacting Dream Homes Real Estate! 
                    We have received your message and will get back to you within 24 hours.
                    
                    Here's a copy of your message:
                    
                    ---
                    {message}
                    ---
                    
                    Best regards,
                    The Dream Homes Team
                    
                    ---
                    Dream Homes Real Estate
                    123 Real Estate Ave
                    Killeen, TX 76542
                    Phone: (555) 123-4567
                    Email: hello@dreamhomes.com
                    """
                    
                    send_mail(
                        user_subject,
                        user_message_content,
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        fail_silently=False,
                    )
                
                # Log successful submission (optional)
                print(f"Contact form submitted successfully by {name} ({email})")
                
                return JsonResponse({
                    'success': True, 
                    'message': 'Message sent successfully! We\'ll get back to you within 24 hours.'
                })
                
            except Exception as mail_error:
                # Log mail error
                print(f"Email sending error: {str(mail_error)}")
                return JsonResponse({
                    'success': False, 
                    'message': 'Error sending email. Please try again later.'
                }, status=500)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False, 
                'message': 'Invalid JSON data.'
            }, status=400)
            
        except Exception as e:
            # Log the error for debugging
            print(f"Contact form error: {str(e)}")
            return JsonResponse({
                'success': False, 
                'message': f'Error processing your request: {str(e)}'
            }, status=500)
    
    # Handle other HTTP methods
    return JsonResponse({
        'success': False, 
        'message': 'Invalid request method. Please use GET or POST.'
    }, status=405)


# ============ SEARCH VIEW ============
def search(request):
    """Search listings with filters"""
    form = ListingSearchForm(request.GET)
    qs = Listing.objects.filter(status='active')
    
    if form.is_valid():
        q = form.cleaned_data.get('q')
        if q:
            qs = qs.filter(
                Q(title__icontains=q) | 
                Q(description__icontains=q) | 
                Q(address__icontains=q)
            )
        
        min_price = form.cleaned_data.get('min_price')
        if min_price:
            qs = qs.filter(price__gte=min_price)
        
        max_price = form.cleaned_data.get('max_price')
        if max_price:
            qs = qs.filter(price__lte=max_price)
        
        city = form.cleaned_data.get('city')
        if city:
            qs = qs.filter(city__icontains=city)
        
        beds = form.cleaned_data.get('beds')
        if beds:
            qs = qs.filter(beds__gte=beds)

    paginator = Paginator(qs.order_by('-created_at'), 12)
    page = request.GET.get('page', 1)
    listings_page = paginator.get_page(page)
    
    return render(request, 'listings/home.html', {
        'listings': listings_page, 
        'form': form
    })


# ============ PROPERTY LIST VIEW ============
def property_list(request):
    """Display property list from JSON file"""
    # Get the path to the JSON file inside your app
    json_path = os.path.join(os.path.dirname(__file__), 'properties.json')

    # Load the data
    with open(json_path, 'r') as file:
        properties = json.load(file)

    # Send data to the template
    return render(request, 'listings/property_list.html', {'properties': properties})


# ============ UTILITY FUNCTIONS ============
def calculate_distance(lat1, lng1, lat2, lng2):
    """Calculate distance between two coordinates using Haversine formula"""
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)
    
    a = (math.sin(delta_lat/2) * math.sin(delta_lat/2) + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * 
         math.sin(delta_lng/2) * math.sin(delta_lng/2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c  # Distance in kilometers


def get_coordinates(address):
    """Get coordinates from address with better error handling"""
    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": address,
            "key": settings.GOOGLE_MAPS_API_KEY
        }
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        print(f"Geocoding API response: {data['status']}")
        
        if data['status'] == 'OK' and data['results']:
            loc = data['results'][0]['geometry']['location']
            return loc['lat'], loc['lng']
        else:
            print(f"Geocoding error: {data.get('error_message', 'Unknown error')}")
            return None, None
            
    except Exception as e:
        print(f"Geocoding exception: {e}")
        return None, None


def get_nearby_places(lat, lng, place_type, keyword=None):
    """Search nearby places with better error handling and ranking"""
    try:
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "location": f"{lat},{lng}",
            "radius": 5000,  # 5km radius
            "key": settings.GOOGLE_MAPS_API_KEY,
            "type": place_type,
        }
        
        if keyword:
            params["keyword"] = keyword
            
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        print(f"Places API response for {place_type}: {data['status']}")
        
        if data['status'] == 'OK':
            places = data.get("results", [])
            
            # Calculate distance for each place and add it to the data
            for place in places:
                place_lat = place['geometry']['location']['lat']
                place_lng = place['geometry']['location']['lng']
                distance = calculate_distance(lat, lng, place_lat, place_lng)
                place['distance_km'] = round(distance, 2)
                place['distance_miles'] = round(distance * 0.621371, 2)  # Convert to miles
                
            return places
        else:
            print(f"Places API error: {data.get('error_message', 'Unknown error')}")
            return []
            
    except Exception as e:
        print(f"Places API exception: {e}")
        return []


# ============ PROPERTY DETAIL VIEW ============
def property_detail(request, pk):
    """Property detail view with improved nearby places functionality"""
    # Load JSON data
    json_path = os.path.join(os.path.dirname(__file__), 'properties.json')
    with open(json_path, 'r') as file:
        properties = json.load(file)

    property_obj = next((p for p in properties if p['id'] == pk), None)
    if not property_obj:
        raise Http404("No Listing matches the given query.")

    # Handle images
    images = property_obj.get('images', [])
    if isinstance(images, str):
        try:
            images = json.loads(images)
        except:
            images = [images]
    
    processed_images = []
    for img in images:
        if img.startswith('/'):
            processed_images.append(img[1:])
        else:
            processed_images.append(img)
    
    property_obj['images'] = processed_images

    # Get coordinates
    address = property_obj.get("address", "Killeen, TX")
    lat, lng = get_coordinates(address)

    # Get nearby places with proper sorting
    groceries = []
    schools = []
    
    if lat and lng:
        # Get grocery stores sorted by distance (nearest first)
        groceries = get_nearby_places(lat, lng, "grocery_store", "grocery")
        groceries.sort(key=lambda x: x.get('distance_km', float('inf')))
        
        # Get schools sorted by rating (highest first), then by distance
        schools = get_nearby_places(lat, lng, "school", "school")
        schools.sort(key=lambda x: (
            -x.get('rating', 0),  # Negative for descending rating
            x.get('distance_km', float('inf'))  # Then by distance
        ))
        
    else:
        print("Could not get coordinates for address")
    
    context = {
        "property": property_obj,
        "groceries": groceries[:10],  # Limit to top 10
        "schools": schools[:10],      # Limit to top 10
        "property_lat": lat or 31.1171,  # Default to Killeen coordinates
        "property_lng": lng or -97.7278,
        "GOOGLE_MAPS_API_KEY": getattr(settings, 'GOOGLE_MAPS_API_KEY', ''),
    }
    return render(request, "listings/property_detail.html", context)


# ============ BUYER WIZARD VIEWS ============
FORMS = [
    ("step1", Step1Form),
    ("step2", Step2Form),
    ("step3", Step3Form),
    ("step4", Step4Form),
]

TEMPLATES = {
    "0": "listings/step1.html",
    "1": "listings/step2.html",
    "2": "listings/step3.html",
    "3": "listings/step4.html",
}


class BuyerWizard(SessionWizardView):
    """Multi-step buyer wizard"""
    template_name = "listings/step1.html"
    form_list = FORMS

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        context = {}
        for form in form_list:
            context.update(form.cleaned_data)

        # Compute outcome
        if context['budget'] == '400+' and context['bedrooms'] == '5+':
            result_tag = 'Luxury-Home'
        elif context['budget'] == '<$250k':
            result_tag = 'FirstTimeBuyer'
        else:
            result_tag = 'MidRange'

        return render(self.request, "listings/results.html", {
            "answers": context,
            "result_tag": result_tag,
        })


class BuyerQuizWizard(SessionWizardView):
    """Buyer quiz wizard"""
    form_list = FORMS

    def get_template_names(self):
        return [TEMPLATES[self.steps.current]]

    def done(self, form_list, **kwargs):
        data = {}
        for form in form_list:
            data.update(form.cleaned_data)

        # Note: BuyerQuizResponse model needs to be defined
        # BuyerQuizResponse.objects.create(
        #     property_type = data['property_type'],
        #     budget = data['budget'],
        #     location = data['location'],
        #     bedrooms = data['bedrooms']
        # )

        return render(self.request, "buyer/results.html", {
            "answers": data,
            "properties": []  # Add matching properties logic here
        })

    def budget_to_max_price(self, budget_choice):
        """Convert budget choice to max price"""
        mapping = {
            '<$250k': 250000,
            '250-400': 400000,
            '>400': 1000000,
        }
        return mapping.get(budget_choice, 500000)


# ============ MISC VIEWS ============
def killeen(request):
    """Killeen information page"""
    return render(request, 'listings/info1.html')


@csrf_exempt
def save_property_interest(request):
    """Save property interest form data"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Create new interest record
            interest = PropertyInterest.objects.create(
                interest_type=data.get('interest_type', 'buyer'),
                name=data.get('name', ''),
                email=data.get('email', ''),
                phone=data.get('phone', ''),
                property_type=data.get('property_type', ''),
                timeline=data.get('timeline', ''),
                budget=data.get('budget', ''),
                pre_approved=data.get('pre_approved', ''),
                bedrooms=data.get('bedrooms', ''),
                property_value=data.get('property_value', ''),
                agent_experience=data.get('agent_experience', ''),
                property_condition=data.get('property_condition', ''),
                message=data.get('message', '')
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Thank you! Your information has been submitted successfully.',
                'id': interest.id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


# ============ AUTHENTICATION VIEWS ============
def login_view(request):
    """Handle user login"""
    if request.user.is_authenticated:
        return redirect('listings:admin_dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                
                # Check if user is admin
                if user.is_staff or user.is_superuser:
                    return redirect('listings:admin_dashboard')
                return redirect('listings:property_list')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'listings/login.html', {'form': form})


def register_view(request):
    """Handle user registration"""
    if request.user.is_authenticated:
        return redirect('listings:property_list')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('listings:property_list')
        else:
            # Show form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserCreationForm()
    
    return render(request, 'listings/register.html', {'form': form})


def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('listings:login')


@login_required
def profile_view(request):
    """User profile page"""
    return render(request, 'listings/profile.html')


# ============ ADMIN DASHBOARD VIEWS ============
def is_admin(user):
    """Check if user is admin/staff"""
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard - only accessible by staff/superusers"""
    # Get counts for stats
    user_count = User.objects.count()
    
    # Get property interest counts
    total_interests = PropertyInterest.objects.count()
    new_interests = PropertyInterest.objects.filter(status='new').count()
    
    context = {
        'user_count': user_count,
        'total_interests': total_interests,
        'new_interests': new_interests,
        'property_count': 0,  # You can add your property count logic
        'lead_count': total_interests,  # Using total interests as leads
    }
    
    return render(request, 'listings/admin_dashboard.html', context)


# ============ PROPERTY INTEREST VIEWS ============
@login_required
@user_passes_test(is_admin)
def interest_dashboard(request):
    """Main dashboard for property interests"""
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    interest_type_filter = request.GET.get('interest_type', 'all')
    priority_filter = request.GET.get('priority', 'all')
    
    # Start with all interests
    interests = PropertyInterest.objects.all().order_by('-created_at')
    
    # Apply filters
    if status_filter != 'all':
        interests = interests.filter(status=status_filter)
    
    if interest_type_filter != 'all':
        interests = interests.filter(interest_type=interest_type_filter)
    
    if priority_filter != 'all':
        interests = interests.filter(priority=priority_filter)
    
    # Get counts for stats
    total_interests = PropertyInterest.objects.count()
    new_interests = PropertyInterest.objects.filter(status='new').count()
    contacted_interests = PropertyInterest.objects.filter(status='contacted').count()
    buyers_count = PropertyInterest.objects.filter(interest_type='buyer').count()
    sellers_count = PropertyInterest.objects.filter(interest_type='seller').count()
    
    # Pagination
    paginator = Paginator(interests, 20)  # 20 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'interests': page_obj,
        'total_interests': total_interests,
        'new_interests': new_interests,
        'contacted_interests': contacted_interests,
        'buyers_count': buyers_count,
        'sellers_count': sellers_count,
        'current_status': status_filter,
        'current_interest_type': interest_type_filter,
        'current_priority': priority_filter,
        'status_choices': dict(PropertyInterest.STATUS_CHOICES),
        'interest_type_choices': dict(PropertyInterest.INTEREST_TYPE_CHOICES),
        'priority_choices': dict(PropertyInterest.PRIORITY_CHOICES),
    }
    
    return render(request, 'listings/interest_dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def interest_detail(request, interest_id):
    """View details of a specific property interest"""
    interest = get_object_or_404(PropertyInterest, id=interest_id)
    
    # Get all staff users for assignment
    staff_users = User.objects.filter(is_staff=True)
    
    if request.method == 'POST':
        # Handle form submission
        action = request.POST.get('action')
        
        if action == 'update_status':
            new_status = request.POST.get('status')
            interest.status = new_status
            if new_status == 'contacted':
                interest.contacted_date = timezone.now()
            interest.save()
            messages.success(request, f'Status updated to {interest.get_status_display()}')
            
        elif action == 'add_note':
            note = request.POST.get('note')
            if note:
                if interest.notes:
                    interest.notes += f"\n\n[{timezone.now().strftime('%Y-%m-%d %H:%M')}] {note}"
                else:
                    interest.notes = f"[{timezone.now().strftime('%Y-%m-%d %H:%M')}] {note}"
                interest.save()
                messages.success(request, 'Note added successfully')
                
        elif action == 'assign_to':
            user_id = request.POST.get('assigned_to')
            if user_id:
                user = get_object_or_404(User, id=user_id)
                interest.assigned_to = user
                interest.save()
                messages.success(request, f'Assigned to {user.username}')
                
        elif action == 'update_priority':
            priority = request.POST.get('priority')
            interest.priority = priority
            interest.save()
            messages.success(request, f'Priority updated to {interest.get_priority_display()}')
            
        return redirect('listings:interest_detail', interest_id=interest_id)
    
    context = {
        'interest': interest,
        'staff_users': staff_users,
    }
    
    return render(request, 'listings/interest_detail.html', context)


@login_required
@user_passes_test(is_admin)
def delete_interest(request, interest_id):
    """Delete a property interest"""
    interest = get_object_or_404(PropertyInterest, id=interest_id)
    
    if request.method == 'POST':
        interest.delete()
        messages.success(request, 'Property interest deleted successfully')
        return redirect('listings:interest_dashboard')
    
    return render(request, 'listings/confirm_delete.html', {'interest': interest})


@login_required
@user_passes_test(is_admin)
def bulk_update_interests(request):
    """Handle bulk actions on interests"""
    if request.method == 'POST':
        action = request.POST.get('bulk_action')
        selected_ids = request.POST.getlist('selected_interests')
        
        if not selected_ids:
            messages.error(request, 'No interests selected')
            return redirect('listings:interest_dashboard')
        
        interests = PropertyInterest.objects.filter(id__in=selected_ids)
        
        if action == 'mark_contacted':
            for interest in interests:
                interest.mark_as_contacted()
            messages.success(request, f'{len(interests)} interests marked as contacted')
            
        elif action == 'delete':
            count = interests.count()
            interests.delete()
            messages.success(request, f'{count} interests deleted')
            
        elif action == 'update_status':
            status = request.POST.get('bulk_status')
            if status:
                interests.update(status=status)
                messages.success(request, f'{len(interests)} interests status updated')
                
        elif action == 'update_priority':
            priority = request.POST.get('bulk_priority')
            if priority:
                interests.update(priority=priority)
                messages.success(request, f'{len(interests)} interests priority updated')
    
    return redirect('listings:interest_dashboard')


@login_required
def interest_analytics(request):
    """Basic property interest analytics"""
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('listings:property_list')
    
    # Simple counts
    interests = PropertyInterest.objects.all()
    
    context = {
        'total': interests.count(),
        'buyers': interests.filter(interest_type='buyer').count(),
        'sellers': interests.filter(interest_type='seller').count(),
        'new': interests.filter(status='new').count(),
        'contacted': interests.filter(status='contacted').count(),
    }
    
    return render(request, 'listings/interest_analytics.html', context)


# ============ REVIEW VIEWS ============
def review_stats(request):
    """Get review statistics for AJAX requests"""
    stats = Review.objects.filter(is_approved=True).aggregate(
        avg_rating=Avg('rating'),
        total_reviews=Count('id'),
        featured_reviews=Count('id', filter=Q(featured=True)),
        five_star_reviews=Count('id', filter=Q(rating=5))
    )
    
    # Calculate percentages
    if stats['total_reviews'] > 0:
        stats['satisfaction_rate'] = round((stats['five_star_reviews'] / stats['total_reviews']) * 100)
    else:
        stats['satisfaction_rate'] = 0
        
    return JsonResponse(stats)


def reviews_list(request):
    """Get reviews for AJAX requests"""
    print("=== DEBUG: reviews_list called ===")
    category = request.GET.get('category', 'all')
    page = request.GET.get('page', 1)
    
    # Debug all reviews
    all_reviews = Review.objects.all()
    print(f"Total reviews in DB: {all_reviews.count()}")
    print(f"Approved reviews: {all_reviews.filter(is_approved=True).count()}")
    print(f"Featured reviews: {all_reviews.filter(featured=True).count()}")
    
    reviews = Review.objects.filter(is_approved=True)
    print(f"Reviews after approval filter: {reviews.count()}")
    
    if category != 'all':
        reviews = reviews.filter(category=category)
        print(f"Reviews after category filter ({category}): {reviews.count()}")
    
    # Show first few reviews for debugging
    for r in reviews[:5]:
        print(f"Review: {r.id} - {r.name} - {r.rating} - Approved: {r.is_approved}")
    
    # Pagination
    paginator = Paginator(reviews.order_by('-featured', '-created_at'), 8)
    try:
        page_obj = paginator.page(page)
    except:
        page_obj = paginator.page(1)
    
    reviews_data = []
    for review in page_obj:
        reviews_data.append({
            'id': str(review.id),
            'name': review.name,
            'avatar_url': review.get_avatar(),
            'rating': review.rating,
            'stars_html': review.get_stars(),
            'comment': review.comment,
            'location': review.location,
            'category': review.get_category_display_name(),
            'date': review.get_display_date(),
            'property_related': review.property_related,
            'featured': review.featured,
            'helpful_count': review.helpful_count,
        })
    
    response_data = {
        'reviews': reviews_data,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
        'total_reviews': reviews.count(),
        'debug': {
            'total_in_db': Review.objects.count(),
            'approved_count': Review.objects.filter(is_approved=True).count(),
            'request_category': category,
        }
    }
    
    print(f"=== DEBUG: Returning {len(reviews_data)} reviews ===")
    return JsonResponse(response_data)
    """Get reviews for AJAX requests"""
    category = request.GET.get('category', 'all')
    page = request.GET.get('page', 1)
    
    reviews = Review.objects.filter(is_approved=True)
    
    if category != 'all':
        reviews = reviews.filter(category=category)
    
    # Pagination
    paginator = Paginator(reviews.order_by('-featured', '-created_at'), 8)
    page_obj = paginator.get_page(page)
    
    reviews_data = []
    for review in page_obj:
        reviews_data.append({
            'id': str(review.id),
            'name': review.name,
            'avatar_url': review.get_avatar(),
            'rating': review.rating,
            'stars_html': review.get_stars(),
            'comment': review.comment,
            'location': review.location,
            'category': review.get_category_display_name(),
            'date': review.get_display_date(),
            'property_related': review.property_related,
            'featured': review.featured,
            'helpful_count': review.helpful_count,
        })
    
    return JsonResponse({
        'reviews': reviews_data,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
    })

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError

@csrf_exempt  # Temporarily disable CSRF for testing
def submit_review(request):
    """Handle review submission with detailed debugging"""
    print("\n" + "="*80)
    print("DEBUG: submit_review() called")
    print(f"Request method: {request.method}")
    print(f"User authenticated: {request.user.is_authenticated}")
    print(f"Content-Type: {request.content_type}")
    print(f"Headers: {dict(request.headers)}")
    
    if request.method == 'POST':
        try:
            # Check if it's JSON or form data
            if request.content_type == 'application/json':
                print("Processing JSON data...")
                data = json.loads(request.body)
                print(f"JSON data: {data}")
                form_data = data
            else:
                print("Processing form data...")
                print(f"POST data: {dict(request.POST)}")
                print(f"FILES data: {dict(request.FILES)}")
                form_data = request.POST
            
            # Create form
            from .forms import ReviewForm
            form = ReviewForm(form_data)
            
            print(f"\nForm validation:")
            print(f"  Is valid: {form.is_valid()}")
            
            if not form.is_valid():
                print(f"  Errors: {form.errors}")
                print("="*80)
                return JsonResponse({
                    'success': False,
                    'errors': form.errors.get_json_data()
                }, status=400)
            
            # Save the review
            review = form.save(commit=False)
            print(f"\nReview object created:")
            print(f"  Name: {review.name}")
            print(f"  Email: {review.email}")
            print(f"  Rating: {review.rating}")
            print(f"  Comment: {review.comment[:50]}...")
            
            # Auto-approve if user is authenticated
            if request.user.is_authenticated:
                review.user = request.user
                review.is_approved = True
                print("  Auto-approved (user authenticated)")
            else:
                review.is_approved = False
                print("  Not approved (anonymous user)")
            
            # Save to database
            review.save()
            print(f"\n✅ Review saved successfully!")
            print(f"  ID: {review.id}")
            print(f"  Created at: {review.created_at}")
            
            # Verify in database
            from .models import Review
            db_check = Review.objects.filter(id=review.id).exists()
            print(f"  Verified in database: {db_check}")
            
            print("="*80)
            
            return JsonResponse({
                'success': True,
                'message': 'Thank you for your review! It has been submitted for approval.',
                'review_id': str(review.id)
            })
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            print("="*80)
            
            return JsonResponse({
                'success': False,
                'error': str(e),
                'message': 'An error occurred while submitting your review.'
            }, status=500)
    
    else:
        print("❌ Invalid request method (not POST)")
        print("="*80)
        return JsonResponse({
            'success': False,
            'error': 'Invalid request method'
        }, status=405)
    """Handle review submission"""
    if request.method == 'POST':
        print("=== DEBUG: SUBMIT REVIEW START ===")
        print(f"User authenticated: {request.user.is_authenticated}")
        print(f"POST data: {dict(request.POST)}")
        
        form = ReviewForm(request.POST)
        print(f"Form valid: {form.is_valid()}")
        
        if not form.is_valid():
            print(f"Form errors: {form.errors}")
            print("=== DEBUG: SUBMIT REVIEW END (INVALID) ===")
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                })
            else:
                messages.error(request, 'Please correct the errors below.')
                return render(request, 'listings/submit_review.html', {'form': form})
        
        try:
            review = form.save(commit=False)
            print(f"Review object created: {review}")
            
            # Set user if authenticated
            if request.user.is_authenticated:
                review.user = request.user
                review.is_approved = True
                print(f"User set: {review.user}, Auto-approved: {review.is_approved}")
            else:
                review.is_approved = False
                print(f"Not authenticated, approval pending: {review.is_approved}")
            
            review.save()
            print(f"Review saved with ID: {review.id}")
            print(f"Review details: {review.name}, {review.rating}, {review.comment[:50]}...")
            
            # Debug: Query to see if review exists in database
            from django.db import connection
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM your_app_review WHERE id = %s", [review.id])
            count = cursor.fetchone()[0]
            print(f"Database check - Reviews with this ID: {count}")
            
            print("=== DEBUG: SUBMIT REVIEW END (SUCCESS) ===")
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Thank you for your review! It has been submitted for approval.',
                    'review_id': str(review.id)
                })
            else:
                messages.success(request, 'Thank you for your review! It has been submitted for approval.')
                return redirect('listings:home')
                
        except Exception as e:
            print(f"=== ERROR SAVING REVIEW: {str(e)} ===")
            import traceback
            traceback.print_exc()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                })
            else:
                messages.error(request, f'Error saving review: {str(e)}')
                return render(request, 'listings/submit_review.html', {'form': form})
    
    else:
        form = ReviewForm()
    
    return render(request, 'listings/submit_review.html', {'form': form})



def mark_helpful(request, review_id):
    """Mark a review as helpful"""
    if request.method == 'POST':
        review = get_object_or_404(Review, id=review_id)
        
        # Use session to prevent multiple votes
        session_key = f'helpful_{review_id}'
        if not request.session.get(session_key):
            review.helpful_count += 1
            review.save()
            request.session[session_key] = True
            
            return JsonResponse({
                'success': True,
                'helpful_count': review.helpful_count
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'You have already marked this review as helpful.'
            })
    
    return HttpResponseForbidden()


@login_required
def admin_review_dashboard(request):
    """Admin dashboard for managing reviews"""
    if not request.user.is_staff:
        return redirect('listings:home')
    
    reviews = Review.objects.all().order_by('-created_at')
    
    # Statistics
    stats = {
        'total': reviews.count(),
        'approved': reviews.filter(is_approved=True).count(),
        'pending': reviews.filter(is_approved=False).count(),
        'featured': reviews.filter(featured=True).count(),
        'avg_rating': reviews.filter(is_approved=True).aggregate(Avg('rating'))['rating__avg'] or 0,
    }
    
    context = {
        'reviews': reviews,
        'stats': stats,
    }
    return render(request, 'listings/admin_review_dashboard.html', context)