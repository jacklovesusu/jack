import os
from pytz import timezone

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    TIMEZONE = timezone('Asia/Shanghai')
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    VERSION = '0.2.0'

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    EOS_ADDR = os.getenv('PLOTTER_DEV_EOS_ADDR', 'http://111.6.78.225:53255')
    REDIS_ADDR = os.getenv('PLOTTER_DEV_REDIS', 'redis://localhost:6379/0')
    MONGO_URI = os.getenv('PLOTTER_DEV_MONGO_URI', 'mongodb://localhost:27017')
    CELERY_RESULT_BACKEND = os.getenv('PLOTTER_DEV_CELERY_RESULT_BACKEND',
                                      'redis://localhost:6379/2')

class TestingConfig(Config):
    TESTING = True
    #WTF_CSRF_ENABLED = False
    EOS_ADDR = os.getenv('PLOTTER_TEST_EOS_ADDR', 'http://111.6.78.225:53255')
    REDIS_ADDR = os.getenv('PLOTTER_TEST_REDIS', 'redis://localhost:6379/0')
    MONGO_URI = os.getenv('PLOTTER_TEST_MONGO_URI', 'mongodb://localhost:27017')
    CELERY_RESULT_BACKEND = os.getenv('PLOTTER_TEST_CELERY_RESULT_BACKEND',
                                      'redis://localhost:6379/2')

class ProductionConfig(Config):
    EOS_ADDR = os.getenv('PLOTTER_PROD_EOS_ADDR')
    REDIS_ADDR = os.getenv('PLOTTER_REDIS', 'redis://localhost:6379/0')
    MONGO_URI = os.getenv('PLOTTER_MONGO_URI', 'mongodb://localhost:27017')
    CELERY_RESULT_BACKEND = os.getenv('PLOTTER_CELERY_RESULT_BACKEND')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig,
}
