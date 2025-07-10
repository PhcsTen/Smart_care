import os
from dotenv import load_dotenv

# โหลดค่า .env
load_dotenv()

# เชื่อมต่อฐานข้อมูล
class Config:
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "smartcare")
    DB_HOST = os.getenv("DB_HOST")
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASS")
    DB_DATABASE = os.getenv("DB_DATABASE")