from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import bcrypt
from fastapi import FastAPI

# ฟังก์ชันแฮชรหัสผ่านก่อนบันทึก
def hash_password(plain_password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed


# โหลดค่า .env
load_dotenv()

app = Flask(__name__)
CORS(app)

# JWT Secret
app.config["JWT_SECRET_KEY"] = "smartcare"  # key
jwt = JWTManager(app)


# เชื่อมต่อฐานข้อมูล
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            database=os.getenv("DB_DATABASE"),
        )
        return connection
    except Error as e:
        print("DB Connection Error:", e)
        raise


# สร้าง API POST สำหรับ Login
@app.route("/login", methods=["POST"])
def login():
    if not request.is_json:
        return jsonify({"message": "Missing JSON in request"}), 400

    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "username and password are required"}), 400

    conn = None
    cursor = None  # กำหนดไว้ก่อน
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE user_name = %s", (username,))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(
            password.encode("utf-8"), user["password"].encode("utf-8")
        ):
            access_token = create_access_token(identity=username)
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


# สร้าง API GET สำหรับดึงข้อมูลเฉพาะ user
@app.route("/user/me", methods=["GET"])
@jwt_required()
def get_current_user():
    username = get_jwt_identity()

    conn = None
    cursor = None  # กำหนดไว้ก่อน
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE user_name = %s", (username,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"message": "User not found"}), 404

        return jsonify(
            {
                "user_id": user["user_id"],
                "user_name": user["user_name"],
                "email": user["email"],
            }
        )

    except Exception as e:
        return jsonify({"message": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# สร้าง API GET สำหรับดึงข้อมูล user
@app.route("/user", methods=["GET"])
@jwt_required()  # บังคับให้ต้องมี JWT access token
def get_user_info():
    current_user = get_jwt_identity()  # ดึงข้อมูล identity จาก token

    conn = None
    cursor = None  # กำหนดไว้ก่อน
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE user_name != 'admin' ORDER BY user_id ASC"
        )
        users = cursor.fetchall()

        if users:
            columns = [col[0] for col in cursor.description]
            result = [dict(zip(columns, row)) for row in users]
            return (
                jsonify(
                    {"current_user": current_user, "users": result}  # แสดงว่าใครเรียก API
                ),
                200,
            )
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# สร้าง API GET สำหรับเพิ่มข้อมูล user
@app.route("/user/insert", methods=["POST"])
@jwt_required()
def insert_user():
    if not request.is_json:
        return jsonify({"message": "Content-Type must be application/json"}), 415

    data = request.get_json()
    user_name = data.get("user_name")
    email = data.get("email")
    password = data.get("password")

    hashed_password = hash_password(password)

    if not user_name or not email or not password:
        return jsonify({"message": "Missing required fields"}), 400

    conn = None
    cursor = None  # กำหนดไว้ก่อน
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 🔎 ตรวจว่าชื่อซ้ำหรือไม่
        cursor.execute("SELECT user_id FROM users WHERE user_name = %s", (user_name,))
        existing_user = cursor.fetchone()

        if existing_user:
            return jsonify({"error": "Username already exists"}), 409  # Conflict

        # เพิ่มผู้ใช้ใหม่
        cursor.execute(
            """
            INSERT INTO users (user_name, password, email, created_date, updated_date)
            VALUES (%s, %s, %s, NOW(), NOW())
            """,
            (user_name, hashed_password, email),
        )
        conn.commit()

        return jsonify({"message": "User created successfully"}), 201

    except Exception as e:
        return jsonify({"message": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# สร้าง API GET สำหรับอัปเดตข้อมูล user
@app.route("/user/update/<int:user_id>", methods=["PUT"])
@jwt_required()
def update_user(user_id):
    data = request.get_json()
    user_name = data.get("user_name")
    email = data.get("email")
    password = data.get("password")  # อาจจะ None

    # print("password in request:", password)

    if not user_name or not email:
        return jsonify({"message": "Missing required fields"}), 400

    conn = None
    cursor = None  # กำหนดไว้ก่อน
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # ถ้ามีการส่ง password → อัปเดตรหัสผ่านด้วย
        if password:
            hashed_password = hash_password(password)
            cursor.execute(
                """
                UPDATE users
                SET user_name = %s,
                    email = %s,
                    password = %s,
                    updated_date = NOW()
                WHERE user_id = %s
                """,
                (user_name, email, hashed_password, user_id),
            )
        else:
            # ไม่ส่ง password → ไม่อัปเดต password
            cursor.execute(
                """
                UPDATE users
                SET user_name = %s,
                    email = %s,
                    updated_date = NOW()
                WHERE user_id = %s
                """,
                (user_name, email, user_id),
            )

        conn.commit()
        return jsonify({"message": "User updated successfully"}), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# สร้าง API GET สำหรับลบข้อมูล user
@app.route("/user/delete/<int:user_id>", methods=["DELETE"])
@jwt_required()
def delete_user(user_id):

    conn = None
    cursor = None  # กำหนดไว้ก่อน
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        conn.commit()
        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    app.run(debug=True)
