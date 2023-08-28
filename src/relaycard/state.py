from __future__ import annotations

from .exceptions import RelayCardError


class RelayState:
    def __init__(self, state: int = 0):
        self._state = self.from_byte(state)

    def __repr__(self) -> str:
        return f"<RelayState mask:{self.to_byte():08b}>"

    def to_byte(self) -> int:
        return int("".join(reversed(["1" if self._state[i] else "0" for i in range(0, 8)])), 2)

    def from_byte(self, state: int) -> dict[int, bool]:
        if not (0 <= state <= 255):
            raise RelayCardError(f"Wrong state {state}. Expected 0-255")
        return dict([(i, j == "1") for i, j in enumerate(reversed(f"{state:08b}"))])

    def get_port(self, port: int) -> bool:
        if not (0 <= port <= 7):
            raise RelayCardError(f"Wrong relay port {port}. Expected 0-7")
        return self._state[port]

    def set_port(self, ports: int | list[int], new_state: bool) -> None:
        if not isinstance(ports, list):
            ports = [ports]

        for port in ports:
            if not (0 <= port <= 7):
                raise RelayCardError(f"Wrong relay port {port}. Expected 0-7")
            self._state[port] = new_state
