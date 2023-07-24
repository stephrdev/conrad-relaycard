import logging
import time
from collections.abc import Callable

import serial

from .constants import CommandCodes, ResponseCodes
from .exceptions import RelayCardError
from .frame import RequestFrame, ResponseFrame
from .state import RelayState


class RelayCard:
    def __init__(self, port: str = "/dev/ttyAMA0"):
        self.port: str = port
        self.card_count: int = 0

    @property
    def is_initialized(self) -> bool:
        return self.card_count > 0

    def _get_serial_port(self, port: str | None = None) -> serial.Serial:
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

        if not self._serial_port.is_open:
            raise RelayCardError(f"Port {self._serial_port.port} could not be opened")

        self._serial_port.reset_input_buffer()
        self._serial_port.reset_output_buffer()

        return self._serial_port

    def _execute(self, command: CommandCodes, address: int = 0, data: int = 0) -> ResponseFrame:
        if not (0 < address <= self.card_count):
            raise RelayCardError(f"Wrong relay address {address}. Expected 1-{self.card_count}")

        return self._send_frame(RequestFrame(command, address, data))

    def _execute_retry(
        self,
        command: CommandCodes,
        validator: Callable[[ResponseFrame], bool],
        address: int = 0,
        data: int = 0,
        retries: int = 3,
    ) -> ResponseFrame:
        error_log = None
        for _i in range(1, retries + 1):
            try:
                response = self._execute(command, address, data)
                if validator(response):
                    break
            except RelayCardError as e:
                error_log = e
        else:
            # this is skipped if break called
            logging.error(f"Error, retry #{_i}: {error_log}")
            raise RelayCardError(f"Retry #{_i}: {error_log}")
        return response

    def _send_frame(self, frame: RequestFrame) -> ResponseFrame:
        logging.info(f"Sending frame: {frame}")
        if not self.is_initialized:
            raise RelayCardError("Initialize serial connection before sending")

        ser = self._get_serial_port()

        out_bytes = frame.to_bytes()
        logging.debug(f"Sending bytes: {repr(out_bytes)}")

        if ser.write(out_bytes) != 4:
            raise RelayCardError(f"Wrong length of send bytes: {out_bytes}. Expected 4")

        in_bytes = ser.read(4)
        logging.debug(f"Received bytes: {repr(bytearray(in_bytes))}")

        response = ResponseFrame(in_bytes)

        ser.reset_input_buffer()
        ser.reset_output_buffer()

        logging.info(f"Received frame: {response}")
        return response

    def setup(self) -> bool:
        ser = self._get_serial_port()

        for _ in range(0, 4):
            logging.debug("Sending setup frame")
            ser.write(RequestFrame(CommandCodes.SETUP, 1).to_bytes())
            time.sleep(0.05)

            if ser.in_waiting > 3:
                logging.info("Setup running, received 4+ bytes")
                break

        time.sleep(0.1)

        for _ in range(0, 4):
            logging.debug("Sending setup frame")
            ser.write(RequestFrame(CommandCodes.SETUP, 1).to_bytes())

        time.sleep(0.1)

        for _ in range(0, 256):
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

        ser.reset_input_buffer()
        ser.reset_output_buffer()

        return self.is_initialized

    def get_ports(self, address: int) -> RelayState:
        response = self._execute_retry(CommandCodes.GETPORT, lambda r: r.command == ResponseCodes.GETPORT, address)
        return RelayState(response.data)

    def get_port(self, address: int, port: int) -> bool:
        if not (0 <= port <= 7):
            raise RelayCardError(f"Wrong relay port {port}. Expected 0-7")

        return self.get_ports(address).get_port(port)

    def set_ports(self, address: int, new_state: RelayState) -> RelayState:
        response = self._execute_retry(
            CommandCodes.SETPORT,
            lambda r: r.command == ResponseCodes.SETPORT,
            address,
            new_state.to_byte(),
        )
        return RelayState(response.data)

    def set_port(self, address: int, port: int, port_state: int) -> RelayState:
        if not (0 <= port <= 7):
            raise RelayCardError(f"Wrong relay port {port}. Expected 0-7")

        new_state = RelayState()
        new_state.set_port(port, True)

        response = self._execute_retry(
            CommandCodes.SETSINGLE if port_state else CommandCodes.DELSINGLE,
            lambda r: bool(
                (port_state and r.command == ResponseCodes.SETSINGLE)
                or (not port_state and r.command == ResponseCodes.DELSINGLE)
            ),
            address,
            new_state.to_byte(),
        )

        return RelayState(response.data)

    def toggle_ports(self, address: int, toggle_state: RelayState) -> RelayState:
        response = self._execute_retry(
            CommandCodes.TOGGLE,
            lambda r: r.command == ResponseCodes.TOGGLE,
            address,
            toggle_state.to_byte(),
        )
        return RelayState(response.data)

    def toggle_port(self, address: int, port: int) -> RelayState:
        if not (0 <= port <= 7):
            raise RelayCardError(f"Wrong relay port {port}. Expected 0-7")

        toggle_state = RelayState()
        toggle_state.set_port(port, True)

        response = self._execute_retry(
            CommandCodes.TOGGLE,
            lambda r: r.command == ResponseCodes.TOGGLE,
            address,
            toggle_state.to_byte(),
        )
        return RelayState(response.data)
