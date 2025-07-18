from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import get_db_connection
from datetime import date, datetime
from flask_jwt_extended import get_jwt
from flask import send_from_directory
import base64
import os

student_bp = Blueprint("student_bp", __name__)

# กำหนด path uploads จริง
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')  # /backend/uploads

@student_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    print(f"Request for image: {filename}")
    return send_from_directory(UPLOAD_FOLDER, filename)

# สร้าง API GET ดึงข้อมูล student
# ฟังก์ชันช่วยแยกที่อยู่ (ไม่จำเป็นต้องใช้ถ้าแค่ rename key)
def parse_address(address_string):
    try:
        parts = address_string.strip().split(" ")
        zip_code = parts[-1]
        province = parts[-2]
        district = parts[-3]
        subdistrict = parts[-4]
        number_and_street = " ".join(parts[:-4])
        return {
            "number": number_and_street,
            "subdistrict": subdistrict,
            "district": district,
            "province": province,
            "zip_code": zip_code
        }
    except Exception:
        return {
            "number": address_string,
            "subdistrict": "",
            "district": "",
            "province": "",
            "zip_code": ""
        }

@student_bp.route("/students_all", methods=["GET"])
@jwt_required()
def get_students_all():
    username = get_jwt_identity()

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT 
                student_id, id_card_number, student_code, prefix_name, 
                first_name, last_name, nickname, gender, birth_date, 
                age_range, qr_code, present_address, permanent_address, 
                latitude, longitude, is_active, student_photo, bmi, 
                blood_group, created_date, created_by, updated_date, updated_by 
            FROM students
            """
        )

        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        result = [dict(zip(columns, row)) for row in rows]

        for item in result:
            # แปลงวันที่ให้เป็น string
            for key, value in item.items():
                if isinstance(value, (datetime, date)):
                    item[key] = value.isoformat()

            # ✅ เปลี่ยนชื่อคีย์ present_address ➜ selectedFullAddressPresent
            item["selectedFullAddressPresent"] = item.pop("present_address")

            # ✅ เปลี่ยนชื่อคีย์ permanent_address ➜ selectedFullAddressPermanent
            item["selectedFullAddressPermanent"] = item.pop("permanent_address")

        return jsonify({"current_user": username, "students": result}), 200

    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# สร้าง API POST สำหรับดึงข้อมูล student
@student_bp.route("/student/insert", methods=["POST"])
@jwt_required()
def insert_student():
    # username = get_jwt_identity()  # "admin"
    claims = get_jwt()  # additional_claims ทั้งหมด
    created_by = claims["user_id"]  # ได้ user_id จาก token

    try:
        data = request.get_json()
        

        # ดึงข้อมูลจาก JSON
        id_card_number = data.get("id_card_number")
        student_code = data.get("student_code")
        prefix_name = data.get("prefix_name")
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        nickname = data.get("nickname")
        gender = data.get("gender")
        # birth_date = data.get("birth_date")
        age_range = data.get("age_range")
        qr_code = data.get("qr_code") or student_code

        present_address = data.get("present_address")
        permanent_address = data.get("permanent_address")
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        
        #is_active = data.get("is_active")
        is_active = 1 if str(data.get("is_active")).lower() in ["1", "true"] else 0

        #print("📦 is_active:", is_active)  # <-- ตรวจว่าค่าเข้ามาเป็นอะไร

        bmi = data.get("bmi")
        blood_group = data.get("blood_group")

        # created_by = get_jwt_identity()
        created_date = datetime.now()
        updated_by = None
        updated_date = None

        print("permanant_address:", permanent_address)

        student_photo = data.get("image")
        raw_date = data.get("birth_date")  # เช่น '2019-07-22T17:00:00.000Z'

        if raw_date:
            # แปลงเป็น datetime object (ตัดตัว Z ออก หรือใช้ fromisoformat แก้ทีหลัง)
            birth_date_obj = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))

            # แปลงกลับเป็น string ที่ MySQL รับได้ (YYYY-MM-DD)
            birth_date_str = birth_date_obj.strftime("%Y-%m-%d")
        else:
            birth_date_str = None

        # 🔐 แปลงและบันทึกรูปภาพ base64 (ถ้ามี)
        img_filename = None
        if student_photo:
            try:
                header, encoded = student_photo.split(",", 1)
                img_bytes = base64.b64decode(encoded)
                img_filename = f"student_{student_code}.jpg"
                os.makedirs("uploads", exist_ok=True)
                img_path = os.path.join("uploads", img_filename)
                with open(img_path, "wb") as f:
                    f.write(img_bytes)
            except Exception as img_err:
                print("⚠️ ไม่สามารถบันทึกรูปภาพได้:", img_err)
                img_filename = None

        permanent_address = data.get("permanent_address")
        if permanent_address is None:
            permanent_address = ""

        # ✅ เชื่อมต่อฐานข้อมูล
        conn = get_db_connection()
        cursor = conn.cursor()

        # 👇 เพิ่มเข้า DB
        cursor.execute(
            """
            INSERT INTO students (
                id_card_number, student_code, prefix_name, first_name, last_name,
                nickname, gender, birth_date, age_range, qr_code,
                present_address, permanent_address, latitude, longitude,
                is_active, student_photo, bmi, blood_group,
                created_date, created_by, updated_date, updated_by
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
            (
                id_card_number,
                student_code,
                prefix_name,
                first_name,
                last_name,
                nickname,
                gender,
                birth_date_str,
                age_range,
                qr_code,
                present_address,
                permanent_address,
                latitude,
                longitude,
                is_active,
                img_filename,
                bmi,
                blood_group,
                created_date,
                created_by,
                updated_date,
                updated_by,
            ),
        )

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "เพิ่มนักเรียนสำเร็จ"}), 200

    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"error": str(e)}), 500


