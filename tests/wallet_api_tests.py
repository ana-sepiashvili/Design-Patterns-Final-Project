import uuid
from dataclasses import dataclass, field
from typing import Any
from unittest.mock import ANY
from uuid import uuid4

import pytest
from faker import Faker
from fastapi.testclient import TestClient

from runner.constants import TEST_DATABASE_NAME
from runner.setup import init_app


@pytest.fixture
def client() -> TestClient:
    return TestClient(init_app(TEST_DATABASE_NAME))


@dataclass
class Fake:
    faker: Faker = field(default_factory=Faker)

    def wallet(self, attributes: dict[str, ANY] = {}) -> dict[str, Any]:
        wallet_dict = {}
        if len(attributes.keys()) == 0:
            wallet_dict = {"owner_id": str(uuid4()), "balance": 1}
        else:
            wallet_dict = attributes
        return wallet_dict

    def transaction(self, attributes: dict[str, ANY] = {}) -> dict[str, Any]:
        transaction_dict = {}
        if len(attributes.keys()) == 0:
            transaction_dict = {"from_id": str(uuid4()),
                                "to_id": str(uuid4()),
                                "bitcoin_amount": 3}
        else:
            transaction_dict = attributes
        return transaction_dict


def test_should_not_read_unknown(client: TestClient) -> None:
    unknown_id = uuid4()
    print(type(unknown_id))

    response = client.get(f"/wallets/{unknown_id}")
    message = {"message": f"Wallet with id<{unknown_id}> does not exist."}
    expected = {"error": message}

    assert response.status_code == 404
    assert response.json() == expected


def test_should_create(client: TestClient) -> None:
    wallet = Fake().wallet()
    response = client.post("/wallets", json=wallet)

    expected = {"wallet_id": ANY, "balance_btc": 1, "balance_usd": 42316.90}
    assert response.status_code == 201
    assert response.json() == {"wallet": expected}


def test_should_not_create_more_than_three(client: TestClient) -> None:
    fake_dict = {"owner_id": str(uuid4()), "balance": 0}
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


def test_should_persist(client: TestClient):
    wallet = Fake().wallet()
    response = client.post("/wallets", json=wallet)
    wallet_id = uuid.UUID(response.json()["wallet"]["wallet_id"])
    print(type(wallet_id))
    response = client.get(f"/wallets/{wallet_id}")

    expected = {"wallet_id": ANY, "balance_btc": 1, "balance_usd": 42316.90}
    assert response.status_code == 200
    assert response.json() == {"wallet": expected}


def test_should_get_transactions(client: TestClient):
    wallet1 = Fake().wallet()
    response = client.post("/wallets", json=wallet1)
    wallet1_id = uuid.UUID(response.json()["wallet"]["wallet_id"])
    wallet2 = Fake().wallet()
    response = client.post("/wallets", json=wallet2)
    wallet2_id = uuid.UUID(response.json()["wallet"]["wallet_id"])

    fake_transaction = {"from_id": wallet1_id,
                        "to_id": wallet2_id,
                        "bitcoin_amount": 3}
    client.post(f"/transactions", json=fake_transaction)

    expected = {"wallet_id": ANY, "balance_btc": 1, "balance_usd": 42316.90}
    assert response.status_code == 200
    assert response.json() == {"wallet": expected}

# def test_read_all(client: TestClient):
#     p1 = {"unit_id": str(uuid4()), "name": "Coa", "barcode": "1", "price": 12}
#     p2 = {"unit_id": str(uuid4()), "name": "Pei", "barcode": "2", "price": 12}
#     product1 = Fake().product(p1)
#     product2 = Fake().product(p2)
#
#     response = client.post("/products", json=product1)
#     product1_id = response.json()["product"]["id"]
#     response = client.post("/products", json=product2)
#     product2_id = response.json()["product"]["id"]
#
#     response = client.get("/products")
#     p1.update({"id": product1_id})
#     p2.update({"id": product2_id})
#
#     expected = [p1, p2]
#     assert response.status_code == 200
#     assert response.json() == {"products": expected}
#
#
# def test_should_update(client: TestClient):
#     product = Fake().product()
#
#     response = client.post("/products", json=product)
#
#     product_id = response.json()["product"]["id"]
#     product["id"] = product_id
#     old_price = product["price"]
#     new_price = old_price + 10
#     product["price"] = new_price
#     update = {"price": new_price}
#     client.patch(f"/products/{product_id}", json=update)
#
#     response = client.get(f"/products/{product_id}")
#     product.__delitem__("id")
#
#     assert response.status_code == 200
#     assert response.json() == {"product": {"id": product_id, **product}}
#
#
# def test_should_not_update(client: TestClient):
#     product = Fake().product()
#
#     product_id = str(uuid4())
#     product["id"] = product_id
#     old_price = product["price"]
#     new_price = old_price + 10
#     product["price"] = new_price
#     response = client.patch(f"/products/{product_id}", json=product)
#
#     message = {"message": f"Product with id<{product_id}> does not exist."}
#     expected = {"error": message}
#
#     assert response.status_code == 404
#     assert response.json() == expected
