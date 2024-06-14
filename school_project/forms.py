from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import DecimalField, StringField, PasswordField, SubmitField, BooleanField, SelectField, DateField, TextAreaField, IntegerField, SelectMultipleField, FormField, FieldList, DateTimeField

from flask_wtf.file import FileField, FileAllowed

from wtforms.validators import DataRequired, Email, Length, ValidationError, Optional, URL, EqualTo, NumberRange
from school_project.models import User, Result


class DummyForm(FlaskForm):
    pass


class StudentForm(FlaskForm):
    user_id = SelectField('User', coerce=int)
    submit = SubmitField('Add Student')


class SchoolForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=255)])
    logo = StringField('Logo URL', validators=[Optional(), Length(max=255)])
    contact_info = TextAreaField(
        'Contact Information', validators=[Optional()])
    principal_id= SelectField('Principal', validators=[
                                 DataRequired()], coerce=int)
    submit = SubmitField('Submit')


class PrincipalRegistrationForm(FlaskForm):
    role = SelectField(
        'Role', choices=[('principal', 'Principal')], validators=[DataRequired()], default='principal')
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Surname', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo(
        'password2', message='Passwords do not match')])
    password2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Register')


class PrincipalProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[
                                     DataRequired(), EqualTo('password')])
    submit = SubmitField('Update Profile')


class StudentProfileForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[
                                     DataRequired(), EqualTo('password')])
    submit = SubmitField('Update Profile')


class StudentRegistrationForm(FlaskForm):
    role = SelectField(
        'Role', choices=[('student', 'Student')], validators=[DataRequired()], default='student')
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Surname', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    # pin = StringField('PIN', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo(
        'password2', message='Passwords do not match')])
    password2 = PasswordField('Confirm Passowrd', validators=[DataRequired()])
    submit = SubmitField('Register')


class TeacherProfileForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[
                                     DataRequired(), EqualTo('password')])
    submit = SubmitField('Update Profile')
    # username = StringField('Username', validators=[DataRequired()])


class TeacherRegistrationForm(FlaskForm):
    role = SelectField(
        'Role', choices=[('teacher', 'Teacher')], validators=[DataRequired()], default='teacher')
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Surname', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    # pin = StringField('PIN', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo(
        'password2', message='Passwords do not match')])
    password2 = PasswordField('Confirm Passowrd', validators=[DataRequired()])
    submit = SubmitField('Register')


class ParentProfileForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[
                                     DataRequired(), EqualTo('password')])
    submit = SubmitField('Update Profile')


class AssignForm(FlaskForm):
    teacher = SelectField('Teacher', choices=[], validators=[DataRequired()])
    class_name = SelectField('Class', choices=[], validators=[DataRequired()])
    subject = SelectField('Subject', choices=[], validators=[DataRequired()])
    # student = SelectField('Student', choices=[])
    submit = SubmitField('Assign')


class SystemLogForm(FlaskForm):
    action = StringField('Action', validators=[
                         DataRequired(), Length(max=100)])
    submit = SubmitField('Create Log')


class AttendanceForm(FlaskForm):
    student_id = SelectField('Student', coerce=int)
    date = StringField('Date', validators=[DataRequired()])
    status = SelectField('Status', choices=[
                         ('Present', 'Present'), ('Absent', 'Absent')], validators=[DataRequired()])
    submit = SubmitField('Mark Attendance')


