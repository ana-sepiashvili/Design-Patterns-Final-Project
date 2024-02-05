import uuid
from unittest.mock import ANY
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from core.constants import (
    DEFAULT_BALANCE,
    TEST_DATABASE_NAME_WITH_USERS_AND_WALLETS,
    TEST_USER1_ID,
    TEST_USER1_WALLET1,
    TEST_USER2_ID,
    TEST_USER2_WALLET,
    TRANSACTION_FEE,
)
from runner.setup import init_app
from runner.setup_database import create_database
from tests.fake import Fake


@pytest.fixture
def client() -> TestClient:
    create_database(TEST_DATABASE_NAME_WITH_USERS_AND_WALLETS)
    return TestClient(init_app(TEST_DATABASE_NAME_WITH_USERS_AND_WALLETS))


def test_should_not_create_for_unknown(client: TestClient) -> None:
    wallet = Fake().wallet({})
    response = client.post("/wallets", headers={"api_key": wallet["owner_id"]})
    expected = {"message": f"User with id<{wallet['owner_id']}> does not exist."}
    assert response.status_code == 400
    assert response.json() == {"error": expected}


def test_should_create(client: TestClient) -> None:
    response = client.post("/wallets", headers={"api_key": TEST_USER1_ID})

    expected = {
        "wallet_id": ANY,
        "balance_btc": DEFAULT_BALANCE,
        "balance_usd": ANY,
    }
    assert response.status_code == 201
    assert response.json() == {"wallet": expected}


def test_should_not_create_more_than_three(client: TestClient) -> None:
    user = Fake().user()
    response = client.post("/users", json=user)
    owner_id = response.json()["id"]
    client.post("/wallets", headers={"api_key": owner_id})
    client.post("/wallets", headers={"api_key": owner_id})
    client.post("/wallets", headers={"api_key": owner_id})
    response = client.post("/wallets", headers={"api_key": owner_id})
    err_msg = f"User with id<{owner_id}> already has 3 wallets."
    message = {"message": err_msg}
    expected = {"error": message}

    assert response.status_code == 409
    assert response.json() == expected


def test_should_not_read_unknown(client: TestClient) -> None:
    unknown_id = uuid4()
    owner_id = TEST_USER1_ID

    response = client.get(f"/wallets/{unknown_id}", headers={"api_key": owner_id})
    message = {"message": f"Wallet with id<{unknown_id}> does not exist."}
    expected = {"error": message}

    assert response.status_code == 404
    assert response.json() == expected


def test_should_read_own(client: TestClient) -> None:
    owner_id = TEST_USER1_ID
    wallet_id = uuid.UUID(TEST_USER1_WALLET1)
    response = client.get(f"/wallets/{wallet_id}", headers={"api_key": owner_id})

    expected = {
        "wallet_id": ANY,
        "balance_btc": DEFAULT_BALANCE,
        "balance_usd": ANY,
    }
    print(response.json())
    assert response.status_code == 200
    assert response.json() == {"wallet": expected}


def test_should_not_read_others_wallet(client: TestClient) -> None:
    owner_id = TEST_USER1_ID
    wallet_id = uuid.UUID(TEST_USER2_WALLET)

    response = client.get(f"/wallets/{wallet_id}", headers={"api_key": owner_id})
    expected = {
        "message": (
            f"User with id<{owner_id}> doesn't " f"own wallet with id<{wallet_id}>"
        )
    }

    assert response.status_code == 400
    assert response.json() == {"error": expected}


