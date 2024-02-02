DATABASE_NAME = "wallet.db"
TEST_DATABASE_NAME = "testing.db"


# UNITS_TABLE_NAME = "Units"
# UNITS_TABLE_COLUMNS = "id TEXT, name TEXT"
#
# PRODUCTS_TABLE_NAME = "Products"
# PRODUCTS_TABLE_COLUMNS = "id TEXT, unit_id TEXT, name TEXT, barcode TEXT, price INTEGER"
#
# RECEIPTS_TABLE_NAME = "Receipts"
# RECEIPTS_TABLE_COLUMNS = "id TEXT, status TEXT, total INTEGER"

TRANSACTIONS_TABLE_NAME = "Transactions"
TRANSACTIONS_TABLE_COLUMNS = (
    "id TEXT, from_id TEXT, to_id TEXT, bitcoin_amount DOUBLE, bitcoin_fee DOUBLE"
)

TRANSACTION_FEE = 0.015
