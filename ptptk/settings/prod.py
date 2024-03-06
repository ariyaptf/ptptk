from .base import *  # noqa

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "w#db!o07l%v8sg5m8p7-o8x#6@t0xe5$qmw+z5k%jo&9=px2qs"

# Add your site's domain name(s) here.
ALLOWED_HOSTS = ["www.ptptk.org"]

# To send email from the server, we recommend django_sendmail_backend
# Or specify your own email backend such as an SMTP server.
# https://docs.djangoproject.com/en/5.0/ref/settings/#email-backend
# EMAIL_BACKEND = "django_sendmail_backend.backends.EmailBackend"

# Default email address used to send messages from the website.
DEFAULT_FROM_EMAIL = "PTF <info@ptptk.org>"

# A list of people who get error notifications.
ADMINS = [
    ("Administrator", "admin@ptptk.org"),
]

# A list in the same format as ADMINS that specifies who should get broken link
# (404) notifications when BrokenLinkEmailsMiddleware is enabled.
MANAGERS = ADMINS

# Email address used to send error messages to ADMINS.
SERVER_EMAIL = DEFAULT_FROM_EMAIL

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": BASE_DIR / "cache",  # noqa
        "KEY_PREFIX": "coderedcms",
        "TIMEOUT": 14400,  # in seconds
    }
}
