from datetime import datetime
from werkzeug.security import generate_password_hash
from flask import render_template, url_for, flash, redirect, Blueprint
from sqlalchemy.exc import IntegrityError


from flask_login import login_required, current_user
from school_project.database import db

from school_project.forms import EventForm, MultiAssignForm, SchoolCalendarForm, AcademicYearForm, TermForm, ClassForm, NotificationForm, MessageForm, AddStudentForm, AddSubjectForm, CreateTeacherForm, CreateStudentForm, PrincipalProfileForm, MultiAssignTeacherForm, SubmissionForm, SystemLogForm, SchoolForm, PrincipalRegistrationForm

import logging

from school_project.models import User, Student, Teacher, Class, Message, Grade, Assignment, SchoolEvent, SchoolCalendar, AcademicYear, Term, Notification, Attendance, Subject, Submission, SystemLog, School, Principal
from school_project.users.views import generate_pin


principal = Blueprint('principal', __name__)

logging.basicConfig(level=logging.DEBUG)


def validate_password(password):
    if not password:
        raise ValueError('Password cannot be empty or None.')
    if len(password) < 8:
        raise ValueError('Password must be at least 12 characters long.')


@principal.route('/generate_pin')
def generate_pin_view():
    pin = generate_pin()
    return render_template('display_pin.html', pin=pin)


@principal.route('/dashboard')
@login_required
def principal_dashboard():
    return render_template('principal_dashboard.html')


@principal.route('/principal/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('users.login'))

    form = PrincipalRegistrationForm()
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

                if user.role == 'principal':
                    principal = Principal.query.filter_by(
                        first_name=user.first_name,
                        last_name=user.last_name,
                        user_id=None,
                    ).first()
                    if principal:
                        principal.user_id = user.id
                        db.session.commit()

                flash('Thanks for registering!', 'success')
                return redirect(url_for('users.login'))
            except ValueError as e:
                flash(str(e), 'danger')
            except IntegrityError as e:
                db.session.rollback()
                logging.error("IntegrityError occurred: %s", e)
                flash(
                    "An error occurred during registration. Please try again.", 'danger')

    return render_template('principal_register.html', form=form)


@principal.route("/manage_users", methods=['GET', 'POST'])
@login_required
def manage_users():
    if current_user.role != "principal":
        flash('Unauthorized access', 'danger')
        return redirect(url_for('core.index'))

    users = User.query.all()
    return render_template('manage_users.html', users=users)


@principal.route('/principal/create_student', methods=['GET', 'POST'])
@login_required
def create_student():
    if current_user.role != 'principal':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('core.index'))

    form = CreateStudentForm()
    if form.validate_on_submit():
        # Create a new user
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            role='student'
        )
        db.session.add(user)
        db.session.commit()

        student = Student(user_id=user.id)
        db.session.add(student)
        db.session.commit()

        flash('Student created successfully!', 'success')
        return redirect(url_for('principal.dashboard'))

    return render_template('create_student.html', form=form)


@principal.route("/create_event", methods=['GET', 'POST'])
@login_required
def create_event():
    if current_user.role != "principal":
        flash('Unauthorized access', 'danger')
        return redirect(url_for('core.index'))

    form = EventForm()
    if form.validate_on_submit():
        event = SchoolEvent(
            name=form.name.data,
            date=form.date.data,
            description=form.description.data
        )
        db.session.add(event)
        db.session.commit()
        flash('Event created successfully', 'success')
        return redirect(url_for('principal.create_event'))

    return render_template('create_event.html', form=form)


@principal.route('/view/events', methods=['GET'])
@login_required
def view_events():
    events = SchoolEvent.query.all()
    return render_template('events.html', title='Events', events=events)


@principal.route("/view_school_calendar")
@login_required
def view_school_calendar():
    calendars = SchoolCalendar.query.all()
    return render_template('school_calendar.html', calendars=calendars)


@principal.route("/view_feedbacks", methods=['GET'])
@login_required
def view_feedbacks():

    feedbacks = Message.query.filter_by(receiver_id=current_user.id).all()
    return render_template('view_feedbacks.html', feedbacks=feedbacks)


@principal.route("/send_feedback", methods=['GET', 'POST'])
@login_required
def send_feedback():
    if current_user.role != "principal":
        flash('Unauthorized access', 'danger')
        return redirect(url_for('core.index'))

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


