from __future__ import annotations

import logging
import time
from contextlib import suppress

import serial

from .constants import ComCodes, CommandCodes
from .exceptions import RelayCardError
from .frame import RequestFrame, ResponseFrame
from .state import RelayState


class RelayCard:
    def __init__(self, port: str):
        self.port: str = port
        self.card_count: int = 0

    @property
    def is_initialized(self) -> bool:
        return self.card_count > 0

    def _try_close(self) -> None:
        with suppress(Exception):
            self._serial_port.close()

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
            self._try_close()
            raise RelayCardError(f"Port {self._serial_port.port} could not be opened")

        self._serial_port.reset_input_buffer()
        self._serial_port.reset_output_buffer()

        return self._serial_port

    def _execute(self, command: CommandCodes, address: int, data: int) -> ResponseFrame:
        if not (0 < address <= self.card_count):
            self._try_close()
            raise RelayCardError(f"Wrong relay address {address}. Expected 1-{self.card_count}")

        return self._send_frame(RequestFrame(command, address, data))

    def _execute_retry(
        self,
        com_codes: ComCodes,
        address: int,
        data: int = 0,
        retries: int = 3,
    ) -> ResponseFrame:
        error_log: None | RelayCardError | str = None
        response = None
        for _i in range(1, retries + 1):
            try:
                response = self._execute(com_codes.command_code, address, data)
                if response.command == com_codes.response_code:
                    break
            except RelayCardError as e:
                error_log = e
        else:
            # this is skipped if break called
            if error_log is None:
                error_log = f"Wrong response value {response}. Expected {com_codes.response_code.name}"
            self._try_close()
            logging.error(f"Error, retry #{_i}: {error_log}")
            raise RelayCardError(f"Retry #{_i}: {error_log}")
        return response

    def _send_frame(self, frame: RequestFrame) -> ResponseFrame:
        logging.info(f"Sending frame: {frame}")
        if not self.is_initialized:
            self._try_close()
            raise RelayCardError("Initialize serial connection before sending")

        ser = self._get_serial_port()

        out_bytes = frame.to_bytes()
        logging.debug(f"Sending bytes: {repr(out_bytes)}")

        if ser.write(out_bytes) != 4:
            self._try_close()
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
        response = self._execute_retry(ComCodes.GETPORT, address)
        return RelayState(response.data)

    def get_port(self, address: int, port: int) -> bool:
        return self.get_ports(address).get_port(port)

    def set_ports(self, address: int, new_state: RelayState) -> RelayState:
        response = self._execute_retry(
            ComCodes.SETPORT,
            address,
            new_state.to_byte(),
        )
        return RelayState(response.data)

    def set_port(self, address: int, port: int, port_state: int) -> RelayState:
        new_state = RelayState()
        new_state.set_port(port, True)

        response = self._execute_retry(
            ComCodes.SETSINGLE if port_state else ComCodes.DELSINGLE,
            address,
            new_state.to_byte(),
        )

        return RelayState(response.data)

    def toggle_ports(self, address: int, toggle_state: RelayState) -> RelayState:
        response = self._execute_retry(
            ComCodes.TOGGLE,
            address,
            toggle_state.to_byte(),
        )
        return RelayState(response.data)

    def toggle_port(self, address: int, port: int) -> RelayState:
        toggle_state = RelayState()
        toggle_state.set_port(port, True)

        response = self._execute_retry(
            ComCodes.TOGGLE,
            address,
            toggle_state.to_byte(),
        )
        return RelayState(response.data)
