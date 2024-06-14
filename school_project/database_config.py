import os
from datetime import timedelta
from school_project import app 

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'school-project.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['USE_SESSION_FOR_NEXT'] = True
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(seconds=20)

if __name__ == '__main__':
    app.run()
