from datetime import datetime, timedelta
import uuid
import random
import string
from flask import Flask
import os
from dotenv import load_dotenv
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash, check_password_hash
from flask import current_app

from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from sqlalchemy import Table, Column, Integer, ForeignKey
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from school_project.database import db

from school_project.login import login_manager


load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class_teachers = Table('class_teachers', db.Model.metadata,
                       Column('class_id', Integer, ForeignKey(
                           'classes.id'), primary_key=True),
                       Column('teacher_id', Integer, ForeignKey(
                           'users.id'), primary_key=True)
                       )


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    is_teacher = db.Column(db.Boolean, default=False)
    first_name = db.Column(db.String(225), nullable=False)
    last_name = db.Column(db.String(225), nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=True)
    email = db.Column(db.String(150), unique=True, nullable=True)
    is_student = db.Column(db.Boolean, default=False)
    is_parent = db.Column(db.Boolean, default=False)

    password = db.Column(db.String(200), nullable=True)
    role = db.Column(db.String(20), nullable=False)
    # pin = db.Column(db.String(10), nullable=False)
    student = db.relationship('Student', back_populates='user', uselist=False)
    teacher = db.relationship('Teacher', back_populates='user', uselist=False)
    parent = db.relationship('Parent', back_populates='user', uselist=False)
    principal = db.relationship(
        'Principal', back_populates='user', uselist=False)
    schools = db.relationship('School', back_populates='principal')
    # head_teacher_of_classes = db.relationship(
    #     'Class', back_populates='head_teacher')
    pins = db.relationship('Pin', back_populates='user',
                           lazy='dynamic')

    reset_token_expiration = db.Column(db.DateTime, nullable=True)
    reset_token = db.Column(db.String(36), unique=True, nullable=True)
    classes = db.relationship(
        'Class', secondary=class_teachers, back_populates='teachers')

    def __init__(self, first_name, last_name, role, email=None, username=None, password=None):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.username = username
        self.password = generate_password_hash(
            password).decode('utf-8') if password else None
        self.role = role

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"Username {self.username}"

    def is_student(self):
        return self.student is not None

    def is_teacher(self):
        return self.teacher is not None

    def generate_reset_token(self, expires_in=1800):
        self.reset_token = str(uuid.uuid4())
        self.reset_token_expiration = datetime.utcnow() + timedelta(seconds=expires_in)
        db.session.commit()
        return self.reset_token

    def verify_reset_token(self, token):
        user = User.query.filter_by(reset_token=token).first()
        if user is None or user.reset_token_expiration < datetime.utcnow():
            return None
        return user


class UserPin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pin_code = db.Column(db.String(10), unique=True, nullable=False)


class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey(
        'classes.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey(
        'parents.id'), nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey(
        'subjects.id'), nullable=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey(
        'teachers.id'), nullable=True)

    user = db.relationship('User', back_populates='student')
    assigned_class = db.relationship('Class', back_populates='students')
    parent = db.relationship('Parent', back_populates='children')
    grades = db.relationship(
        'Grade', order_by='Grade.id', back_populates='student')
    results = db.relationship(
        'Result', back_populates='student_rel', overlaps="student_rel")

    def __init__(self, first_name, user_id, last_name, email=None,  class_id=None):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.user_id = user_id
        self.class_id = class_id


class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=True)

    user = db.relationship('User', back_populates='teacher')
    subjects = db.relationship('Subject', back_populates='teacher')
    # classes = db.relationship(
    #     'Class', back_populates='teachers', secondary='class_teachers')
    students = db.relationship('Student', backref='teacher')

    def __init__(self, first_name, user_id, last_name, department, email=None):
        self.first_name = first_name
        self.last_name = last_name
        self.department = department
        self.email = email
        self.user_id = user_id


