from flask import Blueprint, request, jsonify, render_template, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
from flask_mail import Message
from flask import current_app as app
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from .services.data_retrieval import generate_design
import os



site = Blueprint('site', __name__)


# PAGES
@site.route('/')
def home():
    return render_template('underconstruction.html')

@site.route('/hometest')
def hometest():
    return render_template('home.html')

@site.route('/about')
def about():
    return render_template('about.html')

@site.route('/features')
def features():
    return render_template('features.html')

@site.route('/contact')
def contact():
    return render_template('contact.html')

@site.route('/faqs')
def faqs():
    return render_template('faqs.html')   

# BACKEND PROCESSES
@site.route('/notify-signup', methods=['POST'])
def notify_signup():
    from . import mail
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({'error': 'Email is required.'}), 400

    msg = Message('New Signup Notification',
                  recipients=['anthonyrodriguez726@gmail.com'])
    msg.body = f'{email} has signed up!'
    mail.send(msg)

    return jsonify({'message': 'Notification sent successfully.'}), 200

@site.route('/generate_design', methods=['POST'])
def bing_generate_design():
        data = request.get_json()
        prompt = data.get('prompt')

        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400

        # Directly use the original prompt for design generation
        image_links = generate_design(prompt)
        if image_links:
            return jsonify({"images": image_links})
        else:
            return jsonify({"error": "Failed to generate images"}), 500

@site.route('/bgremover', methods=['GET', 'POST'])
def bgremover():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'image' not in request.files:
            return 'No file part', 400
        file = request.files['image']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            return 'No selected file', 400
        if file and search_info.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            processed_filepath = search_info.process_image(filepath)
            return send_file(processed_filepath, as_attachment=True)
    return render_template('bgremover.html')

@site.route('/send_email', methods=['POST'])
def send_email():
    # Retrieve form data
    name = request.form.get('name')
    email = request.form.get('email')
    message_content = request.form.get('message')

    # Create the email content
    message = Mail(
        from_email='anthonyrodriguez726@gmail.com',  # The email you verified with SendGrid
        to_emails='anthonyrodriguez726@gmail.com',  # The destination email address
        subject=f'New contact form submission from {name}',
        html_content=f'<strong>Name:</strong> {name}<br>'
                     f'<strong>Email:</strong> {email}<br><br>'
                     f'<strong>Message:</strong><br>{message_content}'
    )

    # Send the message via SendGrid
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        return jsonify(success=True), 200
    except Exception as e:
        print(e.message)
        return jsonify(success=False, error=str(e)), 500

if __name__ == "__main__":
    app.run(debug=True)