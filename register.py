from dataclasses import dataclass
from enum import auto, enum


class BitWidth(Enum):
    BYTE = auto()
    WORD = auto()


@dataclass
class Register:
    name: str
    address: int
    width: BitWidth


@dataclass
class ReadOnlyRegister(Register):
    """A register that has read only permissions"""


@dataclass
class WriteOnlyRegister(Register):
    """A register that has write only permissions"""


@dataclass
class ReadWriteRegister(Register):
    """A register that has both read and write permissions"""


class ReadOnlyError(Exception):
    """An exception raised when attempting to write to a register with read only permissions"""


class WriteOnlyError(Exception):
    """An exception raised when attempting to read from a register with write only permissions"""
