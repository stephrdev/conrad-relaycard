import pytest

from conrad_relaycard.exceptions import RelayCardError
from conrad_relaycard.state import RelayState


class TestRelayState:
    @classmethod
    def setup_class(cls):
        cls.rly0 = RelayState(0)
        cls.rly1 = RelayState(128)
        cls.rly2 = RelayState(255)

        assert repr(cls.rly0) == "<RelayState mask:00000000>"
        assert repr(cls.rly1) == "<RelayState mask:10000000>"
        assert repr(cls.rly2) == "<RelayState mask:11111111>"

    def test_relaystate(self):
        assert self.rly0._state == {
            0: False,
            1: False,
            2: False,
            3: False,
            4: False,
            5: False,
            6: False,
            7: False,
        }
        assert self.rly1._state == {
            0: False,
            1: False,
            2: False,
            3: False,
            4: False,
            5: False,
            6: False,
            7: True,
        }
        assert self.rly2._state == {
            0: True,
            1: True,
            2: True,
            3: True,
            4: True,
            5: True,
            6: True,
            7: True,
        }

    def test_relaystate_to_byte(self):
        assert self.rly0.to_byte() == 0
        assert self.rly1.to_byte() == 128
        assert self.rly2.to_byte() == 255

    def test_relaystate_get_port(self):
        assert self.rly0.get_port(7) == 0
        assert self.rly1.get_port(7) == 1
        assert self.rly2.get_port(7) == 1

    def test_relaystate_set_port(self):
        self.rly0.set_port(5, True)
        assert self.rly0.to_byte() == 32

        self.rly1.set_port(5, True)
        assert self.rly1.to_byte() == 160

        self.rly2.set_port(5, True)
        assert self.rly2.to_byte() == 255

        self.rly0.set_port([0, 1, 2], True)
        assert self.rly0.to_byte() == 39


def test_relaystate_error():
    with pytest.raises(RelayCardError, match="Wrong state -1"):
        RelayState(-1)
    with pytest.raises(RelayCardError, match="Wrong state 256"):
        RelayState(256)

    rly = RelayState(0)
    with pytest.raises(RelayCardError, match="Wrong state 2000"):
        rly.from_byte(2000)
    with pytest.raises(RelayCardError, match="Wrong relay port 2000"):
        rly.get_port(2000)
    with pytest.raises(RelayCardError, match="Wrong relay port 2000"):
        rly.set_port(2000, True)
