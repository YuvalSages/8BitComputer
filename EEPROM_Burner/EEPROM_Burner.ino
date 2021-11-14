// imports
#include "Arduino binaries/microCode_2.h"

// pins
#define PIN_ADDRESS_DATA          (2)
#define PIN_ADDRESS_WRITE_CLOCK   (3)
#define PIN_ADDRESS_SHIFT_CLOCK   (4)
#define PIN_EEPROM_WRITE_ENABLE   (5)
#define PIN_EEPROM_OUTPUT_ENABLE  (6)
#define PIN_DATA_1                (A0)
#define PIN_DATA_2                (A1)
#define PIN_DATA_3                (A2)
#define PIN_DATA_4                (A3)
#define PIN_DATA_5                (A4)
#define PIN_DATA_6                (A5)
#define PIN_DATA_7                (7)
#define PIN_DATA_8                (8)

// consts
const bool readMode = true;
const bool writeMode = true;
const int addressSpaceSize = 2048;
const int addressWriteSignalDuration = 1; // in microseconds
const int delayBeforeReading = 10;
const int delayBeforeWriting = 10;
const int writingSignalDuration = 1; // in microseconds
const int delayAfterWriting = 10;





void setup() {
  // put your setup code here, to run once:

  pinMode(PIN_ADDRESS_DATA, OUTPUT);
  pinMode(PIN_ADDRESS_WRITE_CLOCK, OUTPUT);
  pinMode(PIN_ADDRESS_SHIFT_CLOCK, OUTPUT);
  pinMode(PIN_EEPROM_WRITE_ENABLE, OUTPUT);
  pinMode(PIN_EEPROM_OUTPUT_ENABLE, OUTPUT);

  Serial.begin(9600);
  while (!Serial);

  delay(2000);

  if (readMode) {
    ReadEEPROM();
  }

  if (writeMode) {
    WriteEEPROM();
    ReadEEPROM();
  }
}

void loop() {
  // put your main code here, to run repeatedly:

}





void SetAddress(uint16_t address) {
  digitalWrite(PIN_ADDRESS_SHIFT_CLOCK, LOW);
  digitalWrite(PIN_ADDRESS_WRITE_CLOCK, LOW);

  shiftOut(PIN_ADDRESS_DATA, PIN_ADDRESS_SHIFT_CLOCK, LSBFIRST, (uint8_t) address);
  shiftOut(PIN_ADDRESS_DATA, PIN_ADDRESS_SHIFT_CLOCK, LSBFIRST, (uint8_t) (address >> 8));

  digitalWrite(PIN_ADDRESS_SHIFT_CLOCK, LOW);
  digitalWrite(PIN_ADDRESS_WRITE_CLOCK, HIGH);
  delayMicroseconds(addressWriteSignalDuration);
  digitalWrite(PIN_ADDRESS_WRITE_CLOCK, LOW);
}



uint8_t ReadEEPROMByte() {
  pinMode(PIN_DATA_1, INPUT);
  pinMode(PIN_DATA_2, INPUT);
  pinMode(PIN_DATA_3, INPUT);
  pinMode(PIN_DATA_4, INPUT);
  pinMode(PIN_DATA_5, INPUT);
  pinMode(PIN_DATA_6, INPUT);
  pinMode(PIN_DATA_7, INPUT);
  pinMode(PIN_DATA_8, INPUT);
  digitalWrite(PIN_EEPROM_WRITE_ENABLE, HIGH);
  digitalWrite(PIN_EEPROM_OUTPUT_ENABLE, LOW);

  delay(delayBeforeReading);

  uint8_t result = 0;
  result = (result | (((uint8_t) (digitalRead(PIN_DATA_1) == LOW ? 0 : 1)) << 0));
  result = (result | (((uint8_t) (digitalRead(PIN_DATA_2) == LOW ? 0 : 1)) << 1));
  result = (result | (((uint8_t) (digitalRead(PIN_DATA_3) == LOW ? 0 : 1)) << 2));
  result = (result | (((uint8_t) (digitalRead(PIN_DATA_4) == LOW ? 0 : 1)) << 3));
  result = (result | (((uint8_t) (digitalRead(PIN_DATA_5) == LOW ? 0 : 1)) << 4));
  result = (result | (((uint8_t) (digitalRead(PIN_DATA_6) == LOW ? 0 : 1)) << 5));
  result = (result | (((uint8_t) (digitalRead(PIN_DATA_7) == LOW ? 0 : 1)) << 6));
  result = (result | (((uint8_t) (digitalRead(PIN_DATA_8) == LOW ? 0 : 1)) << 7));

  return result;
}



void ReadEEPROMSection(uint8_t* dataBuffer, uint16_t fromAddress, uint16_t bufferSize) {
  for (uint16_t i = 0; i < bufferSize; ++i) {
    SetAddress(fromAddress + i);
    dataBuffer[i] = ReadEEPROMByte();
  }
}



