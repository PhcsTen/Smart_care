import bcrypt

# ฟังก์ชันแฮชรหัสผ่านก่อนบันทึก
def hash_password(plain_password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")  # แปลงเป็น string เพื่อเก็บ DB
