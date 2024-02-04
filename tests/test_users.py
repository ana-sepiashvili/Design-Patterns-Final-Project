from unittest.mock import ANY

import pytest
from fastapi.testclient import TestClient

from tests.fake import Fake
from runner.constants import TEST_DATABASE_NAME
from runner.setup import init_app
from runner.setup_database import create_database


@pytest.fixture
def client() -> TestClient:
    create_database(TEST_DATABASE_NAME)
    return TestClient(init_app(TEST_DATABASE_NAME))


def test_should_create(client: TestClient) -> None:
    user = Fake().user()

    response = client.post("/users", json=user)

    assert response.status_code == 201
    assert response.json() == {"id": ANY}


def test_should_not_create(client: TestClient) -> None:
    user = Fake().user()

    response = client.post("/users", json=user)
    user_email = user["email"]
    assert response.status_code == 201
    assert response.json() == {"id": ANY}

    response = client.post("/users", json=user)
    assert response.status_code == 409
    assert response.json() == {
        "message": f"User with email<{user_email}> already exists."
    }
