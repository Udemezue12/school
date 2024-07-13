from clean import app
import os
from dotenv import load_dotenv
from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer 
import secrets


load_dotenv()
mine = os.getenv('SALT')
salt = mine


# salt = secrets.token_hex(16)

# app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
# app.config['MAIL_SERVER'] = 'smtp.example.com'
# app.config['MAIL_PORT'] = 587
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USERNAME'] = os.getenv('EMAIL_DEFAULT_SENDER')
# app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASSWORD')

# mail = Mail(app)


import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True  # Ensure this is set to True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.getenv('EMAIL_USERNAME')  # Your email address
    MAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')  # App password
    MAIL_DEFAULT_SENDER = os.getenv('EMAIL_USERNAME')  # Your email address
    SALT = os.getenv('SALT')
    # SERVER_URL = os.getenv('SERVER_URL')

    
    SERVER_URL = 'http://127.0.0.1:3000' if os.getenv('FLASK_ENV') == 'development' else 'https://school-portal-dsyf.onrender.com'
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
    PAYSTACK_PUBLIC_KEY = os.getenv('PAYSTACK_PUBLIC_KEY')
    PAYSTACK_SECRET_KEY = os.getenv('PAYSTACK_SECRET_KEY')
    # SECRET_KEY = os.getenv('SECRET_KEY') or 'your_secret_key'
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'school-project.db')
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
    # USE_SESSION_FOR_NEXT = True
    # REMEMBER_COOKIE_DURATION = timedelta(seconds=20)
    

app.config.from_object(Config)
mail = Mail(app)

with app.app_context():
    pass

serializer = URLSafeTimedSerializer(os.getenv('SECRET_KEY'), os.getenv('SALT'))