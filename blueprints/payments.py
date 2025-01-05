from flask import Blueprint, render_template
from models.teacher import Teacher
from datetime import datetime

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/<int:teacher_id>', methods=['GET'])
def list_payments(teacher_id):
    # Fetch the teacher by ID
    teacher = Teacher.query.get_or_404(teacher_id)

    # Get the current month and year
    now = datetime.now()
    year = now.year
    month = now.month

    # Calculate the total payment for this month
    total_payment, payment_breakdown = teacher.calculate_payment(year=year, month=month)

    return render_template('payments/list.html', teacher=teacher, total_payment=total_payment, payment_breakdown=payment_breakdown)