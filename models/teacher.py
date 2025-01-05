from extensions import db
from datetime import datetime

class Teacher(db.Model):
    __tablename__ = 'teachers'
    __table_args__ = {'extend_existing': True}

    teacher_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Name
    title = db.Column(db.String(10), nullable=False)
    f_thai_name = db.Column(db.String(100), nullable=False)
    l_thai_name = db.Column(db.String(100), nullable=False)
    f_eng_name = db.Column(db.String(100), nullable=True)
    l_eng_name = db.Column(db.String(100), nullable=True)

    # Personal details
    email = db.Column(db.String(120), nullable=True)
    phone_num = db.Column(db.String(20), nullable=True)
    
    # How much of the payment the teacher receives
    payment_ratio = db.Column(db.Float, nullable=False, default=0.0)

    # Timestamps
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    # Define the relationship with Registration
    registrations = db.relationship('Registration', back_populates='teacher')

    def calculate_payment(self, year=None, month=None):
        """
        Calculate the payment for the teacher for a specific month and year.
        Defaults to the current month if year and month are not provided.
        Returns a detailed breakdown of payments by subject, including attendance dates.
        """
        if year is None or month is None:
            now = datetime.now()
            year = year or now.year
            month = month or now.month

        # Adjust year to Thai year
        year = year + 543

        payment_breakdown = []
        total_payment = 0

        for registration in self.registrations:
            # Filter attendances for the given month and year
            attendances = [
                attendance.date for attendance in registration.attendances
                if attendance.date.year == year and attendance.date.month == month
            ]
            attendance_count = len(attendances)

            # Calculate payment for this registration
            payment = attendance_count * ((registration.price * self.payment_ratio) // 4)
            total_payment += payment

            payment_breakdown.append({
                'student_name': (registration.student.f_thai_name + ' ' + registration.student.l_thai_name) if registration.student else 'Unknown Student',
                'subject_name': registration.subject_name,
                'calculated_payment': payment,
                'attendance_dates': attendances
            })

        return total_payment, payment_breakdown