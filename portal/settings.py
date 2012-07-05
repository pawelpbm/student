from django_auth_ldap.config import LDAPSearch
import ldap

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

LDAP_SUFFIX = "dc=icis,dc=pcz,dc=pl"

AUTH_LDAP_SERVER_URI = 'ldap://127.0.0.1/'
AUTH_LDAP_BIND_DN = ""
AUTH_LDAP_BIND_PASSWORD = ""
AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=users," + LDAP_SUFFIX, ldap.SCOPE_SUBTREE, "(uid=%(user)s)")

LDAPDB_BIND_DN='cn=admin,' + LDAP_SUFFIX
LDAPDB_BIND_PASSWORD='' #Insert password here

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/var/student/sqlite.db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    },
    'ldap': {
        'ENGINE': 'ldapdb.backends.ldap',
        'NAME': AUTH_LDAP_SERVER_URI,
        'USER': 'cn=admin,' + LDAP_SUFFIX,
        'PASSWORD': '', #Insert password here
        'HOST': '',
        'PORT': '',
    }
}

DATABASE_ROUTERS = ['ldapdb.router.Router']

LOGIN_URL="/"

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'student.icis.pcz.pl@gmail.com'
EMAIL_HOST_PASSWORD = '' #Insert password here
EMAIL_PORT = 587

INITIAL_UID = 20000

#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

TIME_ZONE = 'America/Chicago'

LANGUAGE_CODE = 'pl'

SITE_ID = 1

USE_I18N = True

USE_L10N = True

MEDIA_ROOT = '/var/student/student/management/static/'

MEDIA_URL = ''

STATIC_ROOT = '/var/student/student/management/static/'

STATIC_URL = '/static/'

ADMIN_MEDIA_PREFIX = '/static/admin/'

STATICFILES_DIRS = (
    '/var/student/student/management/static/',
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

SECRET_KEY = 's#xb!owz0%=fpk^v9w9gi^ab6*_dr=r7#vth2v%^n3-grrvib@'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware'
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'django_auth_ldap.backend.LDAPBackend',
)

ROOT_URLCONF = 'student.urls'

TEMPLATE_DIRS = (
    '/var/student/student/management/templates/',
)

SESSION_ENGINE  = 'django.contrib.sessions.backends.file'


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'management',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
