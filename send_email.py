from flask import Flask, request, redirect
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

@app.route('/send_email', methods=['POST'])
def send_email():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    # Create the email content
    email_body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"

    # Create a text/plain message
    msg = MIMEText(email_body)
    msg['Subject'] = f"New contact form submission from {name}"
    msg['From'] = email  # Sender's email
    msg['To'] = 'anthonyrodriguez726@gmail.com'  # Receiver's email

    # Send the message via an SMTP server
    try:
        s = smtplib.SMTP('localhost')  # Use 'localhost' if you have an SMTP server running on your local machine
        s.send_message(msg)
        s.quit()
        return redirect('/thank-you')  # Redirect to a thank-you page
    except Exception as e:
        print(f"An error occurred: {e}")
        return "Failed to send email", 500

if __name__ == '__main__':
    app.run(debug=True)
