DATABASE_NAME = "wallet.db"
TEST_DATABASE_NAME = "../databases/testing.db"
TEST_DATABASE_NAME_WITH_USERS_AND_WALLETS = "users_wallets.db"

USERS_TABLE_NAME = "users"
USERS_TABLE_COLUMNS = "id UUID UNIQUE, " "email TEXT NOT NULL UNIQUE"

WALLETS_TABLE_NAME = "wallets"
WALLETS_TABLE_COLUMNS = "wallet_id TEXT, owner_id TEXT, balance DOUBLE"

TRANSACTIONS_TABLE_NAME = "Transactions"
TRANSACTIONS_TABLE_COLUMNS = (
    "id TEXT, from_id TEXT, to_id TEXT, bitcoin_amount DOUBLE, bitcoin_fee DOUBLE"
)

TRANSACTION_FEE = 0.015

TEST_USER1_ID = "51bb4fc6-9a08-4791-a599-a794543dbde7"
TEST_USER2_ID = "854a7b15-3b4e-4a3c-b100-65bd59ddddba"

TEST_USER1_EMAIL = "email1@gmail.com"
TEST_USER2_EMAIL = "email2@gmail.com"

TEST_USER1_WALLET1 = "8858315c-61cf-4a17-9197-e8880fb57f84"
TEST_USER1_WALLET2 = "23ab2bf9-719d-47dd-95ba-0915175d0f9b"
TEST_USER2_WALLET = "8241a758-407e-4ec1-823f-020f7cf47998"
