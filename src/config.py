import os

basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_RECORD_QUERIES = False
    SQLALCHEMY_EXPIRE_ON_COMMIT = False

    MARSHMALLOW_STRICT = True
    MARSHMALLOW_DATEFORMAT = 'rfc'

    SECRET_KEY = 'test_key'
    SECURITY_LOGIN_SALT = 'test'
    SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'
    SECURITY_TRACKABLE = True
    SECURITY_PASSWORD_SALT = 'something_super_secret_change_in_production'
    WTF_CSRF_ENABLED = False
    SECURITY_LOGIN_URL = '/api/v1/login/'
    SECURITY_LOGOUT_URL = '/api/v1/logout/'
    SECURITY_REGISTER_URL = '/api/v1/register/'
    SECURITY_RESET_URL = '/api/v1/reset/'
    SECURITY_CONFIRM_URL = '/api/v1/confirm/'
    SECURITY_REGISTERABLE = True
    SECURITY_CONFIRMABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_POST_LOGIN_VIEW = '/admin/'
    SECURITY_TOKEN_AUTHENTICATION_HEADER = 'Authorization'
    MAX_AGE = 86400
    GOOGLE_APPLICATION_CREDENTIALS = ''

    @staticmethod
    def init_app(app):
        pass

    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:@localhost/posify'
    ELASTIC_SEARCH_URL = 'http://localhost:9200'


class TestConfig(BaseConfig):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')
    ELASTIC_SEARCH_URL = os.environ.get('ELASTIC_SEARCH_URL')


class ProdConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.environ.get('PROD_DATABASE_URI') or \
                              'sqlite:///{}'.format(os.path.join(basedir, 'why-is-prod-here.db'))


configs = {
    'dev': DevConfig,
    'testing': TestConfig,
    'prod': ProdConfig,
    'default': DevConfig
}
