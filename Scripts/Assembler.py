'''
8 Bit Computer Assembler.


Support all of the 8 bit computer commands.

Support the declaration of:
Defineds - $definedName VALUE            - every mention of a defined will be replaced with its value.
Consts   - $constName {VALUE VALUE, ...} - list of values that will be appended to the program on ROM, every mention of a const will be replaced with its address.
Vars     - $varName [varSize]            - var is a reserved memory on RAM in the length of varSize bytes, every mention of a var will be replaced with its address.
Lables   - $lableName:                   - every mention of a lable will be replaced with the address of the command that follows the lable.

Support comments by the use of '//' or '#'.


Code example:
    // Count the sum of the array [4, 2, 7, 9, 13, 24], multiply the sum by 3 and display the result.

    // declare defines, consts and vars
    $multiplier 3                     // $multiplier mentions will become 3
    $arraySize 6                      // $arraySize mentions will become 6
    $array {4, 2, 7, 0x09, 0x0D, 24}  // will save the array on ROM on $array address
    $index [1]                        // a var on RAM of 1 bytes on $index address
    $sum [1]                          // a var on RAM of 1 bytes on $sum address
    $multiplierIteration [1]          // a var on RAM of 1 bytes on $multiplierIteration address
    $result [1]                       // a var on RAM of 1 bytes on $result address

    // code
    $initializeVars:
        // initialize the variables
        MOV 0 A
        MOV A [$index]
        MOV A [$sum]
        MOV A [$multiplierIteration]
        MOV A [$result]

    $sumArray:
        // if $index reached $arraySize then jump to $multiplySum
        MOV [$index] A
        CMP $arraySize
        JAE $multiplySum

        ADD $array     // calculate the address of the next array item
        MOV {A} A     // put the value of the next array item in A
        ADD [$sum]     // add it to the sum
        MOV A [$sum]  // save the result back to $sum

        // increase $index by 1
        MOV [$index] A
        ADD 0x01
        MOV A [$index]
        JMP $sumArray

    $multiplySum:
        // if $multiplierIteration reached $multiplier then jump to $displayResult
        MOV [$multiplierIteration] A
        CMP $multiplier
        JAE $displayResult

        // add $sum to $result
        MOV [$result] A
        ADD [$sum]
        MOV A [$result]

        // increase $multiplierIteration by 1
        MOV [$multiplierIteration] A
        ADD 1
        MOV A [$multiplierIteration]
        JMP $multiplySum

    $displayResult:
    MOV [$result] C
    HLT
'''


import argparse
from struct import pack
from typing import List, Dict

from parse import parse


WORD_SIZE = 2**8
ROM_SIZE = 2**8
RAM_SIZE = 2**8

