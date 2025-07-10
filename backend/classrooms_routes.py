from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import get_db_connection  # ฟังก์ชันที่คุณสร้างไว้เพื่อเชื่อม MySQL
from datetime import date, datetime
from flask_jwt_extended import get_jwt
import traceback

classrooms_bp = Blueprint("classrooms_bp", __name__)


# ดึงห้องทั้งหมด
@classrooms_bp.route("/classrooms", methods=["GET"])
@jwt_required()
def get_classrooms():
    claims = get_jwt()
    created_by = claims["user_id"]

    conn = None
    cursor = None

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
            SELECT 
                c.classroom_id,
                c.classroom_name,
                c.class_id,
                cls.class_name,
                c.classroom_male,
                c.classroom_female,
                c.classroom_all,
                c.school_id,
                s.school_name,
                GROUP_CONCAT(CONCAT(t.prefix_name, t.first_name, ' ', t.last_name) SEPARATOR ', ') AS teacher_name
            FROM classrooms c
            INNER JOIN classes cls ON c.class_id = cls.class_id
            INNER JOIN schools s ON c.school_id = s.school_id
            LEFT JOIN classroom_teachers ct ON c.classroom_id = ct.classroom_id
            LEFT JOIN teachers t ON ct.teacher_id = t.teacher_id
            WHERE c.created_by = %s
            GROUP BY 
                c.classroom_id,
                c.classroom_name,
                c.class_id,
                cls.class_name,
                c.classroom_male,
                c.classroom_female,
                c.classroom_all,
                c.school_id,
                s.school_name
            ORDER BY c.classroom_name
        """

        cursor.execute(query, (created_by,))
        classrooms = cursor.fetchall()

        if not classrooms:
            return jsonify({"message": "No classrooms found"}), 404

        return jsonify(classrooms), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# เพิ่มห้อง
@classrooms_bp.route("/classrooms/insert", methods=["POST"])
@jwt_required()
def insert_classrooms():
    import traceback

    identity = get_jwt_identity()
    username = identity  # เช่น "admin" (string)

    if not request.is_json:
        return jsonify({"message": "Content-Type must be application/json"}), 415

    data = request.get_json()

    room_name = data.get("room_name")
    room_male = data.get("room_male")
    room_female = data.get("room_female")
    room_all = data.get("room_all")
    level_id = data.get("level_id")
    school_id = data.get("school_id")
    teacher_ids = data.get("teacher_id")  # ควรเป็น list เช่น [1, 2]

    if (
        not room_name
        or level_id is None
        or school_id is None
        or not isinstance(teacher_ids, list)
    ):
        return jsonify({"message": "Missing or invalid required fields"}), 400

    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # ✅ อ่าน result ทันที ป้องกัน unread result
        cursor.execute("SELECT user_id FROM users WHERE user_name = %s", (username,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"message": "User not found"}), 404
        created_by = user[0]

        print(">>> Creating classroom:", room_name)
        print(">>> Teachers:", teacher_ids)

        # ✅ Insert classroom
        cursor.execute(
            """
            INSERT INTO classrooms (
                classroom_name, class_id, classroom_male, classroom_female,
                classroom_all, school_id, created_date, created_by
            )
            VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s)
        """,
            (
                room_name,
                level_id,
                room_male,
                room_female,
                room_all,
                school_id,
                created_by,
            ),
        )
        class_id = cursor.lastrowid

        # ✅ Insert teachers
        for teacher_id in teacher_ids:
            cursor.execute(
                """
                INSERT INTO classroom_teachers (classroom_id, teacher_id)
                VALUES (%s, %s)
            """,
                (class_id, teacher_id),
            )

        conn.commit()
        return jsonify({"message": "เพิ่มห้องเรียนเรียบร้อย", "class_id": class_id}), 201

    except Exception as e:
        print(">>> ERROR:", str(e))
        traceback.print_exc()
        return jsonify({"message": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ✅ อัปเดตข้อมูลห้อง
@classrooms_bp.route("/classrooms/update/<int:classroom_id>", methods=["PUT"])
@jwt_required()
def update_classrooms(classroom_id):
    # username = get_jwt_identity()   # "admin"
    claims = get_jwt()              # additional_claims ทั้งหมด
    created_by = claims["user_id"]     # ได้ user_id จาก token

    data = request.get_json()
    print("📦 รับข้อมูลมา:", data)

    room_name = data.get("room_name")
    room_male = data.get("room_male")
    room_female = data.get("room_female")
    room_all = data.get("room_all")
    level_id = data.get("level_id")
    school_id = data.get("school_id")
    teacher_ids = data.get("teacher_id", [])

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # ✅ อัปเดตตาราง classrooms
        update_query = """
            UPDATE classrooms 
            SET classroom_name=%s, class_id=%s, classroom_male=%s, classroom_female=%s, classroom_all=%s,  school_id=%s, updated_by=%s, updated_date=NOW() 
            WHERE classroom_id=%s
        """
        cursor.execute(update_query, (
            room_name, level_id,  room_male, room_female, room_all,  school_id, created_by, classroom_id
        ))

        # ✅ ลบครูเดิม
        cursor.execute("DELETE FROM classroom_teachers WHERE classroom_id = %s", (classroom_id,))

        # ✅ เพิ่มครูใหม่
        insert_teacher_query = "INSERT INTO classroom_teachers (classroom_id, teacher_id) VALUES (%s, %s)"
        for tid in teacher_ids:
            cursor.execute(insert_teacher_query, (classroom_id, tid))

        conn.commit()
        return jsonify({"message": "Classroom updated successfully"}), 200

    except Exception as e:
        if conn:
            conn.rollback()
        traceback.print_exc()  # เพิ่มบรรทัดนี้เพื่อพิมพ์ stack trace    
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



# # ✅ ลบห้อง
@classrooms_bp.route("/classrooms/delete/<int:classroom_id>", methods=["DELETE"])
@jwt_required()
def delete_classroom(classroom_id):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # ลบความสัมพันธ์ครูกับห้องเรียนก่อน (ถ้ามีตารางเชื่อม many-to-many)
        delete_teachers_query = """
            DELETE FROM classroom_teachers WHERE classroom_id = %s
        """
        cursor.execute(delete_teachers_query, (classroom_id,))

        # ลบห้องเรียนหลัก
        delete_classroom_query = """
            DELETE FROM classrooms WHERE classroom_id = %s
        """
        cursor.execute(delete_classroom_query, (classroom_id,))

        conn.commit()

        return jsonify({"message": "Classroom deleted successfully"}), 200

    except Exception as e:
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
