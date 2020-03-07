
from struct import pack
from enum import IntFlag
from typing import List, Tuple, Generator


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


class MicroCommands(IntFlag):
    NOP = 0

    IP_TO_MP = Signals.IPO | Signals.MPI | Signals.IPC
    MO_TO_IH = Signals.MOO | Signals.IHI

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


ADDRESS_SPACE_SIZE = 2**11
NUM_OF_COMMANDS = 2**8
NUM_OF_MICRO_COMMANDS_PER_COMMAND = 2**3
DEFAULT_MICRO_COMMAND = Signals.CLH
INVERT_ALL = True


class MicroCode():
    def __init__(self):
        self._initializeDataStructure()
        self._fillMicroCode()

    def _initializeDataStructure(self) -> None:
        # create a array representing the default micro code
        self.data = [DEFAULT_MICRO_COMMAND for i in range(ADDRESS_SPACE_SIZE)]

    def _setCommand(self, commandAddress: int, microCommands: List[Signals]) -> None:
        assert commandAddress < NUM_OF_COMMANDS
        assert len(microCommands) <= NUM_OF_MICRO_COMMANDS_PER_COMMAND - 2

        microCommands = [*microCommands, MicroCommands.IP_TO_MP, MicroCommands.MO_TO_IH, Signals.CCR][:8]

        for (i, microCommand) in enumerate(microCommands):
            fullAddress = (i << 8) | commandAddress
            self.data[fullAddress] = microCommand

    def dumps(self) -> Generator[Tuple[bytes, bytes, bytes], None, None]:
        for command in self.data:
            commandBin = pack('<I', command)
            if INVERT_ALL:
                yield (
                    pack('B', ~ commandBin[0] + 2**8),
                    pack('B', ~ commandBin[1] + 2**8),
                    pack('B', ~ commandBin[2] + 2**8)
                )
            else:
                yield (
                    pack('B', commandBin[0]),
                    pack('B', commandBin[1]),
                    pack('B', commandBin[2])
                )

    def dump(self, filePath1: str, filePath2: str, filePath3: str) -> None:
        with open(filePath1, 'wb') as f1:
            with open(filePath2, 'wb') as f2:
                with open(filePath3, 'wb') as f3:
                    for commandBin in self.dumps():
                        f1.write(commandBin[0])
                        f2.write(commandBin[1])
                        f3.write(commandBin[2])

    def _fillMicroCode(self) -> None:
        # fill the micro code commands

        ################################################################################
        # special instructions (0-49)
        ################################################################################

        # HLT
        # halt the clock to stop execution
        self._setCommand(0, [
            Signals.CLH,
        ])

        # NOP
        # don't do anything
        self._setCommand(1, [
            MicroCommands.NOP,
        ])

        ################################################################################
        # MOV register A instructions (100-119)
        ################################################################################

        # MOV B A
        # move register B value to register A
        self._setCommand(100, [
            Signals.RBO | Signals.RAI,
        ])

        # MOV C A
        # move register C value to register A
        self._setCommand(101, [
            Signals.RCO | Signals.RAI,
        ])

        # MOV {A} A
        # move the ROM value that in register A address to register A
        self._setCommand(102, [
            Signals.RAO | Signals.MPI,
            Signals.MOO | Signals.RAI
        ])

        # MOV {B} A
        # move the ROM value that in register B address to register A
        self._setCommand(103, [
            Signals.RBO | Signals.MPI,
            Signals.MOO | Signals.RAI
        ])

        # MOV {C} A
        # move the ROM value that in register C address to register A
        self._setCommand(104, [
            Signals.RCO | Signals.MPI,
            Signals.MOO | Signals.RAI
        ])

        # MOV {ROM_ADDRESS} A
        # move the ROM value that in the given address to register A
        self._setCommand(105, [
            MicroCommands.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.MOO | Signals.RAI
        ])

        # MOV [A] A
        # move the RAM value that in register A address to register A
        self._setCommand(106, [
            Signals.RAO | Signals.MPI,
            Signals.MAO | Signals.RAI
        ])

        # MOV [B] A
        # move the RAM value that in register B address to register A
        self._setCommand(107, [
            Signals.RBO | Signals.MPI,
            Signals.MAO | Signals.RAI
        ])

        # MOV [C] A
        # move the RAM value that in register C address to register A
        self._setCommand(108, [
            Signals.RCO | Signals.MPI,
            Signals.MAO | Signals.RAI
        ])

        # MOV [RAM_ADDRESS] A
        # move the RAM value that in the given address to register A
        self._setCommand(109, [
            MicroCommands.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.MAO | Signals.RAI
        ])

        # MOV VALUE A
        # move the given value to register A
        self._setCommand(110, [
            MicroCommands.IP_TO_MP,
            Signals.MOO | Signals.RAI
        ])

        # MOV A [A]
        # move register A value to RAM in register A address
        self._setCommand(111, [
            Signals.RAO | Signals.MPI,
            Signals.RAO | Signals.MAI
        ])

        # MOV A [B]
        # move register A value to RAM in register B address
        self._setCommand(112, [
            Signals.RBO | Signals.MPI,
            Signals.RAO | Signals.MAI
        ])

        # MOV A [C]
        # move register A value to RAM in register C address
        self._setCommand(113, [
            Signals.RCO | Signals.MPI,
            Signals.RAO | Signals.MAI
        ])

        # MOV A [RAM_ADDRESS]
        # move register A value to RAM in the given address
        self._setCommand(114, [
            MicroCommands.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.RAO | Signals.MAI
        ])

        ################################################################################
        # MOV register B instructions (120-139)
        ################################################################################

        # MOV A B
        # move register A value to register B
        self._setCommand(120, [
            Signals.RAO | Signals.RBI,
        ])

        # MOV C B
        # move register C value to register B
        self._setCommand(121, [
            Signals.RCO | Signals.RBI,
        ])

        # MOV {A} B
        # move the ROM value that in register A address to register B
        self._setCommand(122, [
            Signals.RAO | Signals.MPI,
            Signals.MOO | Signals.RBI
        ])

        # MOV {B} B
        # move the ROM value that in register B address to register B
        self._setCommand(123, [
            Signals.RBO | Signals.MPI,
            Signals.MOO | Signals.RBI
        ])

        # MOV {C} B
        # move the ROM value that in register C address to register B
        self._setCommand(124, [
            Signals.RCO | Signals.MPI,
            Signals.MOO | Signals.RBI
        ])

        # MOV {ROM_ADDRESS} B
        # move the ROM value that in the given address to register B
        self._setCommand(125, [
            MicroCommands.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.MOO | Signals.RBI
        ])

        # MOV [A] B
        # move the RAM value that in register A address to register B
        self._setCommand(126, [
            Signals.RAO | Signals.MPI,
            Signals.MAO | Signals.RBI
        ])

        # MOV [B] B
        # move the RAM value that in register B address to register B
        self._setCommand(127, [
            Signals.RBO | Signals.MPI,
            Signals.MAO | Signals.RBI
        ])

        # MOV [C] B
        # move the RAM value that in register C address to register B
        self._setCommand(128, [
            Signals.RCO | Signals.MPI,
            Signals.MAO | Signals.RBI
        ])

        # MOV [RAM_ADDRESS] B
        # move the RAM value that in the given address to register B
        self._setCommand(129, [
            MicroCommands.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.MAO | Signals.RBI
        ])

        # MOV VALUE B
        # move the given value to register B
        self._setCommand(130, [
            MicroCommands.IP_TO_MP,
            Signals.MOO | Signals.RBI
        ])

        # MOV B [A]
        # move register B value to RAM in register A address
        self._setCommand(131, [
            Signals.RAO | Signals.MPI,
            Signals.RBO | Signals.MAI
        ])

        # MOV B [B]
        # move register B value to RAM in register B address
        self._setCommand(132, [
            Signals.RBO | Signals.MPI,
            Signals.RBO | Signals.MAI
        ])

        # MOV B [C]
        # move register B value to RAM in register C address
        self._setCommand(133, [
            Signals.RCO | Signals.MPI,
            Signals.RBO | Signals.MAI
        ])

        # MOV B [RAM_ADDRESS]
        # move register B value to RAM in the given address
        self._setCommand(134, [
            MicroCommands.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.RBO | Signals.MAI
        ])

        ################################################################################
        # MOV register C instructions (140-159)
        ################################################################################

        # MOV A C
        # move register A value to register C
        self._setCommand(140, [
            Signals.RAO | Signals.RCI
        ])

        # MOV B C
        # move register B value to register C
        self._setCommand(141, [
            Signals.RBO | Signals.RCI
        ])

        # MOV {A} C
        # move the ROM value that in register A address to register C
        self._setCommand(142, [
            Signals.RAO | Signals.MPI,
            Signals.MOO | Signals.RCI
        ])

        # MOV {B} C
        # move the ROM value that in register B address to register C
        self._setCommand(143, [
            Signals.RBO | Signals.MPI,
            Signals.MOO | Signals.RCI
        ])

        # MOV {C} C
        # move the ROM value that in register C address to register C
        self._setCommand(144, [
            Signals.RCO | Signals.MPI,
            Signals.MOO | Signals.RCI
        ])

        # MOV {ROM_ADDRESS} C
        # move the ROM value that in the given address to register C
        self._setCommand(145, [
            MicroCommands.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.MOO | Signals.RCI
        ])

        # MOV [A] C
        # move the RAM value that in register A address to register C
        self._setCommand(146, [
            Signals.RAO | Signals.MPI,
            Signals.MAO | Signals.RCI
        ])

        # MOV [B] C
        # move the RAM value that in register B address to register C
        self._setCommand(147, [
            Signals.RBO | Signals.MPI,
            Signals.MAO | Signals.RCI
        ])

        # MOV [C] C
        # move the RAM value that in register C address to register C
        self._setCommand(148, [
            Signals.RCO | Signals.MPI,
            Signals.MAO | Signals.RCI
        ])

        # MOV [RAM_ADDRESS] C
        # move the RAM value that in the given address to register C
        self._setCommand(149, [
            MicroCommands.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.MAO | Signals.RCI
        ])

        # MOV VALUE C
        # move the given value to register C
        self._setCommand(150, [
            MicroCommands.IP_TO_MP,
            Signals.MOO | Signals.RCI
        ])

        # MOV C [A]
        # move register C value to RAM in register A address
        self._setCommand(151, [
            Signals.RAO | Signals.MPI,
            Signals.RCO | Signals.MAI
        ])

        # MOV C [B]
        # move register C value to RAM in register B address
        self._setCommand(152, [
            Signals.RBO | Signals.MPI,
            Signals.RCO | Signals.MAI
        ])

        # MOV C [C]
        # move register C value to RAM in register C address
        self._setCommand(153, [
            Signals.RCO | Signals.MPI,
            Signals.RCO | Signals.MAI
        ])

        # MOV C [RAM_ADDRESS]
        # move register C value to RAM in the given address
        self._setCommand(154, [
            MicroCommands.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.RCO | Signals.MAI
        ])

        ################################################################################
        # ADD instructions (160-179)
        ################################################################################

        # ADD A
        # calculate the sum of register A value with register A value (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(160, [
            Signals.RAO | Signals.RBI,
            MicroCommands.ADDITION
        ])

        # ADD B
        # calculate the sum of register A value with register B value (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(161, [
            MicroCommands.ADDITION
        ])

        # ADD C
        # calculate the sum of register A value with register C value (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(162, [
            Signals.RCO | Signals.RBI,
            MicroCommands.ADDITION
        ])

        # ADD {A}
        # calculate the sum of register A value with the ROM value that in register A address (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(163, [
            Signals.RAO | Signals.MPI,
            Signals.MOO | Signals.RBI,
            MicroCommands.ADDITION
        ])

        # ADD {B}
        # calculate the sum of register A value with the ROM value that in register B address (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(164, [
            Signals.RBO | Signals.MPI,
            Signals.MOO | Signals.RBI,
            MicroCommands.ADDITION
        ])

        # ADD {C}
        # calculate the sum of register A value with the ROM value that in register C address (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(165, [
            Signals.RCO | Signals.MPI,
            Signals.MOO | Signals.RBI,
            MicroCommands.ADDITION
        ])

        # ADD {ROM_ADDRESS}
        # calculate the sum of register A value with the ROM value that in the given address (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(166, [
            MicroCommands.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.MOO | Signals.RBI,
            MicroCommands.ADDITION
        ])

        # ADD [A]
        # calculate the sum of register A value with the RAM value that in register A address (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(167, [
            Signals.RAO | Signals.MPI,
            Signals.MAO | Signals.RBI,
            MicroCommands.ADDITION
        ])

        # ADD [B]
        # calculate the sum of register A value with the RAM value that in register B address (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(168, [
            Signals.RBO | Signals.MPI,
            Signals.MAO | Signals.RBI,
            MicroCommands.ADDITION
        ])

        # ADD [C]
        # calculate the sum of register A value with the RAM value that in register C address (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(169, [
            Signals.RCO | Signals.MPI,
            Signals.MAO | Signals.RBI,
            MicroCommands.ADDITION
        ])

        # ADD [RAM_ADDRESS]
        # calculate the sum of register A value with the RAM value that in the given address (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(170, [
            MicroCommands.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.MAO | Signals.RBI,
            MicroCommands.ADDITION
        ])

        # ADD VALUE
        # calculate the sum of register A value with the given value (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(171, [
            MicroCommands.IP_TO_MP,
            Signals.MOO | Signals.RBI,
            MicroCommands.ADDITION
        ])

        ################################################################################
        # SUB instructions (180-199)
        ################################################################################

        # SUB A
        # calculate the subtraction of register A value with register A value (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(180, [
            Signals.RAO | Signals.RBI,
            MicroCommands.SUBTRACTION
        ])

        # SUB B
        # calculate the subtraction of register A value with register B value (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(181, [
            MicroCommands.SUBTRACTION
        ])

        # SUB C
        # calculate the subtraction of register A value with register C value (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(182, [
            Signals.RCO | Signals.RBI,
            MicroCommands.SUBTRACTION
        ])

        # SUB {A}
        # calculate the subtraction of register A value with the ROM value that in register A address (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(183, [
            Signals.RAO | Signals.MPI,
            Signals.MOO | Signals.RBI,
            MicroCommands.SUBTRACTION
        ])

        # SUB {B}
        # calculate the subtraction of register A value with the ROM value that in register B address (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(184, [
            Signals.RBO | Signals.MPI,
            Signals.MOO | Signals.RBI,
            MicroCommands.SUBTRACTION
        ])

        # SUB {C}
        # calculate the subtraction of register A value with the ROM value that in register C address (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(185, [
            Signals.RCO | Signals.MPI,
            Signals.MOO | Signals.RBI,
            MicroCommands.SUBTRACTION
        ])

        # SUB {ROM_ADDRESS}
        # calculate the subtraction of register A value with the ROM value that in the given address (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(186, [
            MicroCommands.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.MOO | Signals.RBI,
            MicroCommands.SUBTRACTION
        ])

        # SUB [A]
        # calculate the subtraction of register A value with the RAM value that in register A address (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(187, [
            Signals.RAO | Signals.MPI,
            Signals.MAO | Signals.RBI,
            MicroCommands.SUBTRACTION
        ])

        # SUB [B]
        # calculate the subtraction of register A value with the RAM value that in register B address (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(188, [
            Signals.RBO | Signals.MPI,
            Signals.MAO | Signals.RBI,
            MicroCommands.SUBTRACTION
        ])

        # SUB [C]
        # calculate the subtraction of register A value with the RAM value that in register C address (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(189, [
            Signals.RCO | Signals.MPI,
            Signals.MAO | Signals.RBI,
            MicroCommands.SUBTRACTION
        ])

        # SUB [RAM_ADDRESS]
        # calculate the subtraction of register A value with the RAM value that in the given address (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(190, [
            MicroCommands.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.MAO | Signals.RBI,
            MicroCommands.SUBTRACTION
        ])

        # SUB VALUE
        # calculate the subtraction of register A value with the given value (put the result in register A, override register B, ZF and CF flags are affected)
        self._setCommand(191, [
            MicroCommands.IP_TO_MP,
            Signals.MOO | Signals.RBI,
            MicroCommands.SUBTRACTION
        ])

        ################################################################################
        # CMP instructions (200-219)
        ################################################################################

        # CMP A
        # compare (subtract) register A value with register A value (doesn't save the result, override register B, ZF and CF flags are affected)
        self._setCommand(200, [
            Signals.RAO | Signals.RBI,
            MicroCommands.COMPARE
        ])

        # CMP B
        # compare (subtract) register A value with register B value (doesn't save the result, override register B, ZF and CF flags are affected)
        self._setCommand(201, [
            MicroCommands.COMPARE
        ])

        # CMP C
        # compare (subtract) register A value with register C value (doesn't save the result, override register B, ZF and CF flags are affected)
        self._setCommand(202, [
            Signals.RCO | Signals.RBI,
            MicroCommands.COMPARE
        ])

        # CMP {A}
        # compare (subtract) register A value with the ROM value that in register A address (doesn't save the result, override register B, ZF and CF flags are affected)
        self._setCommand(203, [
            Signals.RAO | Signals.MPI,
            Signals.MOO | Signals.RBI,
            MicroCommands.COMPARE
        ])

        # CMP {B}
        # compare (subtract) register A value with the ROM value that in register B address (doesn't save the result, override register B, ZF and CF flags are affected)
        self._setCommand(204, [
            Signals.RBO | Signals.MPI,
            Signals.MOO | Signals.RBI,
            MicroCommands.COMPARE
        ])

        # CMP {C}
        # compare (subtract) register A value with the ROM value that in register C address (doesn't save the result, override register B, ZF and CF flags are affected)
        self._setCommand(205, [
            Signals.RCO | Signals.MPI,
            Signals.MOO | Signals.RBI,
            MicroCommands.COMPARE
        ])

        # CMP {ROM_ADDRESS}
        # compare (subtract) register A value with the ROM value that in the given address (doesn't save the result, override register B, ZF and CF flags are affected)
        self._setCommand(206, [
            MicroCommands.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.MOO | Signals.RBI,
            MicroCommands.COMPARE
        ])

        # CMP [A]
        # compare (subtract) register A value with the RAM value that in register A address (doesn't save the result, override register B, ZF and CF flags are affected)
        self._setCommand(207, [
            Signals.RAO | Signals.MPI,
            Signals.MAO | Signals.RBI,
            MicroCommands.COMPARE
        ])

        # CMP [B]
        # compare (subtract) register A value with the RAM value that in register B address (doesn't save the result, override register B, ZF and CF flags are affected)
        self._setCommand(208, [
            Signals.RBO | Signals.MPI,
            Signals.MAO | Signals.RBI,
            MicroCommands.COMPARE
        ])

        # CMP [C]
        # compare (subtract) register A value with the RAM value that in register C address (doesn't save the result, override register B, ZF and CF flags are affected)
        self._setCommand(209, [
            Signals.RCO | Signals.MPI,
            Signals.MAO | Signals.RBI,
            MicroCommands.COMPARE
        ])

        # CMP [RAM_ADDRESS]
        # compare (subtract) register A value with the RAM value that in the given address (doesn't save the result, override register B, ZF and CF flags are affected)
        self._setCommand(210, [
            MicroCommands.IP_TO_MP,
            Signals.MOO | Signals.MPI,
            Signals.MAO | Signals.RBI,
            MicroCommands.COMPARE
        ])

        # CMP VALUE
        # compare (subtract) register A value with the given value (doesn't save the result, override register B, ZF and CF flags are affected)
        self._setCommand(211, [
            MicroCommands.IP_TO_MP,
            Signals.MOO | Signals.RBI,
            MicroCommands.COMPARE
        ])

        ################################################################################
        # JMP to register A Value instructions (220-229)
        ################################################################################

        # JMP A
        # jump to the address that in register A
        self._setCommand(220, [
            Signals.RAO | MicroCommands.JMP
        ])

        # JB A
        # jump to the address that in register A if CMP < 0 (CF==1)
        self._setCommand(221, [
            Signals.RAO | MicroCommands.JB
        ])

        # JBE A
        # jump to the address that in register A if CMP <= 0 (ZF==1 or CF==1)
        self._setCommand(222, [
            Signals.RAO | MicroCommands.JBE
        ])

        # JE A
        # jump to the address that in register A if CMP == 0 (ZF==1)
        self._setCommand(223, [
            Signals.RAO | MicroCommands.JE
        ])

        # JNE A
        # jump to the address that in register A if CMP != 0 (ZF==0)
        self._setCommand(224, [
            Signals.RAO | MicroCommands.JNE
        ])

        # JAE A
        # jump to the address that in register A if CMP >= 0 (CF==0)
        self._setCommand(225, [
            Signals.RAO | MicroCommands.JAE
        ])

        # JA A
        # jump to the address that in register A if CMP > 0 (ZF==0 and CF==0)
        self._setCommand(226, [
            Signals.RAO | MicroCommands.JA
        ])

        ################################################################################
        # JMP to given VALUE instructions (230-239)
        ################################################################################

        # JMP VALUE
        # jump to the given address
        self._setCommand(230, [
            MicroCommands.IP_TO_MP,
            Signals.MOO | MicroCommands.JMP
        ])

        # JB VALUE
        # jump to the given address if CMP < 0 (CF==1)
        self._setCommand(231, [
            MicroCommands.IP_TO_MP,
            Signals.MOO | MicroCommands.JB
        ])

        # JBE VALUE
        # jump to the given address if CMP <= 0 (ZF==1 or CF==1)
        self._setCommand(232, [
            MicroCommands.IP_TO_MP,
            Signals.MOO | MicroCommands.JBE
        ])

        # JE VALUE
        # jump to the given address if CMP == 0 (ZF==1)
        self._setCommand(233, [
            MicroCommands.IP_TO_MP,
            Signals.MOO | MicroCommands.JE
        ])

        # JNE VALUE
        # jump to the given address if CMP != 0 (ZF==0)
        self._setCommand(234, [
            MicroCommands.IP_TO_MP,
            Signals.MOO | MicroCommands.JNE
        ])

        # JAE VALUE
        # jump to the given address if CMP >= 0 (CF==0)
        self._setCommand(235, [
            MicroCommands.IP_TO_MP,
            Signals.MOO | MicroCommands.JAE
        ])

        # JA VALUE
        # jump to the given address if CMP > 0 (ZF==0 and CF==0)
        self._setCommand(236, [
            MicroCommands.IP_TO_MP,
            Signals.MOO | MicroCommands.JA
        ])


