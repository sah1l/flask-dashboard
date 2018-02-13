from flask import Flask
from flask_login import LoginManager
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import Config


app = Flask(__name__)
app.config.from_object(Config)
db = create_engine(Config.SQLALCHEMY_DATABASE_URI)
base = declarative_base()
login = LoginManager(app)
session_maker = sessionmaker(db)

# Import module using its blueprint
from app.mod_stats.controllers import mod_stats as statistics_module
from app.mod_auth.controllers import mod_auth as auth_module

# Register blueprints
app.register_blueprint(statistics_module)
app.register_blueprint(auth_module)

from app import routes