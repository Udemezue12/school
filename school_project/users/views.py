import random
import os
import string
from flask_mail import Message
from werkzeug.security import generate_password_hash

from dotenv import load_dotenv
from flask import render_template, url_for, flash, redirect, request, Blueprint, current_app

from sqlalchemy.exc import IntegrityError
from flask_login import login_user, current_user, logout_user, login_required
# from db import db, bcrypt, mail as mailer
from school_project.models import User
from school_project.users.forms import RegistrationForm, LoginForm, UpdateForm, ForgotPasswordForm, ResetPasswordForm
from school_project.utils import save_picture
from school_project.models import Teacher, Student, UserPin

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

from school_project.database import bcrypt, db, mail as mailer


load_dotenv()


senders_mail = os.getenv('MAIL_HOST_USER')


users = Blueprint('users', __name__)


def generate_pin():
    pin = ''.join(random.choices(string.digits, k=6))
    new_pin = UserPin(pin_code=pin)
    db.session.add(new_pin)
    db.session.commit()
    return pin


@users.route('/register', methods=['GET', 'POST'])
def register():
    return render_template('register.html')


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('users.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('core.index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('core.index'))


@users.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'principal':
        return render_template('principal_dashboard.html')
    elif current_user.role == 'teacher':
        return render_template('teacher_dashboard.html')
    elif current_user.role == 'student':
        return render_template('student_dashboard.html')
    elif current_user.role == 'parent':
        return render_template('parent_dashboard.html')
    else:
        return render_template('index.html')


@users.route('/updating_profile', methods=['GET', 'POST'])
@login_required
def profile():
    if current_user.role == 'principal':
        return render_template('principal_update_profile.html')
    elif current_user.role == 'teacher':
        return render_template('teacher_update_profile.html')
    elif current_user.role == 'student':
        return render_template('student_update_profile.html')
    elif current_user.role == 'parent':
        return render_template('parent_update_profile.html')
    else:
        return render_template('index.html')


@users.route("/update_profile", methods=['GET', 'POST'])
@login_required
def update_profile():
    form = UpdateForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.student.profile = form.profile.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.update_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.profile.data = current_user.student.profile
    return render_template('update_profile.html', title='Update Profile', form=form)


# /////////////////////////


# ////////////////////////////////////////


@users.route('/forgot/password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('users.dashboard'))

    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_reset_email(user, token)
            flash(
                'An email has been sent with instructions to reset your password.', 'info')
            return redirect(url_for('users.login'))
        else:
            flash('No account found with that email.', 'danger')
    return render_template('forgot_password.html', title='Forgot Password', form=form)


def send_reset_email(user, token):
    msg = Message('Password Reset Request',
                  sender=current_app.config['MAIL_DEFAULT_SENDER'], recipients=[user.email])

    msg.body = f'''To reset your password, visit the following link:
{url_for('users.reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    try:
        mailer.send(msg)
    except Exception as e:
        flash('Failed to send the reset email. Please try again later.', 'danger')
        print(f"Error sending email: {e}")


@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('users.dashboard'))

    user = User.verify_reset_token(token)
    if user is None:
        flash('The reset link is invalid or has expired.', 'warning')
        return redirect(url_for('users.forgot_password'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.password = generate_password_hash(
            form.password.data).decode('utf-8')
        user.reset_token = None
        user.reset_token_expiration = None
        db.session.commit()
        flash('Your password has been updated!', 'success')
        return redirect(url_for('users.login'))

    return render_template('reset_password.html', title='Reset Password', form=form)
