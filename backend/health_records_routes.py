from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import get_db_connection
from datetime import date, datetime
from flask_jwt_extended import get_jwt
from flask import send_from_directory
import base64
import os

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
                s.student_id, s.student_code, s.prefix_name, s.first_name, s.last_name
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
            ORDER BY s.student_code ASC
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
            item['nails_status'] = bool(item['nails_status'])
            item['hair_status'] = bool(item['hair_status'])
            item['teeth_status'] = bool(item['teeth_status'])
            item['body_status'] = bool(item['body_status'])
            item['eye_status'] = bool(item['eye_status'])
            item['ear_status'] = bool(item['ear_status'])
            item['nose_status'] = bool(item['nose_status'])
            
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


# API Insert
@health_records_bp.route("/health_records/insert", methods=["POST"])
@jwt_required()
def insert_health_record():

    claims = get_jwt()  # additional_claims ทั้งหมด
    created_by = claims["user_id"]  # ได้ user_id จาก token

    try:
        data = request.get_json()
        
        # ดึงข้อมูลจาก JSON
        student_id = data.get("student_id")
        attendance_status = data.get("attendance_status")
        classroom_id = data.get("classroom_id")
        record_date = date.today()
        body_temperature = data.get("body_temperature")
        nails_status = data.get("nails_status")
        hair_status = data.get("hair_status")
        teeth_status = data.get("teeth_status")
        body_status = data.get("body_status")
        eye_status = data.get("eye_status")
        ear_status = data.get("ear_status")
        nose_status = data.get("nose_status")
        student_photo = data.get("student_photo")
        notes = data.get("notes")
        created_date = datetime.now()


        # ✅ เชื่อมต่อฐานข้อมูล
        conn = get_db_connection()
        cursor = conn.cursor()

        # 👇 เพิ่มเข้า DB
        cursor.execute(
            """
            INSERT INTO health_records 
            (student_id, attendance_status, classroom_id, record_date, body_temperature
            , nails_status, hair_status, teeth_status, body_status
            , eye_status, ear_status, nose_status, student_photo, notes
            , created_by, created_date)
            VALUES (%s, %s, %s, %s, %s
            , %s, %s, %s, %s
            , %s, %s, %s, %s, %s
            , %s, %s)
            """,
            (
                student_id, attendance_status, classroom_id, record_date, body_temperature
                , nails_status, hair_status, teeth_status, body_status
                , eye_status, ear_status, nose_status, student_photo, notes
                , created_by, created_date
            ),
        )

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "เพิ่มข้อมูลตรวจสุขภาพสำเร็จ"}), 200

    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"error": str(e)}), 500
    

# API Update
@health_records_bp.route("/health_records/update/<int:health_id>", methods=["PUT"])
@jwt_required()
def update_health_record(health_id):
    claims = get_jwt()  # additional_claims ทั้งหมด
    updated_by = claims["user_id"]  # ได้ user_id จาก token

    try:    
        data = request.get_json()
        
        # ดึงข้อมูลจาก JSON
        attendance_status = data.get("attendance_status")
        body_temperature = data.get("body_temperature")
        nails_status = data.get("nails_status")
        hair_status = data.get("hair_status")
        teeth_status = data.get("teeth_status")
        body_status = data.get("body_status")
        eye_status = data.get("eye_status")
        ear_status = data.get("ear_status")
        nose_status = data.get("nose_status")
        student_photo = data.get("student_photo")
        notes = data.get("notes")
        

        # ✅ เชื่อมต่อฐานข้อมูล
        conn = get_db_connection()
        cursor = conn.cursor()

        # 👇 เพิ่มเข้า DB
        cursor.execute(
            """
            UPDATE health_records
            SET attendance_status = %s, body_temperature = %s, nails_status = %s
            , hair_status = %s, teeth_status = %s, body_status = %s
            , eye_status = %s, ear_status = %s, nose_status = %s
            , student_photo = %s, notes = %s
            , updated_by = %s
            WHERE health_id = %s
            """,
            (
                attendance_status, body_temperature, nails_status
                , hair_status, teeth_status, body_status
                , eye_status, ear_status, nose_status
                , student_photo, notes
                , updated_by, health_id
            ),
        )

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "แก้ไขข้อมูลตรวจสุขภาพสำเร็จ"}), 200

    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"error": str(e)}), 500
    

# API Delete
@health_records_bp.route("/health_records/delete/<int:health_id>", methods=["DELETE"])
@jwt_required()
def delete_health_record(health_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 👇 ลบจาก DB
        cursor.execute("DELETE FROM health_records WHERE health_id = %s", (health_id,))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "ลบข้อมูลตรวจสุขภาพสำเร็จ"}), 200

    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"error": str(e)}), 500