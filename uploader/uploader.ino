#define WRITE_PIN 12
#define SHIFT_DATA_PIN 2
#define LATCH_PIN 3
#define SHIFT_CLOCK_PIN 4
#define ADDRESS_PIN_START 8
#define ADDRESS_PIN_END 11

#define foreach_address for (int pin = ADDRESS_PIN_START; pin <= ADDRESS_PIN_END; pin++)

#define foreach_pin \
    for (int pin = SHIFT_DATA_PIN; pin <= WRITE_PIN; (pin != 4) ? pin++ : pin = ADDRESS_PIN_START)

#define ARRAY_LEN(x) (sizeof(x) / sizeof((x)[0]))

#define SUCCESS 0
#define FAIL 1

boolean textMode = false;

int setAddress(signed char address) {
  if (address < 0 && address >= 16)
    return -1;
  foreach_address {
    digitalWrite(pin, (address >> (pin - ADDRESS_PIN_START)) & 1);
  }
  return 0;
}

int setData(byte data) {
  digitalWrite(LATCH_PIN, LOW);
  shiftOut(SHIFT_DATA_PIN, SHIFT_CLOCK_PIN, MSBFIRST, data);
  digitalWrite(LATCH_PIN, HIGH);
}

int writeData(signed char address, byte data) {
  setPinsAsOutput();
  digitalWrite(WRITE_PIN, HIGH);
  if (setAddress(address) == -1)
    return -1;
  if (setData(data) != 0)
    return -1;
  delay(5);
  digitalWrite(WRITE_PIN, LOW);
  delay(5);
  digitalWrite(WRITE_PIN, HIGH);
  delay(5);
  setPinsAsInput();
  return 0;
}

void setPinsAsOutput() {
  digitalWrite(WRITE_PIN, HIGH);
  foreach_pin {
    pinMode(pin, OUTPUT);
  }
  digitalWrite(WRITE_PIN, HIGH);
  foreach_address {
    digitalWrite(pin, LOW);
  }
  
  digitalWrite(LATCH_PIN, LOW);
}

void setPinsAsInput() {
  digitalWrite(WRITE_PIN, HIGH); 
  foreach_pin {
    pinMode(pin, INPUT);
  }
  digitalWrite(WRITE_PIN, HIGH);
}

int binaryToInt(String string) {
  if (string.startsWith("0b")) {
    int res = 0;
    for (int pos = 2; pos < string.length(); pos++) {
      if (string.charAt(pos) == '1' || string.charAt(pos) == '0') {
        res |= (string.charAt(pos) == '1') ? 1 << (string.length() - pos - 1) : 0;
      } else {
        return -1;
      }
    }
    return res;
  } else {
    return -1;
  }
}

int hexToInt(String string) {
  if (string.startsWith("0x")) {
    int multiplier = 1;
    int res = 0;
    string.toLowerCase();
    for (int pos = string.length() - 1; pos > 1; pos--) {
      int charVal = testHex(string.charAt(pos));
      if (charVal == -1){
        return -1;
      }
      res += charVal * multiplier;
      multiplier *= 16;
    }
    return res;
  }
  return -1;
}

int testHex(char hexChar) {
  for (int toTest = 0; toTest < 16; toTest++) {
    if (hexChar == String(toTest, HEX).charAt(0)) {
      return toTest;
    }
  }
  return -1;
}

int stringToInt(String string) {
  int binVal = binaryToInt(string);
  if (binVal != -1) {
    return binVal;
  }

  int hexVal = hexToInt(string);
  if (hexVal != -1) {
    return hexVal;
  }

  return -1;
}

int parseTextCommand(String command) {
  command.trim();
  if (command.startsWith("SET")) {
    return setCommand(command);
  } else if (command.compareTo("BIN") == 0) {
    textMode = false;
    return 0;
  } else if (command.compareTo("TXT") == 0) {
    textMode = true;
    return 0;
  }
  else {
    Serial.print("INVALID COMMAND. ");
    Serial.println("NO COMMAND NAMED: \"" + command.substring(0, (command.indexOf(" ") != -1) ? command.indexOf(" ") : command.length()) + "\"\r");
    return -1;
  }
}


int count(String string, char value) {
  int found = 0;
  for (int index = 0; index < string.length(); index++) {
    if (string.charAt(index) == value) found++;
  }
  return found;
}

int setCommand(String command) {
  if (count(command, ' ') != 2) {
    Serial.println("INVALID FORMAT FOR \"SET\" COMMAND\r");
    return -1;
  }
  String com = command.substring(0, command.indexOf(" "));
  command.remove(0, command.indexOf(" ") + 1);
  int address = stringToInt(command.substring(0, command.indexOf(" ")));
  command.remove(0, command.indexOf(" ") + 1);
  int value = stringToInt(command);
  if (address == -1 || value == -1) {
    Serial.println("INVALID NUMBER FORMAT\r");
    return -1;
  }
  if (writeData(address, value) != -1) {
    Serial.print("SUCCESS! ADDRESS: 0b");
    Serial.print(String(address, BIN));
    Serial.print(" VALUE: 0b");
    Serial.print(String(value, BIN));
    Serial.println("\r");
    return 0;
  } else {
    Serial.println("FAILED TO WRITE DATA\r");
    return -1;
  }
}

int setBinaryCommand(char command[3]) {
  if (writeData(command[1], command[2]) == 0) {
    Serial.write(SUCCESS);
    return 0;
  } else {
    Serial.write(FAIL);
    return -1;
  }
}

void parseBinaryCommand(char command[3]) {
  char textCommand[4];
  copyArray(command, textCommand, 3),
  textCommand[3] = '\0';
  if (strcmp(textCommand, "TXT") == 0) {
    textMode = true;
    Serial.println("Switched to TXT-mode\r");
  } else if (strcmp(textCommand, "BIN") == 0) {
    textMode = false;
    Serial.write(SUCCESS);
  } else if (command[0] == 1) {
    setBinaryCommand(command);
  } else {
    Serial.write(FAIL);
  }
}


void copyArray(char copyFrom[], char copyTo[], int numToCopy) {
  for (int i = 0; i < numToCopy; i++) {
    copyTo[i] = copyFrom[i];
  }
}

void setup() {
  Serial.begin(9600);
  setPinsAsInput();
  Serial.write(SUCCESS);
  //Serial.println("DONE");
}

void loop() {
  if (Serial.available() > 0) {
    
    if (textMode) {
      String recived = Serial.readString();
      Serial.print(parseTextCommand(recived));
      Serial.println("\r");
    } else {
      char buff[3];
      Serial.readBytes(buff, 3);
      parseBinaryCommand(buff);
    }
  }
  /*for (int i = 0; i < 16; i++) {
    writeData(i, i);
  }
  Serial.println("DONE");
  */
  
}
