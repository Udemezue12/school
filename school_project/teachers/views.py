
from flask import render_template, url_for, flash, abort,  redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
# from db import db
from school_project.utils import generate_pin, save_picture, save_file
from school_project.forms import StudentForm, AttendanceForm, SelectStudentForm, GradeForm, ResourceForm, AssignmentForm, MessageForm, TeacherProfileForm, ResultForm, TeacherRegistrationForm, CalendarForm
from school_project.models import Result, User, Student, Attendance, Grade, Teacher, Resource, Submission, PersonalCalendar, Class, Assignment, SchoolEvent, Message, Pin, SchoolCalendar, SystemLog, School


from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
# from flask_mail import Mail

# from school_project import app

from school_project.database import mail, db, bcrypt


teacher = Blueprint("teacher", __name__)


def validate_password(password):
    if not password:
        raise ValueError('Password cannot be empty or None.')
    if len(password) < 8:
        raise ValueError('Password must be at least 12 characters long.')


@teacher.route('/teacher/profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    if current_user.role != 'teacher':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('core.index'))

    form = TeacherProfileForm(obj=current_user)

    if form.validate_on_submit():
        current_user.email = form.email.data
        if form.password.data:
            current_user.password = generate_password_hash(
                form.password.data).decode('utf-8')
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('users.dashboard'))

    return render_template('teacher_update_profile.html', form=form)


@teacher.route('/teacher/dashboard')
@login_required
def teacher_dashboard():
    return render_template('teacher_dashboard.html')


@teacher.route('/teacher/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('users.login'))

    form = TeacherRegistrationForm()
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
                validate_password(password)

                user = User(
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    role=form.role.data,
                    email=form.email.data,
                    username=form.username.data,
                    password=password
                )

                db.session.add(user)
                db.session.commit()

                if user.role == 'teacher':
                    teacher = Student.query.filter_by(
                        first_name=user.first_name,
                        last_name=user.last_name,
                        user_id=None,
                    ).first()
                    if teacher:
                        teacher.user_id = user.id
                        db.session.commit()

                flash('Thanks for registering!', 'success')
                return redirect(url_for('users.login'))
            except ValueError as e:
                flash(str(e), 'danger')
            except IntegrityError as e:
                db.session.rollback()
                # logging.error("IntegrityError occurred: %s", e)
                flash(
                    "An error occurred during registration. Please try again.", 'danger')

    return render_template('teacher_register.html', form=form)


@teacher.route('/view/events', methods=['GET'])
@login_required
def view_events():
    events = SchoolEvent.query.all()
    return render_template('events.html', title='Events', events=events)


@teacher.route('/students/')
@login_required
def view_students():

    if current_user.role != 'teacher':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('core.index'))

    users = User.query.filter_by(role='student').all()
    return render_template('view_students.html', users=users)


@teacher.route('/teacher/messages', methods=['GET', 'POST'])
@login_required
def send_message():
    form = MessageForm()
    form.receiver_id.choices = [(user.id, user.username)
                                for user in User.query.all()]
    if form.validate_on_submit():
        message = Message(sender_id=current_user.id,
                          receiver_id=form.receiver_id.data, content=form.content.data)
        db.session.add(message)
        db.session.commit()
        flash('Your message has been sent!', 'success')
        return redirect(url_for('users.dashboard'))
    return render_template('send_message.html', form=form)


@teacher.route("/view_messages")
@login_required
def view_messages():
    messages = Message.query.filter_by(receiver_id=current_user.id).all()
    return render_template('view_messages.html', messages=messages)


def mark_attendance(student_id):
    if current_user != 'teacher':
        return redirect(url_for('core.index'))

    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    if not teacher:
        flash('Teacher profile not found.', 'danger')
        return redirect(url_for('core.index'))
    student = Student.query.filter_by(
        id=student_id, class_id=teacher.class_id).first()

    if not student:
        flash('Invalid student selected.', 'danger')
        return redirect(url_for('teacher.select_student'))

    form = AttendanceForm()
    if form.validate_on_submit():
        attendance = Attendance(
            student_id=student_id,
            date=form.date.data,
            status=form.status.data,
            teacher_id=current_user.id,
            class_id=teacher.class_id
        )
        db.session.add(attendance)
        db.session.commit()
        flash('Attendance marked successfully.', 'success')
        return redirect(url_for('teacher.select_student'))

    return render_template('mark_attendance.html', form=form, student=student)


@teacher.route("/view_school_calendar")
@login_required
def view_school_calendar():
    calendars = SchoolCalendar.query.all()
    return render_template('school_calendar.html', calendars=calendars)


