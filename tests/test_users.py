from dataclasses import dataclass, field
from typing import Generator
from unittest.mock import ANY

import pytest
from faker import Faker
from fastapi.testclient import TestClient

from fake import Fake
from runner.constants import TEST_DATABASE_NAME
from runner.setup import init_app

@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    app = init_app(TEST_DATABASE_NAME)
    with TestClient(app) as client:
        yield client


def test_should_create(client: TestClient) -> None:
    user = Fake().user()

    response = client.post("/users", json=user)

    assert response.status_code == 201
    assert response.json() == {"id": ANY}
    client.app.state.users.clear()  # type: ignore


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
    client.app.state.users.clear()  # type: ignore
