import uuid

import pytest
from fastapi.testclient import TestClient

from core.constants import (
    ADMIN_API_KEY,
    TEST_DATABASE_NAME,
    TEST_DATABASE_NAME_WITH_USERS_AND_WALLETS,
    TEST_USER1_ID,
    TEST_USER1_WALLET1,
    TEST_USER2_WALLET,
)
from runner.setup import init_app
from runner.setup_database import create_database


@pytest.fixture
def client() -> TestClient:
    create_database(TEST_DATABASE_NAME)
    return TestClient(init_app(TEST_DATABASE_NAME))


def test_get_statistics_on_empty_table(client: TestClient) -> None:
    response = client.get("/statistics", headers={"api_key": ADMIN_API_KEY})
    res = {"number_of_transactions": 0, "bitcoin_profit": 0.0}
    assert response.status_code == 200
    assert response.json() == {"statistics": {**res}}


def test_should_not_get_statistics(client: TestClient) -> None:
    user_id = uuid.uuid4()
    response = client.get("/statistics", headers={"api_key": str(user_id)})
    assert response.status_code == 403
    assert response.json() == {
        "message": f"User with id<{user_id}> does not have admin access."
    }


def test_should_get_statistics_with_no_profit() -> None:
    create_database(TEST_DATABASE_NAME_WITH_USERS_AND_WALLETS)
    client = TestClient(init_app(TEST_DATABASE_NAME_WITH_USERS_AND_WALLETS))

    transaction = {
        "from_id": TEST_USER1_WALLET1,
        "to_id": TEST_USER2_WALLET,
        "bitcoin_amount": 0.2,
    }
    client.post("/transactions", json=transaction, headers={"api_key": TEST_USER1_ID})
    response = client.get("/statistics", headers={"api_key": ADMIN_API_KEY})
    res = {"number_of_transactions": 1, "bitcoin_profit": 0.003}
    assert response.status_code == 200
    assert response.json() == {"statistics": {**res}}
