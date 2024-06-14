web: waitress-serve  school_project.run:application

web: gunicorn school_project.wsgi:application --bind 0.0.0.0:$PORT
