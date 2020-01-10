import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('inputPath', metavar='inputPath', type=str, help='The input path')
    parser.add_argument('outputPath', metavar='outputPath', type=str, help='The output path')
    args = parser.parse_args()

    with open(args.inputPath, 'rb') as inputFile:
        inputBuffer = inputFile.read(2048)
    inputBuffer += (((16 - (len(inputBuffer) % 16)) % 16) * '\x00')
    inputBufferLen = len(inputBuffer)

    outputBuffer = 'const uint8_t binaryToWrite[] PROGMEM = {\n'

    for i in range(0, 2048, 16):
        if i < inputBufferLen:
            outputBuffer += '    0x{:02x}, 0x{:02x}, 0x{:02x}, 0x{:02x}, 0x{:02x}, 0x{:02x}, 0x{:02x}, 0x{:02x}, 0x{:02x}, 0x{:02x}, 0x{:02x}, 0x{:02x}, 0x{:02x}, 0x{:02x}, 0x{:02x}, 0x{:02x},\n'.format(ord(inputBuffer[i + 0]), ord(inputBuffer[i + 1]), ord(inputBuffer[i + 2]), ord(inputBuffer[i + 3]), ord(inputBuffer[i + 4]), ord(inputBuffer[i + 5]), ord(inputBuffer[i + 6]), ord(inputBuffer[i + 7]), ord(inputBuffer[i + 8]), ord(inputBuffer[i + 9]), ord(inputBuffer[i + 10]), ord(inputBuffer[i + 11]), ord(inputBuffer[i + 12]), ord(inputBuffer[i + 13]), ord(inputBuffer[i + 14]), ord(inputBuffer[i + 15]))
        else:
            outputBuffer += '    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,\n'

    outputBuffer += '    };'

    with open(args.outputPath, 'wt') as outputFile:
        outputFile.write(outputBuffer)

    print('Done!')


if __name__ == '__main__':
    main()
