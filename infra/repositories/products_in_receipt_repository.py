# import uuid
#
# from core.product_in_receipt import ProductInReceipt
# from infra.repositories.database import DatabaseHandler
#
#
# class SqlProductsInReceiptRepository:
#     def __init__(self, database: DatabaseHandler, table_name: str, columns: str):
#         self.database = database
#         self.table_name = table_name
#         self.columns = columns
#
#     def create(self) -> None:
#         self.database.create_table(self.table_name, self.columns)
#
#     def add(self, product: ProductInReceipt) -> None:
#         with self.database.connect() as connection:
#             cursor = connection.cursor()
#             query = f"INSERT INTO {self.table_name} VALUES (?, ?, ?, ?)"
#             cursor.execute(
#                 query,
#                 (
#                     str(product.get_id()),
#                     product.get_quantity(),
#                     product.get_price(),
#                     product.get_total(),
#                 ),
#             )
#             connection.commit()
#
#     def read_all(self) -> list[ProductInReceipt]:
#         with self.database.connect() as connection:
#             cursor = connection.cursor()
#             cursor.execute(f"SELECT * FROM {str(self.table_name)}")
#             values = cursor.fetchall()
#         result = [
#             ProductInReceipt(uuid.UUID(value[0]), value[1], value[2], value[3])
#             for value in values
#         ]
#         return result
#
#     def delete(self) -> None:
#         with self.database.connect() as connection:
#             cursor = connection.cursor()
#             cursor.execute(f"DROP TABLE IF EXISTS {self.table_name}")
#             connection.commit()