class Class(db.Model):
    __tablename__ = 'classes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    section = db.Column(db.String(64), nullable=False)

    # teacher_id = db.Column(db.Integer, db.ForeignKey(
    #     'teachers.id'), nullable=False)
    teachers = db.relationship(
        'User', secondary=class_teachers, back_populates='classes')
    # teacher = db.relationship(
    #     'Teacher', back_populates='classes', secondary='class_teachers')
    students = db.relationship('Student', back_populates='assigned_class')
    subjects = db.relationship(
        'Subject', order_by="Subject.id", back_populates='assigned_class')

    def __init__(self, name, section):
        self.name = name
        # self.teacher_id = teacher_id
        self.section = section


class Pin(db.Model):
    __tablename__ = 'pins'
    id = db.Column(db.Integer, primary_key=True)
    pin = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    results = db.relationship('Result', back_populates='pin')
    user = db.relationship('User', back_populates='pins')


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    sender = db.relationship('User', foreign_keys=[
                             sender_id], backref='sent_messages', lazy=True)
    receiver = db.relationship('User', foreign_keys=[
                               receiver_id], backref='received_messages', lazy=True)

    def __repr__(self):
        return f"Message('{self.sender.username}', '{self.receiver.username}', '{self.timestamp}')"


class Parent(db.Model):
    __tablename__ = 'parents'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    children = db.relationship('Student', back_populates='parent')
    user = db.relationship('User', back_populates='parent')


class Principal(db.Model):
    __tablename__ = 'principals'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', back_populates='principal')
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=True)

    def __init__(self,  user_id, first_name, last_name, email=None):

        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email


class Grade(db.Model):
    __tablename__ = 'grades'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey(
        'students.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey(
        'subjects.id'), nullable=False)
    grade = db.Column(db.Numeric(5, 2), nullable=False)
    remarks = db.Column(db.Text, nullable=True)
    student = db.relationship('Student', back_populates='grades')
    subject = db.relationship('Subject', back_populates='grades')


class Subject(db.Model):
    __tablename__ = 'subjects'  # Ensure this is the correct table name
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey(
        'classes.id'), nullable=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey(
        'teachers.id'), nullable=True)

    teacher = db.relationship('Teacher', back_populates='subjects')
    grades = db.relationship('Grade', order_by=Grade.id,
                             back_populates='subject')
    students = db.relationship('Student', backref='subject', lazy='dynamic')
    assigned_class = db.relationship('Class', back_populates='subjects')


Class.subjects = db.relationship(
    'Subject', order_by=Subject.id, back_populates='assigned_class')


class School(db.Model):
    __tablename__ = 'schools'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    logo = db.Column(db.String(255), nullable=True)
    contact_info = db.Column(db.Text, nullable=True)
    principal_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False)
    principal = db.relationship('User', back_populates='schools')


class AcademicYear(db.Model):
    __tablename__ = 'academic_years'
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.String(9), nullable=False)  # e.g., 2023-2024
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    terms = db.relationship('Term', order_by='Term.id',
                            back_populates='academic_year')

    def __init__(self, year, start_date, end_date, id=None):
        self.end_date = end_date
        self.start_date = start_date
        self.id = id
        self.year = year


class Term(db.Model):
    __tablename__ = 'terms'
    id = db.Column(db.Integer, primary_key=True)
    academic_year_id = db.Column(db.Integer, db.ForeignKey(
        'academic_years.id'), nullable=True)
    name = db.Column(db.String(10), nullable=False)  # e.g., Semester 1
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    academic_year = db.relationship('AcademicYear', back_populates='terms')

    def __init__(self, name, start_date, end_date, academic_year_id=None, id=None):
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.id = id
        self.academic_year_id = academic_year_id


