import os

#application directory
BASEDIR = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DB_CONFIG = {
        'host': 'localhost',
        'port': '5432',
        'database': 'postgres',
        'user': 'postgres',
        'password': 'p05tgre5',
    }

    # class Config(object):
    SQLALCHEMY_DATABASE_URI = "postgresql://%(user)s:%(password)s@%(host)s:%(port)s/%(database)s" % DB_CONFIG
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Enable protection agains *Cross-site Request Forgery (CSRF)*
    CSRF_ENABLED = True

    #secret key for signing the data. 
    CSRF_SESSION_KEY = "secret"

    # Secret key for signing cookies
    SECRET_KEY = "secret"