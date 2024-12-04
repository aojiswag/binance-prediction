from dataclasses import dataclass


@dataclass(frozen=True)
class ApiInfo:
    key: str = ""
    secret: str = ""

    def __getitem__(self, item):
        return self.key, self.secret
