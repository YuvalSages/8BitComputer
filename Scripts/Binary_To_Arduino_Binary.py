
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('inputPath', metavar='inputPath', type=str, help='The input path')
    parser.add_argument('outputPath', metavar='outputPath', type=str, help='The output path')
    args = parser.parse_args()

    with open(args.inputPath, 'rb') as inputFile:
        inputBuffer = inputFile.read()
    assert len(inputBuffer) <= 2**11, Exception(f'Program length {len(inputBuffer)} exceeds the limit of {2**11}')

    inputBuffer = bytearray(inputBuffer)
    inputBuffer.extend(bytearray(2**11 - len(inputBuffer)))

    outputBuffer = bytearray(b'const uint8_t binaryToWrite[] PROGMEM = { ')

    for (i, value) in enumerate(inputBuffer):
        if i % 16 == 0:
            outputBuffer.pop()
            outputBuffer.extend(b'\n    ')

        outputBuffer.extend('0x{:02x}, '.format(value).encode())

    outputBuffer.pop()
    outputBuffer.extend(b'\n    };')

    with open(args.outputPath, 'wt') as outputFile:
        outputFile.write(outputBuffer.decode())

    print('Done!')


if __name__ == '__main__':
    main()