@principal.route("/manage_teachers", methods=['GET', 'POST'])
@login_required
def manage_teachers():
    if current_user.role != "principal":
        flash('Unauthorized access', 'danger')
        return redirect(url_for('core.index'))

    teachers = User.query.filter_by(role='teacher').all()
    return render_template('manage_teachers.html', teachers=teachers)


@principal.route("/create_school_calendar", methods=['GET', 'POST'])
@login_required
def create_school_calendar():
    if current_user.role != "principal":
        flash('Unauthorized access', 'danger')
        return redirect(url_for('core.index'))

    form = SchoolCalendarForm()
    if form.validate_on_submit():
        calendar_entry = SchoolCalendar(
            event_name=form.event_name.data,
            event_date=form.event_date.data
        )
        db.session.add(calendar_entry)
        db.session.commit()
        flash('Calendar entry created successfully', 'success')
        return redirect(url_for('principal.create_school_calendar'))

    return render_template('create_school_calendar.html', form=form)


@principal.route("/add_academic_year", methods=['GET', 'POST'])
@login_required
def add_academic_year():
    if current_user.role != "principal":
        flash('Unauthorized access', 'danger')
        return redirect(url_for('core.index'))

    form = AcademicYearForm()
    if form.validate_on_submit():
        academic_year = AcademicYear(
            year=form.year.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data
        )
        db.session.add(academic_year)
        db.session.commit()
        flash('Academic year added successfully', 'success')
        return redirect(url_for('principal.add_academic_year'))

    return render_template('add_academic_year.html', form=form)


@principal.route("/view/years", methods=['GET'])
@login_required
def view_academic_year():
    years = AcademicYear.query.all()
    return render_template('view_academic_year.html', title='View Classes', years=years)


@principal.route("/add_term", methods=['GET', 'POST'])
@login_required
def add_terms():
    if current_user.role != "principal":
        flash('Unauthorized access', 'danger')
        return redirect(url_for('core.index'))

    form = TermForm()
    # form.academic_year_id.choices = [
    #     (year.id, year.year) for year in AcademicYear.query.all()]
    if form.validate_on_submit():
        term = Term(
            name=form.name.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            # academic_year_id=form.academic_year_id.data
        )
        db.session.add(term)
        db.session.commit()
        flash('Term added successfully', 'success')
        return redirect(url_for('users.dashboard'))

    return render_template('add_term.html', title='Add Subject', form=form)


@principal.route("/view/terms", methods=['GET'])
@login_required
def view_terms():
    terms = Term.query.all()
    return render_template('view_terms.html', title='View Classes', terms=terms)


@principal.route('/principal/create_teacher', methods=['GET', 'POST'])
@login_required
def create_teacher():
    if current_user.role != 'principal':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('core.index'))

    form = CreateTeacherForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(
            first_name=form.first_name.data, last_name=form.last_name.data).first()
        if existing_user:
            flash('Both name already in use. Please use different names.', 'danger')
            return render_template('create_teacher.html', form=form, title='Create Teacher')

        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            # email=form.email.data,
            role='teacher'
        )
        db.session.add(user)
        db.session.commit()
        teacher = Teacher(
            user_id=user.id,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            # email=form.email.data,
            department=form.department.data,
        )
        db.session.add(teacher)
        try:
            db.session.commit()
            flash('Teacher created successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating teacher: {e}', 'danger')

        return redirect(url_for('users.dashboard'))

    return render_template('create_teacher.html', form=form, title='Create Teacher')


@principal.route("/create_class", methods=['GET', 'POST'])
@login_required
def create_class():
    if current_user.role != "principal":
        flash('Unauthorized access', 'danger')
        return redirect(url_for('core.index'))

    form = ClassForm()
    form.teacher.choices = [(teacher.id, f"{teacher.first_name} {teacher.last_name}")
                            for teacher in User.query.filter_by(role='teacher').all()]

    if form.validate_on_submit():
        new_class = Class(
            name=form.name.data,
            section=form.section.data
        )
        db.session.add(new_class)
        db.session.flush()

        teacher = User.query.get(form.teacher.data)
        new_class.teachers.append(teacher)

        db.session.commit()
        flash('Class created successfully', 'success')
        return redirect(url_for('principal.create_class'))

    return render_template('create_class.html', form=form)


