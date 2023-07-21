from unittest import mock

from relaycard.card import RelayCard


def test_relaycard():
    with mock.patch("serial.Serial") as mock_serial:
        mock_serial_instance = mock_serial.return_value
        mock_serial_instance.isOpen.return_value = True
        mock_serial_instance.inWaiting.return_value = True
        mock_serial_instance.read.return_value = b"\x01\x05"

        rly = RelayCard("COM3")
        assert rly.setup() is True
        assert rly.is_initialized is True
        assert rly.card_count == 4

        mock_serial_instance.read.return_value = b"\x01\x00"
        rly = RelayCard("COM3")
        assert rly.setup() is True
        assert rly.is_initialized is True
        assert rly.card_count == 255
