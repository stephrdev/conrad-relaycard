from unittest import mock

import pytest

from conrad_relaycard import RelayCard, RelayCardError, RelayState


def test_relaycard() -> None:
    with mock.patch("serial.Serial") as mock_serial:
        mock_serial_instance = mock_serial.return_value
        mock_serial_instance.is_open = True
        mock_serial_instance.in_waiting = 4
        mock_serial_instance.read.return_value = b"\x01\x05\x00\x00"
        mock_serial_instance.write.return_value = 4

        rly = RelayCard("COM3")
        assert rly.setup() is True
        assert rly.is_initialized is True
        assert rly.card_count == 4

        mock_serial_instance.read.return_value = b"\x01\x00\x00\x00"
        rly = RelayCard("COM3")
        assert rly.setup() is True
        assert rly.is_initialized is True
        assert rly.card_count == 255

        mock_serial_instance.read.return_value = b"\xfd\x00\x00\xfd"
        assert rly.get_port(1, 0) is False
        assert rly.get_ports(1).to_byte() == RelayState(0).to_byte()

        mock_serial_instance.read.return_value = b"\xfd\x00\x01\xfc"
        assert rly.get_port(1, 0) is True
        assert rly.get_ports(1).to_byte() == RelayState(1).to_byte()

        mock_serial_instance.read.return_value = b"\xf9\x00\x00\xf9"
        assert rly.set_port(1, 0, True).to_byte() == RelayState(0).to_byte()

        mock_serial_instance.read.return_value = b"\xfc\x00\x00\xfc"
        assert rly.set_ports(1, RelayState(0)).to_byte() == RelayState(0).to_byte()

        mock_serial_instance.read.return_value = b"\xf7\x00\x00\xf7"
        assert rly.toggle_port(1, 0).to_byte() == RelayState(0).to_byte()
        assert rly.toggle_ports(1, RelayState(0)).to_byte() == RelayState(0).to_byte()


def test_relaycard_error() -> None:
    with mock.patch("serial.Serial") as mock_serial:
        mock_serial_instance = mock_serial.return_value
        mock_serial_instance.is_open = False
        mock_serial_instance.in_waiting = 4
        mock_serial_instance.read.return_value = b"\x01\x00\x00\x01"
        mock_serial_instance.write.return_value = 4

        rly = RelayCard("COM3")
        rly.card_count = 5
        mock_serial_instance.port = "COM3"
        with pytest.raises(RelayCardError, match="Port COM3"):
            rly._get_serial_port()

        mock_serial_instance.is_open = True
        rly._get_serial_port()

        with pytest.raises(RelayCardError, match="Wrong relay address 2000"):
            rly.get_port(2000, 0)
        mock_serial_instance.read.return_value = b"\xfd\x00\x00\xfd"
        with pytest.raises(RelayCardError, match="Wrong relay port 2000"):
            rly.get_port(1, 2000)
        with pytest.raises(RelayCardError, match="Wrong relay address 2000"):
            rly.get_ports(2000)
        with pytest.raises(RelayCardError, match="Wrong relay address 2000"):
            rly.set_port(2000, 0, True)
        with pytest.raises(RelayCardError, match="Wrong relay port 2000"):
            rly.set_port(1, 2000, True)
        with pytest.raises(RelayCardError, match="Wrong relay address 2000"):
            rly.set_ports(2000, RelayState(0))
        with pytest.raises(RelayCardError, match="Wrong relay address 2000"):
            rly.toggle_port(2000, 0)
        with pytest.raises(RelayCardError, match="Wrong relay port 2000"):
            rly.toggle_port(1, 2000)
        with pytest.raises(RelayCardError, match="Wrong relay address 2000"):
            rly.toggle_ports(2000, RelayState(0))

        mock_serial_instance.read.return_value = b"\x00\x00\x00\x00"
        mock_serial_instance.is_open = True
        mock_serial_instance.write.return_value = 3
        rly.card_count = 5
        with pytest.raises(RelayCardError, match="Wrong length of send bytes:"):
            # Retry #3: Wrong response length b'\\xfd\\x00\\x00'. Expected 4
            rly.get_port(1, 0)

        mock_serial_instance.write.return_value = 4
        with pytest.raises(RelayCardError, match="Retry #3: Wrong response 0."):
            rly.get_port(1, 0)


def test_relaycard_internal() -> None:
    with mock.patch("serial.Serial") as mock_serial:
        mock_serial_instance = mock_serial.return_value
        mock_serial_instance.is_open = False
        mock_serial_instance.in_waiting = 0
        mock_serial_instance.read.return_value = b"\x01\x05"

        rly = RelayCard("COM3")
        with pytest.raises(RelayCardError, match="Initialize serial connection before sending"):
            rly._send_frame(0)
