class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "your_secret_key"


class TestingConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///testing.db'
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "test-secret"
    CACHE_TYPE = 'SimpleCache'