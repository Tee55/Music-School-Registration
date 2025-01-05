import io
import os
from flask import Blueprint, Response, jsonify, request, redirect, url_for, send_file
import openpyxl
from datetime import date
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from extensions import db
from models.attendance import Attendance
from models.registration import Registration
from models.student import Student
from models.teacher import Teacher

files_bp = Blueprint('files', __name__)

@files_bp.route('/import_excel', methods=['POST'])
def import_excel():
    # Check if a file is part of the request
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    
    # If no file is selected
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Read the file into a BytesIO buffer
    try:
        file_stream = BytesIO(file.read())
        workbook = openpyxl.load_workbook(file_stream)
    except Exception as e:
        return jsonify({"error": f"Failed to read Excel file: {str(e)}"}), 400

    # Mapping sheet names to models
    tables = {
        'attendances': Attendance,
        'registrations': Registration,
        'students': Student,
        'teachers': Teacher,
    }

    # Iterate through each sheet and process the data
    for sheet_name, model in tables.items():
        if sheet_name not in workbook.sheetnames:
            continue

        sheet = workbook[sheet_name]

        # Read the column names from the first row
        columns = [cell.value for cell in sheet[1]]
        
        # Make sure all required columns exist in the model
        model_columns = [column.name for column in model.__table__.columns]
        missing_columns = [col for col in columns if col not in model_columns]
        if missing_columns:
            return jsonify({"error": f"Missing columns in model for sheet '{sheet_name}': {missing_columns}"}), 400
        
        # Iterate over rows and insert data
        for row in sheet.iter_rows(min_row=2, values_only=True):
            data = dict(zip(columns, row))
            
            # Create a new model instance and populate its fields
            record = model(**data)
            db.session.add(record)
        
        # Commit after processing the current sheet
        db.session.commit()

    # If everything went well, return a success message
    return redirect(url_for('students.list_students'))

@files_bp.route('/export_excel')
def export_excel():
    # List of models to export
    tables = {
        'attendances': Attendance,
        'registrations': Registration,
        'students': Student,
        'teachers': Teacher,
    }

    # Create a BytesIO buffer to hold the Excel file in memory
    output = io.BytesIO()

    # Create a new Excel workbook
    workbook = openpyxl.Workbook()

    # Remove the default sheet (which is automatically created)
    default_sheet = workbook.active
    workbook.remove(default_sheet)

    # Loop through each table, query the data, and add to Excel
    for sheet_name, model in tables.items():
        # Query the model's data
        rows = db.session.query(model).all()

        # Get column names based on the model's columns
        columns = [column.name for column in model.__table__.columns]

        # Create a new sheet in the workbook for each model
        sheet = workbook.create_sheet(title=sheet_name)

        # Write the column headers to the first row
        for col_num, column_title in enumerate(columns, 1):
            sheet.cell(row=1, column=col_num, value=column_title)

        # Write the data rows
        for row_num, row_data in enumerate(rows, 2):
            # Ensure we are iterating over the actual model instance, not the object itself
            for col_num, column in enumerate(columns, 1):
                value = getattr(row_data, column)  # Get the value of the column in the current row
                sheet.cell(row=row_num, column=col_num, value=value)

    # Save the workbook to the BytesIO buffer
    workbook.save(output)

    # Prepare the response
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment;filename=output.xlsx"}
    )

@files_bp.route('/generate-pdf', methods=['POST'])
def generate_pdf():

    def extract_pdf_data_from_form(form):
        """Extract necessary data for the PDF from the form."""
        return {
            'title': form['title'],
            'f_name': form['f_name'],
            'l_name': form['l_name'],
            'subject': form['subject'],
            'times': form['times'],
            'payment': form['payment'],
        }


    def create_pdf(pdf_data):
        """Generate PDF receipt."""

        def set_up_pdf(c):
            """Set up the PDF page layout and fonts."""
            pdfmetrics.registerFont(TTFont('THSarabunNEW', os.path.join(os.path.dirname(__file__), 'fonts', 'THSarabunNew.ttf')))
            c.setFont("THSarabunNEW", 18)
            c.setDash(1, 2)

        def draw_receipt_details(c, pdf_data):
            """Draw all details on the PDF."""

            def draw_checkbox(c, x, y, size=10, checked=False):
                """Draw a checkbox with an optional checkmark."""
                c.setDash([])
                c.setLineWidth(1)
                c.rect(x, y, size, size)

                if checked:
                    c.setLineWidth(1.5)
                    c.line(x, y, x + size, y + size)
                    c.line(x, y + size, x + size, y)

                c.setDash(1, 2)

            width, height = A4
            c.drawCentredString(width / 2, height - 100, "ใบเสร็จรับเงิน")
            c.setFont("THSarabunNEW", 10)
            c.drawCentredString(width / 2, height - 120, "RECEIPT")
            c.setFont("THSarabunNEW", 20)
            c.drawCentredString(width / 2, height - 140, "โรงเรียนศุภนิจการดนตรีและภาษา Supanit Music & Language School")
            c.setFont("THSarabunNEW", 10)
            c.drawCentredString(width / 2, height - 160, "888/5 หมู่ 4 ถนนวัชรพล แขวงคลองถนน เขตสายไหม กรุงเทพ 10220")
            c.drawCentredString(width / 2, height - 170, "โทร. 02-1530775")
            c.setFont("THSarabunNEW", 16)

            c.drawString(400, height - 220, "วันที่:")
            c.drawString(450, height - 220, date.today().strftime("%d/%m/%Y"))
            c.drawString(400, height - 240, "เลขที่:")
            c.line(440, height - 240 - 2, 540, height - 240 - 2)

            c.drawString(60, height - 260, "ได้รับเงินจาก:")
            c.drawString(120, height - 260, f"{pdf_data['title']} {pdf_data['f_name']} {pdf_data['l_name']}")
            c.line(120, height - 260 - 2, 260, height - 260 - 2)

            c.drawString(300, height - 260, "วิชา:")
            c.drawString(360, height - 260, pdf_data['subject'])
            c.line(360, height - 260 - 2, 540, height - 260 - 2)

            c.drawString(60, height - 280, "ชำระสำหรับ:")
            c.drawString(120, height - 280, f"ค่าเรียน {pdf_data['times']} ครั้ง")
            c.line(120, height - 280 - 2, 260, height - 280 - 2)

            c.drawString(300, height - 280, "จำนวนเงิน:")
            c.drawString(360, height - 280, f"{pdf_data['payment']} บาท")
            c.line(360, height - 280 - 2, 540, height - 280 - 2)

            c.setFont("THSarabunNEW", 16)
            c.drawCentredString(width / 2, height - 460, "ใบเสร็จรับเงินที่ถูกต้อง จะต้องมีลายเซ็นของเจ้าหน้าที่ผู้รับมอบอำนาจ และประทับตราโรงเรียน")

            c.drawString(60, height - 320, "รับชำระ:")
            draw_checkbox(c, 120, height - 320, size=12, checked=False)
            c.drawString(140, height - 320, "สแกนจ่าย/Scan")

            draw_checkbox(c, 300, height - 320, size=12, checked=False)
            c.drawString(320, height - 320, "เงินสด/Cash")

            c.drawString(300, height - 400, "ผู้รับเงิน:")
            c.line(350, height - 400 - 2, 540, height - 400 - 2)

            c.setDash([])

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        set_up_pdf(c)
        draw_receipt_details(c, pdf_data)
        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer

    pdf_data = extract_pdf_data_from_form(request.form)
    buffer = create_pdf(pdf_data)
    return send_file(buffer, as_attachment=True, download_name='receipt.pdf', mimetype='application/pdf')
