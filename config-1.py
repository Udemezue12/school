import os
from datetime import timedelta
from dotenv import load_dotenv


load_dotenv()




# if __name__ == '__main__':
#     mapp.run()
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = 587
    MAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'false').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.getenv('EMAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    MAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
    STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'udemezue0009@gmail.com')
    PAYSTACK_PUBLIC_KEY = os.getenv('PAYSTACK_PUBLIC_KEY')
    PAYSTACK_SECRET_KEY = os.getenv('PAYSTACK_SECRET_KEY')
    # SECRET_KEY = os.getenv('SECRET_KEY') or 'your_secret_key'
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'school-project.db')
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
    # USE_SESSION_FOR_NEXT = True
    # REMEMBER_COOKIE_DURATION = timedelta(seconds=20)
    FORUM_TITLE = "School Portal Forum"
    FORUM_SUBTITLE = "A place for students, teachers, parents, and principals to communicate"
    FORUM_TOPICS_PER_PAGE = 20
    FORUM_POSTS_PER_PAGE = 10

    

    
