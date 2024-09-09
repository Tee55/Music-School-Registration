from datetime import date
from datetime import datetime
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

DATABASE = './database.db'


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_database():

    db = get_db()
    c = db.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS students (
              student_id INTEGER PRIMARY KEY UNIQUE, 
              title TEXT NOT NULL,
              f_name TEXT NOT NULL,
              l_name TEXT NOT NULL,
              n_name TEXT,
              address TEXT,
              dob DATE,
              job TEXT,
              email TEXT,
              phone_num TEXT,
              instruments TEXT,

              family_title TEXT,
              family_f_name TEXT,
              family_l_name TEXT,
              family_relationship TEXT,
              
              created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS teachers (
              teacher_id INTEGER PRIMARY KEY UNIQUE, 
              title TEXT NOT NULL,
              f_name TEXT NOT NULL,
              l_name TEXT NOT NULL,
              n_name TEXT,
              address TEXT,
              dob DATE,
              job TEXT,
              email TEXT,
              phone_num TEXT,

              payment_ratio REAL,
              payment INTEGER DEFAULT 0,

              created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS subjects (
              subject_id INTEGER PRIMARY KEY,
              subject_name TEXT
    )''')

    c.execute(
        '''INSERT INTO subjects (subject_name) VALUES ("เปียโนเด็กพื้นฐาน"), ("เปียโนเด็กเดี่ยว (30 นาที)"), ("เปียโนเด็กเดี่ยว (45 นาที)"), ("เปียโนเด็กเดี่ยว (1 ชั่วโมง)"), ("เปียโน"), ("ไวโอลิน"), ("กีต้าร์"), ("ดนตรีไทย")''')

    c.execute('''CREATE TABLE IF NOT EXISTS levels (
              level_id INTEGER PRIMARY KEY,
              level_name TEXT
    )''')

    c.execute(
        '''INSERT INTO levels (level_name) VALUES ("Beginner"), ("Intermediate"), ("Advanced")''')

    c.execute('''CREATE TABLE IF NOT EXISTS registrations (
              registration_id INTEGER PRIMARY KEY,
              student_id INTEGER,
              subject_id INTEGER,
              level_id INTEGER,
              teacher_id INTEGER,
              time_left INTEGER,
              times INTEGER,
              schedule TEXT NOT NULL,
              created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

              FOREIGN KEY (student_id) REFERENCES students(student_id),
              FOREIGN KEY (subject_id) REFERENCES subjects(subject_id),
              FOREIGN KEY (level_id) REFERENCES levels(level_id),
              FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id)
              
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS attendances (
              attendance_id INTEGER PRIMARY KEY,
              student_id INTEGER, 
              subject_id INTEGER,
              level_id INTEGER,
              date DATE,
              created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

              FOREIGN KEY (student_id) REFERENCES students(student_id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS prices (
              price_id INTEGER PRIMARY KEY,
              subject_id INTEGER,
              level_id INTEGER,
              price INTEGER,

              FOREIGN KEY (subject_id) REFERENCES subjects(subject_id),
              FOREIGN KEY (level_id) REFERENCES levels(level_id)
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS payments (
        payment_id INTEGER PRIMARY KEY,
        teacher_id INTEGER,
        attendance_id INTEGER,
        student_id INTEGER,
        subject_id INTEGER,
        level_id INTEGER,
        amount INTEGER,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
              
        FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id),
        FOREIGN KEY (attendance_id) REFERENCES attendances(attendance_id),
        FOREIGN KEY (student_id) REFERENCES students(student_id),
        FOREIGN KEY (subject_id) REFERENCES subjects(subject_id),
        FOREIGN KEY (level_id) REFERENCES levels(level_id)
    )''')

    # Data for testing
    c.execute('''INSERT INTO students (student_id, title, f_name, l_name) VALUES (123, "นาย", "สมชาย", "สมหญิง")''')
    c.execute('''INSERT INTO teachers (teacher_id, title, f_name, l_name, payment_ratio) VALUES (987, "นาย", "Teerapath", "Sattabongkot", 0.5)''')
    c.execute('''INSERT INTO registrations (student_id, subject_id, level_id, teacher_id, time_left, times, schedule) VALUES (123, 1, 1, 987, 5, 8, "วันอังคาร 10:00 - 12:00")''')

    c.execute('''INSERT INTO attendances (student_id, subject_id, level_id, date) VALUES (123, 1, 1, "2024-08-17")''')
    c.execute('''INSERT INTO attendances (student_id, subject_id, level_id, date) VALUES (123, 1, 1, "2024-08-18")''')
    c.execute('''INSERT INTO attendances (student_id, subject_id, level_id, date) VALUES (123, 1, 1, "2024-08-19")''')

    # เปียโนเด็กพื้นฐาน
    c.execute('''INSERT INTO prices (subject_id, level_id, price) VALUES (1, 1, 2800), (1, 2, 3200), (1, 3, 3400)''')

    # Violin
    c.execute('''INSERT INTO prices (subject_id, level_id, price) VALUES (2, 1, 2800), (2, 2, 3200), (2, 3, 3400)''')

    # Guitar
    c.execute('''INSERT INTO prices (subject_id, level_id, price) VALUES (3, 1, 2800), (3, 2, 3200), (3, 3, 3400)''')

    # ดนตรีไทย
    c.execute('''INSERT INTO prices (subject_id, level_id, price) VALUES (4, 1, 2800), (4, 2, 3200), (4, 3, 3400)''')

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

    if request.method == 'POST':
        username_login = request.form['username_login']

        if username_login == "admin":
            return redirect(url_for('students'))
        else:
            flash("ชื่อผู้ใช้งานไม่ถูกต้อง", "danger")
            return render_template('index.html')

    return render_template('index.html')


@app.route("/students", methods=['GET', 'POST'])
@app.route("/students/<student_id>", methods=['GET', 'POST'])
def students(student_id=None):

    if student_id:

        # Get student information
        db = get_db()
        c = db.cursor()
        c.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
        student = c.fetchone()
        db.close()

        return render_template('student_information.html', student=student)

    today = date.today().strftime('%Y-%m-%d')

    db = get_db()
    c = db.cursor()
    c.execute("""
        SELECT 
            students.student_id, 
            students.title, 
            students.f_name, 
            students.l_name, 
            students.n_name, 
            students.email, 
            students.phone_num,
            CASE 
                WHEN attendances.date IS NOT NULL THEN 1
                ELSE 0
            END AS is_attended
        FROM students
        LEFT JOIN attendances 
            ON students.student_id = attendances.student_id 
            AND attendances.date = ?
    """, (today,))
    students = c.fetchall()
    db.close()

    return render_template('students.html', students=students)


@app.route("/teachers", methods=['GET', 'POST'])
@app.route("/teachers/<teacher_id>", methods=['GET', 'POST'])
def teachers(teacher_id=None):

    if teacher_id:

        # Get teacher information
        db = get_db()
        c = db.cursor()
        c.execute("SELECT * FROM teachers WHERE teacher_id = ?", (teacher_id,))
        teacher = c.fetchone()
        db.close()

        return render_template('teacher_information.html', teacher=teacher)

    db = get_db()
    c = db.cursor()
    c.execute(
        "SELECT teacher_id, f_name, l_name, n_name, email, phone_num, payment FROM teachers")
    teachers = c.fetchall()
    db.close()

    return render_template('teachers.html', teachers=teachers)


@app.route("/subjects", methods=['GET', 'POST'])
def subjects():
    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM subjects")
    subjects = c.fetchall()
    db.close()

    return render_template('subjects.html', subjects=subjects)


@app.route("/levels", methods=['GET', 'POST'])
def levels():

    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM levels")
    levels = c.fetchall()
    db.close()

    return render_template('levels.html', levels=levels)


@app.route("/add/<category>", methods=['GET', 'POST'])
def add(category):

    if request.method == 'POST':

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

            family_title = request.form['family_title']
            family_f_name = request.form['family_f_name']
            family_l_name = request.form['family_l_name']
            family_relationship = request.form['family_relationship']

            db = get_db()
            c = db.cursor()
            c.execute('''INSERT INTO students (student_id, title, f_name, l_name, n_name, address, dob, job, email, phone_num, instruments, family_title, family_f_name, family_l_name, family_relationship) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (student_id, title, f_name, l_name, n_name, address, dob, job, email, phone_num, instruments, family_title, family_f_name, family_l_name, family_relationship))
            db.commit()
            db.close()

            flash("เพิ่มนักเรียนสําเร็จ", "success")
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

            payment_ratio = request.form['payment_ratio']

            db = get_db()
            c = db.cursor()
            c.execute('''INSERT INTO teachers (teacher_id, title, f_name, l_name, n_name, address, dob, job, email, phone_num, payment_ratio) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (teacher_id, title, f_name, l_name, n_name, address, dob, job, email, phone_num, payment_ratio))
            db.commit()
            db.close()

            flash("เพิ่มอาจารย์สําเร็จ", "success")
            return redirect(url_for('teachers'))

        elif category == "subject":

            subject_name = request.form['subject_name']

            db = get_db()
            c = db.cursor()
            c.execute('''INSERT INTO subjects (subject_name) 
                    VALUES (?)''', (subject_name,))
            db.commit()
            db.close()

            flash("เพิ่มวิชาสําเร็จ", "success")
            return redirect(url_for('subjects'))
        elif category == "level":

            level_name = request.form['level_name']

            db = get_db()
            c = db.cursor()
            c.execute('''INSERT INTO levels (level_name)
                    VALUES (?)''', (level_name,))
            db.commit()
            db.close()

            flash("เพิ่มระดับชั้นสําเร็จ", "success")
            return redirect(url_for('levels'))

        elif category == "price":

            subject_id = request.form['subject_id']
            level_id = request.form['level_id']
            price = request.form['price']

            db = get_db()
            c = db.cursor()
            c.execute("INSERT INTO prices (subject_id, level_id, price) VALUES (?, ?, ?)",
                      (subject_id, level_id, price))
            db.commit()
            db.close()

            flash("เพิ่มราคาสําเร็จ", "success")
            return redirect(url_for('prices', subject_id=subject_id))

        elif category == "attendance":

            student_id = request.form['student_id']

            # Get subject_id and level_id from registrations according to student_id
            db = get_db()
            c = db.cursor()
            c.execute(
                "SELECT subject_id, level_id FROM registrations WHERE student_id = ?", (student_id,))
            rows = c.fetchall()
            db.close()

            for row in rows:
                print("here")
                add_attendance(student_id, row[0], row[1], date.today())

            flash("เช็คชื่อเรียบร้อยแล้ว", "success")
            return redirect(url_for('students'))
        
        elif category == "registration":

            student_id = request.args.get('student_id')

            subject_id = request.form['subject_id']
            level_id = request.form['level_id']
            teacher_id = request.form['teacher_id']
            times = request.form['times']
            schedule = request.form['schedule']

            if int(times) % 4 != 0:
                flash("จํานวนครั้งที่สอนต้องหาร 4 ลงตัว", "warning")
                return redirect(url_for('registrations', student_id=student_id))
            
            db = get_db()
            c = db.cursor()
            c.execute("INSERT INTO registrations (student_id, subject_id, level_id, teacher_id, time_left, times, schedule) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (student_id, subject_id, level_id, teacher_id, times, times, schedule))
            db.commit()
            db.close()

            flash("เพิ่มวิชาที่เรียนเรียบร้อยแล้ว", "success")

            return redirect(url_for('receipt', student_id=student_id, subject_id=subject_id, level_id=level_id))

    else:
        return redirect(url_for('students'))

@app.route("/update/<category>", methods=['GET', 'POST'])
def update(category):

    if request.method == 'POST':
        if category == "student":

            student_id = request.args.get('student_id')

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

            family_title = request.form['family_title']
            family_f_name = request.form['family_f_name']
            family_l_name = request.form['family_l_name']
            family_relationship = request.form['family_relationship']

            db = get_db()
            c = db.cursor()
            c.execute("""UPDATE students SET title=?, f_name=?, l_name=?, n_name=?, address=?, dob=?, job=?, email=?, phone_num=?, instruments=?, family_title=?, family_f_name=?, family_l_name=?, family_relationship=? 
                      WHERE student_id=?""", (title, f_name, l_name, n_name, address, dob, job, email, phone_num, instruments, family_title, family_f_name, family_l_name, family_relationship, student_id))
            db.commit()
            db.close()

            return redirect(url_for('students'))

        elif category == "teacher":

            teacher_id = request.args.get('teacher_id')

            title = request.form['title']
            f_name = request.form['f_name']
            l_name = request.form['l_name']
            n_name = request.form['n_name']
            address = request.form['address']
            dob = request.form['dob']
            job = request.form['job']
            email = request.form['email']
            phone_num = request.form['phone_num']

            payment_ratio = request.form['payment_ratio']

            db = get_db()
            c = db.cursor()
            c.execute("""UPDATE teachers SET title=?, f_name=?, l_name=?, n_name=?, address=?, dob=?, job=?, email=?, phone_num=?, payment_ratio=? 
                      WHERE teacher_id=?""", (title, f_name, l_name, n_name, address, dob, job, email, phone_num, payment_ratio, teacher_id))
            db.commit()
            db.close()

            return redirect(url_for('teachers'))
        
    else:
        return redirect(url_for('students'))

@app.route("/delete/<category>", methods=['GET', 'POST'])
def delete(category=None):

    if category:

        if category == "student":

            student_id = request.args.get('student_id')

            db = get_db()
            c = db.cursor()
            c.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
            db.commit()
            db.close()

            flash("ลบนักเรียนเรียบร้อยแล้ว", "success")

            return redirect(url_for('students'))

        elif category == "teacher":

            teacher_id = request.args.get('teacher_id')

            db = get_db()
            c = db.cursor()
            c.execute("DELETE FROM teachers WHERE teacher_id = ?", (teacher_id,))
            db.commit()
            db.close()

            flash("ลบอาจารย์เรียบร้อยแล้ว", "success")

            return redirect(url_for('teachers'))

        elif category == "subject":

            subject_id = request.args.get('subject_id')

            db = get_db()
            c = db.cursor()
            c.execute("DELETE FROM subjects WHERE subject_id = ?", (subject_id,))
            db.commit()
            db.close()

            flash("ลบรายวิชาเรียบร้อยแล้ว", "success")

            return redirect(url_for('subjects'))

        elif category == "level":

            level_id = request.args.get('level_id')

            db = get_db()
            c = db.cursor()
            c.execute("DELETE FROM levels WHERE level_id = ?", (level_id,))
            db.commit()
            db.close()

            flash("ลบระดับชั้นเรียบร้อยแล้ว", "success")

            return redirect(url_for('levels'))

        elif category == "registration":

            registration_id = request.args.get('registration_id')

            db = get_db()
            c = db.cursor()
            c.execute(
                "DELETE FROM registrations WHERE registration_id = ?", (registration_id,))
            db.commit()
            db.close()

            flash("ลบการลงวิชาเรียบร้อยแล้ว", "success")

            return redirect(url_for('students'))

        elif category == "attendance":

            student_id = request.args.get('student_id')
            subject_id = request.args.get('subject_id')
            level_id = request.args.get('level_id')
            attendance_id = request.args.get('attendance_id')

            delete_attendance(student_id, subject_id, level_id, attendance_id)

            flash("ลบประวัติการเข้าเรียนเรียบร้อยแล้ว", "success")
            return redirect(url_for('students'))

        elif category == "price":

            price_id = request.args.get('price_id')

            db = get_db()
            c = db.cursor()
            c.execute("DELETE FROM prices WHERE price_id = ?", (price_id,))
            db.commit()
            db.close()

            flash("ลบเรียบร้อยแล้ว", "success")

            return redirect(url_for('prices', subject_id=subject_id))
    else:
        return redirect(url_for('students'))


@app.route("/registrations/<student_id>", methods=['GET', 'POST'])
def registrations(student_id):

    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
    student = c.fetchone()
    db.close()

    if not student:
        flash("ไม่มีนักเรียนไอดีนี้", "warning")
        return redirect(url_for('students'))

    # Get all subjects and its levels
    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM subjects")
    subjects = c.fetchall()
    db.close()

    if len(subjects) == 0:
        flash("ไม่มีรายวิชาที่สอน", "warning")
        return redirect(url_for('students'))

    # Get all teachers
    db = get_db()
    c = db.cursor()
    c.execute("SELECT teacher_id, title, f_name, l_name, n_name FROM teachers")
    teachers = c.fetchall()
    db.close()

    # Get registrations according to student_id
    db = get_db()
    c = db.cursor()
    c.execute("SELECT registrations.registration_id, students.student_id, subjects.subject_id, levels.level_id, subjects.subject_name, levels.level_name, teachers.n_name, registrations.time_left, registrations.times, registrations.schedule FROM registrations JOIN subjects JOIN levels JOIN teachers JOIN students ON registrations.subject_id = subjects.subject_id AND registrations.level_id = levels.level_id AND registrations.teacher_id = teachers.teacher_id WHERE registrations.student_id = ? GROUP BY registrations.registration_id", (student_id,))
    rows = c.fetchall()
    db.close()

    return render_template('registrations.html', student=student, rows=rows, subjects=subjects, teachers=teachers)

@app.route('/get_prices/<int:subject_id>', methods=['GET', 'POST'])
def get_levels(subject_id):
    db = get_db()
    c = db.cursor()
    # Get levels based on the selected subject
    c.execute("SELECT levels.level_id, levels.level_name FROM prices JOIN levels ON prices.level_id = levels.level_id WHERE subject_id = ?", (subject_id,))
    rows = c.fetchall()
    db.close()

    # Convert rows to a list of dictionaries
    levels = [{"level_id": row[0], "level_name": row[1]} for row in rows]
    
    return jsonify(levels)

def add_attendance(student_id, subject_id, level_id, attend_date: date):

    # Add attendance
    db = get_db()
    c = db.cursor()
    c.execute("INSERT INTO attendances (student_id, subject_id, level_id, date) VALUES (?, ?, ?, ?)",
              (student_id, subject_id, level_id, attend_date))
    last_attendance_id = c.lastrowid
    db.commit()
    db.close()

    # Update student subject time left
    db = get_db()
    c = db.cursor()
    c.execute(
        '''UPDATE registrations SET time_left = time_left - 1 WHERE student_id = ? and subject_id = ? and level_id = ?''', (student_id, subject_id, level_id))
    db.commit()
    db.close()

    # Count attendance of attend_date month
    db = get_db()
    c = db.cursor()
    c.execute("SELECT COUNT(*) AS attendance_count FROM attendances WHERE student_id = ? and subject_id = ? and level_id = ? and strftime('%m', date) = ?",
              (student_id, subject_id, level_id, attend_date.strftime('%m')))
    data = c.fetchone()
    db.commit()
    db.close()

    attendance_count = data[0]

    # If attend 4 times, add money to teacher account
    if attendance_count != 0 and attendance_count % 4 == 0:

        db = get_db()
        c = db.cursor()
        c.execute(
            """SELECT teachers.teacher_id, prices.price, teachers.payment_ratio FROM registrations
            JOIN teachers JOIN prices 
            ON registrations.teacher_id = teachers.teacher_id AND registrations.subject_id = prices.subject_id AND registrations.level_id = prices.level_id
            WHERE registrations.student_id = ? AND registrations.subject_id = ? AND registrations.level_id = ?""", (student_id, subject_id, level_id))
        row = c.fetchone()
        db.commit()
        db.close()

        # Calculate money that teacher will get
        teacher_id = row[0]
        subject_price = row[1]
        teacher_payment_ratio = row[2]

        money = subject_price * teacher_payment_ratio

        # Add money to teacher payment
        db = get_db()
        c = db.cursor()
        c.execute(
            "UPDATE teachers SET payment = payment + ? WHERE teacher_id = ?", (money, teacher_id))
        db.commit()
        db.close()

        # Add transaction history to payments
        db = get_db()
        c = db.cursor()
        c.execute("INSERT INTO payments (teacher_id, attendance_id, student_id, subject_id, level_id, amount) VALUES (?, ?, ?, ?, ?, ?)",
                  (teacher_id, last_attendance_id, student_id, subject_id, level_id, money))
        db.commit()
        db.close()


def delete_attendance(student_id, subject_id, level_id, attendance_id):

    # Get date of this attendance
    db = get_db()
    c = db.cursor()
    c.execute("SELECT date FROM attendances WHERE attendance_id = ?",
              (attendance_id,))
    row = c.fetchone()
    db.close()

    month = datetime.strptime(row[0], '%Y-%m-%d').strftime('%m')

    if month == date.today().strftime('%m'):
        # Count attendance of this month
        db = get_db()
        c = db.cursor()
        c.execute("SELECT COUNT(*) AS attendance_count FROM attendances WHERE student_id = ? and subject_id = ? and level_id = ? and strftime('%m', date) = ?",
                  (student_id, subject_id, level_id, date.today().strftime('%m')))
        data = c.fetchone()
        db.close()

        attendance_count = data[0]

        # If attend 4 times, remove money from teacher this month payment
        if attendance_count != 0 and attendance_count % 4 == 0:

            db = get_db()
            c = db.cursor()
            c.execute(
                """SELECT teachers.teacher_id, prices.price, teachers.payment_ratio FROM registrations
                JOIN teachers JOIN prices 
                ON registrations.teacher_id = teachers.teacher_id AND registrations.subject_id = prices.subject_id AND registrations.level_id = prices.level_id
                WHERE registrations.student_id = ? AND registrations.subject_id = ? AND registrations.level_id = ?""", (student_id, subject_id, level_id))
            row = c.fetchone()
            db.close()

            # Calculate money that teacher will get
            teacher_id = row[0]
            subject_price = row[1]
            teacher_payment_ratio = row[2]

            money = subject_price * teacher_payment_ratio

            # Add money to teacher payment
            db = get_db()
            c = db.cursor()
            c.execute(
                "UPDATE teachers SET payment = payment - ? WHERE teacher_id = ?", (money, teacher_id))
            db.commit()
            db.close()

            # Remove transaction history
            db = get_db()
            c = db.cursor()
            c.execute("DELETE FROM payments WHERE attendance_id = ?",
                      (attendance_id,))
            db.commit()
            db.close()

    # Delete attendance
    db = get_db()
    c = db.cursor()
    c.execute("DELETE FROM attendances WHERE attendance_id = ?", (attendance_id,))

    # Update student subject time left
    c.execute(
        '''UPDATE registrations SET time_left = time_left + 1 WHERE student_id = ? and subject_id = ? and level_id = ?''', (student_id, subject_id, level_id))
    db.commit()
    db.close()


@app.route("/attendances/<student_id>", methods=['GET', 'POST'])
def attendances(student_id):

    if request.method == 'POST':

        # Check registration
        # Count attendance of this month
        db = get_db()
        c = db.cursor()
        c.execute("SELECT COUNT(*) AS registration_count FROM registrations WHERE student_id = ?",
                  (student_id, ))
        data = c.fetchone()
        db.close()

        registration_count = data[0]

        if registration_count <= 0:
            flash("ยังไม่มีข้อมูลวิชาที่เรียน", "warning")
            return redirect(url_for('students'))

        attendance_date = request.form['attendance_date']
        attendance_date = datetime.strptime(attendance_date, '%Y-%m-%d').date()

        # Get subject_id and level_id from registrations according to student_id
        db = get_db()
        c = db.cursor()
        c.execute(
            "SELECT subject_id, level_id FROM registrations WHERE student_id = ?", (student_id,))
        rows = c.fetchall()
        db.close()

        for row in rows:
            add_attendance(student_id, row[0], row[1], attendance_date)

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
    c.execute("SELECT attendance_id, date, student_id, subject_id, level_id FROM attendances WHERE student_id = ?", (student_id,))
    attendances = c.fetchall()
    db.close()

    return render_template('attendances.html', student=student, attendances=attendances)


@app.route("/prices/<subject_id>", methods=['GET', 'POST'])
def prices(subject_id):

    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM prices JOIN levels ON prices.level_id = levels.level_id WHERE subject_id = ?", (subject_id,))
    prices = c.fetchall()
    db.close()

    # Get subject id and name
    db = get_db()
    c = db.cursor()
    c.execute(
        "SELECT subject_id, subject_name FROM subjects WHERE subject_id = ?", (subject_id,))
    subject = c.fetchone()
    db.close()

    # Get levels
    db = get_db()
    c = db.cursor()
    c.execute("SELECT level_id, level_name FROM levels")
    levels = c.fetchall()
    db.close()

    return render_template('prices.html', prices=prices, subject=subject, levels=levels)

@app.route("/payments/<teacher_id>", methods=['GET', 'POST'])
def payments(teacher_id):

    # Get teacher
    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM teachers WHERE teacher_id = ?", (teacher_id,))
    teacher = c.fetchone()
    db.close()

    # Get payment from teacher_id
    db = get_db()
    c = db.cursor()
    c.execute("""SELECT students.f_name, students.l_name, students.n_name, subjects.subject_name, levels.level_name, payments.amount, payments.created_at FROM payments 
              JOIN students JOIN subjects JOIN levels ON payments.student_id = students.student_id AND payments.subject_id = subjects.subject_id AND payments.level_id = levels.level_id 
              WHERE teacher_id = ?""", (teacher_id,))
    payments = c.fetchall()
    db.close()

    return render_template('payments.html', payments=payments, teacher=teacher)

@app.route("/reset_payment/<teacher_id>", methods=['GET', 'POST'])
def reset_payment(teacher_id):

    # Reset teacher payment to 0
    db = get_db()
    c = db.cursor()
    c.execute(
        "UPDATE teachers SET payment = 0 WHERE teacher_id = ?", (teacher_id, ))
    db.commit()
    db.close()

    return redirect(url_for('teachers'))


@app.route("/receipt/<student_id>/<subject_id>/<level_id>", methods=['GET', 'POST'])
def receipt(student_id, subject_id, level_id):

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
        """SELECT registrations.times, prices.price, students.f_name, students.student_id, students.title, students.l_name, students.n_name, subjects.subject_name, levels.level_name FROM registrations 
        JOIN students JOIN subjects JOIN levels JOIN prices
        ON registrations.student_id = students.student_id AND registrations.subject_id = subjects.subject_id AND registrations.level_id = levels.level_id AND registrations.subject_id = prices.subject_id
        WHERE registrations.student_id = ? and registrations.subject_id = ? and registrations.level_id = ?""", (student_id, subject_id, level_id))
    data = c.fetchone()
    db.close()

    if int(data[0]) % 4 == 0:
        payment = data[1] * (data[0] // 4)
        return render_template('receipt.html', data=data, payment=payment)
    else:
        flash("จำนวนครั้งหาร 4 ไม่ลงตัว", "warning")
        return redirect(url_for('students'))


@app.route('/save-db', methods=['GET', 'POST'])
def save_db():
    return send_file(DATABASE, as_attachment=True, download_name='database.db')


@app.route('/generate-pdf', methods=['GET', 'POST'])
def generate_pdf():

    if request.method == 'POST':

        title = request.form['title']
        f_name = request.form['f_name']
        l_name = request.form['l_name']
        subject = request.form['subject']
        times = request.form['times']
        payment = request.form['payment']

        buffer = BytesIO()

        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4

        pdfmetrics.registerFont(TTFont('THSarabunNEW', os.path.join(
            os.path.dirname(__file__), 'fonts', 'THSarabunNew.ttf')))

        c.setFont("THSarabunNEW", 18)
        c.drawCentredString(width / 2, height - 100, "ใบเสร็จรับเงิน")

        c.setFont("THSarabunNEW", 10)
        c.drawCentredString(width / 2, height - 120, "RECEIPT")

        c.setFont("THSarabunNEW", 20)
        c.drawCentredString(width / 2, height - 140, "ศุภนิจการดนตรี")

        c.setFont("THSarabunNEW", 10)
        c.drawCentredString(width / 2, height - 160,
                            "55/9 ถนนวัชรพล แขวงท่าแร้ง เขตบางเขน กรุงเทพฯ")
        c.drawCentredString(width / 2, height - 170, "โทร. 02-948 2644")

        c.setFont("THSarabunNEW", 16)
        c.drawCentredString(width / 2, height - 190, "SUPANIT MUSIC ACADEMY")

        c.drawString(400, height - 220, "วันที่:")
        c.drawString(450, height - 220, date.today().strftime("%d/%m/%Y"))

        c.drawString(400, height - 240, "เลขที่:")
        c.drawString(450, height - 240, "5410090863")

        c.drawString(60, height - 260, "ได้รับเงินจาก:")
        c.drawString(120, height - 260, title + " " + f_name + " " + l_name)

        c.drawString(240, height - 260, "วิชา:")
        c.drawString(300, height - 260, subject)

        c.drawString(60, height - 280, "ชำระสำหรับ:")
        c.drawString(120, height - 280, "ค่าเรียน" +
                     " " + times + " " + "ครั้ง")

        c.drawString(240, height - 280, "จำนวนเงิน:")
        c.drawString(300, height - 280, payment)

        c.setFont("THSarabunNEW", 16)
        c.drawCentredString(width / 2, height - 460,
                            "ใบเสร็จรับเงินที่ถูกต้อง จะต้องมีลายเซ็นของเจ้าหน้าที่ผู้รับมอบอำนาจ และประทับตราโรงเรียน")

        c.rect(50, height - 480, width - 80, 450, stroke=1, fill=0)

        c.showPage()
        c.save()

        buffer.seek(0)

        return send_file(buffer, as_attachment=True, download_name='receipt.pdf', mimetype='application/pdf')


def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')


if __name__ == '__main__':
    threading.Timer(1, open_browser).start()
    app.run()
