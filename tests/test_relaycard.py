from relaycard.card import RelayCard


def test_relaycard():
    rly = RelayCard("COM3")
    rly.setup()
    assert "COM3" == rly.get_serial_port()
