from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
from clean import app as application
from school_project.database_config import app



db = SQLAlchemy(app)
migrate = Migrate(app, db)

mail = Mail(application)
bcrypt = Bcrypt(application)
csrf = CSRFProtect(application)
login_manager = LoginManager(application)
