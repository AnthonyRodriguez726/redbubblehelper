from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from .main import site
from .api import api_bp
import logging


db = SQLAlchemy()

mail = Mail()

def create_app():
    app = Flask(__name__, template_folder='../templates')

    # Blueprints
    app.register_blueprint(site)
    app.register_blueprint(api_bp, url_prefix='/api')

    # Config Settings
    app.config.from_object('config.settings')

    # Extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    mail.init_app(app)

    # Logger Settings
    logging.basicConfig(level=logging.DEBUG, filename='/home/bellpep/RedbubbleHelper/logs/debug.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s')

    # Models
    from app import models

    return app