from flask import Blueprint, redirect, render_template, request, flash, url_for
from datetime import datetime
from extensions import db
from models.attendance import Attendance
from models.student import Student

attendances_bp = Blueprint('attendances', __name__)

@attendances_bp.route('/<student_id>', methods=['GET', 'POST'])
def manage_attendances(student_id):

    # Fetch the student
    student = Student.query.get(student_id)
    if not student:
        flash("No student found with this ID", "warning")
        return redirect(url_for('attendance.manage_attendances'))
    
    if request.method == 'POST':
        registration_id = request.form['registration_id'] # Retrieve selected subject name
        attended_dates = request.form.getlist("attended_date[]")  # Retrieve the list of dates

        for attendance_date in attended_dates:
            attendance_date = datetime.strptime(attendance_date, '%d/%m/%Y').date()
            add_attendance(student_id, registration_id, attendance_date)

        return redirect(url_for('attendances.manage_attendances', student_id=student_id))

    # Fetch and return attendance history
    attendances = Attendance.query.filter_by(student_id=student_id).all()

    # Fetch and return registrations
    registrations = student.registrations

    return render_template('attendances/list.html', attendances=attendances, registrations=registrations, student=student)

def add_attendance(student_id, registration_id, attendance_date):
    
    """
    Adds an attendance record for the specified student, subject, level, and date.
    """
    # Check if attendance already exists
    existing_attendance = Attendance.query.filter_by(
        student_id=student_id,
        registration_id=registration_id,
        date=attendance_date
    ).first()

    if existing_attendance:
        flash(f"Attendance already recorded for {attendance_date}", "warning")
        return False

    # Create and save new attendance record
    attendance = Attendance(
        student_id=student_id,
        registration_id=registration_id,
        date=attendance_date
    )

    db.session.add(attendance)
    db.session.commit()

@attendances_bp.route('/delete/<int:attendance_id>', methods=['POST'])
def delete_attendance(attendance_id):
    """
    Handle the deletion of a attendance by ID.
    """
    attendance = Attendance.query.get(attendance_id)
    if not attendance:
        flash("Attendance not found", "danger")
        return redirect(url_for('attendances.manage_attendances', student_id=attendance.student_id))

    try:
        db.session.delete(attendance)
        db.session.commit()
        flash("Registration deleted successfully", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred while deleting: {str(e)}", "danger")

    return redirect(url_for('attendances.manage_attendances', student_id=attendance.student_id))