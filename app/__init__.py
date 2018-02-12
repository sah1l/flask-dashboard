import logging

from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from logging.handlers import RotatingFileHandler
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

# Set up logging
if not app.debug:
    file_handler = RotatingFileHandler('logs/app_info.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.DEBUG)
    app.logger.info('Microblog startup')

from app import routes