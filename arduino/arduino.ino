#include <ESP8266WiFi.h>
#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN 10
#define RST_PIN 9

// Set up RFID reader
MFRC522 mfrc522(SS_PIN, RST_PIN);

//TODO: Replace with actual SSID and Password
const char* ssid = "SSID";
const char* pass = "Password";

WifiClient client;
const char* host = "1.1.1.1";    // Replace with PC's IP
const uint16_t port = 12345;     // Replace with actual port

void setup() {
  Serial.begin(9600);
  WiFi.begin(ssid, pass);
  SPI.begin();
  mfrc522.PCD_init();

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi!");
}

void loop() {
  // Look for new cards
  if (!mfrc522.PICC_IsNewCardPresent()) { return; }    // No card, so return, and don't send data

  // Select one of the cards
  if (!mfrc522.PICC_ReadCardSerial()) { return; }

  // Show UID on serial monitor
  Serial.print("UID tag: ");
  String content = "";
  byte letter;
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    Serial.print(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " ");
    Serial.print(mfrc522.uid.uidByte[i], HEX);
    content.concat(String(mfrc522.uid.uidByte[i] > 0x10 ? " 0" : " "));
    content.concat(String(mfrc522.uid.uidByte[i], HEX));
  }
  Serial.println();

  // Show whether RFID card was accepted
  content.toUpperCase();
  if (content.substring(1) == "  BD 31 15 2B") {  //TODO: Replace with EEPROM list of authorised cards
    Serial.println("Access granted");
    Serial.println();
  } else {
    Serial.println("Access denied");
    Serial.println();
  
  if (client.connect(host, port)) {
    client.println("Hello!");    //TODO: Replace with data to send
  }
  delay(2000);    // Send data every 2 seconds
}
