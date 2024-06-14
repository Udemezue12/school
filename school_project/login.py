
from flask_login import LoginManager


login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.refresh_view = 'users.login'
login_manager.needs_refresh_message = 'You need to need to Login again'