COMMANDS = [
    ################################################################################
    # special instructions (0-49)
    ################################################################################
    (0, 'HLT'),  # HLT - halt the clock to stop execution
    (1, 'NOP'),  # NOP - don't do anything

    ################################################################################
    # MOV register A instructions (100-119)
    ################################################################################
    (100, 'MOV B A'),       # MOV B A             - move register B value to register A
    (101, 'MOV C A'),       # MOV C A             - move register C value to register A
    (102, 'MOV {{A}} A'),   # MOV {A} A           - move the ROM value that in register A address to register A
    (103, 'MOV {{B}} A'),   # MOV {B} A           - move the ROM value that in register B address to register A
    (104, 'MOV {{C}} A'),   # MOV {C} A           - move the ROM value that in register C address to register A
    (105, 'MOV {{{}}} A'),  # MOV {ROM_ADDRESS} A - move the ROM value that in the given address to register A
    (106, 'MOV [A] A'),     # MOV [A] A           - move the RAM value that in register A address to register A
    (107, 'MOV [B] A'),     # MOV [B] A           - move the RAM value that in register B address to register A
    (108, 'MOV [C] A'),     # MOV [C] A           - move the RAM value that in register C address to register A
    (109, 'MOV [{}] A'),    # MOV [RAM_ADDRESS] A - move the RAM value that in the given address to register A
    (110, 'MOV {} A'),      # MOV VALUE A         - move the given value to register A
    (111, 'MOV A [A]'),     # MOV A [A]           - move register A value to RAM in register A address
    (112, 'MOV A [B]'),     # MOV A [B]           - move register A value to RAM in register B address
    (113, 'MOV A [C]'),     # MOV A [C]           - move register A value to RAM in register C address
    (114, 'MOV A [{}]'),    # MOV A [RAM_ADDRESS] - move register A value to RAM in the given address

    ################################################################################
    # MOV register B instructions (120-139)
    ################################################################################
    (120, 'MOV A B'),       # MOV A B             - move register A value to register B
    (121, 'MOV C B'),       # MOV C B             - move register C value to register B
    (122, 'MOV {{A}} B'),   # MOV {A} B           - move the ROM value that in register A address to register B
    (123, 'MOV {{B}} B'),   # MOV {B} B           - move the ROM value that in register B address to register B
    (124, 'MOV {{C}} B'),   # MOV {C} B           - move the ROM value that in register C address to register B
    (125, 'MOV {{{}}} B'),  # MOV {ROM_ADDRESS} B - move the ROM value that in the given address to register B
    (126, 'MOV [A] B'),     # MOV [A] B           - move the RAM value that in register A address to register B
    (127, 'MOV [B] B'),     # MOV [B] B           - move the RAM value that in register B address to register B
    (128, 'MOV [C] B'),     # MOV [C] B           - move the RAM value that in register C address to register B
    (129, 'MOV [{}] B'),    # MOV [RAM_ADDRESS] B - move the RAM value that in the given address to register B
    (130, 'MOV {} B'),      # MOV VALUE B         - move the given value to register B
    (131, 'MOV B [A]'),     # MOV B [A]           - move register B value to RAM in register A address
    (132, 'MOV B [B]'),     # MOV B [B]           - move register B value to RAM in register B address
    (133, 'MOV B [C]'),     # MOV B [C]           - move register B value to RAM in register C address
    (134, 'MOV B [{}]'),    # MOV B [RAM_ADDRESS] - move register B value to RAM in the given address

    ################################################################################
    # MOV register C instructions (140-159)
    ################################################################################
    (140, 'MOV A C'),       # MOV A C             - move register A value to register C
    (141, 'MOV B C'),       # MOV B C             - move register B value to register C
    (142, 'MOV {{A}} C'),   # MOV {A} C           - move the ROM value that in register A address to register C
    (143, 'MOV {{B}} C'),   # MOV {B} C           - move the ROM value that in register B address to register C
    (144, 'MOV {{C}} C'),   # MOV {C} C           - move the ROM value that in register C address to register C
    (145, 'MOV {{{}}} C'),  # MOV {ROM_ADDRESS} C - move the ROM value that in the given address to register C
    (146, 'MOV [A] C'),     # MOV [A] C           - move the RAM value that in register A address to register C
    (147, 'MOV [B] C'),     # MOV [B] C           - move the RAM value that in register B address to register C
    (148, 'MOV [C] C'),     # MOV [C] C           - move the RAM value that in register C address to register C
    (149, 'MOV [{}] C'),    # MOV [RAM_ADDRESS] C - move the RAM value that in the given address to register C
    (150, 'MOV {} C'),      # MOV VALUE C         - move the given value to register C
    (151, 'MOV C [A]'),     # MOV C [A]           - move register C value to RAM in register A address
    (152, 'MOV C [B]'),     # MOV C [B]           - move register C value to RAM in register B address
    (153, 'MOV C [C]'),     # MOV C [C]           - move register C value to RAM in register C address
    (154, 'MOV C [{}]'),    # MOV C [RAM_ADDRESS] - move register C value to RAM in the given address

    ################################################################################
    # ADD instructions (160-179)
    ################################################################################
    (160, 'ADD A'),       # ADD A             - calculate the sum of register A value with register A value (put the result in register A, override register B, ZF and CF flags are affected)
    (161, 'ADD B'),       # ADD B             - calculate the sum of register A value with register B value (put the result in register A, override register B, ZF and CF flags are affected)
    (162, 'ADD C'),       # ADD C             - calculate the sum of register A value with register C value (put the result in register A, override register B, ZF and CF flags are affected)
    (163, 'ADD {{A}}'),   # ADD {A}           - calculate the sum of register A value with the ROM value that in register A address (put the result in register A, override register B, ZF and CF flags are affected)
    (164, 'ADD {{B}}'),   # ADD {B}           - calculate the sum of register A value with the ROM value that in register B address (put the result in register A, override register B, ZF and CF flags are affected)
    (165, 'ADD {{C}}'),   # ADD {C}           - calculate the sum of register A value with the ROM value that in register C address (put the result in register A, override register B, ZF and CF flags are affected)
    (166, 'ADD {{{}}}'),  # ADD {ROM_ADDRESS} - calculate the sum of register A value with the ROM value that in the given address (put the result in register A, override register B, ZF and CF flags are affected)
    (167, 'ADD [A]'),     # ADD [A]           - calculate the sum of register A value with the RAM value that in register A address (put the result in register A, override register B, ZF and CF flags are affected)
    (168, 'ADD [B]'),     # ADD [B]           - calculate the sum of register A value with the RAM value that in register B address (put the result in register A, override register B, ZF and CF flags are affected)
    (169, 'ADD [C]'),     # ADD [C]           - calculate the sum of register A value with the RAM value that in register C address (put the result in register A, override register B, ZF and CF flags are affected)
    (170, 'ADD [{}]'),    # ADD [RAM_ADDRESS] - calculate the sum of register A value with the RAM value that in the given address (put the result in register A, override register B, ZF and CF flags are affected)
    (171, 'ADD {}'),      # ADD VALUE         - calculate the sum of register A value with the given value (put the result in register A, override register B, ZF and CF flags are affected)

    ################################################################################
    # SUB instructions (180-199)
    ################################################################################
    (180, 'SUB A'),       # SUB A             - calculate the subtraction of register A value with register A value (put the result in register A, override register B, ZF and CF flags are affected)
    (181, 'SUB B'),       # SUB B             - calculate the subtraction of register A value with register B value (put the result in register A, override register B, ZF and CF flags are affected)
    (182, 'SUB C'),       # SUB C             - calculate the subtraction of register A value with register C value (put the result in register A, override register B, ZF and CF flags are affected)
    (183, 'SUB {{A}}'),   # SUB {A}           - calculate the subtraction of register A value with the ROM value that in register A address (put the result in register A, override register B, ZF and CF flags are affected)
    (184, 'SUB {{B}}'),   # SUB {B}           - calculate the subtraction of register A value with the ROM value that in register B address (put the result in register A, override register B, ZF and CF flags are affected)
    (185, 'SUB {{C}}'),   # SUB {C}           - calculate the subtraction of register A value with the ROM value that in register C address (put the result in register A, override register B, ZF and CF flags are affected)
    (186, 'SUB {{{}}}'),  # SUB {ROM_ADDRESS} - calculate the subtraction of register A value with the ROM value that in the given address (put the result in register A, override register B, ZF and CF flags are affected)
    (187, 'SUB [A]'),     # SUB [A]           - calculate the subtraction of register A value with the RAM value that in register A address (put the result in register A, override register B, ZF and CF flags are affected)
    (188, 'SUB [B]'),     # SUB [B]           - calculate the subtraction of register A value with the RAM value that in register B address (put the result in register A, override register B, ZF and CF flags are affected)
    (189, 'SUB [C]'),     # SUB [C]           - calculate the subtraction of register A value with the RAM value that in register C address (put the result in register A, override register B, ZF and CF flags are affected)
    (190, 'SUB [{}]'),    # SUB [RAM_ADDRESS] - calculate the subtraction of register A value with the RAM value that in the given address (put the result in register A, override register B, ZF and CF flags are affected)
    (191, 'SUB {}'),      # SUB VALUE         - calculate the subtraction of register A value with the given value (put the result in register A, override register B, ZF and CF flags are affected)

    ################################################################################
    # CMP instructions (200-219)
    ################################################################################
    (200, 'CMP A'),       # CMP A             - compare (subtract) register A value with register A value (doesn't save the result, override register B, ZF and CF flags are affected)
    (201, 'CMP B'),       # CMP B             - compare (subtract) register A value with register B value (doesn't save the result, override register B, ZF and CF flags are affected)
    (202, 'CMP C'),       # CMP C             - compare (subtract) register A value with register C value (doesn't save the result, override register B, ZF and CF flags are affected)
    (203, 'CMP {{A}}'),   # CMP {A}           - compare (subtract) register A value with the ROM value that in register A address (doesn't save the result, override register B, ZF and CF flags are affected)
    (204, 'CMP {{B}}'),   # CMP {B}           - compare (subtract) register A value with the ROM value that in register B address (doesn't save the result, override register B, ZF and CF flags are affected)
    (205, 'CMP {{C}}'),   # CMP {C}           - compare (subtract) register A value with the ROM value that in register C address (doesn't save the result, override register B, ZF and CF flags are affected)
    (206, 'CMP {{{}}}'),  # CMP {ROM_ADDRESS} - compare (subtract) register A value with the ROM value that in the given address (doesn't save the result, override register B, ZF and CF flags are affected)
    (207, 'CMP [A]'),     # CMP [A]           - compare (subtract) register A value with the RAM value that in register A address (doesn't save the result, override register B, ZF and CF flags are affected)
    (208, 'CMP [B]'),     # CMP [B]           - compare (subtract) register A value with the RAM value that in register B address (doesn't save the result, override register B, ZF and CF flags are affected)
    (209, 'CMP [C]'),     # CMP [C]           - compare (subtract) register A value with the RAM value that in register C address (doesn't save the result, override register B, ZF and CF flags are affected)
    (210, 'CMP [{}]'),    # CMP [RAM_ADDRESS] - compare (subtract) register A value with the RAM value that in the given address (doesn't save the result, override register B, ZF and CF flags are affected)
    (211, 'CMP {}'),      # CMP VALUE         - compare (subtract) register A value with the given value (doesn't save the result, override register B, ZF and CF flags are affected)

    ################################################################################
    # JMP to register A Value instructions (220-229)
    ################################################################################
    (220, 'JMP A'),  # JMP A - jump to the address that in register A
    (221, 'JB A'),   # JB A  - jump to the address that in register A if CMP < 0 (CF==1)
    (222, 'JBE A'),  # JBE A - jump to the address that in register A if CMP <= 0 (ZF==1 or CF==1)
    (223, 'JE A'),   # JE A  - jump to the address that in register A if CMP == 0 (ZF==1)
    (224, 'JNE A'),  # JNE A - jump to the address that in register A if CMP != 0 (ZF==0)
    (225, 'JAE A'),  # JAE A - jump to the address that in register A if CMP >= 0 (CF==0)
    (226, 'JA A'),   # JA A  - jump to the address that in register A if CMP > 0 (ZF==0 and CF==0)

    ################################################################################
    # JMP to given VALUE instructions (230-239)
    ################################################################################
    (230, 'JMP {}'),  # JMP VALUE - jump to the given address
    (231, 'JB {}'),   # JB VALUE  - jump to the given address if CMP < 0 (CF==1)
    (232, 'JBE {}'),  # JBE VALUE - jump to the given address if CMP <= 0 (ZF==1 or CF==1)
    (233, 'JE {}'),   # JE VALUE  - jump to the given address if CMP == 0 (ZF==1)
    (234, 'JNE {}'),  # JNE VALUE - jump to the given address if CMP != 0 (ZF==0)
    (235, 'JAE {}'),  # JAE VALUE - jump to the given address if CMP >= 0 (CF==0)
    (236, 'JA {}'),   # JA VALUE  - jump to the given address if CMP > 0 (ZF==0 and CF==0)
]


