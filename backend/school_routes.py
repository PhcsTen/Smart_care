from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import get_db_connection
from datetime import date, datetime
from flask_jwt_extended import get_jwt
import traceback

school_bp = Blueprint("school_bp", __name__)

# สร้าง API GET สำหรับดึงข้อมูล year
@school_bp.route("/school", methods=["GET"])
@jwt_required()
def get_school_info():
    username = get_jwt_identity()  # "admin"
    # claims = get_jwt()              # additional_claims ทั้งหมด
    # created_by = claims["user_id"]     # ได้ user_id จาก token

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM schools ORDER BY school_id ASC")
        schools = cursor.fetchall()

        if not schools:
            return jsonify({"message": "ไม่พบข้อมูลโรงเรียน", "schools": []}), 200
        
        columns = [col[0] for col in cursor.description]
        result = [dict(zip(columns, row)) for row in schools]

        # แปลงวันที่เป็น string
        for item in result:
            for key, value in item.items():
                if isinstance(value, (datetime, date)):
                    item[key] = value.isoformat()

        return jsonify({"current_user": username, "schools": result}), 200
    except Exception as e:
        print("ERROR:", traceback.format_exc())  # DEBUG!
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# สร้าง API GET สำหรับเพิ่มข้อมูล school
@school_bp.route("/school/insert", methods=["POST"])
@jwt_required()
def insert_school():
    #print("Header:", dict(request.headers))
    data = request.get_json()
    # school_id = data.get("school_id")
    school_name = data.get("school_name")
    claims = get_jwt() # additional_claims ทั้งหมด
    created_by = claims["user_id"] # ได้ user_id จาก token

    #print("Headers:", request.headers)
    #print("Content-Type:", request.content_type)
    #print("Raw body:", request.data)

    #print("school_name:", school_name)
    #print("created_by:", created_by)

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(buffered=True)  # ใช้ buffered เพื่อป้องกัน unread result

        cursor.execute(
            "SELECT school_id FROM schools WHERE school_name = %s",
            (school_name,),
        )
        existing_school = cursor.fetchone()

        if existing_school:
            return jsonify({"error": "school_name already exists"}), 409

        cursor.execute(
            "INSERT INTO schools (school_name, created_date, created_by) VALUES (%s, NOW(), %s)",
            (school_name, created_by)
        )
        conn.commit()
        return jsonify({"message": "เพิ่มข้อมูลโรงเรียนเรียบร้อยแล้ว"}), 201

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"message": str(e)}), 500

    finally:
        if cursor: cursor.close()
        if conn: conn.close()


# สร้าง API GET สำหรับอัปเดตข้อมูล school
@school_bp.route("/school/update/<int:school_id>", methods=["PUT"])
@jwt_required()
def update_school(school_id):
    data = request.get_json()
    school_name = data.get("school_name")

    if not school_name:
        return jsonify({"message": "Missing required fields"}), 400

    claims = get_jwt()
    created_by = claims.get("user_id")
    if not created_by:
        return jsonify({"message": "Invalid token"}), 401

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(buffered=True)

        # ตรวจสอบชื่อซ้ำ (ยกเว้นตัวเอง)
        cursor.execute(
            "SELECT school_id FROM schools WHERE school_name = %s",
            (school_name,),  # <- fix tuple
        )
        existing_school = cursor.fetchone()
        if existing_school and existing_school[0] != school_id:
            return jsonify({"error": "school_name already exists"}), 409

        # อัปเดต
        cursor.execute(
            """
            UPDATE schools
            SET school_name = %s,
                updated_date = NOW(),
                updated_by = %s
            WHERE school_id = %s
            """,
            (school_name, created_by, school_id),
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


# สร้าง API GET สำหรับลบข้อมูล year
@school_bp.route("/school/delete/<int:school_id>", methods=["DELETE"])
@jwt_required()
def delete_school(school_id):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM schools WHERE school_id = %s", (school_id,))
        conn.commit()
        return jsonify({"message": "Year deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
