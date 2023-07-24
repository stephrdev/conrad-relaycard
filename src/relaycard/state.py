from .exceptions import RelayCardError


class RelayState:
    state = None

    def __init__(self, state=None):
        if state:
            self.from_byte(state)
        else:
            self.state = dict([(i, False) for i in range(0, 8)])

    def __repr__(self):
        return f"<RelayState mask:{self.to_byte():08b}>"

    def to_byte(self):
        return int("".join(reversed(["1" if self.state[i] else "0" for i in range(0, 8)])), 2)

    def from_byte(self, state):
        if 0 > state > 255:
            RelayCardError(f"Wrong state {state}. Expected 0-255")
        self.state = dict([(i, j == "1") for i, j in enumerate(reversed(f"{state:08b}"))])

    def get_port(self, port):
        if 0 > port > 7:
            RelayCardError(f"Wrong relay port {port}. Expected 0-7")
        return self.state[port]

    def set_port(self, ports, new_state):
        if not isinstance(ports, list):
            ports = [ports]

        for port in ports:
            if 0 > port > 7:
                RelayCardError(f"Wrong relay port {port}. Expected 0-7")
            self.state[port] = new_state
