from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, BooleanField
from wtforms.validators import ValidationError, EqualTo, DataRequired, Email, Length
from school_project.models import User
from flask_wtf.file import FileAllowed, FileField


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    role = SelectField('Role', choices=[('teacher', 'Teacher'), ('student', 'Student'), (
        'parent', 'Parent'), ('principal', 'Principal')], validators=[DataRequired()])
    role = SelectField('Role', choices=[('teacher', 'Teacher'), ('student', 'Student'), (
        'parent', 'Parent'), ('principal', 'Principal')], validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Surname', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    # pin = StringField('PIN', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo(
        'password2', message='Passwords do not match')])
    password2 = PasswordField('Confirm Passowrd', validators=[DataRequired()])
    submit = SubmitField('Register')

    def check_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('The email has already been used.')

    def check_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(
                'Username has already been Used'
            )


class UpdateForm(FlaskForm):
    username = StringField('Username', validators=[
                           DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    picture = FileField('Update Profile Picture', validators=[
                        FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def check_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('The email has already been registered')

    def check_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('The username has already been used')


class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError(
                'There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[
                                     DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