# API to update student
@student_bp.route("/student/update/<int:student_id>", methods=["PUT"])
@jwt_required()
def update_student(student_id):
    claims = get_jwt()
    updated_by = claims["user_id"]

    try:
        data = request.get_json()

        # Process birth date
        raw_date = data.get("birth_date")
        birth_date_str = None
        if raw_date:
            try:
                birth_date_obj = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
                birth_date_str = birth_date_obj.strftime("%Y-%m-%d")
            except Exception as date_err:
                print("⚠️ Date format error:", date_err)

        # Process image
        img_filename = None
        student_photo = data.get("student_photo")
        if student_photo and "," in student_photo:
            try:
                header, encoded = student_photo.split(",", 1)
                img_bytes = base64.b64decode(encoded)
                student_code = data.get("student_code", "temp")
                img_filename = f"student_{student_code}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
                os.makedirs("uploads/students", exist_ok=True)
                img_path = os.path.join("uploads/students", img_filename)
                with open(img_path, "wb") as f:
                    f.write(img_bytes)
            except Exception as img_err:
                print("⚠️ Image processing error:", img_err)

        # ✅ Dynamic field update
        fields = []
        values = []

        def add_field(key, val):
            if val not in [None, ""]:
                fields.append(f"{key} = %s")
                values.append(val)

        add_field("id_card_number", data.get("id_card_number"))
        add_field("student_code", data.get("student_code"))
        add_field("prefix_name", data.get("prefix_name"))
        add_field("first_name", data.get("first_name"))
        add_field("last_name", data.get("last_name"))
        add_field("nickname", data.get("nickname"))
        add_field("gender", data.get("gender"))
        add_field("birth_date", birth_date_str)
        add_field("age_range", data.get("age_range"))
        add_field("present_address", data.get("present_address"))
        add_field("permanent_address", data.get("permanent_address"))
        add_field("latitude", data.get("latitude"))
        add_field("longitude", data.get("longitude"))
        add_field("bmi", data.get("bmi"))
        add_field("blood_group", data.get("blood_group"))

        # ✅ is_active: force convert
        if "is_active" in data:
            is_active = str(data.get("is_active")).lower()
            values.append(1 if is_active in ["1", "true", "yes"] else 0)
            fields.append("is_active = %s")

        if img_filename:
            fields.append("student_photo = %s")
            values.append(img_filename)

        # ✅ Always update updated_by and updated_date
        fields.append("updated_by = %s")
        values.append(updated_by)
        fields.append("updated_date = NOW()")

        # Build final SQL
        sql = f"""
            UPDATE students
            SET {', '.join(fields)}
            WHERE student_id = %s
        """
        values.append(student_id)

        # Run query
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql, tuple(values))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Student updated successfully", "student_id": student_id}), 200

    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"error": str(e)}), 500


# API to delete student
@student_bp.route("/student/delete/<int:student_id>", methods=["DELETE"])
@jwt_required()
def delete_student(student_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 1. ดึงชื่อรูปก่อนลบ
        cursor.execute("SELECT student_photo FROM students WHERE student_id = %s", (student_id,))
        result = cursor.fetchone()

        if not result:
            return jsonify({"message": "Student not found"}), 404

        student_photo = result.get("student_photo")

        # 2. ลบรูปใน filesystem ถ้ามี
        if student_photo:
            # สมมุติโฟลเดอร์อยู่ที่ /backend/uploads หรือ uploads/students
            photo_path = os.path.join(os.getcwd(), "uploads", student_photo)
            if os.path.exists(photo_path):
                os.remove(photo_path)
                print(f"✅ ลบรูปภาพแล้ว: {photo_path}")
            else:
                print(f"⚠️ ไม่พบรูปภาพที่ต้องลบ: {photo_path}")

        # 3. ลบข้อมูลในฐานข้อมูล
        cursor.execute("DELETE FROM students WHERE student_id = %s", (student_id,))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"message": "Student deleted successfully", "student_id": student_id}), 200

    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"error": str(e)}), 500


# API to get single student
@student_bp.route("/student/<int:student_id>", methods=["GET"])
@jwt_required()
def get_student(student_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT 
                student_id, id_card_number, student_code, 
                prefix_name, first_name, last_name, nickname, 
                gender, birth_date, age_range, present_address, 
                permanent_address, latitude, longitude, is_active, 
                student_photo, bmi, blood_group
            FROM students 
            WHERE student_id = %s
        """,
            (student_id,),
        )

        student = cursor.fetchone()
        cursor.close()
        conn.close()

        if not student:
            return jsonify({"message": "Student not found"}), 404

        return jsonify(student), 200

    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"error": str(e)}), 500