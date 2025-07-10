from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import get_db_connection
from datetime import date, datetime
from flask_jwt_extended import get_jwt
import traceback

classes_bp = Blueprint("classes_bp", __name__)


@classes_bp.route("/class", methods=["GET"])
@jwt_required()
def get_class():
    conn = None
    cursor = None

    try:
        # เชื่อมต่อฐานข้อมูล
        conn = get_db_connection()
        cursor = conn.cursor()

        # SQL: JOIN ตาราง classes กับ classrooms และ schools
        query = """
            SELECT 
                c.class_id,
                c.class_name,
                c.school_id,
                s.school_name,
                COUNT(cl.classroom_id) AS room_count
            FROM classes c
            LEFT JOIN schools s ON c.school_id = s.school_id
            LEFT JOIN classrooms cl ON c.class_id = cl.class_id
            GROUP BY c.class_id, c.class_name, s.school_name
            ORDER BY c.class_id ASC
        """
        cursor.execute(query)
        rows = cursor.fetchall()

        # แปลงข้อมูลให้อยู่ในรูปแบบ list of dicts
        columns = [col[0] for col in cursor.description]
        result = [dict(zip(columns, row)) for row in rows]

        if not result:
            return jsonify({"message": "ไม่พบข้อมูลระดับชั้น"}), 404

        return jsonify({"levels": result}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# สร้าง API GET สำหรับเพิ่มข้อมูล class
@classes_bp.route("/class/insert", methods=["POST"])
@jwt_required()
def insert_class():
    # print("Header:", dict(request.headers))
    data = request.get_json()
    school_id = data.get("school_id")
    class_name = data.get("level_name")

    claims = get_jwt()  # additional_claims ทั้งหมด
    created_by = claims["user_id"]  # ได้ user_id จาก token

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(buffered=True)  # ใช้ buffered เพื่อป้องกัน unread result

        cursor.execute(
            "SELECT class_id FROM classes WHERE class_name = %s AND school_id = %s",
            (class_name, school_id),
        )
        existing_school = cursor.fetchone()

        if existing_school:
            return jsonify({"error": "classes_name already exists"}), 409

        cursor.execute(
            "INSERT INTO classes (class_name, school_id, created_date, created_by) VALUES (%s, %s, NOW(), %s)",
            (class_name, school_id, created_by),
        )
        conn.commit()
        return jsonify({"message": "เพิ่มข้อมูลระดับชั้นเรียบร้อยแล้ว"}), 201

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"message": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# สร้าง API GET สำหรับอัปเดตข้อมูล class
@classes_bp.route("/class/update/<int:level_id>", methods=["PUT"])
@jwt_required()
def update_class(level_id):
    # print("Header:", dict(request.headers))
    data = request.get_json()
    school_id = data.get("school_id")
    level_name = data.get("level_name")
    # class_id = data.get("level_id")

    claims = get_jwt()  # additional_claims ทั้งหมด
    created_by = claims["user_id"]  # ได้ user_id จาก token

    if not level_name or not school_id:
        return jsonify({"message": "Missing data"}), 400

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(buffered=True)

        # ตรวจสอบชื่อซ้ำ (ยกเว้นตัวเอง)
        cursor.execute(
            "SELECT class_id FROM classes WHERE class_name = %s AND school_id = %s",
            (level_name, school_id),  # <- fix tuple
        )
        existing_school = cursor.fetchone()
        if existing_school and existing_school[0] != school_id:
            return jsonify({"error": "school_name already exists"}), 409

        # อัปเดต
        cursor.execute(
            """
            UPDATE classes
            SET class_name = %s, 
                school_id = %s,
                updated_date = NOW(),
                updated_by = %s
            WHERE class_id = %s
            """,
            (level_name, school_id, created_by, level_id),
        )

        conn.commit()

        return jsonify({"message": "school updated successfully"}), 200

    except Exception as e:
        import traceback

        traceback.print_exc()  # เพื่อ debug
        return jsonify({"message": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# สร้าง API GET สำหรับลบข้อมูล class
@classes_bp.route("/class/delete/<int:level_id>", methods=["DELETE"])
@jwt_required()
def delete_classl(level_id):
    
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM classes WHERE class_id = %s", (level_id,))
        conn.commit()
        return jsonify({"message": "Year deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

