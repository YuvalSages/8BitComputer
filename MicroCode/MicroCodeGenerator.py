
from enum import IntFlag
from typing import Tuple


NUM_OF_COMMANDS = 2**8
NUM_OF_MICRO_COMMANDS_PER_COMMAND = 2**3


class OutputSignals(IntFlag):
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


class MicroCode(object):
    def __init__(self):
        self._initializeDataStructure()
        self._fillMicroCode()

    def _initializeDataStructure(self) -> None:
        # create a matrix representing the default micro code
        self.data = [[OutputSignals.a for j in range(NUM_OF_MICRO_COMMANDS_PER_COMMAND)] for i in range(NUM_OF_COMMANDS)]

    def _fillMicroCode(self) -> None:
        # fill the micro code commands

        # 
        self._setCommand()

    def _setCommand(self, commandAddress: int, microCommands: Tuple[OutputSignals]) -> None:
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
