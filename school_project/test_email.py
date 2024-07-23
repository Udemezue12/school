from flask import Blueprint, current_app
import smtplib

# Create a blueprint for the test route
test_email_bp = Blueprint('test_email', __name__)

@test_email_bp.route('/test-email', methods=['GET'])
def test_email():
    smtp_server = "smtp.gmail.com"
    port = 465  # For SSL
    sender_email = current_app.config['MAIL_USERNAME']
    password = current_app.config['MAIL_PASSWORD']

    try:
        server = smtplib.SMTP_SSL(smtp_server, port)
        server.login(sender_email, password)
        server.quit()
        return "Login successful"
    except Exception as e:
        current_app.logger.error(f"Error: {str(e)}")
        return f"Error: {str(e)}"
