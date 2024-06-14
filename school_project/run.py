import os
from flask import Flask
from flask_mail import Mail
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect
from whitenoise import WhiteNoise
from config import Config
# from db import db
import school_project.database
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from clean import app

load_dotenv()
app.wsgi_app = WhiteNoise(app.wsgi_app, root='school_project/static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
if app.config['SECRET_KEY'] is None:
    raise ValueError("SECRET_KEY not found in environment variables")

app.config['MAIL_DEFAULT_SENDER'] = os.getenv('EMAIL_HOST_USER')
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS '] = True
app.config['MAIL_USERNAME'] = os.getenv('EMAIL_HOST_USER')
app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASSWORD')

csrf = CSRFProtect(app)
mail = Mail(app)

application = app

if __name__ == '__main__':
    app.run(debug=True, port=2000)
