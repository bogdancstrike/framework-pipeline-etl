# region Database configuration
# MySQL
import ast
from datetime import timedelta
from os import environ, path

from dotenv import load_dotenv

from framework.auth.keys import load_private_key, load_public_key
from framework.commons.logger import logger

basedir = path.abspath(path.dirname(__file__))
load_dotenv(dotenv_path=path.join(basedir, '.env'))


class Config:
    DB_HOST = environ.get('DB_HOST')
    DB_PORT = environ.get('DB_PORT')
    DB_NAME = environ.get('DB_NAME')
    DB_USER = environ.get('DB_USER')
    DB_PASSWORD = environ.get('DB_PASSWORD')
    DB_TABLE_NAME = environ.get('DB_TABLE_NAME')

    # region worker
    WORKER_NAME = 'worker_1'
    # endregion

    """Set Flask configuration from .env file."""

    CERTIFICATE_APP = environ.get('CERTIFICATE_APP')
    KEY_APP = environ.get('KEY_APP')

    # GENERIC - IAM
    IAM_SERVER_URL = environ.get('IAM_SERVER_URL')

    # GENERIC - FLASK
    FLASK_APP = environ.get('FLASK_APP')
    FLASK_DEBUG = environ.get('FLASK_DEBUG')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # GENERIC - SWAGGER
    SWAGGER_UI_DOC_EXPANSION = 'list'
    SWAGGER_UI_OPERATION_ID = True
    SWAGGER_UI_REQUEST_DURATION = True

    # GENERIC - OPENAPI
    OPENAPI_SWAGGER_UI_PATH = '/swagger-ui'
    OPENAPI_URL_PREFIX = '/'
    OPENAPI_SWAGGER_UI_ENABLE_OAUTH = True

    # GENERIC - JWT AUTH
    SECRET_KEY = environ.get('SECRET_KEY')
    TOKEN_URL = environ.get('TOKEN_URL')
    AUTH_URL = environ.get('AUTH_URL')

    # GENERIC - SSL
    SSL_REDIRECT = True
    AUTHLIB_INSECURE_TRANSPORT = True
    AUTHLIB_RELAX_TOKEN_SCOPE = True

    # GENERIC - CORS
    CORS_ALLOWED_ORIGINS = ast.literal_eval(environ.get("CORS_ALLOWED_ORIGINS"))

    # GENERIC - LOGGER
    LOGGING_LEVEL = environ.get('LOGGING_LEVEL')
    logger.setLevel(LOGGING_LEVEL)

