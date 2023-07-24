from .constants import COMMANDS, RESPONSES
from .exceptions import RelayCardError


class RequestFrame:
    def __init__(self, command, address=0, data=0):
        if command not in COMMANDS:
            RelayCardError(f"Wrong command{command}. Not found in {COMMANDS}")
        self.command = command

        if 0 > address > 255:
            RelayCardError(f"Wrong address {address}. Expected 0-255")
        self.address = address

        if 0 > data > 255:
            RelayCardError(f"Wrong data {data}. Expected 0-255")
        self.data = data

    def __repr__(self):
        return f"<RequestFrame {COMMANDS[self.command]}/addr:{self.address} data:{self.data} crc:{self.crc}>"

    @property
    def crc(self):
        return self.command ^ self.address ^ self.data

    def to_bytes(self):
        return bytearray([self.command, self.address, self.data, self.crc])


class ResponseFrame:
    command = None
    address = None
    data = None
    crc = None

    def __init__(self, response):
        if len(response) != 4:
            RelayCardError(f"Wrong response length {response}. Expected 4")
        response = bytearray(response)

        if response[0] not in RESPONSES:
            RelayCardError(f"Wrong response {response[0]}. Not found in {RESPONSES}")
        self.command = response[0]

        self.address = response[1]
        self.data = response[2]

        if response[3] != self.command ^ self.address ^ self.data:
            RelayCardError(f"Wrong responce CRC {response[3]}. Expected {self.command ^ self.address ^ self.data}")
        self.crc = response[3]

    def __repr__(self):
        return f"<ResponseFrame {RESPONSES[self.command]}/addr:{self.address} data:{self.data} crc:{self.cr}>"
