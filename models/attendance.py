from extensions import db

class Attendance(db.Model):
    __tablename__ = 'attendances'
    __table_args__ = {'extend_existing': True}

    attendance_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=True)
    registration_id = db.Column(db.Integer, db.ForeignKey('registrations.registration_id'), nullable=True)
    
    date = db.Column(db.Date, nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    # Relationships
    student = db.relationship('Student', back_populates='attendances')
    registration = db.relationship('Registration', back_populates='attendances')