from typing import Annotated
from typing_extensions import get_args, get_origin

def table(name: str):
    def decorator(cls):
        cls.__table_name__ = name  # Lưu tên bảng ẩn vào thuộc tính của Class
        return cls
    return decorator

class Field:
    def __init__(self, sql_type: str, primary_key: bool = False):
        self.sql_type = sql_type
        self.primary_key = primary_key

@table("tbl_sinh_vien")
class Student:
    rollnumber: Annotated[str, Field(sql_type="VARCHAR(20)", primary_key=True)]
    fullname: Annotated[str, Field(sql_type="VARCHAR(100)")]
    dob: Annotated[str, Field(sql_type="DATE")]

    def __init__(self, rollnumber, fullname, dob):
        self.rollnumber = rollnumber
        self.fullname = fullname
        self.dob = dob