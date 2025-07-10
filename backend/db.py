import mysql.connector
from mysql.connector import Error
from config import Config

# เชื่อมต่อฐานข้อมูล
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASS,
            database=Config.DB_DATABASE,
        )
        return connection
    except Error as e:
        print("DB Connection Error:", e)
        raise