class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey(
        'students.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey(
        'teachers.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    # 'Present', 'Absent', 'Late'
    status = db.Column(db.String(10), nullable=False)


class Assignment(db.Model):
    __tablename__ = 'assignments'
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey(
        'classes.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey(
        'teachers.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    submissions = db.relationship(
        'Submission', backref='assignment', lazy=True)
    student_id = db.Column(db.Integer, db.ForeignKey(
        'students.id'), nullable=True)

    def __init__(self, class_id, due_date, teacher_id, description, title, student_id=None):
        self.class_id = class_id
        self.student_id = student_id
        self.description = description
        self.title = title
        self.due_date = due_date
        self.teacher_id = teacher_id


class Submission(db.Model):
    __tablename__ = 'submissions'
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey(
        'assignments.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey(
        'students.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey(
        'teachers.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_submitted = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
    feedback = db.Column(db.Text, nullable=True)

    def __init__(self, assignment_id, student_id, teacher_id, content, feedback, date_submitted):
        self.assignment_id = assignment_id
        self.content = content
        self.student_id = student_id
        self.date_submitted = date_submitted
        self.feedback = feedback
        self.teacher_id = teacher_id


class Communication(db.Model):
    __tablename__ = 'communications'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipient_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    student_id = db.Column(db.Integer, db.ForeignKey(
        'students.id'), nullable=False)


class ForumThread(db.Model):
    __tablename__ = 'forum_threads'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    created_by = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class ForumPost(db.Model):
    __tablename__ = 'forum_posts'
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_created = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)

    student_id = db.Column(db.Integer, db.ForeignKey(
        'students.id'), nullable=False)


class SchoolEvent(db.Model):
    __tablename__ = 'school_events'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text, nullable=True)

    def __init__(self, name, date, description):
        
        self.name = name
        self.date = date
        self.description = description


class Resource(db.Model):
    __tablename__ = 'resources'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    link = db.Column(db.String(100), nullable=True)
    file = db.Column(db.String(200), nullable=False)
    uploaded_by = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False)


class PersonalCalendar(db.Model):
    __tablename__ = 'personal_calendars'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_name = db.Column(db.String(100), nullable=False)
    event_date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text, nullable=True)


class Announcement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    read = db.Column(db.Boolean, default=False)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    # receiver_id = db.Column(
    #     db.Integer, db.ForeignKey('users.id'), nullable=False)
    sender_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False)
    # 'teacher', 'student', 'parent', 'all'
    recipient_role = db.Column(db.String(20), nullable=False)
    # sender = db.relationship('User', foreign_keys=[
    #                          sender_id], backref='sent_notifications', lazy=True)
    # receiver_id = db.relationship('User', foreign_keys=[
    #                            receiver_id], backref='received_notifications', lazy=True)


class SystemLog(db.Model):
    __tablename__ = 'system_logs'
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Result(db.Model):
    __tablename__ = 'results'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey(
        'students.id'), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Numeric(5, 2), nullable=False)
    grade = db.Column(db.String(2), nullable=False)
    term = db.Column(db.String(20), nullable=False)
    remarks = db.Column(db.Text, nullable=True)
    pin_id = db.Column(db.Integer, db.ForeignKey('pins.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey(
        'teachers.id'), nullable=False)
    student_rel = db.relationship(
        'Student', back_populates='results', overlaps="student")
    principal_id = db.Column(db.Integer, db.ForeignKey(
        'principals.id'), nullable=False)
    school_id = db.Column(db.Integer, db.ForeignKey(
        'schools.id'), nullable=False)
    pin = db.relationship('Pin', back_populates='results')

    def __init__(self, student_id, subject, score, grade, term, remarks, pin_id, pin, principal_id, school_id, teacher_id):
        self.student_id = student_id
        self.subject = subject
        self.score = score
        self.grade = grade
        self.term = term
        self.remarks = remarks
        self.pin_id = pin_id
        self.pin = pin
        self.principal_id = principal_id
        self.teacher_id = teacher_id
        self.school_id = school_id

    # @staticmethod
    # def generate_pin():
    #     return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


class SchoolCalendar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(100), nullable=False)
    event_date = db.Column(db.DateTime, nullable=False)
