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
from .exceptions import RelayCardError
from .frame import RequestFrame, ResponseFrame
from .state import RelayState


class RelayCard:
    def __init__(self, port="/dev/ttyAMA0"):
        self.port = port

    @property
    def is_initialized(self):
        return self.card_count > 0

    def get_serial_port(self, port=None):
        if not hasattr(self, "_serial_port"):
            logging.debug(f"Opening serial port {port or self.port}")
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

        if not self._serial_port.isOpen():
            RelayCardError(f"Port {self._serial_port.port} could not be opened")

        self._serial_port.flushInput()
        self._serial_port.flushOutput()

        return self._serial_port

    def execute(self, command, address=0, data=0):
        if 0 >= address > self.card_count:
            RelayCardError(f"Wrong relay address {address}. Currently, only {self.card_count} cards connected")

        return self.send_frame(RequestFrame(command, address, data))

    def execute_retry(self, command, validator, address=0, data=0, retries=3):
        for _i in range(1, retries + 1):
            response = self.execute(command, address, data)
            if validator(response):
                break
        else:
            # this is skipped if break called
            logging.error(f"Error, retry #{_i}: {response}")
            raise RelayCardError(f"Wrong response {response}")
        return response

    def send_frame(self, frame):
        logging.info(f"Sending frame: {frame}")
        if not self.is_initialized:
            RelayCardError("Initialize serial connection before sending")

        ser = self.get_serial_port()

        out_bytes = frame.to_bytes()
        logging.debug(f"Sending bytes: {repr(out_bytes)}")

        if ser.write(out_bytes) != 4:
            RelayCardError(f"Wrong length of send bytes: {out_bytes}. Expected 4")

        in_bytes = ser.read(4)
        logging.debug(f"Received bytes: {repr(bytearray(in_bytes))}")

        response = ResponseFrame(in_bytes)

        ser.flushInput()
        ser.flushOutput()

        logging.info(f"Received frame: {response}")
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
            logging.debug(f"Received frame: {repr(response)}")

            if response and response[0] == 1:
                logging.debug("Setup frame is back, loading card count")
                if response[1] == 0:
                    self.card_count = 255
                elif response[1] > 0:
                    self.card_count = response[1] - 1

                logging.info(f"New card count: {self.card_count}")

                break

        ser.flushInput()
        ser.flushOutput()

        return self.is_initialized

    def get_ports(self, address):
        response = self.execute_retry(CMD_GETPORT, lambda r: r.command == RESP_GETPORT, address)
        return RelayState(response.data)

    def get_port(self, address, port):
        if 0 > port > 7:
            RelayCardError(f"Wrong relay port {port}. Expected 0-7")

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
        if 0 > port > 7:
            RelayCardError(f"Wrong relay port {port}. Expected 0-7")

        new_state = RelayState()
        new_state.set_port(port, True)

        response = self.execute_retry(
            CMD_SETSINGLE if port_state else CMD_DELSINGLE,
            lambda r: (
                (port_state and r.command == RESP_SETSINGLE) or (not port_state and r.command == RESP_DELSINGLE)
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
        if 0 > port > 7:
            RelayCardError(f"Wrong relay port {port}. Expected 0-7")

        toggle_state = RelayState()
        toggle_state.set_port(port, True)

        response = self.execute(
            CMD_TOGGLE,
            lambda r: r.command == RESP_TOGGLE,
            address,
            toggle_state.to_byte(),
        )
        return RelayState(response.data)
