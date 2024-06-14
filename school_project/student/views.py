import os
import stripe
import requests
from flask import render_template, url_for, flash, abort, redirect, request, Blueprint, session
from sqlalchemy.exc import IntegrityError
from flask_mail import Message
# from clean import app

from werkzeug.security import generate_password_hash
from dotenv import load_dotenv
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
# from db import db, mail
from school_project.utils import generate_pin, generated_pin
from config import Config
from school_project.forms import StudentForm, PaymentForm, AttendanceForm, StudentProfileForm, PinForm, ResultCheckForm, StudentRegistrationForm
from school_project.models import Pin, Result, User, Student, Attendance, Grade, School, Assignment, Submission


from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

from school_project import app
from school_project.database import mail, db, bcrypt


load_dotenv()

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
public_key = os.getenv('STRIPE_PUBLIC_KEY')
senders_mail = os.getenv('EMAIL_USERNAME')
PAYSTACK_PUBLIC_KEY = os.getenv('PAYSTACK_PUBLIC_KEY')
PAYSTACK_SECRET_KEY = os.getenv("PAYPAL_SECRET_KEY")


student = Blueprint('student', __name__)


def validate_password(password):
    if password is None:
        raise ValueError('Password cannot be None.')
    if len(password) < 8:
        raise ValueError('Password must be at least 12 characters long.')
    if not any(char.isdigit() for char in password):
        raise ValueError('Password must contain at least one digit.')
    if not any(char.isupper() for char in password):
        raise ValueError(
            'Password must contain at least one uppercase letter.')
    if not any(char.islower() for char in password):
        raise ValueError(
            'Password must contain at least one lowercase letter.')
    if not any(char in "!@#$%^&*()_+-=[]{}|;:,.<>?/`~" for char in password):
        raise ValueError(
            'Password must contain at least one special character.')


@student.route('/dashboard')
# @login_required
def student_dashboard():
    return render_template('student_dashboard.html')


@student.route("/attendance")
@login_required
def view_attendance():
    if current_user.role != 'student':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('core.index'))

    attendance_records = Attendance.query.filter_by(
        student_id=current_user.id).all()

    return render_template('attendance.html', attendance_records=attendance_records)


@student.route('/student/assignments', methods=['GET'])
@login_required
def student_assignments():
    if current_user.role != 'student':
        flash('You are not authorized to view this page.', 'danger')
        return redirect(url_for('core.index'))

    student = Student.query.filter_by(user_id=current_user.id).first()

    if student is None:
        flash('No Assignment found for you!', 'danger')
        return redirect(url_for('core.index'))

    student_class = student.assigned_class

    assignments = Assignment.query.filter_by(class_id=student_class.id).all()

    return render_template('student_assignments.html', assignments=assignments)


@student.route('/print_results/<pin>', methods=['GET', 'POST'])
@login_required
def print_results(pin):
    if current_user.role != "student":
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('core.index'))

    results = Result.query.filter_by(pin=pin, student_id=current_user.id).all()

    if not results:
        flash('No results found for this PIN', 'danger')
        return redirect(url_for('student.check_results'))

    return render_template('print_results.html', results=results)


@student.route('/pin_payment', methods=['GET', 'POST'])
@login_required
def charge():
    form = PaymentForm()
    if form.validate_on_submit():
        reference = request.form.get('reference')

        headers = {
            'Authorization': f'Bearer {Config.PAYSTACK_SECRET_KEY}',
            'Content-Type': 'application/json',
        }

        verify_url = f'https://api.paystack.co/transaction/verify/{reference}'
        response = requests.get(verify_url, headers=headers)
        response_data = response.json()

        if response_data['status'] and response_data['data']['status'] == 'success':
            result = Result.query.filter_by(student_id=current_user.id).first()
            if result:
                pin = result.pin
                msg = Message('Your Result PIN', sender=Config.MAIL_DEFAULT_SENDER, recipients=[
                              current_user.email])
                msg.body = f'Thank you for your payment. Your result PIN is {pin}'
                mail.send(msg)

            flash('Payment successful! Check your email for the result PIN.', 'success')
            return redirect(url_for('student.payment_success'))
        else:
            flash('Payment verification failed. Please try again.', 'danger')
            return redirect(url_for('student.charge'))

    return render_template('pay_for_pin.html', form=form, PAYSTACK_PUBLIC_KEY=Config.PAYSTACK_PUBLIC_KEY)


@student.route('/payment_success')
@login_required
def payment_success():
    return render_template('payment_success.html')


@student.route('/student/profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    if current_user.role != 'student':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('core.index'))

    form = StudentProfileForm(obj=current_user)

    if form.validate_on_submit():
        current_user.email = form.email.data
        if form.password.data:
            current_user.password = generate_password_hash(
                form.password.data).decode('utf-8')
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('users.dashboard'))

    return render_template('student_update_profile.html', form=form)


@student.route('/check_results', methods=['GET', 'POST'])
@login_required
def check_results():
    if current_user.role != 'student':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('users.dashboard'))

    form = PinForm()
    if form.validate_on_submit():
        pin = form.pin.data
        student_pin = Pin.query.filter_by(user_id=current_user.id).first()

        if student_pin and student_pin.pin == pin:
            session['pin_verified'] = True
            flash('PIN verified successfully! You can now view your results.', 'success')
            return redirect(url_for('students.view_results'))
        else:
            flash('Invalid PIN. Please try again.', 'danger')

    return render_template('check_result.html', form=form)


@student.route('/view_results', methods=['GET', 'POST'])
@login_required
def view_results():
    if current_user.role != 'student':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('users.dashboard'))

    if not session.get('pin_verified'):
        flash('Please enter your PIN to view the results.', 'warning')
        return redirect(url_for('student.check_results'))

    results = Result.query.filter_by(student_id=current_user.id).all()
    return render_template('view_results.html', results=results)


@student.route('/view/submissions', methods=['GET'])
@login_required
def view_submissions():
    submissions = Submission.query.all()
    return render_template('submissions.html', submissions=submissions)


@student.route('/school')
@login_required
def view_schools():
    schools = School.query.all()
    return render_template('view_schools.html', schools=schools)


@student.route('/student/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('users.login'))

    form = StudentRegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash(
                'Username already exists. Please choose a different username.', 'danger')
            return redirect(url_for('users.register'))
        else:
            try:
                password = form.password.data
                validate_password(password)  # Validate the password

                hashed_password = bcrypt.generate_password_hash(
                    password).decode('utf-8')

                user = User(
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    role=form.role.data,
                    email=form.email.data,
                    username=form.username.data,
                    password_hash=hashed_password  # Store the hashed password
                )

                db.session.add(user)
                db.session.commit()

                if user.role == 'student':
                    student = Student.query.filter_by(
                        first_name=user.first_name,
                        last_name=user.last_name,
                        user_id=None,
                    ).first()
                    if student:
                        student.user_id = user.id
                        db.session.commit()

                flash('Thanks for registering!', 'success')
                return redirect(url_for('users.login'))
            except ValueError as e:
                flash(str(e), 'danger')
            except IntegrityError:
                db.session.rollback()
                flash(
                    "An error occurred during registration. Please try again.", 'danger')

    return render_template('student_register.html', form=form)
