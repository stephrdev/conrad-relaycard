import pytest

from relaycard.state import RelayState


class TestRelayState:
    @classmethod
    def setup_class(cls):
        cls.rly0 = RelayState(0)
        cls.rly1 = RelayState(128)
        cls.rly2 = RelayState(255)

    def test_relaystate(self):
        assert self.rly0.state == {
            0: False,
            1: False,
            2: False,
            3: False,
            4: False,
            5: False,
            6: False,
            7: False,
        }
        assert self.rly1.state == {
            0: False,
            1: False,
            2: False,
            3: False,
            4: False,
            5: False,
            6: False,
            7: True,
        }
        assert self.rly2.state == {
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


def test_relaystate_error():
    with pytest.raises(AssertionError, match=""):
        RelayState(-1)
    with pytest.raises(AssertionError, match=""):
        RelayState(256)
