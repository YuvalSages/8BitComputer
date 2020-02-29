import argparse


DIGIT_ENCODING = {
    '0': 0b00111111,
    '1': 0b00000110,
    '2': 0b01011011,
    '3': 0b01001111,
    '4': 0b01100110,
    '5': 0b01101101,
    '6': 0b01111101,
    '7': 0b00000111,
    '8': 0b01111111,
    '9': 0b01101111,
    'A': 0b01110111,
    'B': 0b01111100,
    'C': 0b00111001,
    'D': 0b01011110,
    'E': 0b01111001,
    'F': 0b01110001,
    '-': 0b01000000,
    '': 0b00000000,
    'b0': 0b00010100,
    'b1': 0b00010110,
    'b2': 0b00110100,
    'b3': 0b00110110,
}

common = ''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('outputPath', metavar='outputPath', type=str, help='The output path')
    parser.add_argument('common', metavar='common', type=str, choices=('anode', 'catode'), help='The display common')
    parser.add_argument('displays', metavar='displays', type=str, nargs=2, choices=('positive', 'negative', 'hexa', 'binary'), help='The display types')
    args = parser.parse_args()
    global common
    common = args.common

    displaysFunctions = {
        'positive': getDecimalNaturalDisplay(),
        'negative': getDecimalIntegerDisplay(),
        'hexa': getHexadecimalNaturalDisplay(),
        'binary': getBinaryNaturalDisplay(),
    }

    outputBuffer = displaysFunctions[args.displays[0]] + displaysFunctions[args.displays[1]]

    with open(args.outputPath, 'wb') as outputFile:
        outputFile.write(outputBuffer)

    print('Done!')


def getDigitEncoding(digit):
    global common
    value = DIGIT_ENCODING[digit]
    if common == 'anode':
        value = ~ value + 2**8
    return value


def getDecimalNaturalDisplay():
    buffer = bytearray()

    # digit 1
    for i in range(256):
        buffer.append(getDigitEncoding(str(i % 10)))

    # digit 2
    for i in range(256):
        buffer.append(getDigitEncoding(str(int(i / 10) % 10)))

    # digit 2
    for i in range(256):
        buffer.append(getDigitEncoding(str(int(i / 100) % 10)))

    # digit 2
    for i in range(256):
        buffer.append(getDigitEncoding(''))

    return buffer


def getDecimalIntegerDisplay():
    buffer = bytearray()

    # digit 1
    for i in range(128):
        buffer.append(getDigitEncoding(str(i % 10)))
    for i in range(-128, 0):
        buffer.append(getDigitEncoding(str(i % 10)))

    # digit 2
    for i in range(128):
        buffer.append(getDigitEncoding(str(int(i / 10) % 10)))
    for i in range(-128, 0):
        buffer.append(getDigitEncoding(str(int(i / 10) % 10)))

    # digit 2
    for i in range(128):
        buffer.append(getDigitEncoding(str(int(i / 100) % 10)))
    for i in range(-128, 0):
        buffer.append(getDigitEncoding(str(int(i / 100) % 10)))

    # digit 2
    for i in range(128):
        buffer.append(getDigitEncoding(''))
    for i in range(128):
        buffer.append(getDigitEncoding('-'))

    return buffer


def getHexadecimalNaturalDisplay():
    buffer = bytearray()

    # digit 1
    for i in range(256):
        buffer.append(getDigitEncoding('{:02X}'.format(i)[1]))

    # digit 2
    for i in range(256):
        buffer.append(getDigitEncoding('{:02X}'.format(i)[0]))

    # digit 2
    for i in range(256):
        buffer.append(getDigitEncoding(''))

    # digit 2
    for i in range(256):
        buffer.append(getDigitEncoding(''))

    return buffer


def getBinaryNaturalDisplay():
    buffer = bytearray()

    # digit 1
    for i in range(256):
        a = bool(int('{:08b}'.format(i)[7]))
        b = bool(int('{:08b}'.format(i)[6]))
        buffer.append(getDigitEncoding('b0' if not a and not b else 'b1' if a and not b else 'b2' if not a and b else 'b3' if a and b else ''))

    # digit 2
    for i in range(256):
        a = bool(int('{:08b}'.format(i)[5]))
        b = bool(int('{:08b}'.format(i)[4]))
        buffer.append(getDigitEncoding('b0' if not a and not b else 'b1' if a and not b else 'b2' if not a and b else 'b3' if a and b else ''))

    # digit 2
    for i in range(256):
        a = bool(int('{:08b}'.format(i)[3]))
        b = bool(int('{:08b}'.format(i)[2]))
        buffer.append(getDigitEncoding('b0' if not a and not b else 'b1' if a and not b else 'b2' if not a and b else 'b3' if a and b else ''))

    # digit 2
    for i in range(256):
        a = bool(int('{:08b}'.format(i)[1]))
        b = bool(int('{:08b}'.format(i)[0]))
        buffer.append(getDigitEncoding('b0' if not a and not b else 'b1' if a and not b else 'b2' if not a and b else 'b3' if a and b else ''))

    return buffer


if __name__ == '__main__':
    main()
