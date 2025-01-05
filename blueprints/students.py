from flask import Blueprint, request, render_template, redirect, url_for, flash
from extensions import db
from models.attendance import Attendance
from models.registration import Registration
from models.student import Student
from datetime import datetime

students_bp = Blueprint('students', __name__)

def convert_date(date_str):
    try:
        # Assuming the input is in the format 'DD/MM/YYYY'
        # Adjust year if using Buddhist calendar
        date_parts = date_str.split("/")
        day, month, year = map(int, date_parts)
        if year > 2500:  # Adjust from Buddhist to Gregorian calendar
            year -= 543
        return datetime(year, month, day).date()
    except ValueError:
        return None

# List all students
@students_bp.route('/', methods=['GET'])
def list_students():
    students = Student.query.all()
    return render_template('students/list.html', students=students)


# Show individual student details
@students_bp.route('/<int:student_id>', methods=['GET'])
def student_detail(student_id):
    student = Student.query.get_or_404(student_id)
    return render_template('students/detail.html', student=student)


# Add new student
@students_bp.route('/add', methods=['POST'])
def add_student():
    # Extract form data
    student_data = {

        'register_date': convert_date(request.form['register_date']),

        'title': request.form['title'],
        'f_thai_name': request.form['f_thai_name'],
        'l_thai_name': request.form['l_thai_name'],
        'f_eng_name': request.form['f_eng_name'],
        'l_eng_name': request.form['l_eng_name'],
        'n_name': request.form['n_name'],

        'family_title': request.form['family_title'],
        'family_f_thai_name': request.form['family_f_thai_name'],
        'family_l_thai_name': request.form['family_l_thai_name'],
        'family_f_eng_name': request.form['family_f_eng_name'],
        'family_l_eng_name': request.form['family_l_eng_name'],

        'address': request.form['address'],
        'dob': convert_date(request.form['dob']),
        'job': request.form['job'],
        'email': request.form['email'],
        'phone_num': request.form['phone_num'],

        'instruments': request.form['instruments'],
    }

    # Create and save the new student
    new_student = Student(**student_data)
    db.session.add(new_student)
    db.session.commit()

    flash('Student added successfully!', 'success')
    return redirect(url_for('students.list_students'))



# Edit existing student
@students_bp.route('/edit/<int:student_id>', methods=['POST'])
def edit_student(student_id):
    student = Student.query.get_or_404(student_id)

    # Update student data from form
    student.register_date = convert_date(request.form['register_date'])
    student.title = request.form['title']
    student.f_thai_name = request.form['f_thai_name']
    student.l_thai_name = request.form['l_thai_name']
    student.f_eng_name = request.form['f_eng_name']
    student.l_eng_name = request.form['l_eng_name']
    student.n_name = request.form['n_name']

    student.address = request.form['address']
    student.dob = convert_date(request.form['dob'])
    student.job = request.form['job']
    student.email = request.form['email']
    student.phone_num = request.form['phone_num']

    student.instruments = request.form['instruments']

    db.session.commit()

    flash('Student updated successfully!', 'success')
    return redirect(url_for('students.list_students'))


# Delete student
@students_bp.route('/delete/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)

    # Set the student_id in related registrations to NULL
    registrations = Registration.query.filter_by(student_id=student.student_id).all()
    for registration in registrations:
        registration.student_id = None  # Set the student_id to NULL
    db.session.commit()

    # Set the student_id in related attendances to NULL
    attendances = Attendance.query.filter_by(student_id=student.student_id).all()
    for attendance in attendances:
        attendance.student_id = None  # Set the student_id to NULL
    db.session.commit()

    db.session.delete(student)
    db.session.commit()

    flash('Student deleted successfully!', 'success')
    return redirect(url_for('students.list_students'))
