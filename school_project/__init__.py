from clean import app
from school_project.core.views import core
from school_project.error_pages.handlers import error_pages
from school_project.login import login_manager
from school_project.users.views import users
from school_project.student.views import student
from school_project.principal.views import principal
from school_project.teachers.views import teacher
from school_project.database import db, mail
from school_project.parents.views import parent
from config import Config
from school_project.test_email import test_email_bp

app.register_blueprint(core)
app.register_blueprint(error_pages)
app.register_blueprint(users)
app.register_blueprint(teacher)
app.register_blueprint(parent, url_prefix='/parent')
app.register_blueprint(principal)
app.register_blueprint(student)
app.register_blueprint(test_email_bp)


login_manager.init_app(app)
mail.init_app(app)
# db.init_app(app)
app.config.from_object(Config)

app.template_folder = 'school_project/templates'
app.static_folder = 'school_project/static'