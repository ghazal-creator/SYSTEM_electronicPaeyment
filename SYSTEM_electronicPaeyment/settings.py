"""
Django settings for SYSTEM_electronicPaeyment project.
"""

from pathlib import Path
import os
import dj_database_url  # أهم مكتبة للنشر

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent  # ⬅️ تصحيح: file بدلاً من file

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-default-key-change-immediately')  # ⬅️ تصحيح

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# ⬇️ تصحيح ALLOWED_HOSTS - يجب تحديد النطاقات بدقة
ALLOWED_HOSTS = [
    'systemelectronicpaeyment-production.up.railway.app',
    '127.0.0.1',
    'localhost',
    '.railway.app'
]

# إعدادات الوسائط (Media files)
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'drf_spectacular', 
    'APPLI'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # مهم للملفات الثابتة
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'SYSTEM_electronicPaeyment.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # ⬅️ إضافة مجلد templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'SYSTEM_electronicPaeyment.wsgi.application'

# Database - الإعدادات الجديدة المبسطة
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
# Password validation
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

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [  # ⬅️ إضافة مهمة جداً
    os.path.join(BASE_DIR, 'static'),
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ⬇️ إعدادات أمان - يجب أن تكون خارج الشرط
SECURE_SSL_REDIRECT = not DEBUG  # ⬅️ تصحيح
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# ⬇️ CSRF_TRUSTED_ORIGINS يجب أن تكون دائماً محددة
CSRF_TRUSTED_ORIGINS = [
    'https://systemelectronicpaeyment-production.up.railway.app',
    'https://*.railway.app',
    'http://127.0.0.1:8000',
    'http://localhost:8000',
]

# ⬇️ إعدادات Whitenoise إضافية
WHITENOISE_USE_FINDERS = True
WHITENOISE_MANIFEST_STRICT = False
WHITENOISE_ALLOW_ALL_ORIGINS = True



# ⬇️ إعدادات Logging للتحقق من الأخطاء
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}

# إعدادات REST Framework
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# إعدادات Swagger
SPECTACULAR_SETTINGS = {
    'TITLE': 'نظام الدفع الإلكتروني API',
    'DESCRIPTION': 'توثيق واجهة برمجة التطبيقات لنظام الدفع الإلكتروني',
    'VERSION': '1.0.0',
}