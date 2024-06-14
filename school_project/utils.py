import requests
from functools import wraps
import string
import random
import os
from flask import abort
from flask_login import current_user
from dotenv import load_dotenv
import secrets
from PIL import Image
from flask import current_app
from werkzeug.utils import secure_filename


load_dotenv()

RANDOM_ORG_API_KEY = os.getenv('RANDOM_ORG_API_KEY')


def admin_required(f):
    @wraps(f)
    def decorated_fuction(*args, **kwargs):
        if current_user != 'admin':
            abort(403)
            return f(*args, **kwargs)
        return decorated_fuction


def teacher_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user != 'teacher':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user != 'student':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def principal_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user != 'principal':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def generated_pin():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


def generate_pin():
    url = 'https://api.random.org/json-rpc/4/invoke'
    headers = {
        'Content-Type': 'application/json'
    }
    payload = {
        "jsonrpc": "2.0",
        "method": "generateIntegers",
        "params": {
            "apiKey": RANDOM_ORG_API_KEY,
            "n": 1,
            "min": 100000,
            "max": 999999,
            "replacement": True
        },
        "id": 42
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        result = response.json()
        return str(result['result']['random']['data'][0])
    else:
        raise Exception('Error generating PIN')


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(
        current_app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


def save_file(file):

    upload_folder = os.path.join(current_app.root_path, 'uploads')

    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    # Secure the file name and save the file
    filename = secure_filename(file.filename)
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)

    return file_path
