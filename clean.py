from flask import Flask
import os
from dotenv import load_dotenv
from flask_mail import Mail


load_dotenv()

app = Flask(__name__, template_folder="/templates")


# app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
# app.config['MAIL_SERVER'] = 'smtp.example.com'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USERNAME'] = os.getenv('EMAIL_DEFAULT_SENDER')
# app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASSWORD')

# mail = Mail(app)
