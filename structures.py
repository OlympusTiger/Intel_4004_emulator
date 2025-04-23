from bitarray.util import int2ba, ba2int
from bitarray import bitarray
from typing import Literal, Union
from typeguard import typechecked
from functools import total_ordering


@total_ordering
class Word:
    def __init__(self, value: int = 0, max_bit_size: Literal[4, 8] = 4):
        self.value = value
        self.max_bit_size = max_bit_size

    def __str__(self):
        return f"{self.value}"

    def __repr__(self):
        return f"{self.value}"

    def __getitem__(self, key: Union[int, slice]) -> int | bitarray:
        if isinstance(key, slice):
            return self.as_bits()[key]
        return self.as_bits()[key]

    def __setitem__(self, key: int, value: Literal[0, 1]) -> None:
        new_bits = self.as_bits()
        new_bits[key] = value
        self.value = ba2int(new_bits)

    def __add__(self, other: Union[int, "Word"]) -> "Word":
        if isinstance(other, Word):
            other = other.value
        return self.__class__(self.value + other, self.max_bit_size)

    def __iadd__(self, other: Union[int, "Word"]) -> "Word":
        if isinstance(other, Word):
            other = other.value
        self.value += other
        return self

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Word):
            return self.value == other.value
        if isinstance(other, int):
            return self.value == other
        return NotImplemented

    def __lt__(self, other: object) -> bool:
        if isinstance(other, Word):
            return self.value < other.value
        if isinstance(other, int):
            return self.value < other
        return NotImplemented

    def combine_with(self, other: "Word") -> "Word":
        new_word = self.as_bits()
        new_word.extend(other.as_bits())
        return self.__class__(ba2int(new_word), 8)

    def split(self) -> tuple["Word", "Word"]:
        high_nibble = self.__class__(ba2int(self.as_bits()[:4]))
        low_nibble = self.__class__(ba2int(self.as_bits()[4:]))
        return high_nibble, low_nibble

    def as_bits(self) -> bitarray:
        return int2ba(self.value, length=self.max_bit_size)

    def as_hex(self) -> str:
        return hex(self.value)[2:].upper()

    def _increment(self, overflow_reset: bool) -> None:
        self.value += 1
        if overflow_reset and self.value >= 2**self.max_bit_size:
            self.value = 0

    def increment(self):
        try:
            self.value = ba2int(int2ba(self.value + 1, 4))
        except OverflowError:
            self.value = 0


class Register:
    def __init__(self, size: int, is_ram: bool = False):
        self.size = size
        self.register = [Word() for _ in range(size)]
        self.status = Register(4) if is_ram else None

    def __str__(self) -> str:
        return " ".join(str(word) for word in self.register)

    def __getitem__(self, key: int) -> Word:
        return self.register[key]

    def __setitem__(self, key: int, value: Word):
        self.register[key] = value

    def as_hex(self) -> str:
        return " ".join([word.as_hex() for word in self.register])

    def as_bits(self, word_separator: str = " ") -> str:
        return word_separator.join([word.as_bits().to01() for word in self.register])


@typechecked
class ProgramCounter(Register):
    LOOKUP = {"PAGE": 0, "PM": 1, "PL": 2}

    def __init__(self):
        super().__init__(3)
        self.PAGE = self.register[0]
        self.PM = self.register[1]
        self.PL = self.register[2]

    def __setattr__(self, name: str, value):
        if name in self.LOOKUP:
            self.__dict__[name] = value
            self.register[self.LOOKUP[name]] = value
        else:
            return super().__setattr__(name, value)

    def __add__(self, other: Union[int, Word]) -> Word:
        return self.get_address() + other

    def __iadd__(self, other: Union[int, Word]) -> "ProgramCounter":
        new = self.get_address() + other
        self.PM, self.PL = new.split()
        return self

    def get_address(self) -> Word:
        return self.PM.combine_with(self.PL)

    def set_address(self, *args: Word) -> None:
        """*args can be one 8bit Word or two 4bit Words(first should be the high nibble)"""
        match len(args):
            case 1:
                self.PM, self.PL = args[0].split()
            case 2:
                self.PM = args[0]
                self.PL = args[1]


class IndexRegister(Register):
    def __init__(self):
        super().__init__(16)

    def get_pair(self, pair_key: int) -> Word:
        return self.register[pair_key * 2].combine_with(self.register[pair_key * 2 + 1])

    def set_pair(self, pair_key: int, *args: Word) -> None:
        """*args can be one 8bit Word or two 4bit Words(first should be the high nibble)"""
        match len(args):
            case 1:
                value = args[0]
                high, low = value.split()
                self.register[pair_key * 2] = high
                self.register[pair_key * 2 + 1] = low
            case 2:
                high, low = args
                self.register[pair_key * 2] = high
                self.register[pair_key * 2 + 1] = low
