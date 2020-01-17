
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

    JMP = Signals.IPJ1
    JB = Signals.IPJ2
    JBE = Signals.IPJ1 | Signals.IPJ2
    JE = Signals.IPJ3
    JNE = Signals.IPJ1 | Signals.IPJ3
    JAE = Signals.IPJ2 | Signals.IPJ3
    JA = Signals.IPJ1 | Signals.IPJ2 | Signals.IPJ3


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

    def _setCommand(self, commandAddress: int, microCommands: Tuple[Signals]) -> None:
        microCommands = (*microCommands, MicroInstructions.IP_TO_MP, MicroInstructions.MO_TO_IH)

        assert commandAddress < NUM_OF_COMMANDS
        assert len(microCommands) <= NUM_OF_MICRO_COMMANDS_PER_COMMAND

        for i in range(len(microCommands)):
            self.data[commandAddress][i] = microCommands[i]

    def dumps(self) -> bytes:
        pass

    def _fillMicroCode(self) -> None:
        # fill the micro code commands

        ################################################################################
        # special instructions (0-49)
        ################################################################################

        # HLT
        # halt the clock to stop execution
        self._setCommand(0, (
            Signals.CLH
        ))

        # NOP
        # don't do anything
        self._setCommand(1, (
            MicroInstructions.NOP
        ))

        ################################################################################
        # MOV register A instructions (100-119)
        ################################################################################

        # MOV B A
        # move register B value to register A
        self._setCommand(100, (
            Signals.RBO | Signals.RAI
        ))

        # MOV C A
        # move register C value to register A
        self._setCommand(101, (
            Signals.RCO | Signals.RAI
        ))

        # MOV VALUE A
        # move the given value to register A
        self._setCommand(102, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | Signals.RAI
        ))

        # MOV {A} A
        # move the ROM value that in register A address to register A
        self._setCommand(103, (
            Signals.RAO | Signals.MPI,
            Signals.MOO | Signals.RAI
        ))

        # MOV {B} A
        # move the ROM value that in register B address to register A
        self._setCommand(104, (
            Signals.RBO | Signals.MPI,
            Signals.MOO | Signals.RAI
        ))

        # MOV {C} A
        # move the ROM value that in register C address to register A
        self._setCommand(105, (
            Signals.RCO | Signals.MPI,
            Signals.MOO | Signals.RAI
        ))

        # MOV {ROM_ADDRESS} A
        # move the ROM value that in the given address to register A
        self._setCommand(106, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.MOO | Signals.RAI
        ))

        # MOV [A] A
        # move the RAM value that in register A address to register A
        self._setCommand(107, (
            Signals.RAO | Signals.MPI,
            Signals.MAO | Signals.RAI
        ))

        # MOV [B] A
        # move the RAM value that in register B address to register A
        self._setCommand(108, (
            Signals.RBO | Signals.MPI,
            Signals.MAO | Signals.RAI
        ))

        # MOV [C] A
        # move the RAM value that in register C address to register A
        self._setCommand(109, (
            Signals.RCO | Signals.MPI,
            Signals.MAO | Signals.RAI
        ))

        # MOV [RAM_ADDRESS] A
        # move the RAM value that in the given address to register A
        self._setCommand(110, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.MAO | Signals.RAI
        ))

        # MOV A [A]
        # move register A value to RAM in register A address
        self._setCommand(111, (
            Signals.RAO | Signals.MPI,
            Signals.RAO | Signals.MAI
        ))

        # MOV A [B]
        # move register A value to RAM in register B address
        self._setCommand(112, (
            Signals.RBO | Signals.MPI,
            Signals.RAO | Signals.MAI
        ))

        # MOV A [C]
        # move register A value to RAM in register C address
        self._setCommand(113, (
            Signals.RCO | Signals.MPI,
            Signals.RAO | Signals.MAI
        ))

        # MOV A [RAM_ADDRESS]
        # move register A value to RAM in the given address
        self._setCommand(114, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.RAO | Signals.MAI
        ))

        ################################################################################
        # MOV register B instructions (120-139)
        ################################################################################

        # MOV A B
        # move register A value to register B
        self._setCommand(120, (
            Signals.RAO | Signals.RBI
        ))

        # MOV C B
        # move register C value to register B
        self._setCommand(121, (
            Signals.RCO | Signals.RBI
        ))

        # MOV VALUE B
        # move the given value to register B
        self._setCommand(122, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | Signals.RBI
        ))

        # MOV {A} B
        # move the ROM value that in register A address to register B
        self._setCommand(123, (
            Signals.RAO | Signals.MPI,
            Signals.MOO | Signals.RBI
        ))

        # MOV {B} B
        # move the ROM value that in register B address to register B
        self._setCommand(124, (
            Signals.RBO | Signals.MPI,
            Signals.MOO | Signals.RBI
        ))

        # MOV {C} B
        # move the ROM value that in register C address to register B
        self._setCommand(125, (
            Signals.RCO | Signals.MPI,
            Signals.MOO | Signals.RBI
        ))

        # MOV {ROM_ADDRESS} B
        # move the ROM value that in the given address to register B
        self._setCommand(126, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.MOO | Signals.RBI
        ))

        # MOV [A] B
        # move the RAM value that in register A address to register B
        self._setCommand(127, (
            Signals.RAO | Signals.MPI,
            Signals.MAO | Signals.RBI
        ))

        # MOV [B] B
        # move the RAM value that in register B address to register B
        self._setCommand(128, (
            Signals.RBO | Signals.MPI,
            Signals.MAO | Signals.RBI
        ))

        # MOV [C] B
        # move the RAM value that in register C address to register B
        self._setCommand(129, (
            Signals.RCO | Signals.MPI,
            Signals.MAO | Signals.RBI
        ))

        # MOV [RAM_ADDRESS] B
        # move the RAM value that in the given address to register B
        self._setCommand(130, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.MAO | Signals.RBI
        ))

        # MOV B [A]
        # move register B value to RAM in register A address
        self._setCommand(131, (
            Signals.RAO | Signals.MPI,
            Signals.RBO | Signals.MAI
        ))

        # MOV B [B]
        # move register B value to RAM in register B address
        self._setCommand(132, (
            Signals.RBO | Signals.MPI,
            Signals.RBO | Signals.MAI
        ))

        # MOV B [C]
        # move register B value to RAM in register C address
        self._setCommand(133, (
            Signals.RCO | Signals.MPI,
            Signals.RBO | Signals.MAI
        ))

        # MOV B [RAM_ADDRESS]
        # move register B value to RAM in the given address
        self._setCommand(134, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.RBO | Signals.MAI
        ))

        ################################################################################
        # MOV register C instructions (140-159)
        ################################################################################

        # MOV A C
        # move register A value to register C
        self._setCommand(140, (
            Signals.RAO | Signals.RCI
        ))

        # MOV B C
        # move register B value to register C
        self._setCommand(141, (
            Signals.RBO | Signals.RCI
        ))

        # MOV VALUE C
        # move the given value to register C
        self._setCommand(142, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | Signals.RCI
        ))

        # MOV {A} C
        # move the ROM value that in register A address to register C
        self._setCommand(143, (
            Signals.RAO | Signals.MPI,
            Signals.MOO | Signals.RCI
        ))

        # MOV {B} C
        # move the ROM value that in register B address to register C
        self._setCommand(144, (
            Signals.RBO | Signals.MPI,
            Signals.MOO | Signals.RCI
        ))

        # MOV {C} C
        # move the ROM value that in register C address to register C
        self._setCommand(145, (
            Signals.RCO | Signals.MPI,
            Signals.MOO | Signals.RCI
        ))

        # MOV {ROM_ADDRESS} C
        # move the ROM value that in the given address to register C
        self._setCommand(146, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.MOO | Signals.RCI
        ))

        # MOV [A] C
        # move the RAM value that in register A address to register C
        self._setCommand(147, (
            Signals.RAO | Signals.MPI,
            Signals.MAO | Signals.RCI
        ))

        # MOV [B] C
        # move the RAM value that in register B address to register C
        self._setCommand(148, (
            Signals.RBO | Signals.MPI,
            Signals.MAO | Signals.RCI
        ))

        # MOV [C] C
        # move the RAM value that in register C address to register C
        self._setCommand(149, (
            Signals.RCO | Signals.MPI,
            Signals.MAO | Signals.RCI
        ))

        # MOV [RAM_ADDRESS] C
        # move the RAM value that in the given address to register C
        self._setCommand(150, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.MAO | Signals.RCI
        ))

        # MOV C [A]
        # move register C value to RAM in register A address
        self._setCommand(151, (
            Signals.RAO | Signals.MPI,
            Signals.RCO | Signals.MAI
        ))

        # MOV C [B]
        # move register C value to RAM in register B address
        self._setCommand(152, (
            Signals.RBO | Signals.MPI,
            Signals.RCO | Signals.MAI
        ))

        # MOV C [C]
        # move register C value to RAM in register C address
        self._setCommand(153, (
            Signals.RCO | Signals.MPI,
            Signals.RCO | Signals.MAI
        ))

        # MOV C [RAM_ADDRESS]
        # move register C value to RAM in the given address
        self._setCommand(154, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.RCO | Signals.MAI
        ))

        ################################################################################
        # ADD instructions (160-179)
        ################################################################################

        # ADD A
        # calculate the sum of register A value with register A value (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(160, (
            Signals.RAO | Signals.RBI,
            MicroInstructions.ADDITION
        ))

        # ADD B
        # calculate the sum of register A value with register B value (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(161, (
            MicroInstructions.ADDITION
        ))

        # ADD C
        # calculate the sum of register A value with register C value (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(162, (
            Signals.RCO | Signals.RBI,
            MicroInstructions.ADDITION
        ))

        # ADD VALUE
        # calculate the sum of register A value with the given value (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(163, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | Signals.RBI,
            MicroInstructions.ADDITION
        ))

        # ADD {A}
        # calculate the sum of register A value with the ROM value that in register A address (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(164, (
            Signals.RAO | Signals.MPI,
            Signals.MOO | Signals.RBI,
            MicroInstructions.ADDITION
        ))

        # ADD {B}
        # calculate the sum of register A value with the ROM value that in register B address (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(165, (
            Signals.RBO | Signals.MPI,
            Signals.MOO | Signals.RBI,
            MicroInstructions.ADDITION
        ))

        # ADD {C}
        # calculate the sum of register A value with the ROM value that in register C address (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(166, (
            Signals.RCO | Signals.MPI,
            Signals.MOO | Signals.RBI,
            MicroInstructions.ADDITION
        ))

        # ADD {ROM_ADDRESS}
        # calculate the sum of register A value with the ROM value that in the given address (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(167, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.MOO | Signals.RBI,
            MicroInstructions.ADDITION
        ))

        # ADD [A]
        # calculate the sum of register A value with the RAM value that in register A address (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(168, (
            Signals.RAO | Signals.MPI,
            Signals.MAO | Signals.RBI,
            MicroInstructions.ADDITION
        ))

        # ADD [B]
        # calculate the sum of register A value with the RAM value that in register B address (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(169, (
            Signals.RBO | Signals.MPI,
            Signals.MAO | Signals.RBI,
            MicroInstructions.ADDITION
        ))

        # ADD [C]
        # calculate the sum of register A value with the RAM value that in register C address (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(170, (
            Signals.RCO | Signals.MPI,
            Signals.MAO | Signals.RBI,
            MicroInstructions.ADDITION
        ))

        # ADD [RAM_ADDRESS]
        # calculate the sum of register A value with the RAM value that in the given address (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(171, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.MAO | Signals.RBI,
            MicroInstructions.ADDITION
        ))

        ################################################################################
        # SUB instructions (180-199)
        ################################################################################

        # SUB A
        # calculate the subtraction of register A value with register A value (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(180, (
            Signals.RAO | Signals.RBI,
            MicroInstructions.SUBTRACTION
        ))

        # SUB B
        # calculate the subtraction of register A value with register B value (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(181, (
            MicroInstructions.SUBTRACTION
        ))

        # SUB C
        # calculate the subtraction of register A value with register C value (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(182, (
            Signals.RCO | Signals.RBI,
            MicroInstructions.SUBTRACTION
        ))

        # SUB VALUE
        # calculate the subtraction of register A value with the given value (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(183, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | Signals.RBI,
            MicroInstructions.SUBTRACTION
        ))

        # SUB {A}
        # calculate the subtraction of register A value with the ROM value that in register A address (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(184, (
            Signals.RAO | Signals.MPI,
            Signals.MOO | Signals.RBI,
            MicroInstructions.SUBTRACTION
        ))

        # SUB {B}
        # calculate the subtraction of register A value with the ROM value that in register B address (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(185, (
            Signals.RBO | Signals.MPI,
            Signals.MOO | Signals.RBI,
            MicroInstructions.SUBTRACTION
        ))

        # SUB {C}
        # calculate the subtraction of register A value with the ROM value that in register C address (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(186, (
            Signals.RCO | Signals.MPI,
            Signals.MOO | Signals.RBI,
            MicroInstructions.SUBTRACTION
        ))

        # SUB {ROM_ADDRESS}
        # calculate the subtraction of register A value with the ROM value that in the given address (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(187, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.MOO | Signals.RBI,
            MicroInstructions.SUBTRACTION
        ))

        # SUB [A]
        # calculate the subtraction of register A value with the RAM value that in register A address (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(188, (
            Signals.RAO | Signals.MPI,
            Signals.MAO | Signals.RBI,
            MicroInstructions.SUBTRACTION
        ))

        # SUB [B]
        # calculate the subtraction of register A value with the RAM value that in register B address (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(189, (
            Signals.RBO | Signals.MPI,
            Signals.MAO | Signals.RBI,
            MicroInstructions.SUBTRACTION
        ))

        # SUB [C]
        # calculate the subtraction of register A value with the RAM value that in register C address (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(190, (
            Signals.RCO | Signals.MPI,
            Signals.MAO | Signals.RBI,
            MicroInstructions.SUBTRACTION
        ))

        # SUB [RAM_ADDRESS]
        # calculate the subtraction of register A value with the RAM value that in the given address (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(191, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.MAO | Signals.RBI,
            MicroInstructions.SUBTRACTION
        ))

        ################################################################################
        # CMP instructions (200-219)
        ################################################################################

        # CMP A
        # compare (subtract) register A value with register A value (doesn't save the result, override register B, ZF and CF flags are affected)
        self._setCommand(200, (
            Signals.RAO | Signals.RBI,
            MicroInstructions.COMPARE
        ))

        # CMP B
        # compare (subtract) register A value with register B value (doesn't save the result, override register B, ZF and CF flags are affected)
        self._setCommand(201, (
            MicroInstructions.COMPARE
        ))

        # CMP C
        # compare (subtract) register A value with register C value (doesn't save the result, override register B, ZF and CF flags are affected)
        self._setCommand(202, (
            Signals.RCO | Signals.RBI,
            MicroInstructions.COMPARE
        ))

        # CMP VALUE
        # compare (subtract) register A value with the given value (doesn't save the result, override register B, ZF and CF flags are affected)
        self._setCommand(203, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | Signals.RBI,
            MicroInstructions.COMPARE
        ))

        # CMP {A}
        # compare (subtract) register A value with the ROM value that in register A address (doesn't save the result, override register B, ZF and CF flags are affected)
        self._setCommand(204, (
            Signals.RAO | Signals.MPI,
            Signals.MOO | Signals.RBI,
            MicroInstructions.COMPARE
        ))

        # CMP {B}
        # compare (subtract) register A value with the ROM value that in register B address (doesn't save the result, override register B, ZF and CF flags are affected)
        self._setCommand(205, (
            Signals.RBO | Signals.MPI,
            Signals.MOO | Signals.RBI,
            MicroInstructions.COMPARE
        ))

        # CMP {C}
        # compare (subtract) register A value with the ROM value that in register C address (doesn't save the result, override register B, ZF and CF flags are affected)
        self._setCommand(206, (
            Signals.RCO | Signals.MPI,
            Signals.MOO | Signals.RBI,
            MicroInstructions.COMPARE
        ))

        # CMP {ROM_ADDRESS}
        # compare (subtract) register A value with the ROM value that in the given address (doesn't save the result, override register B, ZF and CF flags are affected)
        self._setCommand(207, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.MOO | Signals.RBI,
            MicroInstructions.COMPARE
        ))

        # CMP [A]
        # compare (subtract) register A value with the RAM value that in register A address (doesn't save the result, override register B, ZF and CF flags are affected)
        self._setCommand(208, (
            Signals.RAO | Signals.MPI,
            Signals.MAO | Signals.RBI,
            MicroInstructions.COMPARE
        ))

        # CMP [B]
        # compare (subtract) register A value with the RAM value that in register B address (doesn't save the result, override register B, ZF and CF flags are affected)
        self._setCommand(209, (
            Signals.RBO | Signals.MPI,
            Signals.MAO | Signals.RBI,
            MicroInstructions.COMPARE
        ))

        # CMP [C]
        # compare (subtract) register A value with the RAM value that in register C address (doesn't save the result, override register B, ZF and CF flags are affected)
        self._setCommand(210, (
            Signals.RCO | Signals.MPI,
            Signals.MAO | Signals.RBI,
            MicroInstructions.COMPARE
        ))

        # CMP [RAM_ADDRESS]
        # compare (subtract) register A value with the RAM value that in the given address (doesn't save the result, override register B, ZF and CF flags are affected)
        self._setCommand(211, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.MAO | Signals.RBI,
            MicroInstructions.COMPARE
        ))

        ################################################################################
        # JMP to given VALUE instructions (220-229)
        ################################################################################

        # JMP VALUE
        # jump to the given address
        self._setCommand(220, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | MicroInstructions.JMP
        ))

        # JB VALUE
        # jump to the given address if CMP < 0 (CF==1)
        self._setCommand(221, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | MicroInstructions.JB
        ))

        # JBE VALUE
        # jump to the given address if CMP <= 0 (ZF==1 or CF==1)
        self._setCommand(222, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | MicroInstructions.JBE
        ))

        # JE VALUE
        # jump to the given address if CMP == 0 (ZF==1)
        self._setCommand(223, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | MicroInstructions.JE
        ))

        # JNE VALUE
        # jump to the given address if CMP != 0 (ZF==0)
        self._setCommand(224, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | MicroInstructions.JNE
        ))

        # JAE VALUE
        # jump to the given address if CMP >= 0 (CF==0)
        self._setCommand(225, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | MicroInstructions.JAE
        ))

        # JA VALUE
        # jump to the given address if CMP > 0 (ZF==0 and CF==0)
        self._setCommand(226, (
            MicroInstructions.IP_TO_MP,
            Signals.MOO | MicroInstructions.JA
        ))

        ################################################################################
        # JMP to register A Value instructions (230-239)
        ################################################################################

        # JMP A
        # jump to the address that in register A
        self._setCommand(230, (
            Signals.RAO | MicroInstructions.JMP
        ))

        # JB A
        # jump to the address that in register A if CMP < 0 (CF==1)
        self._setCommand(231, (
            Signals.RAO | MicroInstructions.JB
        ))

        # JBE A
        # jump to the address that in register A if CMP <= 0 (ZF==1 or CF==1)
        self._setCommand(232, (
            Signals.RAO | MicroInstructions.JBE
        ))

        # JE A
        # jump to the address that in register A if CMP == 0 (ZF==1)
        self._setCommand(233, (
            Signals.RAO | MicroInstructions.JE
        ))

        # JNE A
        # jump to the address that in register A if CMP != 0 (ZF==0)
        self._setCommand(234, (
            Signals.RAO | MicroInstructions.JNE
        ))

        # JAE A
        # jump to the address that in register A if CMP >= 0 (CF==0)
        self._setCommand(235, (
            Signals.RAO | MicroInstructions.JAE
        ))

        # JA A
        # jump to the address that in register A if CMP > 0 (ZF==0 and CF==0)
        self._setCommand(236, (
            Signals.RAO | MicroInstructions.JA
        ))


def main() -> None:
    microCode = MicroCode()
    microCodeBin = microCode.dump()


if __name__ == '__main__':
    main()
