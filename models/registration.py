from extensions import db

class Registration(db.Model):
    __tablename__ = 'registrations'
    __table_args__ = {'extend_existing': True}

    registration_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.teacher_id'), nullable=True)

    subject_name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)

    times_total = db.Column(db.Integer, nullable=False)
    schedule = db.Column(db.String, nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    # Relationships (assuming related models exist with proper back_populates or similar)
    student = db.relationship('Student', back_populates='registrations')
    teacher = db.relationship('Teacher', back_populates='registrations')
    attendances = db.relationship('Attendance', back_populates='registration')

    def count_attendances(self):
        return len(self.attendances)