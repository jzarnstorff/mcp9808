from abc import ABC, abstractmethod
from dataclasses import dataclass

from register import Register


@dataclass
class I2CDevice(ABC):
    bus: int
    address: int

    @abstractmethod
    def read_register(self, register: Register) -> int:
        """Method used to read data from a register"""

    @abstractmethod
    def write_register(self, register: Register, data: int) -> None:
        """Method used to write data to a register"""
