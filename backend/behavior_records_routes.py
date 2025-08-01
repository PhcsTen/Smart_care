from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import get_db_connection
from datetime import date, datetime
from flask_jwt_extended import get_jwt
from flask import send_from_directory
import base64
import os
from werkzeug.utils import secure_filename
import hashlib

behavior_records_bp = Blueprint("behavior_records_bp", __name__)

# API GET ข้อมูลการบันทึกสังเกตพฤติกรรมของนักเรียนในวันปัจจุบัน ด้วย teacher_id
@behavior_records_bp.route("/student_behavior_records/<int:teacher_id>", methods=["GET"])
@jwt_required()
def get_student_behavior_records_by_teacher_id(teacher_id):

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 
                s.student_id, s.student_code, s.prefix_name, s.first_name, s.last_name, c.class_id, c.class_name, 
                cr.classroom_id, cr.classroom_name, br.behavior_id, br.record_date, br.milk_status,
                br.lunch_status, br.snack_status, br.brushing_status, br.sleeping_status, br.toilet_status,
                br.notes, br.record_status, sch.school_name
            FROM students s 
            LEFT JOIN behavior_records br on s.student_id = br.student_id and br.record_date = CURRENT_DATE()
            LEFT JOIN class_history ch on s.student_id = ch.student_id
            LEFT JOIN classroom_teachers ct on ch.classroom_id = ct.classroom_id
            LEFT JOIN classrooms cr on ct.classroom_id = cr.classroom_id
            LEFT JOIN classes c on cr.class_id = c.class_id
            LEFT JOIN schools sch on c.school_id = sch.school_id
            WHERE ct.teacher_id = %s
            ORDER BY s.student_code ASC
        """,
            (teacher_id,),
        
        )

        behavior_records = cursor.fetchall()

        if not behavior_records:
            return jsonify({"message": "ไม่พบข้อมูลบันทึกสังเกตพฤติกรรม", "behavior_records": []}), 404

        columns = [col[0] for col in cursor.description]
        result = [dict(zip(columns, row)) for row in behavior_records]

        for item in result:
            first_name = item.get('first_name', '') 
            last_name = item.get('last_name', '')
            prefix = item.get('prefix_name', '') 

            item['student_fullname'] = f"{prefix}{first_name} {last_name}".strip()
            
            for key, value in item.items():
                if isinstance(value, (datetime, date)):
                    item[key] = value.isoformat()

        return jsonify({"behavior_records": result}), 200
    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# API Insert
@behavior_records_bp.route("/behavior_records/insert", methods=["POST"])
@jwt_required()
def insert_behavior_record():

    claims = get_jwt()  # additional_claims ทั้งหมด
    created_by = claims["user_id"]  # ได้ user_id จาก token

    try:
        data = request.get_json()
        
        # ดึงข้อมูลจาก JSON
        student_id = data.get("student_id")
        class_id = data.get("class_id")
        classroom_id = data.get("classroom_id")
        record_date = date.today()
        milk_status = data.get("milk_status")
        lunch_status = data.get("lunch_status")
        snack_status = data.get("snack_status")
        brushing_status = data.get("brushing_status")
        sleeping_status = data.get("sleeping_status")
        toilet_status = data.get("toilet_status")
        notes = data.get("notes")
        created_date = datetime.now()


        # ✅ เชื่อมต่อฐานข้อมูล
        conn = get_db_connection()
        cursor = conn.cursor()

        # 👇 เพิ่มเข้า DB
        cursor.execute(
            """
            INSERT INTO behavior_records (student_id, class_id, classroom_id, record_date, milk_status, lunch_status, 
            snack_status, brushing_status, sleeping_status, toilet_status, notes, created_by, created_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                student_id,
                class_id,
                classroom_id,
                record_date,
                milk_status,
                lunch_status,
                snack_status,
                brushing_status,
                sleeping_status,
                toilet_status,
                notes,
                created_by,
                created_date,
            ),
        )

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "เพิ่มข้อมูลบันทึกสังเกตพฤติกรรมสำเร็จ"}), 200

    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"error": str(e)}), 500
    

# API Update
@behavior_records_bp.route("/behavior_records/update/<int:behavior_id>", methods=["PUT"])
@jwt_required()
def update_behavior_record(behavior_id):
    claims = get_jwt()  # additional_claims ทั้งหมด
    updated_by = claims["user_id"]  # ได้ user_id จาก token

    try:    
        data = request.get_json()
        
        # ดึงข้อมูลจาก JSON
        student_id = data.get("student_id")
        class_id = data.get("class_id")
        classroom_id = data.get("classroom_id")
        record_date = date.today()
        milk_status = data.get("milk_status")
        lunch_status = data.get("lunch_status")
        snack_status = data.get("snack_status")
        brushing_status = data.get("brushing_status")
        sleeping_status = data.get("sleeping_status")
        toilet_status = data.get("toilet_status")
        notes = data.get("notes")

        # ✅ เชื่อมต่อฐานข้อมูล
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        

        cursor.execute("SELECT * FROM behavior_records WHERE behavior_id = %s", (behavior_id,))
        result = cursor.fetchone()

        if not result:
            cursor.close()
            conn.close()
            return jsonify({'error': 'ไม่พบข้อมูล'}), 404
        

        # UPDATE DB
        cursor.execute(
            """
            UPDATE behavior_records 
            SET 
                student_id = %s,
                class_id = %s,
                classroom_id = %s,
                milk_status = %s,
                lunch_status = %s,
                snack_status = %s,
                brushing_status = %s,
                sleeping_status = %s,
                toilet_status = %s,
                notes = %s,
                updated_by = %s
            WHERE behavior_id = %s
            """,
            (
                student_id,
                class_id,
                classroom_id,
                milk_status,
                lunch_status,
                snack_status,
                brushing_status,
                sleeping_status,
                toilet_status,
                notes,
                updated_by, 
                behavior_id
            ),
        )

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "แก้ไขข้อมูลบันทึกสังเกตพฤติกรรมสำเร็จ"}), 200

    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"error": str(e)}), 500
    

# API Delete
@behavior_records_bp.route("/behavior_records/delete/<int:behavior_id>", methods=["DELETE"])
@jwt_required()
def delete_behavior_record(behavior_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("DELETE FROM behavior_records WHERE behavior_id = %s", (behavior_id,))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "ลบข้อมูลบันทึกสังเกตพฤติกรรมสำเร็จ"}), 200

    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"error": str(e)}), 500

# def find_teacher_by_user_id(user_id):
#     conn = get_db_connection()
#     cursor = conn.cursor(dictionary=True)
#     cursor.execute("SELECT * FROM teachers WHERE user_id = %s", (user_id,))
#     teacher = cursor.fetchone()
#     cursor.close()
#     conn.close()
#     return teacher
