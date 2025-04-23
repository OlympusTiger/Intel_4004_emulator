from collections import defaultdict
from structures import Word, Register


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
