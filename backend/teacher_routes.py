from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import get_db_connection
from datetime import date, datetime
from flask_jwt_extended import get_jwt

teacher_bp = Blueprint("teacher_bp", __name__)

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
            
@teacher_bp.route("/teachers_all", methods=["GET"])
@jwt_required()
def get_teachers_all():
    username = get_jwt_identity()
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM teachers ORDER BY teacher_id ASC")
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

            # เพิ่มชื่อเต็ม
            item["full_name"] = f"{item.get('prefix_name', '')}{item.get('first_name', '')} {item.get('last_name', '')}".strip()
            result.append(item)

        # ✅ DEBUG log JSON ส่งออก
        print("=== JSON RESULT ===")
        print(json.dumps({"current_user": username, "teachers": result}, indent=2, ensure_ascii=False))

        return jsonify({"current_user": username, "teachers": result}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()            
