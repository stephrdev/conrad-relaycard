from relaycard.constants import CMD_NOOP, RESP_NOOP
from relaycard.frame import RequestFrame, ResponseFrame


def test_requestframe():
    req_frame = RequestFrame(CMD_NOOP, 1, 1)
    assert req_frame.crc == 0
    assert req_frame.to_bytes() == b"\x00\x01\x01\x00"


def test_responseframe():
    resp_frame = ResponseFrame([RESP_NOOP, 1, 1, 255])
    assert resp_frame.command == RESP_NOOP
    assert resp_frame.crc == 255
    assert resp_frame.address == 1
    assert resp_frame.data == 1
