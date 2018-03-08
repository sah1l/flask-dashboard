from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config


# app init
app = Flask(__name__)
app.config.from_object(Config)

# database init
db = SQLAlchemy(app)


def session_add(obj):
    """
    Custom function for adding data obj to database
    :param data: data obj needed to save to database
    """
    db.session.add(obj)


def session_commit():
    """
    Custom commit to database
    """
    db.session.commit()


def session_delete(obj):
    """
    Custom delete from database function
    :param obj: data object to delete
    """
    db.session.delete(obj)


# migrate init
migrate = Migrate(app, db)

# login init
login = LoginManager(app)
login.login_view = 'auth.login'

# Import module using its blueprint
from app.mod_stats.controllers import mod_stats as statistics_module
from app.mod_auth.controllers import mod_auth as auth_module
from app.mod_admin.controllers import mod_admin as admin_module

# Register blueprints
app.register_blueprint(statistics_module)
app.register_blueprint(auth_module)
app.register_blueprint(admin_module)

from app import routes
