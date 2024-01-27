# import uuid
# from uuid import UUID
#
# from core.errors import DoesNotExistError, ExistsError
# from core.product import Product
# from infra.repositories.database import DatabaseHandler
#
#
# class SqlProductRepository:
#     def __init__(self, database: DatabaseHandler, table_name: str, columns: str):
#         self.database = database
#         self.table_name = table_name
#         self.columns = columns
#
#     def create(self) -> None:
#         self.database.create_table(self.table_name, self.columns)
#
#     def add(self, product: Product) -> None:
#         with self.database.connect() as connection:
#             cursor = connection.cursor()
#             cursor.execute(
#                 f"SELECT * FROM {self.table_name} WHERE barcode = ?",
#                 (product.get_barcode(),),
#             )
#             elems = cursor.fetchone()
#             if elems is not None:
#                 raise ExistsError(product.get_barcode())
#             else:
#                 query = f"INSERT INTO {self.table_name} VALUES (?, ?, ?, ?, ?)"
#                 cursor.execute(
#                     query,
#                     (
#                         str(product.get_id()),
#                         str(product.get_unit_id()),
#                         product.get_name(),
#                         product.get_barcode(),
#                         product.get_price(),
#                     ),
#                 )
#                 connection.commit()
#
#     def read(self, product_id: uuid.UUID) -> Product:
#         with self.database.connect() as connection:
#             cursor = connection.cursor()
#             cursor.execute(
#                 f"SELECT * FROM {self.table_name} WHERE id = ?", (str(product_id),)
#             )
#             values = cursor.fetchone()
#             if values is None:
#                 raise DoesNotExistError(product_id)
#             else:
#                 return Product(
#                     uuid.UUID(values[1]),
#                     values[2],
#                     values[3],
#                     values[4],
#                     uuid.UUID(values[0]),
#                 )
#
#     def read_all(self) -> list[Product]:
#         with self.database.connect() as connection:
#             cursor = connection.cursor()
#             cursor.execute(f"SELECT * FROM {self.table_name}")
#             values = cursor.fetchall()
#         result = [
#             Product(
#                 uuid.UUID(value[1]), value[2], value[3], value[4], uuid.UUID(value[0])
#             )
#             for value in values
#         ]
#         return result
#
#     def update(self, product_id: UUID, price: int) -> None:
#         with self.database.connect() as connection:
#             cursor = connection.cursor()
#             cursor.execute(
#                 f"SELECT * FROM {self.table_name} WHERE id = ?", (str(product_id),)
#             )
#             values = cursor.fetchone()
#             if values is None:
#                 raise DoesNotExistError(product_id)
#             else:
#                 cursor.execute(
#                     f"UPDATE {self.table_name} SET price = {price} "
#                     f"WHERE id = '{str(product_id)}'"
#                 )
#                 connection.commit()