class AssignmentForm(FlaskForm):
    title = StringField('Title', validators=[
                        DataRequired(), Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[
                                DataRequired(), Length(min=10, max=500)])
    due_date = DateField('Due Date', validators=[
                         DataRequired()], format='%Y-%m-%d')
    class_id = SelectField('Class', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Create Assignment')


class StudentResultForm(FlaskForm):
    student_id = IntegerField('Student ID', validators=[DataRequired()])
    subject = StringField('Subject', validators=[
                          DataRequired(), Length(max=50)])
    score = DecimalField('Score', validators=[
                         DataRequired(), NumberRange(min=0, max=100)])
    grade = StringField('Grade', validators=[DataRequired(), Length(max=2)])
    remarks = TextAreaField('Remarks', validators=[Length(max=500)])
    term = StringField('Term', validators=[DataRequired(), Length(max=20)])
    principal_id = IntegerField('Principal ID', validators=[DataRequired()], )
    school_id = IntegerField('School ID', validators=[DataRequired()])


class GradeForm(FlaskForm):
    results = FieldList(FormField(StudentResultForm),
                        min_entries=1, max_entries=50)
    submit = SubmitField('Upload Results')


class SelectStudentForm(FlaskForm):
    student_id = SelectField('Student', coerce=int,
                             validators=[DataRequired()])
    subject_id = SelectField('Subject', coerce=int,
                             validators=[DataRequired()])
    teacher_id = SelectField('Teacher', coerce=int,
                             validators=[DataRequired()])
    submit = SubmitField('Select Student')


class CalendarForm(FlaskForm):
    event_name = StringField('Event Name', validators=[DataRequired()])
    event_date = DateTimeField(
        'Event Date', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    description = TextAreaField('Description')


class MessageForm(FlaskForm):
    receiver_id = SelectField('To', coerce=int)
    content = StringField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')


class ForumThreadForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    submit = SubmitField('Create Thread')


class ForumPostForm(FlaskForm):
    content = StringField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')


class AnnouncementForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = StringField('Content', validators=[DataRequired()])
    submit = SubmitField('Create Announcement')


class AddSubjectForm(FlaskForm):
    name = StringField('Subject Name', validators=[
                       DataRequired(), Length(min=2, max=235)])
    submit = SubmitField('Add Subject')


class AssignTeacherToClassForm(FlaskForm):
    class_id = SelectField('Class', coerce=int,
                           validators=[DataRequired()])
    teacher_id = SelectField('Teacher', coerce=int,
                             validators=[DataRequired()])
    submit = SubmitField('Assign Teacher to Class')


class AssignSubjectToClassForm(FlaskForm):
    subject_id = SelectField('Subject', coerce=int,
                             validators=[DataRequired()])
    class_id = SelectField('Class', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Assign Subject to Class')


class ResourceForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    file = FileField('File', validators=[FileAllowed(['pdf', 'doc', 'docx'])])
    link = StringField('Link', validators=[Optional(), URL()])
    submit = SubmitField('Upload Resource')


class CheckResultForm(FlaskForm):
    pin = StringField('Result Check PIN', validators=[DataRequired()])
    submit = SubmitField('Check Result')

    def validate_pin(self, pin):
        result_pin = Result.query.filter_by(
            pin=pin.data, student_id=current_user.students.id, used=False).first()
        if not result_pin:
            raise ValidationError('Invalid or already used PIN.')


class PaymentForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Pay')


class AddStudentForm(FlaskForm):
    first_name = StringField('First Name', validators=[
                             DataRequired(), Length(min=2, max=100)])
    last_name = StringField('Last Name', validators=[
                            DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])

    class_id = SelectField('Class', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Add Student')


class EventForm(FlaskForm):
    name = StringField('Event Name', validators=[DataRequired()])
    date = DateField('Event Date', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[
                                Optional(), Length(max=500)])
    submit = SubmitField('Create Event')


class SubmissionForm(FlaskForm):
    teacher_id = SelectField('Teacher', validators=[DataRequired()])
    content = StringField('Content', validators=[DataRequired()
                                                 ])
    date_submitted = DateField('Data Submiited', validators=[DataRequired()])
    feedback = StringField('Feedback', validators=[DataRequired()])
    student_id = SelectField('Student', validators=[DataRequired()])
    submit = SubmitField('Submit')


class SchoolCalendarForm(FlaskForm):
    event_name = StringField('Event Name', validators=[DataRequired()])
    event_date = DateField('Event Date', validators=[DataRequired()])
    submit = SubmitField('Create Calendar Entry')

    def __repr__(self):
        return f'<SchoolCalendar {self.event_name}>'


class AcademicYearForm(FlaskForm):
    year = StringField('Academic Year (e.g., 2023-2024)',
                       validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    submit = SubmitField('Add Academic Year')


class MultiAssignForm(FlaskForm):
    students = SelectMultipleField(
        'Students', coerce=int, validators=[DataRequired()])
    classes = SelectMultipleField(
        'Classes', coerce=int, validators=[DataRequired()])
    subjects = SelectMultipleField(
        'Subjects', coerce=int, validators=[DataRequired()])
    teachers = SelectMultipleField(
        'Teachers', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Assign')


class MultiAssignTeacherForm(FlaskForm):
    # students = SelectMultipleField('Students', coerce=int, validators=[DataRequired()])
    classes = SelectMultipleField(
        'Classes', coerce=int, validators=[DataRequired()])
    subjects = SelectMultipleField(
        'Subjects', coerce=int, validators=[DataRequired()])
    teachers = SelectMultipleField(
        'Teachers', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Assign')


class TermForm(FlaskForm):
    name = StringField('Term Name (e.g., Semester 1)',
                       validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[DataRequired()])
    # academic_year_id = SelectField(
    #     'Academic Year', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Add Term')


class ClassForm(FlaskForm):
    name = StringField('Class Name', validators=[DataRequired()])
    section = StringField('Section', validators=[DataRequired()])
    teacher = SelectField('Teacher', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Create Class')


class ResultForm(FlaskForm):
    student_id = SelectField('Student', validators=[DataRequired()])
    subject = StringField('Subject', validators=[DataRequired()])
    score = DecimalField('Score', validators=[
                         DataRequired(), NumberRange(min=0, max=100)])
    grade = StringField('Grade', validators=[DataRequired()])
    term = StringField('Term', validators=[DataRequired()])
    submit = SubmitField('Upload Result')


class CreateTeacherForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    department = StringField('Department')
    submit = SubmitField('Create Teacher')


class PinForm(FlaskForm):
    user_id = IntegerField('User ID', validators=[DataRequired()])
    submit = SubmitField('Generate PIN')
    pin = IntegerField('Pin', validators=[DataRequired()])


class ResultCheckForm(FlaskForm):
    pin = StringField('PIN', validators=[DataRequired()])
    submit = SubmitField('Check Result')


class CreateStudentForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])

    submit = SubmitField('Create Student')


class NotificationForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])
    recipient_role = SelectField('Recipient Role', choices=[('teachers', 'Teachers'), (
        'students', 'Students'), ('parents', 'Parents')], validators=[DataRequired()])
    submit = SubmitField('Send Notification')