@principal.route('/add_student', methods=['GET', 'POST'])
@login_required
def add_student():
    if current_user.role != 'principal':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('core.index'))

    form = AddStudentForm()
    form.class_id.choices = [(c.id, f"{c.name} {c.section}")
                             for c in Class.query.all()]

    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already in use. Please use a different email.', 'danger')
            return render_template('add_student.html', form=form, title='Add Student')

        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            role='student'
        )
        db.session.add(user)
        db.session.commit()

        student = Student(
            user_id=user.id,
            class_id=form.class_id.data
        )
        db.session.add(student)
        db.session.commit()

        flash('Student has been added successfully!', 'success')
        return redirect(url_for('principal.principal_dashboard'))
    return render_template('add_student.html', form=form, title='Add Student')


@principal.route('/create_notifications')
@login_required
def create_notification():
    if current_user.role != "principal":
        flash('Unauthorized access', 'danger')
        return redirect(url_for('core.index'))

    form = NotificationForm()
    if form.validate_on_submit():
        recipient_role = form.recipient_role.data
        recipients = []

        if recipient_role == 'teachers':
            recipients = User.query.filter_by(is_teacher=True).all()
        elif recipient_role == 'students':
            recipients = User.query.filter_by(is_student=True).all()
        elif recipient_role == 'parents':
            recipients = User.query.filter_by(is_parent=True).all()

        for recipient in recipients:
            notification = Notification(
                title=form.title.data,
                message=form.message.data,
                sender_id=current_user.id,
                recipient_role=recipient_role,
                date=datetime.utcnow()
            )
            db.session.add(notification)

        db.session.commit()
        flash('Notification created successfully', 'success')
        return redirect(url_for('principal.create_notification'))

    return render_template('create_notification.html', form=form)


@principal.route("/view_student_grades", methods=['GET'])
@login_required
def view_student_grades():
    if current_user.role != "principal":
        flash('Unauthorized access', 'danger')
        return redirect(url_for('core.index'))

    students = User.query.filter_by(is_student=True).all()
    student_grades = {}

    for student in students:
        grades = Grade.query.filter_by(student_id=student.id).all()
        student_grades[student] = grades

    return render_template('view_student_grades.html', student_grades=student_grades)


@principal.route("/view_student_assignments", methods=['GET'])
@login_required
def view_student_assignments():
    if current_user.role != "principal":
        flash('Unauthorized access', 'danger')
        return redirect(url_for('core.index'))

    students = User.query.filter_by(is_student=True).all()
    student_assignments = {}

    for student in students:
        assignments = Assignment.query.filter_by(
            student_id=student.id).all()
        student_assignments[student] = assignments

    return render_template('view_student_assignments.html', student_assignments=student_assignments)


@principal.route("/view_student_attendance", methods=['GET'])
@login_required
def view_student_attendance():
    if current_user.role != "principal":
        flash('Unauthorized access', 'danger')
        return redirect(url_for('core.index'))

    students = User.query.filter_by(is_student=True).all()
    student_attendance = {}

    for student in students:
        attendance_records = Attendance.query.filter_by(
            student_id=student.id).all()
        student_attendance[student] = attendance_records

    return render_template('view_student_attendance.html', student_attendance=student_attendance)


@principal.route("/add_subject", methods=['GET', 'POST'])
@login_required
def add_subject():
    if current_user.role != 'principal':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('core.index'))

    form = AddSubjectForm()
    if form.validate_on_submit():
        subject = Subject(name=form.name.data)
        db.session.add(subject)
        db.session.commit()
        flash('Subject has been added successfully!', 'success')
        return redirect(url_for('core.index'))

    return render_template('add_subject.html', title='Add Subject', form=form)


# @principal.route('/teacher/student/add', methods=['GET', 'POST'])
# @login_required
# def assign_student():
#     if current_user.role != 'principal':
#         flash('Unauthorized access', 'danger')
#         return redirect(url_for('core.index'))

#     students = User.query.filter_by(role='student').all()
#     classes = Class.query.all()
#     subjects = Subject.query.all()
#     teachers = User.query.filter_by(role='teacher').all()

#     form = MultiAssignForm()

#    form.students.choices = [(student.id, f"{student.last_name}, {student.first_name}") for student in User.query.filter_by(role='student').all()]
#     form.classes.choices = [(class_.id, class_.name) for class_ in Class.query.all()]
#     form.subjects.choices = [(subject.id, subject.name) for subject in Subject.query.all()]
#     form.teachers.choices = [(teacher.id, f"{teacher.last_name}, {teacher.first_name}") for teacher in User.query.filter_by(role='teacher').all()]

