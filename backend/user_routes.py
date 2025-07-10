from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import get_db_connection
from utils import hash_password
from flask_jwt_extended import get_jwt

user_bp = Blueprint("user_bp", __name__)

# ✅ ดึง user info ของตัวเอง
@user_bp.route("/user/me", methods=["GET"])
@jwt_required()
def get_current_user():
    username = get_jwt_identity()   # "admin"
    # claims = get_jwt()              # additional_claims ทั้งหมด
    # created_by = claims["user_id"]     # ได้ user_id จาก token

    # print("created_by:", created_by)

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE user_name = %s", (username,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"message": "User not found"}), 404
        return jsonify({
            "user_id": user["user_id"],
            "user_name": user["user_name"],
            "email": user["email"],
        })
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


# ✅ ดึงผู้ใช้ทั้งหมด (ยกเว้น admin)
@user_bp.route("/user", methods=["GET"])
@jwt_required()
def get_user_info():
    username = get_jwt_identity()
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_name != 'admin' ORDER BY user_id ASC")
        users = cursor.fetchall()
        if users:
            columns = [col[0] for col in cursor.description]
            result = [dict(zip(columns, row)) for row in users]
            return jsonify({"current_user": username, "users": result}), 200
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


# ✅ เพิ่มผู้ใช้ใหม่
@user_bp.route("/user/insert", methods=["POST"])
@jwt_required()
def insert_user():
    # username = get_jwt_identity()   # "admin"
    claims = get_jwt()              # additional_claims ทั้งหมด
    created_by = claims["user_id"]     # ได้ user_id จาก token

    print("created_by:", created_by)

    if not request.is_json:
        return jsonify({"message": "Content-Type must be application/json"}), 415

    data = request.get_json()
    user_name = data.get("user_name")
    email = data.get("email")
    password = data.get("password")

    if not user_name or not email or not password:
        return jsonify({"message": "Missing required fields"}), 400

    hashed_password = hash_password(password)
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users WHERE user_name = %s", (user_name,))
        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({"error": "Username already exists"}), 409

        cursor.execute("""
            INSERT INTO users (user_name, password, email, created_date, created_by, updated_date)
            VALUES (%s, %s, %s, NOW(), %s, NOW())
        """, (user_name, hashed_password, email, created_by))
        conn.commit()
        return jsonify({"message": "User created successfully"}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


# ✅ อัปเดตข้อมูลผู้ใช้
@user_bp.route("/user/update/<int:user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id):
    # username = get_jwt_identity()   # "admin"
    claims = get_jwt()              # additional_claims ทั้งหมด
    updated_by = claims["user_id"]     # ได้ user_id จาก token


    data = request.get_json()
    user_name = data.get("user_name")
    email = data.get("email")
    password = data.get("password")

    if not user_name or not email:
        return jsonify({"message": "Missing required fields"}), 400

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if password:
            hashed_password = hash_password(password)
            cursor.execute("""
                UPDATE users
                SET user_name = %s,
                    email = %s,
                    password = %s,
                    updated_date = NOW(),
                    updated_by = %s
                WHERE user_id = %s
            """, (user_name, email, hashed_password, updated_by, user_id))
        else:
            cursor.execute("""
                UPDATE users
                SET user_name = %s,
                    email = %s,
                    updated_date = NOW(),
                    updated_by = %s
                WHERE user_id = %s
            """, (user_name, email, updated_by, user_id))

        conn.commit()
        return jsonify({"message": "User updated successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


# ✅ ลบผู้ใช้
@user_bp.route("/user/delete/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        conn.commit()
        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
