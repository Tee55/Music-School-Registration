from datetime import date
from io import BytesIO
import os
from flask import Flask, request, redirect, render_template, url_for, flash, jsonify, send_from_directory, send_file
import sqlite3

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

import webbrowser
import threading

app = Flask(__name__)
app.secret_key = os.urandom(24)

DATABASE = os.path.join(os.path.dirname(__file__), 'database', 'database.db')

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_database():

    db = get_db()
    c = db.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS students (
              id INTEGER PRIMARY KEY,
              student_id INTEGER UNIQUE, 
              title TEXT,
              f_name TEXT,
              l_name TEXT,
              n_name TEXT,
              address TEXT,
              dob DATE,
              job TEXT,
              email TEXT,
              phone_num TEXT,
              instruments TEXT,

              created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS teachers (
              id INTEGER PRIMARY KEY,
              teacher_id INTEGER UNIQUE, 
              title TEXT,
              f_name TEXT,
              l_name TEXT,
              n_name TEXT,
              address TEXT,
              dob DATE,
              job TEXT,
              email TEXT,
              phone_num TEXT,

              created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS subjects (
              subject_id INTEGER PRIMARY KEY,
              subject_name TEXT
    )''')

    c.execute(
        '''INSERT INTO subjects (subject_name) VALUES ("เปียโน"), ("ไวโอลิน"), ("กีต้าร์"), ("ดนตรีไทย")''')

    c.execute('''CREATE TABLE IF NOT EXISTS levels (
              level_id INTEGER PRIMARY KEY,
              level_name TEXT
    )''')

    c.execute(
        '''INSERT INTO levels (level_name) VALUES ("Beginner"), ("Intermediate"), ("Advanced")''')

    c.execute('''CREATE TABLE IF NOT EXISTS students_subjects (
              id INTEGER PRIMARY KEY,
              student_id INTEGER,
              subject_id INTEGER,
              level_id INTEGER,
              time_left INTEGER DEFAULT 4,
              created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

              FOREIGN KEY (student_id) REFERENCES students(student_id),
              FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS teachers_subjects (
              id INTEGER PRIMARY KEY,
              teacher_id INTEGER, 
              subject_id INTEGER,

              FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id),
              FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
              id INTEGER PRIMARY KEY,
              student_id INTEGER, 
              date DATE,
              FOREIGN KEY (student_id) REFERENCES students(student_id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS payments (
              id INTEGER PRIMARY KEY,
              subject_id INTEGER,
              level_id INTEGER,
              price INTEGER
    )''')

    # Piano
    c.execute('''INSERT INTO payments (subject_id, level_id, price) VALUES (1, 1, 2800), (1, 2, 3200), (1, 3, 3400)''')

    # Violin
    c.execute('''INSERT INTO payments (subject_id, level_id, price) VALUES (2, 1, 2800), (2, 2, 3200), (2, 3, 3400)''')

    # Guitar
    c.execute('''INSERT INTO payments (subject_id, level_id, price) VALUES (3, 1, 2800), (3, 2, 3200), (3, 3, 3400)''')

    # ดนตรีไทย
    c.execute('''INSERT INTO payments (subject_id, level_id, price) VALUES (4, 1, 2800), (4, 2, 3200), (4, 3, 3400)''')

    db.commit()
    db.close()


@app.route('/favicon.ico', methods=['GET', 'POST'])
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/", methods=['GET', 'POST'])
def main():
    if not os.path.exists(DATABASE):
        os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
        create_database()
        
    return render_template('index.html')


@app.route("/students", methods=['GET', 'POST'])
def students():

    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM students")
    students = c.fetchall()
    db.close()

    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM attendance WHERE date = ?", (date.today(),))
    rows = c.fetchall()
    db.close()

    students_attended = []
    for row in rows:
        students_attended.append(row[1])

    return render_template('students.html', students=students, students_attended=students_attended)


@app.route("/teachers", methods=['GET', 'POST'])
def teachers():

    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM teachers")
    teachers = c.fetchall()
    db.close()

    return render_template('teachers.html', teachers=teachers)


@app.route("/add", methods=['GET', 'POST'])
def add():

    if request.method == 'POST':

        category = request.args.get('category')

        if category == "student":
            student_id = request.form['student_id']
            title = request.form['title']
            f_name = request.form['f_name']
            l_name = request.form['l_name']
            n_name = request.form['n_name']
            address = request.form['address']
            dob = request.form['dob']
            job = request.form['job']
            email = request.form['email']
            phone_num = request.form['phone_num']
            instruments = request.form['instruments']

            db = get_db()
            c = db.cursor()
            c.execute('''INSERT INTO students (student_id, title, f_name, l_name, n_name, address, dob, job, email, phone_num, instruments) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (student_id, title, f_name, l_name, n_name, address, dob, job, email, phone_num, instruments))
            db.commit()
            db.close()

            return redirect(url_for('students'))

        elif category == "teacher":
            teacher_id = request.form['teacher_id']
            title = request.form['title']
            f_name = request.form['f_name']
            l_name = request.form['l_name']
            n_name = request.form['n_name']
            address = request.form['address']
            dob = request.form['dob']
            job = request.form['job']
            email = request.form['email']
            phone_num = request.form['phone_num']

            db = get_db()
            c = db.cursor()
            c.execute('''INSERT INTO teachers (teacher_id, title, f_name, l_name, n_name, address, dob, job, email, phone_num) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (teacher_id, title, f_name, l_name, n_name, address, dob, job, email, phone_num))
            db.commit()
            db.close()

            return redirect(url_for('teachers'))

        elif category == "subject":

            subject_name = request.form['subject_name']

            db = get_db()
            c = db.cursor()
            c.execute('''INSERT INTO subjects (subject_name) 
                    VALUES (?)''', (subject_name,))
            db.commit()
            db.close()

            return redirect(url_for('subjects'))
    else:
        return redirect(url_for('students'))


@app.route("/add_student", methods=['GET', 'POST'])
def add_student():
    return render_template('add_student.html')


@app.route("/add_teacher", methods=['GET', 'POST'])
def add_teacher():
    return render_template('add_teacher.html')


@app.route("/add_subject", methods=['GET', 'POST'])
def add_subject():
    return render_template('add_subject.html')


@app.route("/registration", methods=['GET', 'POST'])
def registration():

    if request.method == 'POST':
        student_id = request.form['student_id']
        subject_id = request.form['subject_id']
        level_id = request.form['level_id']
        time_left = request.form['time_left']

        db = get_db()
        c = db.cursor()
        c.execute("INSERT INTO students_subjects (student_id, subject_id, level_id, time_left) VALUES (?, ?, ?, ?)",
                  (student_id, subject_id, level_id, time_left))
        db.commit()
        db.close()

        return redirect(url_for('recipt', student_id=student_id, subject_id=subject_id, level_id=level_id))

    student_id = request.args.get('student_id')

    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
    student = c.fetchone()
    db.close()

    if not student:
        flash("ไม่มีนักเรียนไอดีนี้", "warning")
        return redirect(url_for('students'))

    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM subjects")
    subjects = c.fetchall()
    db.close()

    if len(subjects) == 0:
        flash("ไม่มีรายวิชาที่สอน", "warning")
        return redirect(url_for('students'))

    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM levels")
    levels = c.fetchall()
    db.close()

    if len(levels) == 0:
        flash("ไม่มีข้อมูลระดับ", "warning")
        return redirect(url_for('students'))

    return render_template('registration.html', student=student, subjects=subjects, levels=levels)

@app.route("/history/<student_id>", methods=['GET', 'POST'])
def history(student_id):

    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
    student = c.fetchone()
    db.close()

    if not student:
        flash("ไม่มีนักเรียนไอดีนี้", "warning")
        return redirect(url_for('students'))
    

    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM students_subjects JOIN subjects JOIN levels ON students_subjects.subject_id = subjects.subject_id AND students_subjects.level_id = levels.level_id WHERE students_subjects.student_id = ?", (student_id,))
    history = c.fetchall()
    db.close()

    return render_template('history.html', student=student, history=history)

@app.route("/subjects", methods=['GET', 'POST'])
def subjects():

    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM subjects")
    subjects = c.fetchall()
    db.close()

    return render_template('subjects.html', subjects=subjects)


@app.route("/recipt/<student_id>/<subject_id>/<level_id>", methods=['GET', 'POST'])
def recipt(student_id, subject_id, level_id):

    # Get student data
    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
    student = c.fetchone()
    db.close()

    if not student:
        flash("ไม่มีนักเรียนไอดีนี้", "warning")
        return redirect(url_for('students'))

    # Get registration data
    db = get_db()
    c = db.cursor()
    c.execute(
        "SELECT * FROM students_subjects WHERE student_id = ? and subject_id = ? and level_id = ?", (student_id, subject_id, level_id))
    data = c.fetchone()
    db.close()

    if not data:
        flash("ไม่มีใบเสร็จตามข้อมูลดังกล่าว", "warning")
        return redirect(url_for('students'))

    time_left = data[4]

    # Get subject data
    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM subjects WHERE subject_id = ?", (subject_id,))
    subject = c.fetchone()
    db.close()

    if not subject:
        flash("ไม่มีรายวิชานี้", "warning")
        return redirect(url_for('students'))

    # Get payment data
    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM payments WHERE subject_id = ? and level_id = ?",
              (subject_id, level_id))
    payment = c.fetchone()
    db.close()

    if not payment:
        flash("ไม่มีข้อมูลการเงินของวิชานี้", "warning")
        return redirect(url_for('students'))

    if time_left % 4 == 0:
        pay_amount = (time_left / 4) * payment[3]
    else:
        flash("จำนวนครั้งที่จะเรียนหาร 4 ไม่ลงตัว", "warning")
        return redirect(url_for('students'))

    return render_template('recipt.html', student=student, subject=subject, time_left=time_left, pay_amount=pay_amount)


@app.route("/attendance", methods=['GET', 'POST'])
def attendance():

    if request.method == 'POST':
        student_id = request.form['student_id']

        # Check if attendance is already recorded
        db = get_db()
        c = db.cursor()
        c.execute("SELECT * FROM attendance WHERE student_id = ? AND date = ?",
                  (student_id, date.today()))
        attendance = c.fetchone()
        db.close()

        if attendance:
            # Remove attendance
            db = get_db()
            c = db.cursor()
            c.execute("DELETE FROM attendance WHERE student_id = ? AND date = ?",
                      (student_id, date.today()))
            c.execute(
                '''UPDATE students_subjects SET time_left = time_left + 1 WHERE student_id = ?''', (student_id, ))
            db.commit()
            db.close()

            return jsonify({'message': 'success'})

        else:
            # Add attendance
            db = get_db()
            c = db.cursor()
            c.execute("INSERT INTO attendance (student_id, date) VALUES (?, ?)",
                      (student_id, date.today()))
            c.execute(
                '''UPDATE students_subjects SET time_left = time_left - 1 WHERE student_id = ?''', (student_id, ))
            db.commit()
            db.close()

            return jsonify({'message': 'success'})

@app.route("/attendances/<student_id>", methods=['GET', 'POST'])
def attendances(student_id):

    # Get student
    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
    student = c.fetchone()
    db.close()

    if not student:
        flash("ไม่มีนักเรียนไอดีนี้", "warning")
        return redirect(url_for('students'))
        
    # Get attendance history
    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM attendance WHERE student_id = ?", (student_id,))
    attendances = c.fetchall()
    db.close()

    if len(attendances) == 0:
        flash("ไม่มีประวัติการเข้าเรียน", "warning")
        return redirect(url_for('students'))
              
    return render_template('attendances.html', student=student, attendances=attendances)

@app.route("/attendances/<attendance_id>/delete", methods=['GET', 'POST'])
def attendance_delete(attendance_id):

    # Delete attendance
    db = get_db()
    c = db.cursor()
    c.execute("DELETE FROM attendance WHERE id = ?", (attendance_id,))
    db.commit()
    db.close()

    flash("ลบประวัติการเข้าเรียนเรียบร้อยแล้ว", "success")
    return redirect(url_for('students'))

@app.route('/generate-pdf', methods=['GET', 'POST'])
def generate_pdf():

    if request.method == 'POST':

        title = request.form['title']
        f_name = request.form['f_name']
        l_name = request.form['l_name']
        subject = request.form['subject']
        time_left = request.form['time_left']
        pay_amount = request.form['pay_amount']

        buffer = BytesIO()
        
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        pdfmetrics.registerFont(TTFont('THSarabunNEW', os.path.join(os.path.dirname(__file__), 'fonts', 'THSarabunNew.ttf')))
        
        c.setFont("THSarabunNEW", 18)
        c.drawCentredString(width / 2, height - 100, "ใบเสร็จรับเงิน")
        
        c.setFont("THSarabunNEW", 10)
        c.drawCentredString(width / 2, height - 120, "RECEIPT")

        c.setFont("THSarabunNEW", 20)
        c.drawCentredString(width / 2, height - 140, "ศุภนิจการดนตรี")

        c.setFont("THSarabunNEW", 10)
        c.drawCentredString(width / 2, height - 150, "55/9 ถนนวัชรพล แขวงท่าแร้ง เขตบางเขน กรุงเทพฯ")
        c.drawCentredString(width / 2, height - 160, "โทร. 02-948 2644")
        
        c.setFont("THSarabunNEW", 16)
        c.drawCentredString(width / 2, height - 180, "SUPANIT MUSIC ACADEMY")
        
        c.setFont("THSarabunNEW", 12)
        c.drawString(400, height - 200, "วันที่:")
        c.drawString(450, height - 200, date.today().strftime("%d/%m/%Y"))
        
        c.drawString(400, height - 220, "เลขที่:")
        c.drawString(450, height - 220, "5410090863")
        
        c.setFont("THSarabunNEW", 12)
        c.drawString(60, height - 240, "ได้รับเงินจาก:")
        c.drawString(120, height - 240, title + " " + f_name + " " + l_name)
        
        c.setFont("THSarabunNEW", 12)
        c.drawString(200, height - 240, "วิชา:")
        c.drawString(260, height - 240, subject)
        
        c.rect(50, height - 480, width - 100, 450, stroke=1, fill=0)
        
        c.showPage()
        c.save()
        
        buffer.seek(0)
        
        return send_file(buffer, as_attachment=True, download_name='receipt.pdf', mimetype='application/pdf')

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

if __name__ == '__main__':
    threading.Timer(1, open_browser).start()
    app.run()