@teacher.route('/teacher/class/<int:class_id>/attendance/report')
@login_required
def view_attendance(class_id):
    class_ = Class.query.get_or_404(class_id)
    if class_.teacher_id != current_user.id:
        flash("You do not have access to this class.", 'danger')
        return redirect(url_for('teacher.teacher_dashboard'))
    attendance_records = Attendance.query.all()
    return render_template('view_attendance.html', attendance_records=attendance_records, class_id=class_)


@teacher.route('/teacher/class/<int:class_id>/roster')
@login_required
def view_class_roster(class_id):
    class_ = Class.query.get_or_404(class_id)
    if class_.teacher_id != current_user.id:
        flash("You do not have access to this class.", 'danger')
        return redirect(url_for('teacher.teacher_dashboard'))

    students = Student.query.filter_by(class_id=class_id).all()
    return render_template('class_roster.html', class_=class_, students=students)


@teacher.route("/view_grades", methods=['GET', 'POST'])
@login_required
def view_grades():
    grades = Grade.query.all()
    return render_template('view_grades.html', grades=grades)


@teacher.route('/teacher/class/<int:class_id>/gradebook', methods=['GET', 'POST'])
@login_required
def manage_gradebook(class_id):
    form = GradeForm()
    if form.validate_on_submit():
        grade = Grade(student_id=form.student_id.data,
                      subject=form.subject.data, grade=form.grade.data)
        db.session.add(grade)
        db.session.commit()
        flash("Grade added successfully!", 'success')
        return redirect(url_for('teacher.manage_gradebook', class_id=class_id))
    form.student_id.choices = [(student.id, f"{student.users.first_name} {student.users.last_name}")
                               for student in Student.query.filter_by(class_id=class_id).all()]
    grades = Grade.query.filter_by(class_id=class_id).all()
    return render_template('gradebook.html', form=form, grades=grades)


@teacher.route('/assignments', methods=['GET', 'POST'])
@login_required
def create_assignment():
    if current_user.role != 'teacher':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('main.index'))

    form = AssignmentForm()

    if hasattr(current_user, 'classes'):
        form.class_id.choices = [(c.id, c.name) for c in current_user.classes]

    if form.validate_on_submit():
        assignment = Assignment(
            class_id=form.class_id.data,
            teacher_id=current_user.id,
            title=form.title.data,
            description=form.description.data,
            due_date=form.due_date.data
        )
        db.session.add(assignment)
        db.session.commit()
        flash("Assignment created successfully!", 'success')
        return redirect(url_for('teacher.teacher_dashboard'))

    return render_template('create_assignment.html', form=form)


@teacher.route('/view/assignments', methods=['GET', 'POST'])
@login_required
def view_assignments():
    # student_class_id = current_user.class_id
    assignments = Assignment.query.all()
    return render_template('assignments.html', assignments=assignments)


@teacher.route('/view_submissions/<int:assignment_id>', methods=['GET', 'POST'])
@login_required
def view_submissions(assignment_id):
    assignment = Assignment.query.get_or_404(assignment_id)
    if current_user.role != 'teacher' and current_user.role != 'principal':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('core.index'))

    submissions = Submission.query.filter_by(assignment_id=assignment_id).all()
    return render_template('view_submissions.html', submissions=submissions)


@teacher.route('/submission/<int:submission_id>/feedback', methods=['GET', 'POST'])
@login_required
def provide_feedback(submission_id):
    if current_user.role != 'teacher':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('core.index'))

    submission = Submission.query.get_or_404(submission_id)
    submissions = Submission.query.filter_by(teacher_id=current_user.id).all()
    if request.method == 'POST':
        feedback = request.form['feedback']
        submission.feedback = feedback
        db.session.commit()
        flash('Feedback provided successfully', 'success')
        return redirect(url_for('teacher.view_submissions', assignment_id=submission.assignment_id))

    return render_template('provide_feedback.html', submission=submission, submissions=submissions)


@teacher.route('/view/submissions', methods=['GET'])
@login_required
def view_submission():
    submissions = Submission.query.all()
    return render_template('submissions.html', submissions=submissions)


@teacher.route('/resources', methods=['GET', 'POST'])
@login_required
def resources():
    if current_user.role != 'teacher':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('core.index'))

    form = ResourceForm()

    if form.validate_on_submit():
        file_path = None
        if form.file.data:
            file_path = save_file(form.file.data)
        resource = Resource(
            title=form.title.data,
            description=form.description.data,
            file_path=file_path,
            link=form.link.data,
            uploaded_by=current_user.id
        )
        db.session.add(resource)
        db.session.commit()
        flash('Resource uploaded successfully', 'success')
        return redirect(url_for('teacher.resources'))

    resources = Resource.query.filter_by(uploaded_by=current_user.id).all()
    return render_template('resources.html', form=form, resources=resources)


