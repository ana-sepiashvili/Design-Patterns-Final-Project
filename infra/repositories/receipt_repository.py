# import uuid
# from uuid import UUID
#
# from core.errors import DoesNotExistError, ReceiptClosedError
# from core.product_in_receipt import ProductInReceipt
# from core.receipt import Receipt, ReceiptProtocol
# from infra.repositories.database import DatabaseHandler
# from infra.repositories.products_in_receipt_repository import (
#     SqlProductsInReceiptRepository,
# )
# from runner.constants import PRODUCTS_IN_REPOSITORY_COLUMNS
#
#
# class SqlReceiptRepository:
#     def __init__(self, database: DatabaseHandler, table_name: str, columns: str):
#         self.database = database
#         self.table_name = table_name
#         self.columns = columns
#
#     def create(self) -> None:
#         self.database.create_table(self.table_name, self.columns)
#
#     def add(self, receipt: ReceiptProtocol) -> None:
#         with self.database.connect() as connection:
#             cursor = connection.cursor()
#             query = f"INSERT INTO {self.table_name} VALUES (?, ?, ?)"
#             cursor.execute(
#                 query,
#                 (
#                     str(receipt.get_id()),
#                     receipt.get_status(),
#                     receipt.get_total(),
#                 ),
#             )
#             connection.commit()
#             products_in_receipt_repo = SqlProductsInReceiptRepository(
#                 self.database,
#                 "a" + str(receipt.get_id()).replace("-", "_"),
#                 PRODUCTS_IN_REPOSITORY_COLUMNS,
#             )
#             products_in_receipt_repo.create()
#
#     def add_product(self, receipt_id: UUID, product: ProductInReceipt) -> None:
#         with self.database.connect() as connection:
#             products_in_receipt_repo = SqlProductsInReceiptRepository(
#                 self.database,
#                 "a" + str(receipt_id).replace("-", "_"),
#                 PRODUCTS_IN_REPOSITORY_COLUMNS,
#             )
#             products_in_receipt_repo.add(product)
#
#             cursor = connection.cursor()
#             cursor.execute(
#                 f"UPDATE {self.table_name} SET total = total + {product.get_total()} "
#                 f"WHERE id = '{str(receipt_id)}'"
#             )
#             connection.commit()
#
#     def read(self, receipt_id: UUID) -> ReceiptProtocol:
#         with self.database.connect() as connection:
#             cursor = connection.cursor()
#             cursor.execute(
#                 f"SELECT * FROM {self.table_name} WHERE id = ?", (str(receipt_id),)
#             )
#             values = cursor.fetchone()
#             if values is None:
#                 raise DoesNotExistError(receipt_id)
#             else:
#                 products_in_receipt_repo = SqlProductsInReceiptRepository(
#                     self.database,
#                     "a" + values[0].replace("-", "_"),
#                     PRODUCTS_IN_REPOSITORY_COLUMNS,
#                 )
#                 return Receipt(
#                     uuid.UUID(values[0]),
#                     values[1],
#                     products_in_receipt_repo.read_all(),
#                     values[2],
#                 )
#
#     def close(self, receipt_id: UUID, status: str) -> None:
#         with self.database.connect() as connection:
#             cursor = connection.cursor()
#             cursor.execute(
#                 f"SELECT * FROM {self.table_name} WHERE id = ?", (str(receipt_id),)
#             )
#             values = cursor.fetchone()
#             if values is None:
#                 raise DoesNotExistError(receipt_id)
#             else:
#                 cursor.execute(
#                     f"UPDATE {self.table_name} SET status = ? WHERE id = ?",
#                     (status, str(receipt_id)),
#                 )
#                 connection.commit()
#
#     def delete(self, receipt_id: UUID) -> None:
#         with self.database.connect() as connection:
#             cursor = connection.cursor()
#             cursor.execute(
#                 f"SELECT * FROM {self.table_name} WHERE id = ?", (str(receipt_id),)
#             )
#             values = cursor.fetchone()
#             if values is None:
#                 raise DoesNotExistError(receipt_id)
#             if values[1] == "closed":
#                 raise ReceiptClosedError(receipt_id)
#             else:
#                 cursor.execute(
#                     f"DELETE FROM {self.table_name} WHERE id = '{str(receipt_id)}'"
#                 )
#                 connection.commit()
#                 products_in_receipt_repo = SqlProductsInReceiptRepository(
#                     self.database,
#                     "a" + str(receipt_id).replace("-", "_"),
#                     PRODUCTS_IN_REPOSITORY_COLUMNS,
#                 )
#                 products_in_receipt_repo.delete()
