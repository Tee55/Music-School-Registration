import os
from flask import Flask, redirect, url_for
from config import Config
from extensions import db, migrate
from blueprints.students import students_bp
from blueprints.teachers import teachers_bp
from blueprints.payments import payments_bp
from blueprints.attendances import attendances_bp
from blueprints.registrations import registrations_bp
from blueprints.files import files_bp
import threading
import webbrowser

# Application factory pattern
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    app.register_blueprint(students_bp, url_prefix="/students")
    app.register_blueprint(teachers_bp, url_prefix="/teachers")
    app.register_blueprint(payments_bp, url_prefix="/payments")
    app.register_blueprint(attendances_bp, url_prefix="/attendances")
    app.register_blueprint(registrations_bp, url_prefix="/registrations")
    app.register_blueprint(files_bp, url_prefix='/files')

    # Create the database if it doesn't exist (for SQLite)
    if not os.path.exists(Config.SQLALCHEMY_DATABASE_URI):
        print("Database does not exist. Creating database...")
        with app.app_context():
            db.create_all()  # Create the tables if they do not exist

    # Route for root ("/") to redirect to /students
    @app.route('/')
    def index():
        return redirect(url_for('students.list_students'))

    # Error handling
    @app.errorhandler(404)
    def not_found_error(error):
        return "Page not found.", 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return "An unexpected error occurred.", 500

    return app


def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/students')


if __name__ == "__main__":
    threading.Timer(1, open_browser).start()
    app = create_app()
    app.run(debug=True)
