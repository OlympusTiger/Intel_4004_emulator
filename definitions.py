from enum import IntEnum, StrEnum, auto, Enum


class Instruction(Enum):
    NOP = auto()
    JCN = auto()
    FIM = auto()
    SRC = auto()
    FIN = auto()
    JIN = auto()
    JUN = auto()
    JMS = auto()
    INC = auto()
    ISZ = auto()
    ADD = auto()
    SUB = auto()
    LD = auto()
    XCH = auto()
    BBL = auto()
    LDM = auto()
    WRM = auto()
    WMP = auto()
    WRR = auto()
    WPM = auto()
    WR0 = auto()
    WR1 = auto()
    WR2 = auto()
    WR3 = auto()
    SBM = auto()
    RDM = auto()
    RDR = auto()
    ADM = auto()
    RD0 = auto()
    RD1 = auto()
    RD2 = auto()
    RD3 = auto()
    CLB = auto()
    CLC = auto()
    IAC = auto()
    CMC = auto()
    CMA = auto()
    RAL = auto()
    RAR = auto()
    TCC = auto()
    DAC = auto()
    TCS = auto()
    STC = auto()
    DAA = auto()
    KBP = auto()
    DCL = auto()


class InstructionHex(Enum):
    NOP = "00"
    JCN = "10"
    FIM = "20"
    SRC = "21"
    FIN = "30"
    JIN = "31"
    JUN = "40"
    JMS = "50"
    INC = "60"
    ISZ = "70"
    ADD = "80"
    SUB = "90"
    LD = "A0"
    XCH = "B0"
    BBL = "C0"
    LDM = "D0"
    WRM = "E0"
    WMP = "E1"
    WRR = "E2"
    WPM = "E3"
    WR0 = "E4"
    WR1 = "E5"
    WR2 = "E6"
    WR3 = "E7"
    SBM = "E8"
    RDM = "E9"
    RDR = "EA"
    ADM = "EB"
    RD0 = "EC"
    RD1 = "ED"
    RD2 = "EE"
    RD3 = "EF"
    CLB = "F0"
    CLC = "F1"
    IAC = "F2"
    CMC = "F3"
    CMA = "F4"
    RAL = "F5"
    RAR = "F6"
    TCC = "F7"
    DAC = "F8"
    TCS = "F9"
    STC = "FA"
    DAA = "FB"
    KBP = "FC"
    DCL = "FD"


class Flag(IntEnum):
    CLEAR = 0
    SET = 1

    def __str__(self) -> str:
        return self.name


class InstructionPhase(IntEnum):
    FETCH_NEXT = 0
    CONTINUE = 1

    def __str__(self) -> str:
        return self.name


# class InstructionFormat(IntEnum):
#     SINGLE = 0
#     DOUBLE = 1


class MemoryType(StrEnum):
    RAM = auto()
    ROM = auto()


class MemoryAccess(StrEnum):
    READ = auto()
    WRITE = auto()


class MemoryData(StrEnum):
    RAM_CHAR = auto()
    RAM_STATUS = auto()
    RAM_OUTPUT = auto()
    ROM_ADDR = auto()
    ROM_IO = auto()
