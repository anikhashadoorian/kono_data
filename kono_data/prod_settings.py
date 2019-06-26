import os
import logging.config
import bugsnag

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ['DB_NAME'],
        'USER': os.environ['DB_USER'],
        'PASSWORD': os.environ['DB_PASSWORD'],
        'HOST': os.environ['DB_HOST'],
        'PORT': os.environ['DB_PORT'],
    }
}
AWS_STORAGE_BUCKET_NAME = 'konodata-prod'
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
STATIC_URL = "https://%s/" % AWS_S3_CUSTOM_DOMAIN
STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
DEBUG = False
SECRET_KEY = os.environ['SECRET_KEY']
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'


BUGSNAG_API_KEY = os.environ.get('BUGSNAG_API_KEY')
if BUGSNAG_API_KEY:
    bugsnag.configure(auto_capture_sessions=True)
    LOGGING_CONFIG = None
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'console': {
                'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'console',
            },
            # Add Handler for bugsnag for `warning` and above
            'bugsnag': {
                'level': 'WARNING',
                'class': 'bugsnag.handlers.BugsnagHandler',
            },
        },
        'loggers': {
            '': {
                'level': 'WARNING',
                'handlers': ['console', 'bugsnag'],
            },
        },
    })
