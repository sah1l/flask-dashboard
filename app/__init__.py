from flask import Flask
from flask_login import LoginManager
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

# Import module using its blueprint
from app.mod_stats.controllers import mod_stats as statistics_module
from app.mod_auth.controllers import mod_auth as auth_module
from app.mod_admin.controllers import mod_admin as admin_module

# Register blueprints
app.register_blueprint(statistics_module)
app.register_blueprint(auth_module)
app.register_blueprint(admin_module)

from app import routes
