import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = '_l0XgqOF53bq-TvscAvN3OCWJGzsl2Badks7PIJz7R0'
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    # SQLALCHEMY_DATABASE_URI = "mysql://root:Passw0rd-123!@localhost:3306/webProject"


class ProductionConfig(Config):
    DEBUG = False


class StagingConfig(Config):
    DEBUG = True
    DEVELOPMENT = True


class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True

    def __repr__(self):
        return str("Database: {}".format(self.SQLALCHEMY_DATABASE_URI))


class TestingConfig(Config):
    TESTING = True
