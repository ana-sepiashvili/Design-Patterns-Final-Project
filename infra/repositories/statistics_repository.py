from uuid import UUID

from core.constants import ADMIN_API_KEY
from core.errors import NoAccessError
from core.statistics import StatisticsProtocol, Statistics
from infra.repositories.database import DatabaseHandler


class SqlStatisticsRepository:
    def __init__(self, db: DatabaseHandler, table: str, vals: str) -> None:
        self.database = db
        self.table_name = table
        self.columns = vals

    def read_statistics(self, admin_key: UUID) -> StatisticsProtocol:
        if str(admin_key) != ADMIN_API_KEY:
            raise NoAccessError(str(admin_key))

        with self.database.connect() as connection:
            cursor = connection.cursor()
            cursor.execute(f"SELECT COUNT(*), SUM(bitcoin_fee) FROM {self.table_name}")

            values = cursor.fetchone()
            n_transactions = values[0]
            profit = 0.0
            if n_transactions != 0:
                profit = values[1]
            return Statistics(n_transactions, profit)
