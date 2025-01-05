from extensions import db

class Student(db.Model):
    __tablename__ = 'students'
    __table_args__ = {'extend_existing': True}

    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Registration details
    register_date = db.Column(db.Date, nullable=False)

    # Name
    title = db.Column(db.String(10), nullable=False)
    f_thai_name = db.Column(db.String(100), nullable=False)
    l_thai_name = db.Column(db.String(100), nullable=False)
    f_eng_name = db.Column(db.String(100), nullable=True)
    l_eng_name = db.Column(db.String(100), nullable=True)
    n_name = db.Column(db.String(100), nullable=True)

    # Personal details
    address = db.Column(db.String(255), nullable=True)
    dob = db.Column(db.Date, nullable=True)
    job = db.Column(db.String(100), nullable=True)                      
    email = db.Column(db.String(120), nullable=True)
    phone_num = db.Column(db.String(20), nullable=True)

    # Family details
    family_title = db.Column(db.String(10), nullable=True)
    family_f_thai_name = db.Column(db.String(100), nullable=True)
    family_l_thai_name = db.Column(db.String(100), nullable=True)
    family_f_eng_name = db.Column(db.String(100), nullable=True)
    family_l_eng_name = db.Column(db.String(100), nullable=True)
    family_relation = db.Column(db.String(100), nullable=True)

    # Music details
    instruments = db.Column(db.String(255), nullable=True)

    # Timestamps
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    # Define the relationship with Registration
    registrations = db.relationship('Registration', back_populates='student')
    attendances = db.relationship('Attendance', back_populates='student')
