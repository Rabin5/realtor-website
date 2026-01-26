from django.urls import path
from . import views
from .forms import Step1Form, Step2Form, Step3Form, Step4Form
from .views import (
    login_view, register_view, logout_view, 
    profile_view, admin_dashboard, BuyerWizard
)
from django.contrib.auth.decorators import login_required, user_passes_test 
from django.contrib.auth import views as auth_views  # Add this import


app_name = 'listings'

# Custom test functions
def is_staff_user(user):
    return user.is_authenticated and user.is_staff

urlpatterns = [
    # Public URLs (no protection needed)
    path('', views.home, name='home'),
    path('listing/<int:pk>/', views.property_detail, name='property_detail'),
    path('contact/', views.contact_view, name='contact'),
    path('search/', views.search, name='search'),
    path("proprty_list/", views.property_list, name="property_list"),
    path('killeen/', views.killeen, name='killeen'),
    path('save-interest/', views.save_property_interest, name='save_interest'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    
    # 🔒 PROTECTED URLs - Redirect to login if unauthorized
    
    # Regular user URLs
    path('profile/', login_required(login_url='listings:login')(profile_view), name='profile'),
    
    # Buyer questionnaire
    path(
        "buyer-questionnaire/",
        login_required(login_url='listings:login')(
            BuyerWizard.as_view([Step1Form, Step2Form, Step3Form, Step4Form])
        ),
        name="buyer_questionnaire",
    ),
    
    # 🔒 ADMIN URLs - Staff only, redirect to login if not staff
    path('admin-dashboard/', 
         user_passes_test(is_staff_user, login_url='listings:login')(admin_dashboard), 
         name='admin_dashboard'),
    
    # Interest management URLs (Admin only)
    path('interest-dashboard/', 
         user_passes_test(is_staff_user, login_url='listings:login')(views.interest_dashboard), 
         name='interest_dashboard'),
    
    path('interest/<int:interest_id>/', 
         user_passes_test(is_staff_user, login_url='listings:login')(views.interest_detail), 
         name='interest_detail'),
    
    path('interest/<int:interest_id>/delete/', 
         user_passes_test(is_staff_user, login_url='listings:login')(views.delete_interest), 
         name='delete_interest'),
    
    path('bulk-update-interests/', 
         user_passes_test(is_staff_user, login_url='listings:login')(views.bulk_update_interests), 
         name='bulk_update_interests'),
    
    path('interest-analytics/', 
         user_passes_test(is_staff_user, login_url='listings:login')(views.interest_analytics), 
         name='interest_analytics'),

        # 🔄 Password Reset URLs
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='listings/password_reset.html',
             email_template_name='listings/password_reset_email.html',
             subject_template_name='listings/password_reset_subject.txt',
             success_url='/password-reset/done/'
         ), 
         name='password_reset'),
    
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='listings/password_reset_done.html'
         ), 
         name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='listings/password_reset_confirm.html',
             success_url='/password-reset/complete/'
         ), 
         name='password_reset_confirm'),
    
    path('password-reset/complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='listings/password_reset_complete.html'
         ), 
         name='password_reset_complete'),



         # ============ REVIEW URLS ============
    path('reviews/stats/', views.review_stats, name='review_stats'),
    path('reviews/list/', views.reviews_list, name='reviews_list'),
    path('reviews/submit/', views.submit_review, name='submit_review'),
    path('reviews/<uuid:review_id>/helpful/', views.mark_helpful, name='mark_helpful'),
    
    # Admin dashboard
    path('admin/reviews/dashboard/', views.admin_review_dashboard, name='admin_review_dashboard'),    
]



