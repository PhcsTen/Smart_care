from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import get_db_connection
from datetime import date, datetime
from flask_jwt_extended import get_jwt
import traceback

health_records_bp = Blueprint("health_records_bp", __name__)

# API GET ข้อมูลการตรวจสุขภาพของนักเรียนในวันปัจจุบัน ด้วย teacher_id
@health_records_bp.route("/student_health_records/<int:teacher_id>", methods=["GET"])
@jwt_required()
def get_student_health_records_by_teacher_id(teacher_id):

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                s.student_id, s.prefix_name, s.first_name, s.last_name
                , c.classroom_id, c.classroom_name, hr.health_id 
                , hr.attendance_status, hr.record_date, hr.body_temperature
                , hr.nails_status, hr.hair_status, hr.teeth_status
                , hr.body_status, hr.eye_status, hr.ear_status
                , hr.nose_status, hr.notes, hr.student_photo
            FROM students s 
            LEFT JOIN health_records hr on s.student_id = hr.student_id and hr.record_date = CURRENT_DATE()
            LEFT JOIN class_history ch on s.student_id = ch.student_id
            LEFT JOIN classroom_teachers ct on ch.classroom_id = ct.classroom_id
            LEFT JOIN classrooms c on ct.classroom_id = c.classroom_id
            WHERE ct.teacher_id = %s
        """,
            (teacher_id,),
        
        )

        health_records = cursor.fetchall()

        if not health_records:
            return jsonify({"message": "ไม่พบข้อมูลตรวจสุขภาพ", "health_records": []}), 404

        columns = [col[0] for col in cursor.description]
        result = [dict(zip(columns, row)) for row in health_records]

        for item in result:
            first_name = item.get('first_name', '') 
            last_name = item.get('last_name', '')
            prefix = item.get('prefix_name', '') 

            item['student_fullname'] = f"{prefix}{first_name} {last_name}".strip()

            for key, value in item.items():
                if isinstance(value, (datetime, date)):
                    item[key] = value.isoformat()

        return jsonify({"health_records": result}), 200
    except Exception as e:
        print("ERROR:", traceback.format_exc())  # DEBUG!
        return jsonify({"message": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()