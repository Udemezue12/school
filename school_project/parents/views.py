from flask import render_template, url_for, flash, redirect, request, abort, Blueprint
from flask_login import current_user, login_required
from werkzeug.security import generate_password_hash
from datetime import datetime
from school_project.models import User, Student, Attendance, Grade, Message, ForumThread, ForumPost, Resource, Result, Assignment, Notification, Communication, SchoolCalendar
from school_project.forms import StudentForm, AttendanceForm, GradeForm, MessageForm, ForumThreadForm, ForumPostForm, AnnouncementForm, ResourceForm, CheckResultForm, ParentProfileForm
from school_project.database import db, mail

parent = Blueprint('parent', __name__)


def get_child_communication(student_id):
    return Communication.query.filter_by(student_id=student_id).all()

# @parent.route("/dashboard")
# @login_required
# def dashboard():
#     # Assuming a one-to-many relationship between User and Student
#     students = current_user.student
#     return render_template('dashboard.html', students=students)


@parent.route('/parent/dashboard')
@login_required
def parent_dashboard():
    return render_template('parent_dashboard.html')


@parent.route("/child/<int:student_id>")
@login_required
def child_details(student_id):
    student = Student.query.get_or_404(student_id)
    if student.parent_id != current_user.id:
        abort(403)

    communication = get_child_communication(student_id)

    attendance = Attendance.query.filter_by(student_id=student_id).all()
    grades = Grade.query.filter_by(student_id=student_id).all()
    messages = Message.query.filter_by(receiver_id=current_user.id).all()
    child_assignments = Assignment.query.filter_by(
        student_id=student_id).all()  # Assuming an Assignment model
    child_upcoming_assignments = [
        a for a in child_upcoming_assignments if a.deadline > datetime.utcnow()]

    return render_template('child_details.html', student=student, attendance=attendance, grades=grades, messages=messages, child_assignments=child_assignments, child_upcoming_assignments=child_upcoming_assignments)


# @parent.route("/school_calendar")
# @login_required
# def school_calendar():
#     calendar_events = Notification.query.all()
#     return render_template('school_calendar.html', calendar_events=calendar_events)


@parent.route("/upcoming_assignment/<int:student_id>")
@login_required
def upcoming_assignment(student_id):
    student = Student.query.get_or_404(student_id)
    if student.parent_id != current_user.id:
        abort(403)

    assignments = Assignment.query.filter_by(
        student_id=student_id).all()  # Assuming an Assignment model
    upcoming_assignments = [
        a for a in assignments if a.deadline > datetime.utcnow()]

    return render_template('upcoming_assignments.html', student=student, upcoming_assignments=upcoming_assignments)


@parent.route('/parent/profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    if current_user.role != 'parent':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('core.index'))

    form = ParentProfileForm(obj=current_user)

    if form.validate_on_submit():
        current_user.email = form.email.data
        if form.password.data:
            current_user.password = generate_password_hash(
                form.password.data).decode('utf-8')
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('users.dashboard'))

    return render_template('parent_update_profile.html', form=form)


@parent.route("/view_messages")
@login_required
def view_messages():
    messages = Message.query.filter_by(receiver_id=current_user.id).all()
    return render_template('view_messages.html', messages=messages)


@parent.route("/assignments/<int:student_id>")
@login_required
def assignments(student_id):
    student = Student.query.get_or_404(student_id)
    if student.parent_id != current_user.id:
        abort(403)

    assignment = Assignment.query.filter_by(student_id=student_id).all()
    return render_template('show_assignments.html', student=student, assignment=assignment)


@parent.route("/message", methods=['GET', 'POST'])
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


@parent.route("/forum", methods=['GET', 'POST'])
@login_required
def create_thread():
    form = ForumThreadForm()
    if form.validate_on_submit():
        thread = ForumThread(title=form.title.data, author_id=current_user.id)
        db.session.add(thread)
        db.session.commit()
        flash('Forum thread has been created!', 'success')
        return redirect(url_for('parent.dashboard'))

    threads = ForumThread.query.all()
    return render_template('forum.html', form=form, threads=threads)


@parent.route("/post_to_thread/<int:thread_id>", methods=['GET', 'POST'])
@login_required
def post_to_thread(thread_id):
    thread = ForumThread.query.get_or_404(thread_id)
    form = ForumPostForm()
    if form.validate_on_submit():
        post = ForumPost(content=form.content.data,
                         author_id=current_user.id, thread_id=thread.id)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been added!', 'success')
        return redirect(url_for('parent.forum_thread', thread_id=thread.id))

    posts = ForumPost.query.filter_by(thread_id=thread.id).all()
    return render_template('forum_thread.html', thread=thread, form=form, posts=posts)


@parent.route("/view_thread_posts/<int:thread_id>")
@login_required
def view_thread_posts(thread_id):
    thread = ForumThread.query.get_or_404(thread_id)
    posts = ForumPost.query.filter_by(thread_id=thread.id).all()
    return render_template('view_thread_posts.html', thread=thread, posts=posts)


@parent.route('/view_threads')
@login_required
def view_threads():
    threads = ForumThread.query.all()
    return render_template('view_threads.html', threads=threads)


@parent.route("/check_result", methods=['GET', 'POST'])
@login_required
def check_result():
    form = CheckResultForm()
    if form.validate_on_submit():
        result_pin = Result.query.filter_by(
            pin=form.pin.data, student_id=current_user.students.id, used=False).first()
        if result_pin:
            result_pin.used = True
            db.session.commit()
            grades = Grade.query.filter_by(
                student_id=current_user.students.id).all()
            return render_template('result_sheet.html', grades=grades)
        else:
            flash('Invalid or already used PIN.', 'danger')

    return render_template('check_result.html', form=form)


@parent.route('/teacher/calendar')
@login_required
def school_calendars():
    events = SchoolCalendar.query.all()
    return render_template('school_calendar.html', events=events)
