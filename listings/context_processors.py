# listings/context_processors.py
from .models import Listing, AgentProfile, ContactInquiry, Testimonial
from django.utils import timezone
from datetime import timedelta

def admin_stats(request):
    if request.path.startswith('/admin/'):
        return {
            'total_listings': Listing.objects.count(),
            'active_listings': Listing.objects.filter(status='active').count(),
            'featured_listings': Listing.objects.filter(featured=True).count(),
            'total_agents': AgentProfile.objects.filter(is_active=True).count(),
            'recent_listings': Listing.objects.filter(
                created_at__gte=timezone.now() - timedelta(days=7)
            ).count(),
            'pending_inquiries': ContactInquiry.objects.count(),
            'total_testimonials': Testimonial.objects.filter(is_active=True).count(),
        }
    return {}