class Assembler():

    def __init__(self, lines: List[str]):
        self._consts: Dict[str, bytearray] = {}
        self._vars: Dict[str, int] = {}
        self._defineds: Dict[str, int] = {}
        self._lables: Dict[str, int] = {}
        self._program: bytearray = bytearray()
        self._fetchingMap: Dict[str, List[int]] = {}

        # Add 2 NOPs to the start of each program
        self._program.append(1)
        self._program.append(1)

        self._parseLines(lines)
        self._fetchParams()

        assert len(self._program) < ROM_SIZE

    def dump(self) -> bytes:
        return pack('{}s'.format(ROM_SIZE), self._program)

    def _parseLines(self, lines: List[str]) -> None:
        for (lineNum, line) in enumerate(lines, 1):
            line = self._cleanLine(line)
            if len(line) == 0:
                continue

            if self._parseConst(line) or \
                    self._parseVar(line) or \
                    self._parseDefined(line) or \
                    self._parseLable(line) or \
                    self._parseCommand(line):
                print(f'Successfully parsed line {lineNum:04}: {line}')
                continue

            raise Exception(f'Invalid line {lineNum:04}: "{line}"')

    @staticmethod
    def _cleanLine(line: str) -> str:
        # remove comments
        line = line.partition('#')[0]
        line = line.partition('//')[0]

        # remove whitespaces
        line = line.strip()

        return line

    def _parseConst(self, line: str) -> bool:
        match = parse('${} {{{}}}', line)
        if match:
            (key, constValues) = match.fixed
            constValues = constValues.replace(', ', ' ').replace(',', ' ')
            constValues = (self._parseValue(v) for v in constValues.split(' '))
            constValues = bytearray(constValues)
            self._consts[key] = constValues
            return True
        return False

    def _parseVar(self, line: str) -> bool:
        match = parse('${} [{:d}]', line)
        if match:
            (key, varSize) = match.fixed
            self._vars[key] = varSize
            return True
        return False

    def _parseDefined(self, line: str) -> bool:
        match = parse('${} {}', line)
        if match:
            (key, definedValue) = match.fixed
            definedValue = self._parseValue(definedValue)
            self._defineds[key] = definedValue
            return True
        return False

    def _parseLable(self, line: str) -> bool:
        match = parse('${}:', line)
        if match:
            key = match.fixed[0]
            lableAddress = len(self._program)
            self._lables[key] = lableAddress
            return True
        return False

    def _parseCommand(self, line: str) -> bool:
        for (commandNum, commandFormat) in COMMANDS:
            match = parse(commandFormat, line)
            if match:
                self._program.append(commandNum)
                for value in match.fixed:
                    value = self._parseValue(value, includeParams=True)
                    self._program.append(value)
                return True
        return False

    def _parseValue(self, value: str, includeParams: bool = False) -> int:
        if includeParams:
            match = parse('${}', value)
            if match:
                key = match.fixed[0]
                self._fetchingMap.setdefault(key, [])
                self._fetchingMap[key].append(len(self._program))
                return 0

        match = parse('0x{:x}', value)
        if match:
            value = match.fixed[0]
            assert 0 <= value < WORD_SIZE
            return value

        match = parse('{:d}', value)
        if match:
            value = match.fixed[0]
            assert 0 <= value < WORD_SIZE
            return value

        raise Exception(f'Invalid value: "{value}"')

    def _fetchParams(self) -> None:
        self._fetchConsts()
        self._fetchVars()
        self._fetchDefineds()
        self._fetchLables()

        assert len(self._fetchingMap) == 0

    def _fetchConsts(self) -> None:
        for (key, constValues) in self._consts.items():
            for fetchingAddress in self._fetchingMap.pop(key, []):
                self._program[fetchingAddress] = len(self._program)

            self._program.extend(constValues)

    def _fetchVars(self) -> None:
        varsCounter = 0
        for (key, varSize) in self._vars.items():
            for fetchingAddress in self._fetchingMap.pop(key, []):
                self._program[fetchingAddress] = varsCounter

            varsCounter += varSize
            assert varsCounter < RAM_SIZE

    def _fetchDefineds(self) -> None:
        for (key, definedValue) in self._defineds.items():
            for fetchingAddress in self._fetchingMap.pop(key, []):
                self._program[fetchingAddress] = definedValue

    def _fetchLables(self) -> None:
        for (key, lableAddress) in self._lables.items():
            for fetchingAddress in self._fetchingMap.pop(key, []):
                self._program[fetchingAddress] = lableAddress


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('inputPath', metavar='inputPath', type=str, help='The input path')
    parser.add_argument('outputPath', metavar='outputPath', type=str, help='The output path')
    args = parser.parse_args()

    # get the input content
    lines = []
    with open(args.inputPath, 'rt') as f:
        lines = f.readlines()
    lines = [str(line) for line in lines]

    # compile
    program = Assembler(lines)

    # save the output
    with open(args.outputPath, 'wb') as f:
        f.write(program.dump())


if __name__ == '__main__':
    main()