@teacher.route('/view_resources')
@login_required
def view_resources():
    if current_user.role != 'teacher':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('core.index'))

    resources = Resource.query.filter_by(uploaded_by=current_user.id).all()

    return render_template('view_resource.html', resources=resources)


@teacher.route('/calendar', methods=['GET', 'POST'])
@login_required
def personal_calendar():
    if current_user.role != 'teacher':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('core.index'))
    form = CalendarForm()
    if form.validate_on_submit():
        new_event = PersonalCalendar(
            event_name=form.event_name.data,
            event_date=form.event_date.data,
            description=form.description.data,
            user_id=current_user.id
        )
        db.session.add(new_event)

        db.session.commit()
        flash('Event added to calendar', 'success')
        return redirect(url_for('teacher.view_personal_calendar'))

    return render_template('personal_calendar.html', form=form)

# @teacher.route('/create/personal/calendar', methods=['GET', 'POST'])
# @login_required
# def create_calendar():
#     if current_user.role != 'teacher':
#         flash('Unauthorized access', 'danger')
#         return redirect(url_for('core.index'))
#     form = CalendarForm()
#     if form.validate_on_submit():
#         new_event = PersonalCalendar(
#             event_name=form.event_name.data,
#             event_date=form.event_date.data,
#             description=form.description.data,
#             user_id=current_user.id
#         )
#         db.session.add(new_event)

#         db.session.commit()
#         flash('Event added to calendar', 'success')
#         return redirect(url_for('teacher.view_personal_calendar'))


@teacher.route('/view/calendar', methods=['GET'])
@login_required
def view_personal_calendar():
    calendars = PersonalCalendar.query.filter_by(user_id=current_user.id).all()
    return render_template('view_personal_calendar.html', calendars=calendars)


@teacher.route('/teacher/calendar')
@login_required
def view_schoolevent():
    events = SchoolEvent.query.all()
    return render_template('calendar.html', events=events)


# /////////////////////////////////////////////
@teacher.route('/upload/results', methods=['GET', 'POST'])
@login_required
def upload_results():
    if current_user.role != "teacher":
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('core.index'))

    form = GradeForm()
    students = User.query.filter_by(role='student').all()
    principals = User.query.filter_by(role='principal').all()
    schools = User.query.all()

    if form.validate_on_submit():
        for student_result_form in form.results:
            student_result = student_result_form
            pin = generate_pin()

            student = User.query.filter_by(
                id=student_result['student_id'], role='student').first()
            principal = User.query.filter_by(
                id=student_result['principal_id'], role='principal').first()
            school = User.query.filter_by(
                id=student_result['school_id']).first()

            if not student or not principal or not school:
                flash('Invalid student, principal, or school ID provided.', 'danger')
                return redirect(url_for('teacher.upload_results'))

            student_pin = Pin(pin=pin, user_id=student.id)
            db.session.add(student_pin)

            result = Result(
                student_id=student.id,
                subject=student_result['subject'],
                score=student_result['score'],
                grade=student_result['grade'],
                remarks=student_result['remarks'],
                term=student_result['term'],
                principal_id=principal.id,
                school_id=school.id,
                pin_id=student_pin.id,
                teacher_id=current_user.id
            )

            db.session.add(result)

        db.session.commit()
        flash('Results uploaded successfully and PINs generated!', 'success')
        return redirect(url_for("users.dashboard"))

    return render_template('upload_results.html', title='Upload Results', form=form, students=students, principals=principals, schools=schools)


# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

@teacher.route('/select_student', methods=['GET', 'POST'])
@login_required
def select_student():
    if current_user != 'teacher':
        return redirect(url_for('core.index'))

    teacher = Teacher.query.filter_by(user_id=current_user.id).first()
    if not teacher:
        return redirect(url_for('core.index'))

    students = Student.query.filter_by(class_id=teacher.class_id).all()

    return render_template('select_student.html', students=students)


@teacher.route('/logs')
@login_required  # Assuming you want to protect this route
def view_logs():
    logs = SystemLog.query.all()
    return render_template('view_logs.html', logs=logs)


@teacher.route('/school')
@login_required
def view_schools():

    schools = School.query.all()
    return render_template('view_schools.html', schools=schools)
