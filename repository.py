from typing import TypeVar, Generic, Optional, Type, Annotated  # Thêm Annotated vào đây
from typing_extensions import get_args, get_origin
from typing import get_type_hints
import mysql.connector
from models import Field
T = TypeVar('T')

class BaseRepository(Generic[T]):
    def __init__(self, connection, model_class: Type[T]):
        self.conn = connection
        self.model_class = model_class
        
        # REFLECTION 1: Xác định tên bảng (Ưu tiên tên cấu hình trong decorator, ngược lại lấy tên class viết thường)
        self.table_name = getattr(model_class, "__table_name__", model_class.__name__.lower())

        # REFLECTION 2: Quét các trường dữ liệu và khóa chính được định nghĩa qua cấu trúc Annotated
        self.fields = []
        self.primary_keys = []

        type_hints = get_type_hints(self.model_class, include_extras=True)
        for field_name, hint in type_hints.items():
            if get_origin(hint) is Annotated:
                metadata = get_args(hint)  # Trích xuất đối tượng cấu hình Field
                field_obj = next((arg for arg in metadata if isinstance(arg, Field)), None)
                if field_obj:
                    self.fields.append(field_name)
                    if field_obj.primary_key:
                        self.primary_keys.append(field_name)

    def _execute_write(self, sql: str, values: list) -> bool:
        """Phương thức dùng chung để thực thi các tác vụ ghi (Insert, Update, Delete)"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, tuple(values))
            self.conn.commit()
            cursor.close()
            return True
        except mysql.connector.Error as err:
            print(f"[Database Error]: {err}")
            return False

    # 1. Phương thức INSERT (Tự động trích xuất thuộc tính để biên dịch câu lệnh)
    def insert(self, obj: T) -> bool:
        actual_data = vars(obj)  # REFLECTION 3: Lấy dictionary các thuộc tính thực tế của object
        columns = [col for col in actual_data.keys() if col in self.fields]
        placeholders = ", ".join(["%s"] * len(columns))
        values = [actual_data[col] for col in columns]

        sql = f"INSERT INTO {self.table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        return self._execute_write(sql, values)

    # 2. Phương thức FIND BY ID (Tự động map dữ liệu từ DB ngược thành Object)
    def find_by_id(self, *id_args) -> Optional[T]:
        where_clauses = [f"{pk} = %s" for pk in self.primary_keys]
        sql = f"SELECT {', '.join(self.fields)} FROM {self.table_name} WHERE {' AND '.join(where_clauses)}"

        cursor = self.conn.cursor(dictionary=True)  # Thiết lập cấu trúc trả về dạng Dictionary
        cursor.execute(sql, id_args)
        row = cursor.fetchone()
        cursor.close()

        # REFLECTION 4: Áp dụng toán tử ** (kwargs unpacking) để tái tạo bản ghi thành thực thể lớp T
        return self.model_class(**row) if row else None

    # 3. Phương thức DELETE BY ID
    def delete_by_id(self, *id_args) -> bool:
        where_clauses = [f"{pk} = %s" for pk in self.primary_keys]
        sql = f"DELETE FROM {self.table_name} WHERE {' AND '.join(where_clauses)}"
        return self._execute_write(sql, id_args)