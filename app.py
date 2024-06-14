
from flask import render_template
from flask import Flask, render_template
from school_project import app

# app = Flask(__name__)

# @app.route('/')
# def index():
#     return render_template('/templates/core/index.html')
if __name__ == "__main__":
    app.run(debug=True, port=2000)
