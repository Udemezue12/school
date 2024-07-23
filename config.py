from clean import app
import os
from dotenv import load_dotenv
from flask_mail import Mail
from itsdangerous import URLSafeTimedSerializer 
import secrets
import smtplib , ssl


load_dotenv()
mine = os.getenv('SALT')
salt = mine


# salt = secrets.token_hex(16)



# mail = Mail(app)


import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    MAIL_SERVER = 'smtp.gmail.com'
    # MAIL_USE_SSL = smtplib.SMTP_SSL("smtp.gmail.com",465)
    MAIL_USE_SSL =True
    MAIL_USE_TLS= False
    MAIL_PORT = 465
    MAIL_USERNAME = os.getenv('EMAIL_USERNAME')  
    MAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    SALT = os.getenv('SALT')
    SERVER_URL = 'http://127.0.0.1:3000' if os.getenv('FLASK_ENV') == 'development' else 'https://school-portal-dsyf.onrender.com'
    PAYSTACK_PUBLIC_KEY = os.getenv('PAYSTACK_PUBLIC_KEY')
    PAYSTACK_SECRET_KEY = os.getenv('PAYSTACK_SECRET_KEY')
    TERMII_API_KEY = os.getenv('TERMII_API_KEY')
    TERMII_MAIL_URL = os.getenv('TERMII_MAIL_URL')
  
    

app.config.from_object(Config)
mail = Mail(app)

with app.app_context():
    pass

serializer = URLSafeTimedSerializer(os.getenv('SECRET_KEY'), os.getenv('SALT'))