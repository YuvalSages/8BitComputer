
from enum import IntFlag
from typing import Tuple


class Signals(IntFlag):
    CLH = 2**0    # CLOCK                 HALT
    MAO = 2**1    # MEMORY       RAM      OUTPUT
    MPI = 2**2    # MEMORY       POINTER  INPUT
    MAI = 2**3    # MEMORY       RAM      INPUT
    MOO = 2**4    # MEMORY       ROM      OUTPUT
    IPO = 2**5    # INSTRUCTION  POINTER  OUTPUT
    IPC = 2**6    # INSTRUCTION  POINTER  COUNT
    IPR = 2**7    # INSTRUCTION  POINTER  RESET

    IHI = 2**8    # INSTRUCTION  HOLDER   INPUT
    CCR = 2**9    # CLOCK        COUNTER  RESET
    RFI = 2**10   # REGISTER     FLAGS    INPUT
    RAO = 2**11   # REGISTER     A        OUTPUT
    RAI = 2**12   # REGISTER     A        INPUT
    ALO = 2**13   # ALU                   OUTPUT
    ALF = 2**14   # ALU                   FLAG
    RBO = 2**15   # REGISTER     B        OUTPUT

    RBI = 2**16   # REGISTER     B        INPUT
    RCF = 2**17   # REGISTER     C        FLAG
    RCO = 2**18   # REGISTER     C        OUTPUT
    RCI = 2**19   # REGISTER     C        INPUT
    IPJ1 = 2**20  # INSTRUCTION  POINTER  JUMP_1
    IPJ2 = 2**21  # INSTRUCTION  POINTER  JUMP_2
    IPJ3 = 2**22  # INSTRUCTION  POINTER  JUMP_3
    IPJ4 = 2**23  # INSTRUCTION  POINTER  JUMP_4


class MicroInstructions(Signals):
    NOP = 0
    IP_TO_MP = Signals.IPO | Signals.MPI | Signals.IPC
    MO_TO_IH = Signals.MOO | Signals.IHI | Signals.CCR
    ADDITION = Signals.ALO | Signals.RAI | Signals.RFI
    SUBTRACTION = Signals.ALO | Signals.RAI | Signals.RFI | Signals.ALF
    COMPARE = Signals.ALO | Signals.RFI | Signals.ALF

NUM_OF_COMMANDS = 2**8
NUM_OF_MICRO_COMMANDS_PER_COMMAND = 2**3
DEFAULT_MICRO_INSTRUCTION = Signals.CLH


