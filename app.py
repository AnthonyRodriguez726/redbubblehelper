from flask import Flask, render_template, request, jsonify, send_file
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from db_config import db
from models import User, Subscription
from forms import RegistrationForm, LoginForm
from werkzeug.utils import secure_filename
import logging
import requests
import os
import api  # Import API routes from api.py

google_app_pass = os.environ.get('GOOGLE_APP_PASSWORD')
database_pass = os.environ.get('POSTGRES_PASS')
database_name = os.environ.get('DB_NAME')
database_user = os.environ.get('DB_USER')
database_host = os.environ.get('DB_HOST')

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{database_user}:{database_pass}@{database_host}/{database_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'userUploads/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

db.init_app(app)
migrate = Migrate(app, db)

logging.basicConfig(level=logging.DEBUG, filename='debug.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s')

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'anthonyrodriguez726@gmail.com'
app.config['MAIL_PASSWORD'] = google_app_pass
app.config['MAIL_DEFAULT_SENDER'] = 'signup@redbubblehelper.com'

mail = Mail(app)

@app.route('/')
def home():
    return render_template('underconstruction.html')

@app.route('/notify-signup', methods=['POST'])
def notify_signup():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({'error': 'Email is required.'}), 400

    msg = Message('New Signup Notification',
                  recipients=['anthonyrodriguez726@gmail.com'])
    msg.body = f'{email} has signed up!'
    mail.send(msg)

    return jsonify({'message': 'Notification sent successfully.'}), 200

# Include API routes from api.py
api.register_api_routes(app)

if __name__ == '__main__':
    app.run(debug=True)