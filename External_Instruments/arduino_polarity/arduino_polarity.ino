void setup() {
  // Initialize the serial communication at 9600 baud rate
  Serial.begin(9600);

  // Initialize the pins as OUTPUT
  pinMode(12, OUTPUT);
  pinMode(11, OUTPUT);
  pinMode(10, OUTPUT);
}

void loop() {
  if (Serial.available() >= 3) { // Check if at least 3 characters are available to read
    char pin12 = Serial.read(); // Read the incoming byte for pin 13
    char pin11 = Serial.read(); // Read the incoming byte for pin 12
    char pin10 = Serial.read(); // Read the incoming byte for pin 11

    // Set pin 12
    if (pin12 == '1') {
      digitalWrite(12, HIGH);
    } else {
      digitalWrite(12, LOW);
    }

    // Set pin 11
    if (pin11 == '1') {
      digitalWrite(11, HIGH);
    } else {
      digitalWrite(11, LOW);
    }

    // Set pin 10
    if (pin10 == '1') {
      digitalWrite(10, HIGH);
    } else {
      digitalWrite(11, LOW);
    }
  }
}
