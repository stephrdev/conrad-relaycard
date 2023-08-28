import pytest

from conrad_relaycard.constants import CommandCodes, ResponseCodes
from conrad_relaycard.exceptions import RelayCardError
from conrad_relaycard.frame import RequestFrame, ResponseFrame


def test_requestframe():
    req_frame = RequestFrame(CommandCodes.NOOP, 1, 1)
    assert req_frame.crc == 0
    assert req_frame.to_bytes() == b"\x00\x01\x01\x00"

    assert repr(req_frame) == "<RequestFrame 0/addr:1 data:1 crc:0>"


def test_requestframe_error():
    # with pytest.raises(RelayCardError, match="Wrong command"):
    RequestFrame(1000, 1, 1)  # This must be catched by typing and mypy
    with pytest.raises(RelayCardError, match="Wrong address"):
        RequestFrame(CommandCodes.NOOP, 1000, 1)
    with pytest.raises(RelayCardError, match="Wrong data"):
        RequestFrame(CommandCodes.NOOP, 1, 1000)


def test_responseframe():
    resp_frame = ResponseFrame([ResponseCodes.NOOP, 1, 1, 255])
    assert resp_frame.command == ResponseCodes.NOOP
    assert resp_frame.crc == 255
    assert resp_frame.address == 1
    assert resp_frame.data == 1

    assert repr(resp_frame) == "<ResponseFrame 255/addr:1 data:1 crc:255>"


def test_responseframe_error():
    with pytest.raises(RelayCardError, match="Wrong response 100"):
        ResponseFrame([100, 1, 1, 255])
    with pytest.raises(RelayCardError, match="Wrong responce CRC"):
        ResponseFrame([ResponseCodes.NOOP, 0, 1, 255])
    with pytest.raises(RelayCardError, match="Wrong response length"):
        ResponseFrame([ResponseCodes.NOOP, 0, 1, 255, "extra"])