def test_should_get_transactions(client: TestClient) -> None:
    owner1_id = TEST_USER1_ID
    wallet1_id = uuid.UUID(TEST_USER1_WALLET1)
    wallet2_id = uuid.UUID(TEST_USER2_WALLET)

    fake_trans_dict = {
        "from_id": str(wallet1_id),
        "to_id": str(wallet2_id),
        "bitcoin_amount": 0.2,
    }
    fake_transaction = Fake().transaction_for_wallet(fake_trans_dict)
    client.post(
        "/transactions", json=fake_transaction, headers={"api_key": TEST_USER1_ID}
    )
    response = client.get(
        f"/wallets/{wallet1_id}/transactions",
        headers={"api_key": owner1_id},
    )
    expected = [
        {
            "transaction_id": ANY,
            "from_id": str(wallet1_id),
            "to_id": str(wallet2_id),
            "bitcoin_amount": 0.197,
            "bitcoin_fee": 0.003,
        }
    ]
    assert response.status_code == 200
    assert response.json() == {"transactions": expected}


def test_transaction_should_reflect_on_wallet(client: TestClient) -> None:
    wallet2_id = uuid.UUID(TEST_USER2_WALLET)
    wallet1_id = uuid.UUID(TEST_USER1_WALLET1)
    owner1_id = TEST_USER1_ID

    fake_trans_dict = {
        "from_id": str(wallet1_id),
        "to_id": str(wallet2_id),
        "bitcoin_amount": 0.2,
    }
    fake_transaction = Fake().transaction_for_wallet(fake_trans_dict)
    client.post("/transactions", json=fake_transaction, headers={"api_key": owner1_id})
    response = client.get(
        f"/wallets/{wallet1_id}",
        headers={"api_key": owner1_id},
    )
    expected = {
        "balance_btc": 0.7999999999999999,
        "balance_usd": ANY,
        "wallet_id": str(wallet1_id),
    }
    assert response.status_code == 200
    assert response.json() == {"wallet": expected}


def test_should_not_get_transactions_with_fake_key(client: TestClient) -> None:
    random_id1 = str(uuid4())
    random_id2 = str(uuid4())
    response = client.get(
        f"/wallets/{random_id1}/transactions", headers={"api_key": random_id2}
    )
    expected = {"message": f"User with id<{random_id2}> does not exist."}

    assert response.status_code == 404
    assert response.json() == {"error": expected}


def test_should_not_get_transactions_of_fake_wallet(client: TestClient) -> None:
    owner_id = TEST_USER1_ID
    random_id = str(uuid4())

    response = client.get(
        f"/wallets/{random_id}/transactions", headers={"api_key": owner_id}
    )
    expected = {"message": f"Wallet with id<{random_id}> does not exist."}

    assert response.status_code == 404
    assert response.json() == {"error": expected}


def test_should_not_get_transactions_of_others_wallet(client: TestClient) -> None:
    other_id = TEST_USER2_ID
    wallet_id = TEST_USER1_WALLET1

    response = client.get(
        f"/wallets/{wallet_id}/transactions", headers={"api_key": other_id}
    )
    expected = {
        "message": (
            f"User with id<{other_id}> doesn't " f"own wallet with id<{wallet_id}>"
        )
    }

    assert response.status_code == 400
    assert response.json() == {"error": expected}


def test_should_update_wallet_including_fee_after_transaction() -> None:
    create_database(TEST_DATABASE_NAME_WITH_USERS_AND_WALLETS)
    client = TestClient(init_app(TEST_DATABASE_NAME_WITH_USERS_AND_WALLETS))
    fake_trans_dict = {
        "from_id": TEST_USER1_WALLET1,
        "to_id": TEST_USER2_WALLET,
        "bitcoin_amount": 0.3,
        "bitcoin_fee": 0.0,
    }
    client.post(
        "/transactions", json=fake_trans_dict, headers={"api_key": TEST_USER1_ID}
    )

    client.get(f"/wallets/{TEST_USER1_WALLET1}", headers={"api_key": TEST_USER1_ID})

    response = client.get(
        f"/wallets/{TEST_USER2_WALLET}", headers={"api_key": TEST_USER2_ID}
    )

    assert response.status_code == 200
    assert response.json() == {
        "wallet": {
            "wallet_id": TEST_USER2_WALLET,
            "balance_btc": 1.0 + 0.3 * (1 - TRANSACTION_FEE),
            "balance_usd": ANY,
        }
    }