void ReadEEPROM() {
  uint8_t dataBuffer[16];
  char stringBuffer[60];

  Serial.println("");
  Serial.println("");
  Serial.println("READING...");
  Serial.println("");
  Serial.println("         0  1  2  3  4  5  6  7     8  9  A  B  C  D  E  F ");
  Serial.println("");

  for (uint16_t i = 0; i < addressSpaceSize; i += 16) {
    ReadEEPROMSection(dataBuffer, i, 16);
    sprintf(stringBuffer, "%04x:    %02x %02x %02x %02x %02x %02x %02x %02x    %02x %02x %02x %02x %02x %02x %02x %02x", i,
            dataBuffer[0], dataBuffer[1], dataBuffer[2], dataBuffer[3], dataBuffer[4], dataBuffer[5], dataBuffer[6], dataBuffer[7],
            dataBuffer[8], dataBuffer[9], dataBuffer[10], dataBuffer[11], dataBuffer[12], dataBuffer[13], dataBuffer[14], dataBuffer[15]);
    Serial.println(stringBuffer);
  }

  Serial.println("");
  Serial.println("");
}



void WriteEEPROMByte(uint8_t data) {
  digitalWrite(PIN_EEPROM_WRITE_ENABLE, HIGH);
  digitalWrite(PIN_EEPROM_OUTPUT_ENABLE, HIGH);
  pinMode(PIN_DATA_1, OUTPUT);
  pinMode(PIN_DATA_2, OUTPUT);
  pinMode(PIN_DATA_3, OUTPUT);
  pinMode(PIN_DATA_4, OUTPUT);
  pinMode(PIN_DATA_5, OUTPUT);
  pinMode(PIN_DATA_6, OUTPUT);
  pinMode(PIN_DATA_7, OUTPUT);
  pinMode(PIN_DATA_8, OUTPUT);

  digitalWrite(PIN_DATA_1, ((data >> 0) & 1) == 0 ? LOW : HIGH);
  digitalWrite(PIN_DATA_2, ((data >> 1) & 1) == 0 ? LOW : HIGH);
  digitalWrite(PIN_DATA_3, ((data >> 2) & 1) == 0 ? LOW : HIGH);
  digitalWrite(PIN_DATA_4, ((data >> 3) & 1) == 0 ? LOW : HIGH);
  digitalWrite(PIN_DATA_5, ((data >> 4) & 1) == 0 ? LOW : HIGH);
  digitalWrite(PIN_DATA_6, ((data >> 5) & 1) == 0 ? LOW : HIGH);
  digitalWrite(PIN_DATA_7, ((data >> 6) & 1) == 0 ? LOW : HIGH);
  digitalWrite(PIN_DATA_8, ((data >> 7) & 1) == 0 ? LOW : HIGH);

  delay(delayBeforeWriting);

  digitalWrite(PIN_EEPROM_WRITE_ENABLE, LOW);
  delayMicroseconds(writingSignalDuration);
  digitalWrite(PIN_EEPROM_WRITE_ENABLE, HIGH);

  delay(delayAfterWriting);
}



void WriteEEPROMSection(const uint8_t* dataBuffer, uint16_t fromAddress, uint16_t bufferSize) {
  for (uint16_t i = 0; i < bufferSize; ++i) {
    SetAddress(fromAddress + i);
    WriteEEPROMByte(dataBuffer[i]);
  }
}



void WriteEEPROM() {
  uint8_t dataBuffer[16];
  char stringBuffer[60];

  Serial.println("");
  Serial.println("");
  Serial.println("WRITING...");
  Serial.println("");
  Serial.println("         0  1  2  3  4  5  6  7     8  9  A  B  C  D  E  F ");
  Serial.println("");

  for (uint16_t i = 0; i < addressSpaceSize; i += 16) {
    for (uint8_t j = 0; j < 16; ++j) {
      dataBuffer[j] = pgm_read_byte_near(binaryToWrite + i + j);
    }
    
    WriteEEPROMSection(dataBuffer, i, 16);
    sprintf(stringBuffer, "%04x:    %02x %02x %02x %02x %02x %02x %02x %02x    %02x %02x %02x %02x %02x %02x %02x %02x", i,
            dataBuffer[0], dataBuffer[1], dataBuffer[2], dataBuffer[3], dataBuffer[4], dataBuffer[5], dataBuffer[6], dataBuffer[7],
            dataBuffer[8], dataBuffer[9], dataBuffer[10], dataBuffer[11], dataBuffer[12], dataBuffer[13], dataBuffer[14], dataBuffer[15]);
    Serial.println(stringBuffer);
  }

  Serial.println("");
  Serial.println("");
}
