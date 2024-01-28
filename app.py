from flask import Flask, render_template, request, jsonify
from flask_mail import Mail, Message
import logging
import requests
import os
import api  # Import API routes from api.py

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG, filename='debug.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s')

google_app_pass = os.environ.get('GOOGLE_APP_PASSWORD')

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