#     if form.validate_on_submit():
#         student_ids = form.students.data
#         class_ids = form.classes.data
#         subject_ids = form.subjects.data
#         teacher_ids = form.teachers.data

#         students = Student.query.filter(Student.id.in_(student_ids)).all()
#         classes = Class.query.filter(Class.id.in_(class_ids)).all()
#         subjects = Subject.query.filter(Subject.id.in_(subject_ids)).all()
#         teachers = Teacher.query.filter(Teacher.id.in_(teacher_ids)).all()

#         for student in students:
#             for class_ in classes:
#                 if student not in class_.students:
#                     class_.students.append(student)
#             for subject in subjects:
#                 if student not in subject.students:
#                     subject.students.append(student)
#             for teacher in teachers:
#                 if student not in teacher.students:
#                     teacher.students.append(student)

#         db.session.commit()

#         flash('Students assigned successfully!', 'success')
#         return redirect(url_for('assign_student'))


#     return render_template('assign_teacher.html', teachers=teachers, classes=classes, subjects=subjects, students=students)

@principal.route('/teacher/student/add', methods=['GET', 'POST'])
@login_required
def assign_student():
    if current_user.role != 'principal':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('users.principal_dashboard'))

    students = User.query.filter_by(role='student').all()
    classes = Class.query.all()
    subjects = Subject.query.all()
    teachers = User.query.filter_by(role='teacher').all()

    form = MultiAssignForm()

    form.students.choices = [(student.id, f"{student.last_name}, {student.first_name}")
                             for student in User.query.filter_by(role='student').all()]
    form.classes.choices = [(class_.id, class_.name)
                            for class_ in Class.query.all()]
    form.subjects.choices = [(subject.id, subject.name)
                             for subject in Subject.query.all()]
    form.teachers.choices = [(teacher.id, f"{teacher.last_name}, {teacher.first_name}")
                             for teacher in User.query.filter_by(role='teacher').all()]

    if form.validate_on_submit():
        student_ids = form.students.data
        class_ids = form.classes.data
        subject_ids = form.subjects.data
        teacher_ids = form.teachers.data

        students = Student.query.filter(Student.id.in_(student_ids)).all()
        classes = Class.query.filter(Class.id.in_(class_ids)).all()
        subjects = Subject.query.filter(Subject.id.in_(subject_ids)).all()
        teachers = Teacher.query.filter(Teacher.id.in_(teacher_ids)).all()

        for student in students:
            for class_ in classes:
                if student not in class_.students:
                    class_.students.append(student)
            for subject in subjects:
                if student not in subject.students:
                    subject.students.append(student)
            for teacher in teachers:
                if student not in teacher.students:
                    teacher.students.append(student)

        db.session.commit()

        flash('Students assigned successfully!', 'success')
        return redirect(url_for('users.dashboard'))

    return render_template('assign_student.html', form=form)


@principal.route('/teacher/class', methods=['GET', 'POST'])
@login_required
def assign_teacher():
    if current_user.role != 'principal':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('users.dashboard'))

    form = MultiAssignTeacherForm()

    teachers = db.session.query(User).filter_by(role='teacher').all()
    classes = db.session.query(Class.name).all()
    subjects = db.session.query(Subject.name).all()

    form.classes.choices = [(class_.id, class_.name)
                            for class_ in Class.query.all()]
    form.subjects.choices = [(subject.id, subject.name)
                             for subject in Subject.query.all()]
    form.teachers.choices = [(teacher.id, f"{teacher.last_name}, {teacher.first_name}")
                             for teacher in User.query.filter_by(role='teacher').all()]

    if form.validate_on_submit():

        # student_ids = form.students.data
        class_ids = form.classes.data
        subject_ids = form.subjects.data
        teacher_ids = form.teachers.data

        # students = Student.query.filter(Student.id.in_(student_ids)).all()
        classes = Class.query.filter(Class.id.in_(class_ids)).all()
        subjects = Subject.query.filter(Subject.id.in_(subject_ids)).all()
        teachers = Teacher.query.filter(Teacher.id.in_(teacher_ids)).all()

        for teacher in teachers:
            for class_ in classes:
                if teacher not in class_.students:
                    class_.students.append(teacher)
            for subject in subjects:
                if teacher not in subject.students:
                    subject.students.append(teacher)

        flash('STeachers assigned successfully!', 'success')
        return redirect(url_for('assign'))

    return render_template('assign_teacher.html', teachers=teachers, classes=classes, subjects=subjects, form=form)


