import mysql.connector
from models import Student
from repository import BaseRepository

if __name__ == "__main__":
    # Cấu hình các tham số kết nối hệ quản trị cơ sở dữ liệu MySQL
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='school_db'
    )

    # Đăng ký Repository dành riêng cho đối tượng Student
    student_repo = BaseRepository(conn, Student)

    # Kiểm thử tác vụ: Insert dữ liệu
    new_student = Student("SE160001", "Nguyễn Văn A", "2002-05-15")
    if student_repo.insert(new_student):
        print("[Thành công] Hệ thống tự động biên dịch và thực thi câu lệnh SQL INSERT.")

    # Kiểm thử tác vụ: Truy vấn dữ liệu theo ID
    sv = student_repo.find_by_id("SE160001")
    if sv:
        print(f"[Thành công] Thực thể truy vấn từ DB thông qua Reflection: {sv.fullname}")

    conn.close()