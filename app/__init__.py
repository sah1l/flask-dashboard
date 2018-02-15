from flask import Flask
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import Config


# app init
app = Flask(__name__)
app.config.from_object(Config)

# database init
db = create_engine(Config.SQLALCHEMY_DATABASE_URI)
session_maker = sessionmaker(db)
base = declarative_base()

# login init
login = LoginManager(app)
login.login_view = 'auth.login'

# admin init
from app.mod_auth.models import User

admin = Admin(app, template_mode='bootstrap3')
session = session_maker()
admin.add_view(ModelView(User, session))

# Import module using its blueprint
from app.mod_stats.controllers import mod_stats as statistics_module
from app.mod_auth.controllers import mod_auth as auth_module

# Register blueprints
app.register_blueprint(statistics_module)
app.register_blueprint(auth_module)

from app import routes
