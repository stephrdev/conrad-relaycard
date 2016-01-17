class RelayState(object):
    state = None

    def __init__(self, state=None):
        if state:
            self.from_byte(state)
        else:
            self.state = dict([(i, False) for i in range(0, 8)])

    def __repr__(self):
        return '<RelayState mask:%s>' % '{0:08b}'.format(self.to_byte())

    def to_byte(self):
        return int(''.join(reversed(
            ['1' if self.state[i] else '0' for i in range(0, 8)])), 2)

    def from_byte(self, state):
        assert 0 <= state < 256
        self.state = dict([(i, j == '1') for i, j in enumerate(
            reversed('{0:08b}'.format(state)))])

    def get_port(self, port):
        assert 0 <= port < 8
        return self.state[port]

    def set_port(self, ports, new_state):
        if not isinstance(ports, list):
            ports = [ports]

        for port in ports:
            assert 0 <= port < 8
            self.state[port] = new_state
