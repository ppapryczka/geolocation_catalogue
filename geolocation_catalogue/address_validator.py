import ipaddress
import re
from abc import ABC, abstractstaticmethod
from socket import gaierror, gethostbyname

from fastapi import HTTPException

DOMAIN_NAME_PATTERN: str = (
    r"^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$"
)
# domain pattern taken from this answer: https://stackoverflow.com/a/30007882


class AddressValidator(ABC):
    @abstractstaticmethod
    def get_validator_name(self) -> str:
        return self._validator_name

    @abstractstaticmethod
    def is_valid(self, address: str) -> bool:
        pass

    @abstractstaticmethod
    def to_ip(self, address: str) -> str:
        pass


class IpValidator(AddressValidator):
    @staticmethod
    def get_validator_name() -> str:
        return "IPv4"

    @staticmethod
    def is_valid(address: str) -> bool:
        try:
            ipaddress.ip_address(address)
        except ValueError:
            return False

        return True

    @staticmethod
    def to_ip(address: str) -> str:
        return address


class DomainNameValidator(AddressValidator):
    @staticmethod
    def get_validator_name() -> str:
        return "domain name"

    @staticmethod
    def is_valid(address: str) -> bool:
        return re.match(DOMAIN_NAME_PATTERN, address)

    @staticmethod
    def to_ip(address: str) -> str:
        try:
            return gethostbyname(address)
        except gaierror:
            raise HTTPException(
                status_code=404, detail="Error when trying to resolve domain IP."
            )


def validate_address(address: str) -> str:
    for validator in AddressValidator.__subclasses__():
        if validator.is_valid(address):
            return validator.to_ip(address)

    appropriate_formats = ", ".join(
        [v.get_validator_name() for v in AddressValidator.__subclasses__()]
    )
    raise HTTPException(
        status_code=422,
        detail=f"Address given in wrong format! It should be on of: {appropriate_formats}.",
    )
