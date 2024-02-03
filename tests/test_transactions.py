from unittest.mock import ANY
from uuid import uuid4, UUID

import pytest
from starlette.testclient import TestClient

from runner.constants import (
    TEST_DATABASE_NAME_WITH_USERS_AND_WALLETS,
    TEST_USER1_WALLET1,
    TEST_USER1_WALLET2,
    TRANSACTION_FEE,
    TEST_USER2_WALLET,
    TEST_USER1_ID,
    TEST_USER2_ID,
)
from runner.setup import init_app
from runner.setup_database import create_database


@pytest.fixture
def client() -> TestClient:
    create_database(TEST_DATABASE_NAME_WITH_USERS_AND_WALLETS)
    return TestClient(init_app(TEST_DATABASE_NAME_WITH_USERS_AND_WALLETS))


def test_should_create(client: TestClient) -> None:
    fake_trans_dict = {
        "from_id": TEST_USER1_WALLET1,
        "to_id": TEST_USER1_WALLET2,
        "bitcoin_amount": 0.3,
        "bitcoin_fee": 0.0,
    }
    response = client.post("/transactions", json=fake_trans_dict)

    assert response.status_code == 201
    assert response.json() == {"transaction": {"id": ANY, **fake_trans_dict}}


def test_should_create_with_fee(client: TestClient) -> None:
    fake_trans_dict = {
        "from_id": TEST_USER1_WALLET1,
        "to_id": TEST_USER2_WALLET,
        "bitcoin_amount": 0.3,
    }
    response = client.post("/transactions", json=fake_trans_dict)

    assert response.status_code == 201
    assert response.json() == {
        "transaction": {
            "id": ANY,
            "from_id": TEST_USER1_WALLET1,
            "to_id": TEST_USER2_WALLET,
            "bitcoin_amount": 0.3 * (1 - TRANSACTION_FEE),
            "bitcoin_fee": 0.3 * TRANSACTION_FEE,
        }
    }


def test_should_not_create_with_unknown_wallet(client: TestClient) -> None:
    unknown_id = str(uuid4())
    fake_trans_dict = {
        "from_id": unknown_id,
        "to_id": TEST_USER1_WALLET2,
        "bitcoin_amount": 0.3,
    }
    response = client.post("/transactions", json=fake_trans_dict)

    assert response.status_code == 404
    assert response.json() == {
        "error": {"message": f"Wallet with id<{unknown_id}> does not exist."}
    }


def test_should_not_create_with_same_wallet(client: TestClient) -> None:
    fake_trans_dict = {
        "from_id": TEST_USER1_WALLET1,
        "to_id": TEST_USER1_WALLET1,
        "bitcoin_amount": 0.3,
    }
    response = client.post("/transactions", json=fake_trans_dict)

    assert response.status_code == 400
    assert response.json() == {
        "error": {
            "message": f"You cannot transfer from wallet with id<{TEST_USER1_WALLET1}> to itself."
        }
    }


def test_user_transactions_on_empty(client: TestClient) -> None:
    response = client.get(f"/transactions/{UUID(TEST_USER1_ID)}")

    assert response.status_code == 200
    assert response.json() == {"transactions": []}


def test_get_from_user_transactions(client: TestClient) -> None:
    fake_trans_dict = {
        "from_id": TEST_USER1_WALLET1,
        "to_id": TEST_USER2_WALLET,
        "bitcoin_amount": 0.3,
    }
    client.post("/transactions", json=fake_trans_dict)
    response = client.get(f"/transactions/{UUID(TEST_USER1_ID)}")

    assert response.status_code == 200
    assert response.json() == {
        "transactions": [
            {
                "id": ANY,
                "from_id": TEST_USER1_WALLET1,
                "to_id": TEST_USER2_WALLET,
                "bitcoin_amount": 0.3 * (1 - TRANSACTION_FEE),
                "bitcoin_fee": 0.3 * TRANSACTION_FEE,
            }
        ]
    }


def test_get_to_user_transactions(client: TestClient) -> None:
    fake_trans_dict = {
        "from_id": TEST_USER1_WALLET1,
        "to_id": TEST_USER2_WALLET,
        "bitcoin_amount": 0.3,
    }
    client.post("/transactions", json=fake_trans_dict)
    response = client.get(f"/transactions/{UUID(TEST_USER2_ID)}")

    assert response.status_code == 200
    assert response.json() == {
        "transactions": [
            {
                "id": ANY,
                "from_id": TEST_USER1_WALLET1,
                "to_id": TEST_USER2_WALLET,
                "bitcoin_amount": 0.3 * (1 - TRANSACTION_FEE),
                "bitcoin_fee": 0.3 * TRANSACTION_FEE,
            }
        ]
    }


def test_should_not_get_unknown_user_transactions(client: TestClient) -> None:
    unknown_id = str(uuid4())
    fake_trans_dict = {
        "from_id": str(uuid4()),
        "to_id": str(uuid4()),
        "bitcoin_amount": 0.3,
    }
    client.post("/transactions", json=fake_trans_dict)
    response = client.get(f"/transactions/{UUID(unknown_id)}")

    assert response.status_code == 404
    assert response.json() == {
        "error": {"message": f"User with id<{unknown_id}> does not exist."}
    }
