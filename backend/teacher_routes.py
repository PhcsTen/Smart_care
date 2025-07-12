from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import get_db_connection
from datetime import date, datetime
from flask_jwt_extended import get_jwt

teacher_bp = Blueprint("teacher_bp", __name__)

# สร้าง API GET สำหรับแสดงข้อมูลเฉพราะการใช้ select ใน teacher
@teacher_bp.route("/teachers", methods=["GET"])
@jwt_required()
def get_teachers():
    username = get_jwt_identity()  # "admin"
    # claims = get_jwt()              # additional_claims ทั้งหมด
    # created_by = claims["user_id"]     # ได้ user_id จาก token

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT teacher_id, first_name, last_name FROM teachers")
        schools = cursor.fetchall()

        columns = [col[0] for col in cursor.description]
        result = [dict(zip(columns, row)) for row in schools]

        # แปลงวันที่เป็น string
        for item in result:
            for key, value in item.items():
                if isinstance(value, (datetime, date)):
                    item[key] = value.isoformat()

        return jsonify({"current_user": username, "teachers": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# สร้าง API GET สำหรับแสดงข้อมูลทั้งหมด teacher all
@teacher_bp.route("/teachers_all", methods=["GET"])
@jwt_required()
def get_teachers_all():
    username = get_jwt_identity()
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # ✅ JOIN กับ schools เพื่อให้ได้ school_name
        cursor.execute("""
            SELECT t.*, s.school_name
            FROM teachers t
            LEFT JOIN schools s ON t.school_id = s.school_id
            ORDER BY t.teacher_id ASC
        """)

        teachers = cursor.fetchall()

        if not teachers:
            return jsonify({"message": "ไม่พบข้อมูลครู", "teachers": []}), 200

        columns = [col[0] for col in cursor.description]
        result = []

        for row in teachers:
            item = dict(zip(columns, row))
            for key, value in item.items():
                if isinstance(value, (datetime, date)):
                    item[key] = value.isoformat()

            # ✅ เพิ่มชื่อเต็ม
            item["full_name"] = (
                f"{item.get('prefix_name', '')}{item.get('first_name', '')} {item.get('last_name', '')}".strip()
            )
            result.append(item)

        return jsonify({"current_user": username, "teachers": result}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# สร้าง API POST สำหรับเพิ่มข้อมูล teacher
@teacher_bp.route("/teacher/insert", methods=["POST"])
@jwt_required()
def insert_teacher():
    # print("Header:", dict(request.headers))
    claims = get_jwt()  # additional_claims ทั้งหมด
    created_by = claims["user_id"]  # ได้ user_id จาก token
    print("created_by:", created_by)

    data = request.get_json()
    print("DATA RECEIVED:", data)

    # teacher_id = data.get("teacher_id")
    prefix_name = data.get("prefix_name")
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    email = data.get("email")
    phone_number = data.get("phone_number")
    school_id = data.get("school_id")

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(buffered=True)  # ใช้ buffered เพื่อป้องกัน unread result

        cursor.execute(
            "INSERT INTO teachers (prefix_name, first_name, last_name, school_id,email,phone_number,created_date, created_by) VALUES (%s,%s,%s,%s,%s,%s, NOW(), %s)",
            (
                prefix_name,
                first_name,
                last_name,
                school_id,
                email,
                phone_number,
                created_by,
            ),
        )
        conn.commit()
        return jsonify({"message": "เพิ่มข้อมูลครูเรียบร้อยแล้ว"}), 201

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"message": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# สร้าง API PUT สำหรับ update teacher
@teacher_bp.route("/teacher/update/<int:teacher_id>", methods=["PUT"])
@jwt_required()
def update_teacher(teacher_id):
    claims = get_jwt()
    updated_by = claims["user_id"]
    
    data = request.get_json()
    
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE teachers 
            SET 
                prefix_name = %s,
                first_name = %s,
                last_name = %s,
                email = %s,
                phone_number = %s,
                school_id = %s,
                updated_by = %s,
                updated_date = NOW()
            WHERE teacher_id = %s
        """, (
            data.get("prefix_name"),
            data.get("first_name"),
            data.get("last_name"),
            data.get("email"),
            data.get("phone_number"),
            data.get("school_id"),
            updated_by,
            teacher_id
        ))
        
        conn.commit()
        return jsonify({"message": "Teacher updated successfully"}), 200
        
    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# ลบ teacher
@teacher_bp.route("/teacher/delete/<int:teacher_id>", methods=["DELETE"])
@jwt_required()
def delete_teacher(teacher_id):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM teachers WHERE teacher_id = %s", (teacher_id,))
        conn.commit()
        return jsonify({"message": "Teachers deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
