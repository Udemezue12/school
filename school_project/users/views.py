import random
import os
import string
from flask_mail import Message
import secrets
import requests
from werkzeug.security import generate_password_hash
from clean import app
from dotenv import load_dotenv
from flask import render_template, url_for, flash, redirect, request, Blueprint, current_app
import css_inline
from itsdangerous.exc import BadTimeSignature, BadSignature
from sqlalchemy.exc import IntegrityError
from flask_login import login_user, current_user, logout_user, login_required
# from db import db, bcrypt, mail as mailer
from school_project.models import User
from school_project.users.forms import RegistrationForm, LoginForm, UpdateForm, ForgotPasswordForm, ResetPasswordForm
from school_project.utils import save_picture
from school_project.models import Teacher, Student, UserPin
from ssl import create_default_context
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import logging
from school_project.database import bcrypt, db
from smtplib import SMTP_SSL, SMTP
import ssl
from email.utils import formataddr
from config import mail, serializer, salt

load_dotenv()


users = Blueprint('users', __name__)

sender = os.getenv('EMAIL_USERNAME')

def generate_pin():
    pin = ''.join(random.choices(string.digits, k=6))
    new_pin = UserPin(pin_code=pin)
    db.session.add(new_pin)
    db.session.commit()
    return pin


def generate_four_digit_code():
    return random.randint(1000, 9999)


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
        if user and bcrypt.check_password_hash(user.password, form.password.data + os.getenv('SALT')):
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


# def send_mail_starttls(to, template, subject, link, username, **kwargs):
#     try:
#         with current_app.app_context():
#             msg = Message(subject=subject, sender=os.getenv('MAIL_USERNAME'), recipients=[to])
#             html = render_template(template, username=username, link=link, **kwargs)
#             inlined = css_inline.inline(html)
#             msg.html = inlined
#             # SSL context setup
#             context = ssl.create_default_context()
#             with SMTP('smtp-relay.sendinblue.com', 587) as conn:
#                 conn.starttls(context=context)
#                 conn.login(os.getenv('MAIL_USERNAME'), os.getenv('MAIL_PASSWORD'))
#                 conn.sendmail(
#                     os.getenv('MAIL_USERNAME'),
#                     [to],
#                     msg.as_string().encode('UTF-8')
#                 )
#             current_app.logger.info(f"Email sent to {to}")
#     except Exception as e:
#         current_app.logger.error(f"Failed to send email: {str(e)}")
#         raise
def send_mail(to, template, subject, link, username, **kwargs):
    try:
        with current_app.app_context():
            msg = Message(subject=subject, sender=sender, recipients=[to])
            html = render_template(template, username=username, link=link, **kwargs)
            inlined = css_inline.inline(html)
            msg.html = inlined
            mail.send(msg)
            current_app.logger.info(f"Email sent to {to}")
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {str(e)}")
        raise
        raise

@users.route("/reset_password", methods=["POST", "GET"])
def forgot_password():
    # sender = app.config['MAIL_DEFAULT_SENDER']
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user:
            try:
                username = user.username
                hashCode = serializer.dumps(email, salt='reset-password')
                user.hashCode = hashCode
                server = os.getenv('DEV_URL') if os.getenv('FLASK_ENV') == 'development' else os.getenv('PROD_URL')
                link = f"{server}/{hashCode}"
                db.session.commit()
                send_mail(
                    to=email,
                    # sender=sender,
                    template="email.html",
                    subject="Reset Password",
                    username=username,
                    link=link,
                )
                flash("A password reset link has been sent to your email!", "success")
                return redirect(url_for('users.login'))
            except Exception as e:
                current_app.logger.error(f"Error during password reset: {str(e)}")
                flash("An error occurred. Please try again later.", "danger")
        else:
            flash("User does not exist!", "danger")

    return render_template('forgot_password.html', title='Forgot Password', form=form)


@users.route("/<string:hashCode>", methods=["GET", "POST"])
def hashcode(hashCode):
    try:
        email = serializer.loads(hashCode, salt="reset-password", max_age=3600)
    except BadTimeSignature:
        flash("The password reset link has expired. Please request a new one.", "danger")
        return redirect(url_for("core.index"))
    except BadSignature:
        flash("Invalid password reset link. Please request a new one.", "danger")
        return redirect(url_for("core.index"))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash("User does not exist!", "danger")
        return redirect(url_for("core.index"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        if form.password.data == form.confirm_password.data:
            user.password = bcrypt.generate_password_hash(form.password.data + os.getenv('SALT')).decode('utf-8')
            user.hashCode = None
            db.session.commit()
            flash("Your password has been reset successfully!", "success")
            return redirect(url_for("users.login"))
        else:
            flash("Password fields do not match.", "danger")

    return render_template("reset_password.html", form=form, hashCode=hashCode)