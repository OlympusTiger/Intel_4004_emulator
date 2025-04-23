from enum import IntEnum, StrEnum, auto


class Instruction(StrEnum):
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


class Flag(IntEnum):
    CLEAR = 0
    SET = 1

    def __str__(self):
        return self.name


class InstructionPhase(IntEnum):
    FETCH_NEXT = 0
    CONTINUE = 1

    def __str__(self):
        return self.name


class InstructionFormat(IntEnum):
    SINGLE = 0
    DOUBLE = 1
