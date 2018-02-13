import logging

from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from config import Config


app = Flask(__name__)
app.config.from_object(Config)
# db = SQLAlchemy(app)
db = create_engine(Config.SQLALCHEMY_DATABASE_URI)
base = declarative_base()

# Import module using its blueprint
from app.mod_stats.controllers import mod_stats as statistics_module
# from app.mod_db_manage.db_update import mod_db_manage as db_manager_module

# Register blueprints
app.register_blueprint(statistics_module)

from app import routes