class MicroCode(object):
    def __init__(self):
        self._initializeDataStructure()
        self._fillMicroCode()

    def _initializeDataStructure(self) -> None:
        # create a matrix representing the default micro code
        self.data = [[DEFAULT_MICRO_INSTRUCTION for j in range(NUM_OF_MICRO_COMMANDS_PER_COMMAND)] for i in range(NUM_OF_COMMANDS)]

    def _fillMicroCode(self) -> None:
        # fill the micro code commands

        # NOP
        # don't do anything
        self._setCommand(0, (
            MicroInstructions.NOP,
            MicroInstructions.IP_TO_MP,
            MicroInstructions.MO_TO_IH
        ))

        ################################################################################
        # MOV
        ################################################################################

        # MOV A B
        # move register A value to register B
        self._setCommand(1, (
            Signals.RAO | Signals.RBI,
            MicroInstructions.IP_TO_MP,
            MicroInstructions.MO_TO_IH
        ))

        # MOV A C
        # move register A value to register C
        self._setCommand(2, (
            Signals.RAO | Signals.RCI,
            MicroInstructions.IP_TO_MP,
            MicroInstructions.MO_TO_IH
        ))

        # MOV B A
        # move register B value to register A
        self._setCommand(3, (
            Signals.RBO | Signals.RAI,
            MicroInstructions.IP_TO_MP,
            MicroInstructions.MO_TO_IH
        ))

        # MOV B C
        # move register B value to register C
        self._setCommand(4, (
            Signals.RBO | Signals.RCI,
            MicroInstructions.IP_TO_MP,
            MicroInstructions.MO_TO_IH
        ))

        # MOV C A
        # move register C value to register A
        self._setCommand(5, (
            Signals.RCO | Signals.RAI,
            MicroInstructions.IP_TO_MP,
            MicroInstructions.MO_TO_IH
        ))

        # MOV C B
        # move register C value to register B
        self._setCommand(6, (
            Signals.RCO | Signals.RBI,
            MicroInstructions.IP_TO_MP,
            MicroInstructions.MO_TO_IH
        ))

        # MOV VALUE A
        # move the given value to register A
        self._setCommand(7, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | Signals.RAI,
            MicroInstructions.IP_TO_MP,
            MicroInstructions.MO_TO_IH
        ))

        # MOV {ROM_ADDRESS} A
        # move the ROM value that in the given address to register A
        self._setCommand(8, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.MOO | Signals.RAI,
            MicroInstructions.IP_TO_MP,
            MicroInstructions.MO_TO_IH
        ))

        # MOV [RAM_ADDRESS] A
        # move the RAM value that in the given address to register A
        self._setCommand(9, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.MAO | Signals.RAI,
            MicroInstructions.IP_TO_MP,
            MicroInstructions.MO_TO_IH
        ))

        # MOV A [RAM_ADDRESS]
        # move register A value to RAM in the given address
        self._setCommand(10, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.RAO | Signals.MAI,
            MicroInstructions.IP_TO_MP,
            MicroInstructions.MO_TO_IH
        ))

        # MOV VALUE B
        # move the given value to register B
        self._setCommand(11, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | Signals.RBI,
            MicroInstructions.IP_TO_MP,
            MicroInstructions.MO_TO_IH
        ))

        # MOV {ROM_ADDRESS} B
        # move the ROM value that in the given address to register B
        self._setCommand(12, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.MOO | Signals.RBI,
            MicroInstructions.IP_TO_MP,
            MicroInstructions.MO_TO_IH
        ))

        # MOV [RAM_ADDRESS] B
        # move the RAM value that in the given address to register B
        self._setCommand(13, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.MAO | Signals.RBI,
            MicroInstructions.IP_TO_MP,
            MicroInstructions.MO_TO_IH
        ))

        # MOV B [RAM_ADDRESS]
        # move register B value to RAM in the given address
        self._setCommand(14, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.RBO | Signals.MAI,
            MicroInstructions.IP_TO_MP,
            MicroInstructions.MO_TO_IH
        ))

        # MOV VALUE C
        # move the given value to register C
        self._setCommand(15, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | Signals.RCI,
            MicroInstructions.IP_TO_MP,
            MicroInstructions.MO_TO_IH
        ))

        # MOV {ROM_ADDRESS} C
        # move the ROM value that in the given address to register C
        self._setCommand(16, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.MOO | Signals.RCI,
            MicroInstructions.IP_TO_MP,
            MicroInstructions.MO_TO_IH
        ))

        # MOV [RAM_ADDRESS] C
        # move the RAM value that in the given address to register C
        self._setCommand(17, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.MAO | Signals.RCI,
            MicroInstructions.IP_TO_MP,
            MicroInstructions.MO_TO_IH
        ))

        # MOV C [RAM_ADDRESS]
        # move register C value to RAM in the given address
        self._setCommand(18, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.RCO | Signals.MAI,
            MicroInstructions.IP_TO_MP,
            MicroInstructions.MO_TO_IH
        ))

        ################################################################################
        # ADD
        ################################################################################

        # ADD A
        # calculate the sum of register A value and register A value (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(19, (
            Signals.RAO | Signals.RBI,
            MicroInstructions.ADDITION,
            MicroInstructions.IP_TO_MP,
            MicroInstructions.MO_TO_IH
        ))

        # ADD B
        # calculate the sum of register A value and register B value (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(20, (
            MicroInstructions.ADDITION,
            MicroInstructions.IP_TO_MP,
            MicroInstructions.MO_TO_IH
        ))

        # ADD C
        # calculate the sum of register A value and register C value (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(21, (
            Signals.RCO | Signals.RBI,
            MicroInstructions.ADDITION,
            MicroInstructions.IP_TO_MP,
            MicroInstructions.MO_TO_IH
        ))

        # ADD VALUE
        # calculate the sum of register A value and the given value (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(22, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | Signals.RBI,
            MicroInstructions.ADDITION,
            MicroInstructions.IP_TO_MP,
            MicroInstructions.MO_TO_IH
        ))

        # ADD {ROM_ADDRESS}
        # calculate the sum of register A value and the ROM value that in the given address (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(23, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.MOO | Signals.RBI,
            MicroInstructions.ADDITION,
            MicroInstructions.IP_TO_MP,
            MicroInstructions.MO_TO_IH
        ))

        # ADD [RAM_ADDRESS]
        # calculate the sum of register A value and the RAM value that in the given address (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(24, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.MAO | Signals.RBI,
            MicroInstructions.ADDITION,
            MicroInstructions.IP_TO_MP,
            MicroInstructions.MO_TO_IH
        ))

        ################################################################################
        # SUB
        ################################################################################

        # SUB A
        # calculate the subtraction of register A value and register A value (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(25, (
            Signals.RAO | Signals.RBI,
            MicroInstructions.SUBTRACTION,
            MicroInstructions.IP_TO_MP,
            MicroInstructions.MO_TO_IH
        ))

        # SUB B
        # calculate the subtraction of register A value and register B value (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(26, (
            MicroInstructions.SUBTRACTION,
            MicroInstructions.IP_TO_MP,
            MicroInstructions.MO_TO_IH
        ))

        # SUB C
        # calculate the subtraction of register A value and register C value (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(27, (
            Signals.RCO | Signals.RBI,
            MicroInstructions.SUBTRACTION,
            MicroInstructions.IP_TO_MP,
            MicroInstructions.MO_TO_IH
        ))

        # SUB VALUE
        # calculate the subtraction of register A value and the given value (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(28, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | Signals.RBI,
            MicroInstructions.SUBTRACTION,
            MicroInstructions.IP_TO_MP,
            MicroInstructions.MO_TO_IH
        ))

        # SUB {ROM_ADDRESS}
        # calculate the subtraction of register A value and the ROM value that in the given address (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(29, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.MOO | Signals.RBI,
            MicroInstructions.SUBTRACTION,
            MicroInstructions.IP_TO_MP,
            MicroInstructions.MO_TO_IH
        ))

        # SUB [RAM_ADDRESS]
        # calculate the subtraction of register A value and the RAM value that in the given address (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(30, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.MAO | Signals.RBI,
            MicroInstructions.SUBTRACTION,
            MicroInstructions.IP_TO_MP,
            MicroInstructions.MO_TO_IH
        ))

    def _setCommand(self, commandAddress: int, microCommands: Tuple[Signals]) -> None:
        assert commandAddress < NUM_OF_COMMANDS

        microCommandsLength = len(microCommands)
        assert microCommandsLength <= NUM_OF_MICRO_COMMANDS_PER_COMMAND

        for i in range(microCommandsLength):
            self.data[commandAddress][i] = microCommands[i]

    def dumps(self) -> bytes:
        pass


def main() -> None:
    microCode = MicroCode()
    microCodeBin = microCode.dump()


if __name__ == '__main__':
    main()
