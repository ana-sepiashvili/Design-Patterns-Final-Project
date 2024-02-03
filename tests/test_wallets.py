import uuid
from unittest.mock import ANY
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from core.converter import btc_to_usd
from fake import Fake
from runner.constants import TEST_DATABASE_NAME, DEFAULT_BALANCE
from runner.setup import init_app
from runner.setup_database import create_database


@pytest.fixture
def client() -> TestClient:
    create_database(TEST_DATABASE_NAME)
    return TestClient(init_app(TEST_DATABASE_NAME))


def test_shouldnt_create_for_unknown(client: TestClient) -> None:
    wallet = Fake().wallet({})
    response = client.post("/wallets", json=wallet)

    expected = {"message": f"User with id<{wallet['owner_id']}> does not exist."}
    assert response.status_code == 400
    assert response.json() == {"error": expected}


def test_should_create(client: TestClient) -> None:
    user = Fake().user()
    response = client.post("/users", json=user)
    owner_id = response.json()["id"]
    wallet = Fake().wallet({"owner_id": owner_id})
    response = client.post("/wallets", json=wallet)

    print("TTTTTTTTTTTTT")
    print(btc_to_usd(1.0))
    expected = {"wallet_id": ANY,
                "balance_btc": DEFAULT_BALANCE,
                "balance_usd": btc_to_usd(DEFAULT_BALANCE)}
    assert response.status_code == 201
    assert response.json() == {"wallet": expected}


def test_should_not_create_more_than_three(client: TestClient) -> None:
    user = Fake().user()
    response = client.post("/users", json=user)
    owner_id = response.json()["id"]
    fake_dict = {"owner_id": owner_id}
    wallet1 = Fake().wallet(fake_dict)
    client.post("/wallets", json=wallet1)
    wallet2 = Fake().wallet(fake_dict)
    client.post("/wallets", json=wallet2)
    wallet3 = Fake().wallet(fake_dict)
    client.post("/wallets", json=wallet3)
    wallet4 = Fake().wallet(fake_dict)
    response = client.post("/wallets", json=wallet4)
    err_msg = f"User with id<{fake_dict['owner_id']}> already has 3 wallets."
    message = {"message": err_msg}
    expected = {"error": message}

    assert response.status_code == 409
    assert response.json() == expected


def test_should_not_read_unknown(client: TestClient) -> None:
    unknown_id = uuid4()

    response = client.get(f"/wallets/{unknown_id}")
    message = {"message": f"Wallet with id<{unknown_id}> does not exist."}
    expected = {"error": message}

    assert response.status_code == 404
    assert response.json() == expected


def test_should_read_exsistent(client: TestClient) -> None:
    user = Fake().user()
    response = client.post("/users", json=user)
    owner_id = response.json()["id"]
    wallet = Fake().wallet({"owner_id": owner_id})
    response = client.post("/wallets", json=wallet)
    wallet_id = uuid.UUID(response.json()["wallet"]["wallet_id"])
    response = client.get(f"/wallets/{wallet_id}")

    expected = {"wallet_id": ANY,
                "balance_btc": DEFAULT_BALANCE,
                "balance_usd": btc_to_usd(DEFAULT_BALANCE)}
    assert response.status_code == 200
    assert response.json() == {"wallet": expected}


def test_should_get_transactions(client: TestClient) -> None:
    user1 = Fake().user()
    response = client.post("/users", json=user1)
    owner1_id = response.json()["id"]
    user2 = Fake().user()
    response = client.post("/users", json=user2)
    owner2_id = response.json()["id"]
    wallet1 = Fake().wallet({"owner_id": owner1_id})
    response = client.post("/wallets", json=wallet1)
    wallet1_id = response.json()["wallet"]["wallet_id"]
    wallet2 = Fake().wallet({"owner_id": owner2_id})
    response = client.post("/wallets", json=wallet2)
    wallet2_id = response.json()["wallet"]["wallet_id"]

    fake_trans_dict = {
        "from_id": str(wallet1_id),
        "to_id": str(wallet2_id),
        "bitcoin_amount": 0.2,
    }
    fake_transaction = Fake().transaction_for_wallet(fake_trans_dict)
    client.post("/transactions", json=fake_transaction)
    response = client.get(f"/wallets/{uuid.UUID(wallet1_id)}/transactions")
    expected = [
        {
            "transaction_id": ANY,
            "from_id": wallet1_id,
            "to_id": wallet2_id,
            "bitcoin_amount": 0.197,
            "bitcoin_fee": 0.003,
        }
    ]

    assert response.status_code == 200
    assert response.json() == {"transactions": expected}


def test_shouldnt_get_nonexsistent_transactions(client: TestClient) -> None:
    random_id = uuid4()
    response = client.get(f"/wallets/{random_id}/transactions")
    expected = {"message": f"Wallet with id<{random_id}> does not exist."}

    assert response.status_code == 404
    assert response.json() == {"error": expected}
