from flask import Flask, request, jsonify, flash, redirect, url_for, render_template, send_file
from flask_mail import Mail, Message
from flask_login import login_user
from models import User, db
from forms import RegistrationForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from BingImageCreator import ImageGen
from email.mime.text import MIMEText
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import search_info
import smtplib
import logging
import pytz
import os


logging.basicConfig(level=logging.DEBUG, filename='debug.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s')

def register_api_routes(app):
    @app.route('/generate_design', methods=['POST'])
    def generate_design():
        data = request.get_json()
        prompt = data.get('prompt')
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        design_url = search_info.generate_design(prompt)
        if design_url:
            return jsonify({"design_url": design_url})
        else:
            return jsonify({"error": "Failed to generate design"}), 500


    @app.route('/search', methods=['GET'])
    def search():
        cst_timezone = pytz.timezone('America/Chicago')  # CST timezone
        current_time_cst = datetime.now(cst_timezone).strftime('%Y-%m-%d %I:%M:%S %p')

        query = request.args.get('query')
        if not query:
            return jsonify({"error": "No query provided"}), 400

        logging.debug(f"Searching Redbubble for {query} - {current_time_cst}")
        try:
            # Use the scraper to get the results
            results = search_info.search_redbubble(query)
            return jsonify({"results": results})
        except Exception as e:
            return jsonify({"error": str(e)}), 500


    @app.route('/multi_search', methods=['POST'])
    def multi_search():
        cst_timezone = pytz.timezone('America/Chicago')  # CST timezone
        current_time_cst = datetime.now(cst_timezone).strftime('%Y-%m-%d %I:%M:%S %p')
        data = request.get_json()
        if not data or 'searches' not in data:
            return jsonify({"error": "No searches provided"}), 400

        logging.debug(f"Starting Redbubble Multi Search at {current_time_cst}")
        results = {}
        for search in data['searches']:
            query = search.get('query')
            media_type = search.get('media_type', 'unknown')  # Default to 'unknown' if not provided
            if query:
                try:
                    # Use the scraper to get results and URL for each query
                    search_result, search_url = search_info.search_redbubble(query)
                    results[query] = {
                        'result': search_result,
                        'url': search_url,
                        'media_type': media_type  # Include the media type in the response
                    }
                except Exception as e:
                    results[query] = {"error": f"An error occurred: {str(e)}"}
            else:
                results[query] = {"error": "Missing query"}

        return jsonify(results)


    @app.route('/toptv', methods=['GET'])
    def top_tv_shows():

        try:
            # Use the scraper to get the results
            results = search_info.find_top_tv_shows()
            return jsonify({"results": results})
        except Exception as e:
            return jsonify({"error": str(e)}), 500


    @app.route('/topmedia', methods=['GET'])
    def top_media():

        try:
            # Use the scraper to get the results
            results = search_info.find_top_media()
            return jsonify({"results": results})
        except Exception as e:
            return jsonify({"error": str(e)}), 500


    @app.route('/generate_design', methods=['POST'])
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


    @app.route('/hometest')
    def hometest():
        return render_template('home.html')

    @app.route('/about')
    def about():
        return render_template('about.html')

    @app.route('/features')
    def features():
        return render_template('features.html')

    @app.route('/contact')
    def contact():
        return render_template('contact.html')

    @app.route('/faqs')
    def faqs():
        return render_template('faqs.html')   

    @app.route('/underconstruction')
    def underconstruction():
        return render_template('underconstruction.html')

    @app.route('/bgremover', methods=['GET', 'POST'])
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


    @app.route('/send_email', methods=['POST'])
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
            return jsonify(success=True), 200  # Return success response
        except Exception as e:
            print(e.message)
            return jsonify(success=False, error=str(e)), 500  # Return error response
