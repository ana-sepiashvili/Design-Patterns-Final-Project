from dataclasses import dataclass, field
from typing import Any

from faker import Faker


@dataclass
class Fake:
    faker: Faker = field(default_factory=Faker)

    def wallet(self, attributes=None) -> dict[str, Any]:
        if attributes is None:
            attributes = {}
        wallet_dict = {}
        if len(attributes.keys()) == 0:
            wallet_dict = {"owner_id": str(self.faker.uuid4()), "balance": 1}
        else:
            wallet_dict = attributes
        return wallet_dict

    def transaction_for_wallet(self, attributes=None) -> dict[str, Any]:
        if attributes is None:
            attributes = {}
        transaction_dict = {}
        if len(attributes.keys()) == 0:
            transaction_dict = {
                "from_id": str(self.faker.uuid4()),
                "to_id": str(self.faker.uuid4()),
                "bitcoin_amount": 3,
            }
        else:
            transaction_dict = attributes
        return transaction_dict

    def transaction(self) -> dict[str, Any]:
        return {
            "from_id": str(self.faker.uuid4()),
            "to_id": str(self.faker.uuid4()),
            "bitcoin_amount": self.faker.random_float(),
            "bitcoin_fee": self.faker.random_float(),
        }

    def user(self) -> dict[str, str]:
        return {"email": self.faker.catch_phrase()}
