from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from db import get_db_connection
import bcrypt
from flask_cors import CORS

auth_bp = Blueprint("auth_bp", __name__)

# สร้าง API POST สำหรับ Login


@auth_bp.route("/login", methods=["POST"])
def login():
    if not request.is_json:
        return jsonify({"message": "Missing JSON in request"}), 400

    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    print("username:",username)
    # print("password:",password)

    if not username or not password:
        return jsonify({"message": "username and password are required"}), 400

    conn = None
    cursor = None  # กำหนดไว้ก่อน
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE user_name = %s", (username,))
        user = cursor.fetchone()

        # print("user:",user)

        if user and bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
            # ใส่แค่ username ลงไปใหน่วยความจำ
            # access_token = create_access_token(identity=username)
            access_token = create_access_token(
                identity=user["user_name"],
                additional_claims={"user_id": user["user_id"]}
            )

            # print("access_token:",access_token)

            return jsonify({"access_token": access_token}), 200
        else:
            return jsonify({"message": "ข้อมูลไม่ถูกต้อง"}), 401
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
