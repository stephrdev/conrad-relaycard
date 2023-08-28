from .constants import CommandCodes, ResponseCodes
from .exceptions import RelayCardError


class RequestFrame:
    def __init__(self, command: CommandCodes, address: int = 0, data: int = 0) -> None:
        self.command = command

        if not (0 <= address <= 255):
            raise RelayCardError(f"Wrong address {address}. Expected 0-255")
        self.address = address

        if not (0 <= data <= 255):
            raise RelayCardError(f"Wrong data {data}. Expected 0-255")
        self.data = data

    def __repr__(self) -> str:
        return f"<RequestFrame {self.command}/addr:{self.address} data:{self.data} crc:{self.crc}>"

    @property
    def crc(self) -> int:
        return self.command ^ self.address ^ self.data

    def to_bytes(self) -> bytearray:
        return bytearray([self.command, self.address, self.data, self.crc])


class ResponseFrame:
    def __init__(self, response: bytes) -> None:
        if len(response) != 4:
            raise RelayCardError(f"Wrong response length {response!r}. Expected 4")
        response = bytearray(response)

        if response[0] not in ResponseCodes:
            raise RelayCardError(f"Wrong response {response[0]}. Not found in {ResponseCodes}")
        self.command = response[0]

        self.address = response[1]
        self.data = response[2]

        expected_crc = self.command ^ self.address ^ self.data

        if response[3] != expected_crc:
            raise RelayCardError(f"Wrong responce CRC {response[3]}. Expected {expected_crc} ({hex(expected_crc)})")
        self.crc = response[3]

    def __repr__(self) -> str:
        return f"<ResponseFrame {self.command}/addr:{self.address} data:{self.data} crc:{self.crc}>"
