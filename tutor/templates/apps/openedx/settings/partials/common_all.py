####### Settings common to LMS and CMS
import json
import os

DEFAULT_FROM_EMAIL = ENV_TOKENS["CONTACT_EMAIL"]
DEFAULT_FEEDBACK_EMAIL = ENV_TOKENS["CONTACT_EMAIL"]
SERVER_EMAIL = ENV_TOKENS["CONTACT_EMAIL"]
TECH_SUPPORT_EMAIL = ENV_TOKENS["CONTACT_EMAIL"]
CONTACT_EMAIL = ENV_TOKENS["CONTACT_EMAIL"]
BUGS_EMAIL = ENV_TOKENS["CONTACT_EMAIL"]
UNIVERSITY_EMAIL = ENV_TOKENS["CONTACT_EMAIL"]
PRESS_EMAIL = ENV_TOKENS["CONTACT_EMAIL"]
PAYMENT_SUPPORT_EMAIL = ENV_TOKENS["CONTACT_EMAIL"]
BULK_EMAIL_DEFAULT_FROM_EMAIL = "no-reply@" + ENV_TOKENS["LMS_BASE"]
API_ACCESS_MANAGER_EMAIL = ENV_TOKENS["CONTACT_EMAIL"]
API_ACCESS_FROM_EMAIL = ENV_TOKENS["CONTACT_EMAIL"]

# Load module store settings from config files
update_module_store_settings(MODULESTORE, doc_store_settings=DOC_STORE_CONFIG)
DATA_DIR = "/openedx/data/"
for store in MODULESTORE["default"]["OPTIONS"]["stores"]:
   store["OPTIONS"]["fs_root"] = DATA_DIR

# Get rid completely of coursewarehistoryextended, as we do not use the CSMH database
INSTALLED_APPS.remove("coursewarehistoryextended")
DATABASE_ROUTERS.remove(
    "openedx.core.lib.django_courseware_routers.StudentModuleHistoryExtendedRouter"
)

# Set uploaded media file path
MEDIA_ROOT = "/openedx/media/"

# Video settings
VIDEO_IMAGE_SETTINGS["STORAGE_KWARGS"]["location"] = MEDIA_ROOT
VIDEO_TRANSCRIPTS_SETTINGS["STORAGE_KWARGS"]["location"] = MEDIA_ROOT

GRADES_DOWNLOAD = {
    "STORAGE_TYPE": "",
    "STORAGE_KWARGS": {
        "base_url": "/media/grades/",
        "location": "/openedx/media/grades",
    },
}

ORA2_FILEUPLOAD_BACKEND = "filesystem"
ORA2_FILEUPLOAD_ROOT = "/openedx/data/ora2"
ORA2_FILEUPLOAD_CACHE_NAME = "ora2-storage"

# Change syslog-based loggers which don't work inside docker containers
LOGGING["handlers"]["local"] = {
    "class": "logging.handlers.WatchedFileHandler",
    "filename": os.path.join(LOG_DIR, "all.log"),
    "formatter": "standard",
}
LOGGING["handlers"]["tracking"] = {
    "level": "DEBUG",
    "class": "logging.handlers.WatchedFileHandler",
    "filename": os.path.join(LOG_DIR, "tracking.log"),
    "formatter": "standard",
}
LOGGING["loggers"]["tracking"]["handlers"] = ["console", "local", "tracking"]
# Disable django/drf deprecation warnings
import logging
import warnings
from django.utils.deprecation import RemovedInDjango30Warning, RemovedInDjango31Warning
from rest_framework import RemovedInDRF310Warning, RemovedInDRF311Warning
warnings.simplefilter('ignore', RemovedInDjango30Warning)
warnings.simplefilter('ignore', RemovedInDjango31Warning)
warnings.simplefilter('ignore', RemovedInDRF310Warning)
warnings.simplefilter('ignore', RemovedInDRF311Warning)

# Email
EMAIL_USE_SSL = {{ SMTP_USE_SSL }}
# Forward all emails from edX's Automated Communication Engine (ACE) to django.
ACE_ENABLED_CHANNELS = ["django_email"]
ACE_CHANNEL_DEFAULT_EMAIL = "django_email"
ACE_CHANNEL_TRANSACTIONAL_EMAIL = "django_email"
EMAIL_FILE_PATH = "/tmp/openedx/emails"

LOCALE_PATHS.append("/openedx/locale/contrib/locale")
LOCALE_PATHS.append("/openedx/locale/user/locale")

# Allow the platform to include itself in an iframe
X_FRAME_OPTIONS = "SAMEORIGIN"

{% set jwt_rsa_key = rsa_import_key(JWT_RSA_PRIVATE_KEY) %}
JWT_AUTH["JWT_ISSUER"] = "{{ JWT_COMMON_ISSUER }}"
JWT_AUTH["JWT_AUDIENCE"] = "{{ JWT_COMMON_AUDIENCE }}"
JWT_AUTH["JWT_SECRET_KEY"] = "{{ JWT_COMMON_SECRET_KEY }}"
JWT_AUTH["JWT_PRIVATE_SIGNING_JWK"] = json.dumps(
    {
        "kid": "openedx",
        "kty": "RSA",
        "e": "{{ jwt_rsa_key.e|long_to_base64 }}",
        "d": "{{ jwt_rsa_key.d|long_to_base64 }}",
        "n": "{{ jwt_rsa_key.n|long_to_base64 }}",
        "p": "{{ jwt_rsa_key.p|long_to_base64 }}",
        "q": "{{ jwt_rsa_key.q|long_to_base64 }}",
    }
)
JWT_AUTH["JWT_PUBLIC_SIGNING_JWK_SET"] = json.dumps(
    {
        "keys": [
            {
                "kid": "openedx",
                "kty": "RSA",
                "e": "{{ jwt_rsa_key.e|long_to_base64 }}",
                "n": "{{ jwt_rsa_key.n|long_to_base64 }}",
            }
        ]
    }
)
JWT_AUTH["JWT_ISSUERS"] = [
    {
        "ISSUER": "{{ JWT_COMMON_ISSUER }}",
        "AUDIENCE": "{{ JWT_COMMON_AUDIENCE }}",
        "SECRET_KEY": "{{ OPENEDX_SECRET_KEY }}"
    }
]

AWS_S3_HOST = "{{ S3_HOST }}"
AWS_S3_PORT = {{ S3_PORT }}
AWS_S3_USE_SSL = {{ "True" if S3_USE_SSL else "False" }}
AWS_S3_SECURE_URLS = {{ "True" if S3_USE_SSL else "False" }}
AWS_S3_CALLING_FORMAT = "boto.s3.connection.OrdinaryCallingFormat"
AWS_AUTO_CREATE_BUCKET = {{ "True" if S3_AUTO_CREATE_BUCKET else "False" }}

# Configuring boto is required for ora2 because ora2 does not read
# host/port/ssl settings from django. Hence this hack.
# http://docs.pythonboto.org/en/latest/boto_config_tut.html
import os
os.environ["AWS_CREDENTIAL_FILE"] = "/tmp/boto.cfg"
with open("/tmp/boto.cfg", "w") as f:
    f.write("""[Boto]
is_secure = {{ "True" if S3_USE_SSL else "False" }}
[s3]
host = {{ S3_HOST }}:{{ S3_PORT }}
calling_format = boto.s3.connection.OrdinaryCallingFormat""")

{{ patch("openedx-common-settings") }}
######## End of settings common to LMS and CMS
