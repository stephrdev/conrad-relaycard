import logging
import time

import serial

from .constants import (
    CMD_DELSINGLE,
    CMD_GETPORT,
    CMD_SETPORT,
    CMD_SETSINGLE,
    CMD_SETUP,
    CMD_TOGGLE,
    RESP_DELSINGLE,
    RESP_GETPORT,
    RESP_SETPORT,
    RESP_SETSINGLE,
    RESP_TOGGLE,
)
from .frame import RequestFrame, ResponseFrame
from .state import RelayState


class RelayCard:
    port = None
    card_count = 0
    is_initialized = False

    def __init__(self, port="/dev/ttyAMA0"):
        self.port = port

    @property
    def is_initialized(self):
        return self.card_count > 0

    def get_serial_port(self, port=None):
        if not hasattr(self, "_serial_port"):
            logging.debug("Opening serial port %s" % (port or self.port))
            self._serial_port = serial.Serial(
                port or self.port,
                baudrate=19200,
                parity=serial.PARITY_NONE,
                bytesize=serial.EIGHTBITS,
                stopbits=serial.STOPBITS_ONE,
                xonxoff=False,
                rtscts=False,
                dsrdtr=False,
                timeout=1,
            )

        assert self._serial_port.isOpen()

        self._serial_port.flushInput()
        self._serial_port.flushOutput()

        return self._serial_port

    def execute(self, command, address=0, data=0):
        assert 0 < address <= self.card_count

        return self.send_frame(RequestFrame(command, address, data))

    def execute_retry(self, command, validator, address=0, data=0, retries=3):
        for i in range(1, retries + 1):
            try:
                response = self.execute(command, address, data)
                assert validator(response)
                return response
            except AssertionError as e:
                logging.error("Error, retry #%d: %s" % (i, e))
                if i >= retries:
                    raise e

    def send_frame(self, frame):
        logging.info("Sending frame: %s" % frame)
        assert self.is_initialized

        ser = self.get_serial_port()

        out_bytes = frame.to_bytes()
        logging.debug("Sending bytes: %s" % repr(out_bytes))

        assert ser.write(out_bytes) == 4

        in_bytes = ser.read(4)
        logging.debug("Received bytes: %s" % repr(bytearray(in_bytes)))

        response = ResponseFrame(in_bytes)

        ser.flushInput()
        ser.flushOutput()

        logging.info("Received frame: %s" % response)
        return response

    def setup(self):
        ser = self.get_serial_port()

        for _i in range(0, 4):
            logging.debug("Sending setup frame")
            ser.write(RequestFrame(CMD_SETUP, 1).to_bytes())
            time.sleep(0.05)

            if ser.inWaiting() > 3:
                logging.info("Setup running, received 4+ bytes")
                break

        time.sleep(0.1)

        for _i in range(0, 4):
            logging.debug("Sending setup frame")
            ser.write(RequestFrame(CMD_SETUP, 1).to_bytes())

        time.sleep(0.1)

        for _i in range(0, 256):
            response = bytearray(ser.read(4))
            logging.debug("Received frame: %s" % repr(response))

            if response and response[0] == 1:
                logging.debug("Setup frame is back, loading card count")
                if response[1] == 0:
                    self.card_count = 255
                elif response[1] > 0:
                    self.card_count = response[1] - 1

                logging.info("New card count: %s" % self.card_count)

                break

        ser.flushInput()
        ser.flushOutput()

        return self.is_initialized

    def get_ports(self, address):
        response = self.execute_retry(
            CMD_GETPORT, lambda r: r.command == RESP_GETPORT, address
        )
        return RelayState(response.data)

    def get_port(self, address, port):
        assert 0 <= port < 8

        return self.get_ports(address).get_port(port)

    def set_ports(self, address, new_state):
        response = self.execute_retry(
            CMD_SETPORT,
            lambda r: r.command == RESP_SETPORT,
            address,
            new_state.to_byte(),
        )
        return RelayState(response.data)

    def set_port(self, address, port, port_state):
        assert 0 <= port < 8

        new_state = RelayState()
        new_state.set_port(port, True)

        response = self.execute_retry(
            CMD_SETSINGLE if port_state else CMD_DELSINGLE,
            lambda r: (
                (port_state and r.command == RESP_SETSINGLE)
                or (not port_state and r.command == RESP_DELSINGLE)
            ),
            address,
            new_state.to_byte(),
        )

        return RelayState(response.data)

    def toggle_ports(self, address, toggle_state):
        response = self.execute_retry(
            CMD_TOGGLE,
            lambda r: r.command == RESP_TOGGLE,
            address,
            toggle_state.to_byte(),
        )
        return RelayState(response.data)

    def toggle_port(self, address, port):
        assert 0 <= port < 8

        toggle_state = RelayState()
        toggle_state.set_port(port, True)

        response = self.execute(
            CMD_TOGGLE,
            lambda r: r.command == RESP_TOGGLE,
            address,
            toggle_state.to_byte(),
        )
        return RelayState(response.data)
