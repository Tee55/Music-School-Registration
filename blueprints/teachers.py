from flask import Blueprint, request, render_template, redirect, url_for, flash
from extensions import db
from models.registration import Registration
from models.teacher import Teacher
import datetime

teachers_bp = Blueprint('teachers', __name__)

@teachers_bp.route('/', methods=['GET'])
def list_teachers():
    teachers = Teacher.query.all()

    # Get the current date
    today = datetime.date.today()

    # Calculate the past 5 months
    past_months = []

    # Add the current month first
    past_months.append({
        'year': today.year,
        'month': today.month,
        'thai_year': today.year + 543  # Convert to Thai year
    })

    for _ in range(4):
        # Subtract months
        first = today.replace(day=1)
        past_month = first - datetime.timedelta(days=1)
        today = past_month
        past_months.append({
            'year': past_month.year,
            'month': past_month.month,
            'thai_year': past_month.year + 543  # Convert to Thai year
        })

    # Calculate total payment for all teachers per month
    total_payments = []
    for month_info in past_months:
        total_payment_for_month = sum(
            teacher.calculate_payment(month_info['year'], month_info['month'])[0] for teacher in teachers
        )
        total_payments.append({
            'date': "{}/{}".format(month_info['month'], month_info['thai_year']),
            'total_payment': total_payment_for_month
        })
        
    return render_template('teachers/list.html', teachers=teachers, total_payments=total_payments)


@teachers_bp.route('/<int:teacher_id>', methods=['GET'])
def teacher_detail(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    return render_template('teachers/detail.html', teacher=teacher)


@teachers_bp.route('/add', methods=['POST'])
def add_teacher():
    teacher_data = {
        'title': request.form['title'],
        'f_thai_name': request.form['f_thai_name'],
        'l_thai_name': request.form['l_thai_name'],
        'f_eng_name': request.form['f_eng_name'],
        'l_eng_name': request.form['l_eng_name'],

        'email': request.form['email'],
        'phone_num': request.form['phone_num'],

        'payment_ratio': float(request.form['payment_ratio'])
    }

    new_teacher = Teacher(**teacher_data)
    db.session.add(new_teacher)
    db.session.commit()

    flash('Teacher added successfully!', 'success')
    return redirect(url_for('teachers.list_teachers'))


@teachers_bp.route('/edit/<int:teacher_id>', methods=['POST'])
def edit_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)

    teacher.title = request.form['title']
    teacher.f_thai_name = request.form['f_thai_name']
    teacher.l_thai_name = request.form['l_thai_name']
    teacher.f_eng_name = request.form['f_eng_name']
    teacher.l_eng_name = request.form['l_eng_name']

    teacher.email = request.form['email']
    teacher.phone_num = request.form['phone_num']

    teacher.payment_ratio = float(request.form['payment_ratio'])

    db.session.commit()

    flash('Teacher updated successfully!', 'success')
    return redirect(url_for('teachers.list_teachers'))



@teachers_bp.route('/delete/<int:teacher_id>', methods=['POST'])
def delete_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)

    # Set the teacher_id in related registrations to NULL
    registrations = Registration.query.filter_by(teacher_id=teacher.teacher_id).all()
    for registration in registrations:
        registration.teacher_id = None  # Set the teacher_id to NULL
    db.session.commit()

    db.session.delete(teacher)
    db.session.commit()

    flash('Teacher deleted successfully!', 'success')
    return redirect(url_for('teachers.list_teachers'))
