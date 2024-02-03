from dataclasses import dataclass


class ThreeWalletsError(Exception):
    pass


class ExistsError(Exception):
    pass


@dataclass
class DoesNotExistError(Exception):
    id: str

    def get_id(self) -> str:
        return self.id


class ConverterError(Exception):
    pass
