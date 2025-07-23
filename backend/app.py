from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from auth import auth_bp
from user_routes import user_bp
from year_routes import year_bp
from classrooms_routes import classrooms_bp
from school_routes import school_bp
from teacher_routes import teacher_bp
from classes_routes import classes_bp
from student_routes import student_bp
from health_records_routes import health_records_bp

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = Config.JWT_SECRET_KEY

# ตั้งค่า CORS เฉพาะ origin http://localhost:3000 และรองรับ credentials
CORS(app, origins=["http://localhost:8081","http://localhost:3000"], supports_credentials=True)

jwt = JWTManager(app)

# ลงทะเบียน blueprint
app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(year_bp)
app.register_blueprint(classrooms_bp)
app.register_blueprint(school_bp)
app.register_blueprint(teacher_bp)
app.register_blueprint(classes_bp)
app.register_blueprint(student_bp)
app.register_blueprint(health_records_bp)

if __name__ == "__main__":
    app.run(debug=True)
