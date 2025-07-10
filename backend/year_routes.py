from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import get_db_connection
from datetime import date, datetime
from flask_jwt_extended import get_jwt

year_bp = Blueprint("year_bp", __name__)


# สร้าง API GET สำหรับดึงข้อมูล year
@year_bp.route("/academic_years", methods=["GET"])
@jwt_required()
def get_academic_years_info():
    username = get_jwt_identity()   # "admin"
    # claims = get_jwt()              # additional_claims ทั้งหมด
    # created_by = claims["user_id"]     # ได้ user_id จาก token
    
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM academic_years ORDER BY academic_year_id ASC")
        academic_years = cursor.fetchall()

        columns = [col[0] for col in cursor.description]
        result = [dict(zip(columns, row)) for row in academic_years]

        # แปลงวันที่เป็น string
        for item in result:
            for key, value in item.items():
                if isinstance(value, (datetime, date)):
                    item[key] = value.isoformat()

        return jsonify({"current_user": username, "academic_years": result}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# สร้าง API GET สำหรับเพิ่มข้อมูล years
@year_bp.route("/academic_year/insert", methods=["POST"])
@jwt_required()
def insert_year():
    # username = get_jwt_identity()   # "admin"
    claims = get_jwt()              # additional_claims ทั้งหมด
    created_by = claims["user_id"]     # ได้ user_id จาก token
    
    if not request.is_json:
        return jsonify({"message": "Content-Type must be application/json"}), 415

    data = request.get_json()
    year_name = data.get("year_name")
    start_date = data.get("start_date")
    end_date = data.get("end_date")

    if not year_name or not start_date or not end_date:
        return jsonify({"message": "Missing required fields"}), 400

    conn = None
    cursor = None  # กำหนดไว้ก่อน
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # ตรวจว่าปีการศึกษาซ้ำหรือไม่
        cursor.execute(
            "SELECT academic_year_id FROM academic_years WHERE year_name = %s",
            (year_name,),
        )
        existing_year = cursor.fetchone()

        # Conflict
        if existing_year:
            return jsonify({"error": "year_name already exists"}), 409

        # เพิ่มปีการศึกษาใหม่
        cursor.execute(
            """
            INSERT INTO academic_years (year_name, start_date, end_date, created_date, created_by, updated_date)
            VALUES (%s, %s, %s, NOW(), %s, NOW())
        """,
            (year_name, start_date, end_date, created_by),
        )
        conn.commit()
        return jsonify({"message": "Year created successfully"}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# สร้าง API GET สำหรับอัปเดตข้อมูล years
@year_bp.route("/academic_year/update/<int:year_id>", methods=["PUT"])
@jwt_required()
def update_year(year_id):
    # username = get_jwt_identity()   # "admin"
    claims = get_jwt()              # additional_claims ทั้งหมด
    updated_by = claims["user_id"]     # ได้ user_id จาก token
    
    data = request.get_json()
    year_name = data.get("year_name")
    start_date = data.get("start_date")
    end_date = data.get("end_date")

    if not year_name or not start_date or not end_date:
        return jsonify({"message": "Missing required fields"}), 400

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # ตรวจสอบว่าปีการศึกษา (ชื่อ) ซ้ำหรือไม่ ยกเว้นของตัวเอง
        cursor.execute(
            "SELECT academic_year_id FROM academic_years WHERE year_name = %s",
            (year_name,),
        )
        existing_year = cursor.fetchone()
        if existing_year and existing_year[0] != year_id:
            return jsonify({"error": "year_name already exists"}), 409

        # อัปเดตข้อมูล
        cursor.execute(
            """
            UPDATE academic_years
            SET year_name = %s,
                start_date = %s,
                end_date = %s,
                updated_date = NOW(),
                updated_by = %s
            WHERE academic_year_id = %s
        """,
            (year_name, start_date, end_date, updated_by, year_id),
        )
        conn.commit()

        return jsonify({"message": "Year updated successfully"}), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# สร้าง API GET สำหรับลบข้อมูล year
@year_bp.route("/academic_year/delete/<int:year_id>", methods=["DELETE"])
@jwt_required()
def delete_academic_year(year_id):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM academic_years WHERE academic_year_id = %s", (year_id,)
        )
        conn.commit()
        return jsonify({"message": "Year deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
