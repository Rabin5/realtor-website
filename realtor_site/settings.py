import os
from pathlib import Path
from decouple import config, Csv
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-development-key-change-this')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', 
                      default='localhost,127.0.0.1,www.realtorrajaram.com,realtorrajaram.com',
                      cast=Csv())


# Add CSRF trusted origins for production
CSRF_TRUSTED_ORIGINS = [
    'https://realtorrajaram.com',
    'https://www.realtorrajaram.com',
]

# ================= SITE SETTINGS =================
SITE_NAME = config('SITE_NAME', default='Raja Ram Real Estate')
SITE_DOMAIN = config('SITE_DOMAIN', default='realtorrajaram.com')
SITE_ID = 1

# Meta tags for SEO
META_DESCRIPTION = 'Raja Ram - Professional Real Estate Agent specializing in Texas properties. Find your dream home with expert guidance.'
META_KEYWORDS = 'real estate, Texas properties, home buying, property sale, realtor, Raja Ram'
META_AUTHOR = 'Raja Ram'

# Contact information
CONTACT_EMAIL = config('CONTACT_EMAIL', default='contact@realtorrajaram.com')
CONTACT_PHONE = config('CONTACT_PHONE', default='+1 (832) 420-2131')
CONTACT_ADDRESS = config('CONTACT_ADDRESS', default='Austin, Texas')

# Social media
SOCIAL_MEDIA = {
    'facebook': config('FACEBOOK_URL', default='https://facebook.com/rajaramgautamrealtor'),
    'instagram': config('INSTAGRAM_URL', default='https://instagram.com/@realtor_rajaram'),
}

# ================= APPLICATION DEFINITION =================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'whitenoise.runserver_nostatic',
    
    # Your apps
    'listings',
    'formtools',
    'mortgage_calculator',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'realtor_site.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'listings.context_processors.admin_stats',
            ],
        },
    },
]

WSGI_APPLICATION = 'realtor_site.wsgi.application'

# ================= DATABASE CONFIGURATION =================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='realtorrajaram_db'),
        'USER': config('DB_USER', default='realtorrajaram_user'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}

# ================= PASSWORD VALIDATION =================

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ================= INTERNATIONALIZATION =================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Chicago'
USE_I18N = True
USE_TZ = True

# ================= STATIC & MEDIA FILES =================

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ================= API KEYS =================

MOCKAROO_API_URL = config('MOCKAROO_API_URL', 
                         default='https://api.mockaroo.com/api/2889f130?count=1000&key=7c109e60')
GOOGLE_MAPS_API_KEY = config('GOOGLE_MAPS_API_KEY', 
                            default='AIzaSyBSNRml4NWtm8UmG_Loe_QKDD5udQD82-0')

# ================= EMAIL CONFIGURATION =================

#EMAIL_BACKEND = config('EMAIL_BACKEND', 
#                      default='django.core.mail.backends.smtp.EmailBackend')
#EMAIL_HOST = config('EMAIL_HOST', default='email-smtp.us-east-1.amazonaws.com')
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.zoho.com'
#EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_PORT = 587
EMAIL_USE_TLS = True
#EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
#EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
#EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='') 
EMAIL_HOST_USER = '1-8324202131_602@zohomail.com'
EMAIL_HOST_PASSWORD = 'KnZ1AN9shzPR'
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER)
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# ================= SECURITY SETTINGS =================
if not DEBUG:
    # HTTPS/SSL Settings
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Cookie Security
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = True
    
    # Browser Security
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    
    # Referrer Policy
    SECURE_REFERRER_POLICY = 'same-origin'

# ================= LOGGING CONFIGURATION =================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# ================= FILE UPLOAD SETTINGS =================

DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
FILE_UPLOAD_PERMISSIONS = 0o644
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o755

# ================= APPLICATION SPECIFIC SETTINGS =================

PROPERTY_IMAGES_PER_PAGE = config('PROPERTY_IMAGES_PER_PAGE', default=12, cast=int)
FEATURED_PROPERTIES_COUNT = config('FEATURED_PROPERTIES_COUNT', default=6, cast=int)
