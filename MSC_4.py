from processor import CPU
from definitions import MemoryData
from main import mem


def main():
    c = 0
    cpu = CPU()

    while True:
        print()
        print()
        print()
        print()
        print()
        input("Hit enter to continue")
        rom_page = cpu.program_counter.PAGE.value
        rom_addr = cpu.program_counter.get_address()
        rom_data = mem.read(MemoryData.ROM_ADDR, bank=rom_page, byte=rom_addr)
        cpu.instruction_set(rom_data)
        print(cpu)
        c += 1
        print(f"{c=}")
        breakpoint()
        mem.RAM[0][0].print_all()


main()
