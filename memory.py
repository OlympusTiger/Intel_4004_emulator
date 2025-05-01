from collections import defaultdict
from structures import Word, Register, ba2int
from definitions import MemoryData
from typing import List, Tuple, Any
from icecream import ic


class ROMChip:
    def __init__(self):
        self.chip = defaultdict(lambda: Word(0, max_bit_size=8))
        self.io = Word(0)

    def read_from_file(self, file: str) -> None:
        with open(file, "r") as f:
            for i, line in enumerate(f):
                self.chip[i] = Word(int(line, 16), max_bit_size=8)

    def __str__(self) -> str:
        return " ".join(str(v) for k, v in self.chip.items())

    def __getitem__(self, key: int):
        return self.chip[key]


class RAMChip:
    def __init__(self):
        self.chip = [Register(16, is_ram=True) for _ in range(4)]
        self.output = Word(0)

    def __str__(self) -> str:
        return "\n".join(str(i) for i in self.chip)

    def __repr__(self) -> str:
        return "\n".join(str(i) for i in self.chip)

    def print_all(self) -> None:
        print("       0 1 2 3 4 5 6 7 8 9 A B C D E F   0 1 2 3")
        for i, r in enumerate(self.chip):
            print(f"reg{i}", str(r), str(r.status), sep="   ")

    def __getitem__(self, key: int) -> Register:
        return self.chip[key]

    def __setitem__(self, key, value: Register):
        self.chip[key] = value


class MemoryManager:
    def __init__(self, ram_banks: int = 4, ram_per_bank: int = 4, rom_banks: int = 16):
        self.ROM: List[ROMChip] = [ROMChip() for _ in range(rom_banks)]
        self.RAM: List[List[RAMChip]] = [
            [RAMChip() for _ in range(ram_per_bank)] for _ in range(ram_banks)
        ]

    def write(
        self,
        operation: MemoryData,
        bank: int | None,
        byte: Word,
        write_data: Word,
        ram_status_char: int | None = None,
    ) -> None:
        write_data = write_data.copy()
        match operation:
            case MemoryData.RAM_CHAR:
                chip, reg, char = self.decode(operation, byte)

                self.RAM[bank][chip][reg][char] = write_data

            case MemoryData.RAM_OUTPUT:
                chip, _, _ = self.decode(operation, byte)
                self.RAM[bank][chip].output = write_data
            case MemoryData.ROM_IO:
                chip, _, _ = self.decode(operation, byte)
                ic(chip)
                self.ROM[chip].io = write_data
            case MemoryData.RAM_STATUS:
                chip, reg, _ = self.decode(operation, byte)
                self.RAM[bank][chip][reg].status[ram_status_char] = write_data

    def read(
        self,
        operation: MemoryData,
        bank: int | None,
        byte: Word,
        ram_status_char: int | None = None,
    ) -> Word:
        match operation:
            case MemoryData.RAM_CHAR:
                chip, reg, char = self.decode(operation, byte)
                return self.RAM[bank][chip][reg][char]
            case MemoryData.RAM_OUTPUT:
                chip, _, _ = self.decode(operation, byte)
                return self.RAM[bank][chip].output
            case MemoryData.ROM_IO:
                chip, _, _ = self.decode(operation, byte)
                return self.ROM[chip].io
            case MemoryData.RAM_STATUS:
                chip, reg, _ = self.decode(operation, byte)
                return self.RAM[bank][chip][reg].status[ram_status_char]
            case MemoryData.ROM_ADDR:
                addr, _, _ = self.decode(operation, byte)
                print(type(bank))
                return self.ROM[bank][addr]

    @staticmethod
    def decode(operation: MemoryData, byte: Word) -> Tuple[int, Any, Any]:
        match operation:
            case MemoryData.RAM_CHAR:
                chip = ba2int(byte.as_bits()[:2])
                reg = ba2int(byte.as_bits()[2:4])
                char = ba2int(byte.as_bits()[4:])
                return chip, reg, char
            case MemoryData.RAM_OUTPUT:
                chip = ba2int(byte.as_bits()[:2])
                return chip, None, None
            case MemoryData.ROM_IO:
                chip = ba2int(byte.as_bits()[:4])
                return chip, None, None
            case MemoryData.RAM_STATUS:
                chip = ba2int(byte.as_bits()[:2])
                reg = ba2int(byte.as_bits()[2:4])
                return chip, reg, None
            case MemoryData.ROM_ADDR:
                addr = ba2int(byte.as_bits())
                return addr, None, None


# m = MemoryManager()

# m.write(
#     operation=MemoryData.RAM_STATUS,
#     ram_bank=1,
#     byte=Word(80, 8),
#     write_data=Word(10),
#     ram_status_char=0,
# )
# print(m.RAM[1][1].print_all())
