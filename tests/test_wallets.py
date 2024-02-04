import uuid
from unittest.mock import ANY
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from core.errors import ConverterError
from runner.constants import (
    DEFAULT_BALANCE,
    TEST_DATABASE_NAME,
    TEST_USER1_WALLET1,
    TEST_USER1_ID,
    TEST_DATABASE_NAME_WITH_USERS_AND_WALLETS,
    TEST_USER2_WALLET,
    TEST_USER2_ID,
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
    try:
        wallet = Fake().wallet({})
        response = client.post("/wallets", headers={"api_key": wallet["owner_id"]})
        expected = {"message": f"User with id<{wallet['owner_id']}> does not exist."}
        assert response.status_code == 400
        assert response.json() == {"error": expected}
    except ConverterError as e:
        print(e.get_error_message())


def test_should_create(client: TestClient) -> None:
    try:
        user = Fake().user()
        response = client.post("/users", json=user)
        owner_id = response.json()["id"]
        response = client.post("/wallets", headers={"api_key": owner_id})

        expected = {
            "wallet_id": ANY,
            "balance_btc": DEFAULT_BALANCE,
            "balance_usd": ANY,
        }
        assert response.status_code == 201
        assert response.json() == {"wallet": expected}
    except ConverterError as e:
        print(e.get_error_message())


def test_should_not_create_more_than_three(client: TestClient) -> None:
    try:
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
    except ConverterError as e:
        print(e.get_error_message())


def test_should_not_read_unknown(client: TestClient) -> None:
    try:
        unknown_id = uuid4()
        user = Fake().user()
        response = client.post("/users", json=user)
        owner_id = response.json()["id"]

        response = client.get(f"/wallets/{unknown_id}", headers={"api_key": owner_id})
        message = {"message": f"Wallet with id<{unknown_id}> does not exist."}
        expected = {"error": message}

        assert response.status_code == 404
        assert response.json() == expected
    except ConverterError as e:
        print(e.get_error_message())


def test_should_read_own(client: TestClient) -> None:
    try:
        user = Fake().user()
        response = client.post("/users", json=user)
        owner_id = response.json()["id"]
        response = client.post("/wallets", headers={"api_key": owner_id})
        wallet_id = uuid.UUID(response.json()["wallet"]["wallet_id"])
        response = client.get(f"/wallets/{wallet_id}", headers={"api_key": owner_id})

        expected = {
            "wallet_id": ANY,
            "balance_btc": DEFAULT_BALANCE,
            "balance_usd": ANY,
        }
        print(response.json())
        assert response.status_code == 200
        assert response.json() == {"wallet": expected}
    except ConverterError as e:
        print(e.get_error_message())


def test_should_not_read_others_wallet(client: TestClient) -> None:
    try:
        user1 = Fake().user()
        user2 = Fake().user()
        response = client.post("/users", json=user1)
        owner1_id = response.json()["id"]
        response = client.post("/wallets", headers={"api_key": owner1_id})
        wallet_id = uuid.UUID(response.json()["wallet"]["wallet_id"])
        response = client.post("/users", json=user2)
        owner2_id = response.json()["id"]

        response = client.get(f"/wallets/{wallet_id}", headers={"api_key": owner2_id})
        expected = {
            "message": (
                f"User with id<{owner2_id}> doesn't " f"own wallet with id<{wallet_id}>"
            )
        }

        assert response.status_code == 400
        assert response.json() == {"error": expected}
    except ConverterError as e:
        print(e.get_error_message())


def test_should_get_transactions(client: TestClient) -> None:
    try:
        user1 = Fake().user()
        response = client.post("/users", json=user1)
        owner1_id = response.json()["id"]
        user2 = Fake().user()
        response = client.post("/users", json=user2)
        owner2_id = response.json()["id"]
        response = client.post("/wallets", headers={"api_key": owner1_id})
        wallet1_id = response.json()["wallet"]["wallet_id"]
        response = client.post("/wallets", headers={"api_key": owner2_id})
        wallet2_id = response.json()["wallet"]["wallet_id"]

        fake_trans_dict = {
            "from_id": str(wallet1_id),
            "to_id": str(wallet2_id),
            "bitcoin_amount": 0.2,
        }
        fake_transaction = Fake().transaction_for_wallet(fake_trans_dict)
        client.post(f"/transactions/{uuid.UUID(owner1_id)}", json=fake_transaction)
        response = client.get(
            f"/wallets/{uuid.UUID(wallet1_id)}/transactions",
            headers={"api_key": owner1_id},
        )
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
    except ConverterError as e:
        print(e.get_error_message())


def test_should_not_get_transactions_with_fake_key(client: TestClient) -> None:
    try:
        random_id1 = str(uuid4())
        random_id2 = str(uuid4())
        response = client.get(
            f"/wallets/{random_id1}/transactions", headers={"api_key": random_id2}
        )
        expected = {"message": f"User with id<{random_id2}> does not exist."}

        assert response.status_code == 404
        assert response.json() == {"error": expected}
    except ConverterError as e:
        print(e.get_error_message())


def test_should_not_get_transactions_of_fake_wallet(client: TestClient) -> None:
    try:
        user = Fake().user()
        response = client.post("/users", json=user)
        owner_id = response.json()["id"]
        random_id = str(uuid4())

        response = client.get(
            f"/wallets/{random_id}/transactions", headers={"api_key": owner_id}
        )
        expected = {"message": f"Wallet with id<{random_id}> does not exist."}

        assert response.status_code == 404
        assert response.json() == {"error": expected}
    except ConverterError as e:
        print(e.get_error_message())


def test_should_not_get_transactions_of_others_wallet(client: TestClient) -> None:
    try:
        user1 = Fake().user()
        user2 = Fake().user()
        response = client.post("/users", json=user1)
        owner1_id = response.json()["id"]
        response = client.post("/users", json=user2)
        owner2_id = response.json()["id"]
        response = client.post("/wallets", headers={"api_key": owner1_id})
        wallet_id = uuid.UUID(response.json()["wallet"]["wallet_id"])

        response = client.get(
            f"/wallets/{wallet_id}/transactions", headers={"api_key": owner2_id}
        )
        expected = {
            "message": (
                f"User with id<{owner2_id}> doesn't " f"own wallet with id<{wallet_id}>"
            )
        }

        assert response.status_code == 400
        assert response.json() == {"error": expected}
    except ConverterError as e:
        print(e.get_error_message())


def test_should_update_wallet_including_fee_after_transaction() -> None:
    create_database(TEST_DATABASE_NAME_WITH_USERS_AND_WALLETS)
    client = TestClient(init_app(TEST_DATABASE_NAME_WITH_USERS_AND_WALLETS))
    fake_trans_dict = {
        "from_id": TEST_USER1_WALLET1,
        "to_id": TEST_USER2_WALLET,
        "bitcoin_amount": 0.3,
        "bitcoin_fee": 0.0,
    }
    client.post(f"/transactions/{uuid.UUID(TEST_USER1_ID)}", json=fake_trans_dict)

    response = client.get(
        f"/wallets/{TEST_USER1_WALLET1}", headers={"api_key": TEST_USER1_ID}
    )

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
