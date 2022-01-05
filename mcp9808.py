from dataclasses import dataclass
from typing import Tuple

from smbus2 import SMBus

from i2cdevice import I2CDevice
from register import (
    BitWidth,
    ReadOnlyError,
    ReadOnlyRegister,
    ReadWriteRegister,
    Register,
    WriteOnlyError,
    WriteOnlyRegister,
)


@dataclass
class MCP9808(I2CDevice):
    """
     ----------------------------------
    |   Address Code    | Slave Address|
    |----------------------------------|
    | A6 | A5 | A4 | A3 | A2 | A1 | A0 |
    |  0 |  0 |  1 |  1 |  x |  x |  x |
     ----------------------------------
    """

    def __post_init__(self) -> None:
        self.reserved = ReadOnlyRegister(name="Reserved", address=0x00, width=BitWidth.WORD)
        self.configuration = ReadWriteRegister(name="Configuration", address=0x01, width=BitWidth.WORD)
        self.alert_upper = ReadWriteRegister(name="Alert Temperature Upper Boundary Trip", address=0x02, width=BitWidth.WORD)
        self.alert_lower = ReadWriteRegister(name="Alert Temperature Lower Boundary Trip", address=0x03, width=BitWidth.WORD)
        self.critical = ReadWriteRegister(name="Critical Temperature Trip", address=0x04, width=BitWidth.WORD)
        self.temperature = ReadWriteRegister(name="Temperature", address=0x05, width=BitWidth.WORD)
        self.manufacturing_id = ReadOnlyRegister(name="Manufacturing ID", address=0x06, width=BitWidth.WORD)
        self.device_id_revision = ReadOnlyRegister(name="Device ID/Revision", address=0x07, width=BitWidth.WORD)
        self.resolution = ReadWriteRegister(name="Resolution", address=0x08, width=BitWidth.BYTE)

    @staticmethod
    def word_swap(word: int) -> Tuple[int, int]:
        """
        A 16 bit word read when using smbus returns the MSB and LSB swapped.
        Return most significant byte and the least significant byte
        """
        return (word & 0xFF), ((word & ~0xFF) >> 8)

    def _read_byte(self, register: Register) -> int:
        """Return one byte from specified register"""
        with SMBus(self.bus) as bus:
            return bus.read_byte_data(self.address, register.address)

    def _read_word(self, register: Register) -> int:
        """Return 16 bit word from specified register"""
        with SMBus(self.bus) as bus:
            return bus.read_word_data(self.address, register.address)

    def _write_byte(self, register: Register, data: int) -> None:
        """Write one byte to specified register"""
        with SMBus(self.bus) as bus:
            return bus.write_byte_data(self.address, register.address, data)

    def _write_word(self, register: Register, data: int) -> None:
        """Write 16 bit word to specified register"""
        with SMBus(self.bus) as bus:
            return bus.write_word_data(self.address, register.address, data)

    def read_register(self, register: Register) -> int:
        if isinstance(register, WriteOnlyRegister):
            raise WriteOnlyError(
                f"Cannot read from {register.name} register with write only permissions"
            )

        if register.width == BitWidth.WORD:
            return self._read_word(register)

        return self._read_byte(register)

    def write_register(self, register: Register, data: int) -> None:
        if isinstance(register, ReadOnlyRegister):
            raise ReadOnlyError(
                f"Cannot write to {register.name} register with read only permissions"
            )

        if register.width == BitWidth.WORD:
            return self._write_word(register, data)

        return self._write_byte(register, data)

    def get_temperature(self) -> float:
        """Calculate and return temperature as float in Celsius"""
        msb, lsb = self.word_swap(self.read_register(self.temperature))
        msb &= 0x1F  # clear T_CRIT, T_UPPER, and T_LOWER flags

        if msb & (1 << 4):  # temperature < 0°C
            msb &= 0xF  # clear sign bit
            return 256 - ((msb * 16) + (lsb / 16))

        return (msb * 16) + (lsb / 16)  # temperature >= 0°C
