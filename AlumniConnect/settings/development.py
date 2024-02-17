from AlumniConnect.settings.common import *

SECRET_KEY = "dikj)qxgkhe7v$y7l))d!!nkut&^6q7+x^@ys7c1z!#!&*94r5"

DEBUG = True

# ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
ALLOWED_HOSTS = ['*']


# EMAIL SETTINGS
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_FROM = 'pvpitconnect@gmail.com'
EMAIL_HOST_USER = 'pvpitconnect@gmail.com'
EMAIL_HOST_PASSWORD = 'dcnabpuieczdjnfl'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

DEFAULT_FROM_EMAIL = "pvpitconnect@gmail.com"
BCC_EMAILS = ["bpvpitconnect@gmail.com", "pvpitconnect@gmail.com"]

if DEBUG:
    STATICFILES_DIRS = (os.path.join(BASE_DIR, '..', 'static/'),)

    MIDDLEWARE += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )
    INSTALLED_APPS += (
        'debug_toolbar',
    )
    INTERNAL_IPS = ('127.0.0.1',)
