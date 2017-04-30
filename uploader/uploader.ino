#define WRITE_PIN 12
#define SHIFT_DATA_PIN 2
#define LATCH_PIN 3
#define SHIFT_CLOCK_PIN 4
#define ADDRESS_PIN_START 8
#define ADDRESS_PIN_END 11

#define foreach_address for (int pin = ADDRESS_PIN_START; pin <= ADDRESS_PIN_END; pin++)



#define foreach_pin \
    for (int pin = SHIFT_DATA_PIN; pin <= WRITE_PIN; (pin != 4) ? pin++ : pin = ADDRESS_PIN_START)


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

void setup() {
  Serial.begin(9600);
  setPinsAsInput();
  
  
}

void loop() {
  while (Serial.available() == 0) {}
  Serial.read();
  Serial.println("RECIVED");
  for (int i = 0; i < 16; i++) {
    writeData(i, i);
  }
  Serial.println("DONE");
}