class SecondaryMicroCode_InSignals(IntFlag):
    IPJ1 = 2**0  # INSTRUCTION  POINTER  JUMP_1
    IPJ2 = 2**1  # INSTRUCTION  POINTER  JUMP_2
    IPJ3 = 2**2  # INSTRUCTION  POINTER  JUMP_3
    IPJ4 = 2**3  # INSTRUCTION  POINTER  JUMP_4

    CF = 2**8  # CARRY FLAG
    ZF = 2**9  # ZERO FLAG


class SecondaryMicroCode_OutSignals(IntFlag):
    NOP = 0
    IPJ = 2**0  # INSTRUCTION  POINTER  JUMP_1


class SecondaryMicroCode(object):

    def __init__(self):
        self._initializeDataStructure()
        self._fillMicroCode()

    def _initializeDataStructure(self) -> None:
        # create a array representing the default secondary micro code
        self.data = [SecondaryMicroCode_OutSignals.NOP for i in range(ADDRESS_SPACE_SIZE)]

    def _setJumpCommand(self, inSignals: SecondaryMicroCode_InSignals, zf: bool = None, cf: bool = None) -> None:
        assert inSignals < 2**4
        inSignals = 0b1111 - inSignals

        for i in range(2**7):
            fullAddress = (i << 4) | inSignals

            if (zf is False and fullAddress & SecondaryMicroCode_InSignals.ZF != 0) or \
                    (zf is True and fullAddress & SecondaryMicroCode_InSignals.ZF == 0) or \
                    (cf is False and fullAddress & SecondaryMicroCode_InSignals.CF != 0) or \
                    (cf is True and fullAddress & SecondaryMicroCode_InSignals.CF == 0):
                break

            self.data[fullAddress] = SecondaryMicroCode_OutSignals.IPJ

    def dumps(self) -> Generator[bytes, None, None]:
        for command in self.data:
            if INVERT_ALL:
                yield pack('B', ~ command + 2**8)
            else:
                yield pack('B', command)

    def dump(self, filePath: str) -> None:
        with open(filePath, 'wb') as f:
            for commandBin in self.dumps():
                f.write(commandBin)

    def _fillMicroCode(self) -> None:
        # fill the micro code commands

        ################################################################################
        # JMP secondary instructions
        ################################################################################

        # JMP
        # jump to the given address
        self._setJumpCommand(
            SecondaryMicroCode_InSignals.IPJ1
        )

        # JB
        # jump to the given address if CMP < 0 (CF==1)
        self._setJumpCommand(
            SecondaryMicroCode_InSignals.IPJ2,
            cf=True
        )

        # JBE
        # jump to the given address if CMP <= 0 (ZF==1 or CF==1)
        self._setJumpCommand(
            SecondaryMicroCode_InSignals.IPJ1 | SecondaryMicroCode_InSignals.IPJ2,
            zf=True
        )
        self._setJumpCommand(
            SecondaryMicroCode_InSignals.IPJ1 | SecondaryMicroCode_InSignals.IPJ2,
            cf=True
        )

        # JE
        # jump to the given address if CMP == 0 (ZF==1)
        self._setJumpCommand(
            SecondaryMicroCode_InSignals.IPJ3,
            zf=True
        )

        # JNE
        # jump to the given address if CMP != 0 (ZF==0)
        self._setJumpCommand(
            SecondaryMicroCode_InSignals.IPJ1 | SecondaryMicroCode_InSignals.IPJ3,
            zf=False
        )

        # JAE
        # jump to the given address if CMP >= 0 (CF==0)
        self._setJumpCommand(
            SecondaryMicroCode_InSignals.IPJ2 | SecondaryMicroCode_InSignals.IPJ3,
            cf=False
        )

        # JA
        # jump to the given address if CMP > 0 (ZF==0 and CF==0)
        self._setJumpCommand(
            SecondaryMicroCode_InSignals.IPJ1 | SecondaryMicroCode_InSignals.IPJ1 | SecondaryMicroCode_InSignals.IPJ3,
            zf=False,
            cf=False
        )


def main() -> None:
    microCode = MicroCode()
    secondaryMicroCode = SecondaryMicroCode()

    microCode.dump('./microCode_1.bin', './microCode_2.bin', './microCode_3.bin')
    secondaryMicroCode.dump('./secondaryMicroCode.bin')


if __name__ == '__main__':
    main()
