# import uuid
#
# from core.errors import DoesNotExistError, ExistsError
# from core.unit import Unit
# from infra.repositories.database import DatabaseHandler
#
#
# class SqlUnitRepository:
#     def __init__(self, database: DatabaseHandler, table_name: str, columns: str):
#         self.database = database
#         self.table_name = table_name
#         self.columns = columns
#
#     def create(self) -> None:
#         self.database.create_table(self.table_name, self.columns)
#
#     def add(self, unit: Unit) -> None:
#         with self.database.connect() as connection:
#             cursor = connection.cursor()
#             cursor.execute(
#                 f"SELECT * FROM {self.table_name} WHERE name = ?", (unit.get_name(),)
#             )
#             elems = cursor.fetchone()
#             if elems is not None:
#                 raise ExistsError(unit.get_name())
#             else:
#                 query = f"INSERT INTO {self.table_name} VALUES (?, ?)"
#                 cursor.execute(query, (str(unit.get_id()), unit.get_name()))
#
#     def read(self, unit_id: uuid.UUID) -> Unit:
#         with self.database.connect() as connection:
#             cursor = connection.cursor()
#             cursor.execute(
#                 f"SELECT * FROM {self.table_name} WHERE id = ?", (str(unit_id),)
#             )
#             values = cursor.fetchone()
#             if values is None:
#                 raise DoesNotExistError(unit_id)
#             else:
#                 return Unit(values[1], uuid.UUID(values[0]))
#
#     def read_all(self) -> list[Unit]:
#         with self.database.connect() as connection:
#             cursor = connection.cursor()
#             cursor.execute(f"SELECT * FROM {self.table_name}")
#             values = cursor.fetchall()
#         result = [Unit(value[1], uuid.UUID(value[0])) for value in values]
#         return result