@principal.route("/view_classes", methods=['GET'])
@login_required
def view_classes():
    classes = Class.query.all()
    return render_template('view_classes.html', title='View Classes', classes=classes)


@principal.route("/view_teachers", methods=['GET'])
@login_required
def view_teachers():
    # teachers = db.session.query(Teacher).filter(Teacher.id,
    #     Teacher.first_name, Teacher.last_name, Teacher.department).all()
    # return render_template('view_teacher.html', title='View Teachers', teachers=teachers)
    teachers = Teacher.query.all()
    return render_template('view_teacher.html', title='View Teachers', teachers=teachers)


@principal.route("/view_subjects", methods=['GET'])
@login_required
def view_subjects():
    # subjects = db.session.query(Subject).filter(Subject.id, Subject.name).all()
    subjects = Subject.query.all()
    return render_template('view_subjects.html', title='View Subjects', subjects=subjects)


@principal.route('/submissions', methods=['GET', 'POST'])
@login_required
def create_submissions():
    if current_user.role != 'principal':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('users.dashboard'))

    form = SubmissionForm()
    if form.validate_on_submit():
        submission = Submission(
            content=form.content.data,
            assignment_id=form.assignment_id.data,
            student_id=form.student_id.data,
            teacher_id=form.teacher_id.data,
            feedback=form.feedback.data,
            date_submitted=form.data_submitted.data
        )
        db.session.add(submission)
        db.session.commit()
        flash('Sucessfull', 'success')
        return redirect(url_for('principal.view_submissions'))
    return render_template('create_submissions.html', form=form, title='Create Submission')


@principal.route('/create/logs', methods=['GET', 'POST'])
@login_required
def create_logs():
    # if current_user.role != ' principal':
    #     flash('Unauthorized access!', 'danger')
    #     return redirect(url_for('users.dashboard'))
    form = SystemLogForm()
    if form.validate_on_submit():
        new_log = SystemLog(
            action=form.action.data,
            user_id=current_user.id,
            timestamp=datetime.utcnow()
        )
        db.session.add(new_log)
        db.session.commit()
        flash('New log entry created successfully!', 'success')
        return redirect(url_for('principal.view_logs'))
    return render_template('new_log.html', form=form)


@principal.route('/logs')
@login_required
def view_logs():
    logs = SystemLog.query.all()
    return render_template('view_logs.html', logs=logs)


@principal.route('/view/submissions', methods=['GET'])
@login_required
def view_submissions():
    submissions = Submission.query.all()
    return render_template('submissions.html', submissions=submissions)


@principal.route('/principal/profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    if current_user.role != 'principal':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('core.index'))

    form = PrincipalProfileForm(obj=current_user)

    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        if form.password.data:
            current_user.password = generate_password_hash(
                form.password.data).encode('utf-8')
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('users.dashboard'))

    return render_template('principal_update_profile.html', form=form)


@principal.route('/creating/school/name', methods=['GET', 'POST'])
@login_required
def new_school():
    if current_user.role != 'principal':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('core.index'))
    form = SchoolForm()
    form.principal_id.choices = [
        (u.id, f"{u.first_name} {u.last_name}") for u in User.query.filter_by(role='principal').all()]
    if form.validate_on_submit():
        principal = User.query.get(form.principal_id.data)
        new_school = School(
            name=form.name.data,
            logo=form.logo.data,
            contact_info=form.contact_info.data,
            principal=principal
        )
        db.session.add(new_school)
        db.session.commit()
        flash('New school created successfully!', 'success')
        return redirect(url_for('principal.view_schools'))
    return render_template('new_school.html', form=form)


@principal.route('/school/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_school(id):
    if current_user.role != 'principal':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('core.index'))
    school = School.query.get_or_404(id)
    form = SchoolForm(obj=school)
    form.principal.choices = [
        (u.id, f"{u.first_name} {u.last_name}") for u in User.query.filter_by(role='principal').all()]
    if form.validate_on_submit():
        school.name = form.name.data
        school.logo = form.logo.data
        school.contact_info = form.contact_info.data
        principal = principal
        db.session.commit()
        flash('School updated successfully!', 'success')
        return redirect(url_for('principal.view_schools'))
    return render_template('edit_school.html', form=form)


@principal.route('/school')
@login_required
def view_schools():

    schools = School.query.all()
    return render_template('view_schools.html', schools=schools)
