# from core.sales import Sales
# from infra.repositories.database import DatabaseHandler
#
#
# class SqlSalesRepository:
#     def __init__(self, database: DatabaseHandler, table_name: str):
#         self.database = database
#         self.table_name = table_name
#
#     def read(self) -> Sales:
#         with self.database.connect() as connection:
#             cursor = connection.cursor()
#             cursor.execute(f"SELECT COUNT(*), SUM(total) FROM {self.table_name}")
#             values = cursor.fetchone()
#             n_receipts = values[0]
#             revenue = 0
#             if n_receipts != 0:
#                 revenue = values[1]
#             return Sales(n_receipts, revenue)
