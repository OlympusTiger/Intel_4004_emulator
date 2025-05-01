from structures import Word, ProgramCounter, IndexRegister, bitarray, ba2int
from definitions import (
    Flag,
    Instruction,
    InstructionPhase,
    MemoryData,
)
from itertools import batched
from collections import deque
from main import mem
from icecream import ic


class CPU:
    def __init__(self):
        self.program_counter = ProgramCounter()  # TODO stack
        self.index_registers = IndexRegister()
        self.ram_bank = 0
        self.accumulator = Word(0)
        self.carry = Flag.CLEAR
        self.test = Flag.CLEAR

        self.current_instruction = None
        self.instruction_phase = InstructionPhase.FETCH_NEXT
        self.memory_pointer = None
        self.target_pair = None
        self.buffer = None

    def __str__(self):
        attributes = vars(self)  # Get instance attributes as dict
        return "\n".join(f"{k}: {v}" for k, v in attributes.items())

    @property
    def pairs_index_registers(self):
        return [Word.combine_nibbles(*p) for p in batched(self.index_registers, 2)]

    @staticmethod
    def identify_instruction(byte: Word) -> Instruction:
        opr, opa = Word.split(byte)
        match opr.value:
            case 0:
                return Instruction.NOP
            case 1:
                return Instruction.JCN
            case 2:
                if opa[-1] == 0:
                    return Instruction.FIM
                else:
                    return Instruction.SRC
            case 3:
                if opa[-1] == 0:
                    return Instruction.FIN
                else:
                    return Instruction.JIN
            case 4:
                return Instruction.JUN
            case 5:
                return Instruction.JMS
            case 6:
                return Instruction.INC
            case 7:
                return Instruction.ISZ
            case 8:
                return Instruction.ADD
            case 9:
                return Instruction.SUB
            case 10:
                return Instruction.LD
            case 11:
                return Instruction.XCH
            case 12:
                return Instruction.BBL
            case 13:
                return Instruction.LDM
            case 14:
                match opa.value:
                    case 0:
                        return Instruction.WRM
                    case 1:
                        return Instruction.WMP
                    case 2:
                        return Instruction.WRR
                    # case 3:
                    #     return Instruction.WR0
                    case 4:
                        return Instruction.WR0
                    case 5:
                        return Instruction.WR1
                    case 6:
                        return Instruction.WR2
                    case 7:
                        return Instruction.WR3
                    case 8:
                        return Instruction.SBM
                    case 9:
                        return Instruction.RDM
                    case 10:
                        return Instruction.RDR
                    case 11:
                        return Instruction.ADM
                    case 12:
                        return Instruction.RD0
                    case 13:
                        return Instruction.RD1
                    case 14:
                        return Instruction.RD2
                    case 15:
                        return Instruction.RD3
            case 15:
                match opa.value:
                    case 0:
                        return Instruction.CLB
                    case 1:
                        return Instruction.CLC
                    case 2:
                        return Instruction.IAC
                    case 3:
                        return Instruction.CMC
                    case 4:
                        return Instruction.CMA
                    case 5:
                        return Instruction.RAL
                    case 6:
                        return Instruction.RAR
                    case 7:
                        return Instruction.TCC
                    case 8:
                        return Instruction.DAC
                    case 9:
                        return Instruction.TCS
                    case 10:
                        return Instruction.STC
                    case 11:
                        return Instruction.DAA
                    case 12:
                        return Instruction.KBP
                    case 13:
                        return Instruction.DCL

        raise ValueError(f"Invalid instruction {byte}")

    def instruction_set(self, byte: Word) -> None:
        if self.instruction_phase == InstructionPhase.FETCH_NEXT:
            self.target_pair = None
            self.current_instruction = self.identify_instruction(byte)

        opr, opa = Word.split(byte)

        match self.current_instruction:
            case Instruction.NOP:
                self.program_counter += 1
                return
            case Instruction.JCN:
                if self.instruction_phase == InstructionPhase.FETCH_NEXT:
                    conditions = (
                        (opa[3] == 1 and self.test == Flag.CLEAR)
                        or (opa[2] == 1 and self.carry == Flag.SET)
                        or (opa[1] == 1 and self.accumulator == 0)
                    )

                    if opa[0] == 0:
                        if conditions:
                            self.instruction_phase = InstructionPhase.CONTINUE
                            self.program_counter += 1
                        else:
                            self.instruction_phase = InstructionPhase.FETCH_NEXT
                            self.program_counter += 2
                    else:
                        if conditions:
                            self.instruction_phase = InstructionPhase.FETCH_NEXT
                            self.program_counter += 1
                        else:
                            self.instruction_phase = InstructionPhase.CONTINUE
                            self.program_counter += 2
                else:
                    if self.program_counter.get_address() >= 254:
                        self.program_counter.PAGE += 1
                    self.program_counter.set_address(opr, opa)
                    self.instruction_phase = InstructionPhase.FETCH_NEXT
            case Instruction.FIM:
                if self.instruction_phase == InstructionPhase.FETCH_NEXT:
                    self.target_pair = ba2int(opa[:3])
                    self.instruction_phase = InstructionPhase.CONTINUE

                else:
                    self.index_registers.set_pair(self.target_pair, opr, opa)
                    self.instruction_phase = InstructionPhase.FETCH_NEXT
                self.program_counter += 1

            case Instruction.SRC:
                self.memory_pointer = self.index_registers.get_pair(ba2int(opa[:3]))
                self.program_counter += 1
            case Instruction.FIN:
                self.target_pair = ba2int(opa[:3])
                fetch_address = self.index_registers.get_pair(0)
                fetch_page = self.program_counter.PAGE.value
                if self.program_counter.get_address() == 255:
                    fetch_page += 1
                read_data = mem.read(MemoryData.ROM_ADDR, fetch_page, fetch_address)
                self.index_registers.set_pair(self.target_pair, read_data)
                self.program_counter += 1
            case Instruction.JIN:
                self.target_pair = ba2int(opa[:3])
                self.program_counter.set_address(
                    self.index_registers.get_pair(self.target_pair)
                )

                if self.program_counter.PAGE == 255:
                    self.program_counter.PAGE += 1

                # self.program_counter[1] = self.index_registers[self.target_pair * 2]
                # self.program_counter[2] = self.index_registers[self.target_pair * 2 + 1]
            case Instruction.JUN:
                if self.instruction_phase == InstructionPhase.FETCH_NEXT:
                    self.buffer = opa
                    self.instruction_phase = InstructionPhase.CONTINUE
                    self.program_counter += 1
                else:
                    self.program_counter.PAGE = self.buffer
                    # self.program_counter[1] = opr
                    # self.program_counter[2] = opa
                    ic(opr.as_hex(), opa.as_hex())
                    self.program_counter.set_address(opr, opa)
                    ic(self.program_counter.get_address())
                    self.instruction_phase = InstructionPhase.FETCH_NEXT
            case Instruction.JMS:
                pass
                # TODO JMS
            case Instruction.INC:
                self.index_registers[opa.value].increment()
                self.program_counter += 1
            case Instruction.ISZ:
                if self.instruction_phase == InstructionPhase.FETCH_NEXT:
                    self.index_registers[opa.value].increment()
                    if self.index_registers[opa.value] != 0:
                        self.instruction_phase = InstructionPhase.CONTINUE
                        self.program_counter += 1
                    else:
                        self.program_counter += 2
                else:
                    # self.program_counter[1] = opr
                    # self.program_counter[2] = opa
                    self.program_counter.set_address(opr, opa)
                    if self.program_counter.get_address() >= 254:
                        self.program_counter.PAGE += 1
                    self.instruction_phase = InstructionPhase.FETCH_NEXT
            case Instruction.ADD:
                temp = self.index_registers[opa.value] + self.accumulator + self.carry
                self.adder_and_carry(temp)
                self.program_counter += 1
                # self.accumulator = Word(temp % 16)
                # if temp >= 16:
                #     self.carry = Flag.SET
                # else:
                #     self.carry = Flag.CLEAR
            case Instruction.SUB:
                temp = (
                    self.accumulator.value
                    + (self.index_registers[opa.value].value ^ 15)
                    + (self.carry.value ^ 1)
                )
                self.adder_and_carry(temp, subtraction=True)
                self.program_counter += 1
            case Instruction.LD:
                self.accumulator = self.index_registers[opa.value]
                self.program_counter += 1
            case Instruction.XCH:
                self.accumulator, self.index_registers[opa.value] = (
                    self.index_registers[opa.value],
                    self.accumulator,
                )
                self.program_counter += 1
            case Instruction.BBL:
                pass  # TODO BBL
            case Instruction.LDM:
                self.accumulator = opa
                self.program_counter += 1
            case Instruction.WRM:
                mem.write(
                    MemoryData.RAM_CHAR,
                    bank=self.ram_bank,
                    byte=self.memory_pointer,
                    write_data=self.accumulator,
                )
                self.program_counter += 1
            case Instruction.WMP:
                mem.write(
                    MemoryData.RAM_OUTPUT,
                    bank=self.ram_bank,
                    byte=self.memory_pointer,
                    write_data=self.accumulator,
                )
                self.program_counter += 1
            case Instruction.WPM:
                pass  # TODO WPM. <program RAM> implementation
            case Instruction.WRR:
                mem.write(
                    MemoryData.ROM_IO,
                    bank=None,
                    byte=self.memory_pointer,
                    write_data=self.accumulator,
                )
                self.program_counter += 1
            case Instruction.WR0:
                mem.write(
                    MemoryData.RAM_STATUS,
                    bank=self.ram_bank,
                    byte=self.memory_pointer,
                    write_data=self.accumulator,
                    ram_status_char=0,
                )
                self.program_counter += 1
            case Instruction.WR1:
                mem.write(
                    MemoryData.RAM_STATUS,
                    bank=self.ram_bank,
                    byte=self.memory_pointer,
                    write_data=self.accumulator,
                    ram_status_char=1,
                )
                self.program_counter += 1
            case Instruction.WR2:
                mem.write(
                    MemoryData.RAM_STATUS,
                    bank=self.ram_bank,
                    byte=self.memory_pointer,
                    write_data=self.accumulator,
                    ram_status_char=2,
                )
                self.program_counter += 1
            case Instruction.WR3:
                mem.write(
                    MemoryData.RAM_STATUS,
                    bank=self.ram_bank,
                    byte=self.memory_pointer,
                    write_data=self.accumulator,
                    ram_status_char=3,
                )
                self.program_counter += 1
            case Instruction.SBM:
                read_data = mem.read(
                    MemoryData.RAM_CHAR,
                    bank=self.ram_bank,
                    byte=self.memory_pointer,
                )

                temp = (
                    self.accumulator.value
                    + (read_data.value ^ 15)
                    + (self.carry.value ^ 1)
                )
                self.adder_and_carry(temp, subtraction=True)
                self.program_counter += 1
            case Instruction.RDM:
                read_data = mem.read(
                    MemoryData.RAM_CHAR,
                    bank=self.ram_bank,
                    byte=self.memory_pointer,
                )
                self.accumulator = read_data
                self.program_counter += 1
            case Instruction.RDR:  # TODO input/output lines
                read_data = mem.read(
                    MemoryData.ROM_IO,
                    bank=None,
                    byte=self.memory_pointer,
                )
                self.accumulator = read_data
                self.program_counter += 1
            case Instruction.ADM:
                read_data = mem.read(
                    MemoryData.RAM_CHAR,
                    bank=self.ram_bank,
                    byte=self.memory_pointer,
                )
                temp = read_data + self.accumulator + self.carry
                self.adder_and_carry(temp)
                self.program_counter += 1
            case Instruction.RD0:
                read_data = mem.read(
                    MemoryData.RAM_STATUS,
                    bank=self.ram_bank,
                    byte=self.memory_pointer,
                    ram_status_char=0,
                )
                self.accumulator = read_data
                self.program_counter += 1
            case Instruction.RD1:
                read_data = mem.read(
                    MemoryData.RAM_STATUS,
                    bank=self.ram_bank,
                    byte=self.memory_pointer,
                    ram_status_char=1,
                )
                self.accumulator = read_data
                self.program_counter += 1
            case Instruction.RD2:
                read_data = mem.read(
                    MemoryData.RAM_STATUS,
                    bank=self.ram_bank,
                    byte=self.memory_pointer,
                    ram_status_char=2,
                )
                self.accumulator = read_data
                self.program_counter += 1
            case Instruction.RD3:
                read_data = mem.read(
                    MemoryData.RAM_STATUS,
                    bank=self.ram_bank,
                    byte=self.memory_pointer,
                    ram_status_char=3,
                )
                self.accumulator = read_data
                self.program_counter += 1
            case Instruction.CLB:
                self.accumulator = Word(0)
                self.carry = Flag.CLEAR
                self.program_counter += 1
            case Instruction.CLC:
                self.carry = Flag.CLEAR
                self.program_counter += 1
            case Instruction.IAC:
                self.accumulator.increment()
                if self.accumulator == 0:
                    self.carry = Flag.SET
                else:
                    self.carry = Flag.CLEAR
                self.program_counter += 1
            case Instruction.CMC:
                if self.carry == Flag.CLEAR:
                    self.carry = Flag.SET
                else:
                    self.carry = Flag.CLEAR
                self.program_counter += 1
            case Instruction.CMA:
                self.accumulator = Word(self.accumulator.value ^ 15 & 15)
                self.program_counter += 1
            case Instruction.RAL:
                temp = deque([self.carry.value] + list(self.accumulator.as_bits()))
                temp.rotate(-1)
                self.carry = Flag(temp[0])
                self.accumulator = Word(ba2int(bitarray(list(temp)[1:])))
                self.program_counter += 1
            case Instruction.RAR:
                temp = deque([self.carry.value] + list(self.accumulator.as_bits()))
                temp.rotate(1)
                self.carry = Flag(temp[0])
                self.accumulator = Word(ba2int(bitarray(list(temp)[1:])))
                self.program_counter += 1
            case Instruction.TCC:
                self.accumulator = Word(self.carry.value)
                self.carry = Flag.CLEAR
                self.program_counter += 1
            case Instruction.DAC:
                temp = self.accumulator.value + 15
                self.adder_and_carry(temp)
                self.program_counter += 1
            case Instruction.TCS:
                if self.carry == Flag.CLEAR:
                    self.accumulator = Word(9)
                else:
                    self.accumulator = Word(10)
                self.carry = Flag.CLEAR
                self.program_counter += 1
            case Instruction.STC:
                self.carry = Flag.SET
                self.program_counter += 1
            case Instruction.DAA:
                if self.accumulator > 9 or self.carry == Flag.SET:
                    temp = self.accumulator + 6
                    self.adder_and_carry(temp, carry_unaffected=True)
                self.program_counter += 1
            case Instruction.KBP:
                if sum(self.accumulator) > 1:
                    self.accumulator = Word(15)
                else:
                    self.accumulator = Word(self.accumulator[::-1].find(1) + 1)
                self.program_counter += 1
            case Instruction.DCL:
                self.ram_bank = ba2int(self.accumulator[1:])
                self.program_counter += 1
            # 0,1,2,3 for now #TODO expand to multiple banks or decoder 3205

    def adder_and_carry(self, temp, carry_unaffected=False, subtraction=False):
        self.accumulator = Word(temp % 16)
        if temp >= 16:
            if subtraction:
                self.carry = Flag.CLEAR
            else:
                self.carry = Flag.SET
        elif not carry_unaffected:
            self.carry = Flag.CLEAR
