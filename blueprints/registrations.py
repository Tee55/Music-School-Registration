from flask import Blueprint, request, render_template, redirect, url_for, flash
from extensions import db
from models.attendance import Attendance
from models.registration import Registration
from models.student import Student
from models.teacher import Teacher

registrations_bp = Blueprint('registrations', __name__)


@registrations_bp.route('/<int:student_id>', methods=['GET', 'POST'])
def manage_registrations(student_id):
    # Fetch the student
    student = Student.query.get(student_id)
    if not student:
        flash("No student found with this ID", "warning")
        return redirect(url_for('students.manage_students'))

    if request.method == 'POST':
        return handle_registration_creation(student_id)

    # Fetch existing registrations
    registrations = Registration.query.filter_by(student_id=student_id).all()

    # Fetch subjects, teachers, and levels for dropdowns
    teachers = Teacher.query.all()

    return render_template(
        'registrations/list.html',
        student=student,
        registrations=registrations,
        teachers=teachers,
    )

# Show individual registration details
@registrations_bp.route('/detail/<int:registration_id>', methods=['GET'])
def registration_detail(registration_id):
    registration = Registration.query.get_or_404(registration_id)

    # Fetch subjects, teachers, and levels for dropdowns
    teachers = Teacher.query.all()

    return render_template('registrations/detail.html', registration=registration, teachers=teachers)

def handle_registration_creation(student_id):
    """
    Handle the creation of a new registration.
    """
    try:
        registration_data = {
            'student_id': student_id,
            'teacher_id': int(request.form['teacher_id']),

            'subject_name': request.form['subject_name'],
            'price': int(request.form['price']),

            'times_total': int(request.form['times']),
            'schedule': request.form['schedule'],
        }

        # Create new registration
        registration = Registration(**registration_data)
        db.session.add(registration)
        db.session.commit()

        flash("Registration added successfully", "success")
        return redirect(url_for('registrations.manage_registrations', student_id=student_id))
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred: {str(e)}", "danger")
        return redirect(request.url)

@registrations_bp.route('/edit/<int:registration_id>', methods=['POST'])
def edit_registration(registration_id):
    """
    Handle the editing of a registration by its ID.
    """
    registration = Registration.query.get(registration_id)
    if not registration:
        flash("Registration not found", "danger")
        return redirect(url_for('registrations.manage_registrations', student_id=registration.student_id))

    try:
        registration.teacher_id = int(request.form['teacher_id'])
        registration.subject_name = request.form['subject_name']
        registration.price = int(request.form['price'])
        registration.times_left = int(request.form['times'])
        registration.times_total = int(request.form['times'])
        registration.schedule = request.form['schedule']

        db.session.commit()
        flash("Registration updated successfully", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while updating: {str(e)}", "danger")

    return redirect(url_for('registrations.manage_registrations', student_id=registration.student_id))

@registrations_bp.route('/receipt/<int:registration_id>', methods=['POST'])
def receipt_form(registration_id):
    registration = Registration.query.get(registration_id)
    if not registration:
        flash("Registration not found", "danger")
        return redirect(url_for('registrations.manage_registrations', student_id=registration.student_id))
    
    # Calculate the payment
    payment = registration.price * registration.times_total // 4

    return render_template('registrations/receipt.html', registration=registration, student=registration.student, payment=payment)


@registrations_bp.route('/delete/<int:registration_id>', methods=['POST'])
def delete_registration(registration_id):
    """
    Handle the deletion of a registration by its ID.
    """
    registration = Registration.query.get(registration_id)
    if not registration:
        flash("Registration not found", "danger")
        return redirect(url_for('registrations.manage_registrations', student_id=registration.student_id))

    try:

        # Set the registration_id in related attendances to NULL
        attendances = Attendance.query.filter_by(registration_id=registration.registration_id).all()
        for attendance in attendances:
            attendance.registration_id = None  # Set the student_id to NULL
        db.session.commit()

        db.session.delete(registration)
        db.session.commit()
        flash("Registration deleted successfully", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while deleting: {str(e)}", "danger")

    return redirect(url_for('registrations.manage_registrations', student_id=registration.student_id))
