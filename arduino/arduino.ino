#include <Arduino.h>
#include <EEPROM.h>
#include <ESP8266WiFi.h>
#include <MFRC522.h>
#include <SPI.h>

#define SS_PIN 10
#define RST_PIN 9

#define GREEN_LED 7
#define RED_LED 6

#define MAX_UID_LEN 10                           // Maximum supported UID length for RFID keys
#define SLOT_SIZE (1 + MAX_UID_LEN + 1)          // [len][uid (padded to MAX_UID_LEN)][checksum]
#define MAX_SLOTS (EEPROM.length() / SLOT_SIZE)

// Set up RFID reader
MFRC522 mfrc522(SS_PIN, RST_PIN);

//TODO: Replace with actual SSID and Password
const char* ssid = "SSID";
const char* pass = "Password";

WifiClient client;
const char* host = "1.1.1.1";       // Replace with PC's IP
const uint16_t port = 12345;        // Replace with actual port

void setup() {
  Serial.begin(9600);
  while (!Serial) { ; }             // Wait for Serial to connect
  
  WiFi.begin(ssid, pass);
  SPI.begin();
  mfrc522.PCD_init();

  pinMode(LED_BUILTIN, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);
  pinMode(RED_LED, OUTPUT);

  Serial.println("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) { ; }    // Loop to stop progression until WiFi is connected
  Serial.println("Connected to WiFi!");
}

void loop() {
  // Turn LEDs off
  digitalWrite(GREEN_LED, LOW);
  digitalWrite(RED_LED, LOW);

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
  if (content.substring(1) == "BD 31 15 2B") {  //TODO: Replace with EEPROM list of authorised cards
    Serial.println("Access granted");
    Serial.println();
    digitalWrite(GREEN_LED, HIGH);
  } else {
    Serial.println("Access denied");
    Serial.println();
    digitalWrite(RED_LED, HIGH);
  
  if (client.connect(host, port)) {
    client.println("Hello!");    //TODO: Replace with data to send
  }
  delay(2000);    // Send data every 2 seconds
}

// Helper function to compute 1-byte checksum (XOR of length + UID bytes)
uint8_t computeChecksum(const uint8_t* data, uint8_t len) {
  uint8_t cs = 0;

  // Include len in checksum so len corruption is detected
  cs ^= len;
  for (uint8_t i = 0; i < len; ++i) cs ^= data[i];
  return cs;
}

// Validate slot index (returns true if slot fits in EEPROM)
bool validSlot(uint16_t slot) {
  if (slot >= MAX_SLOTS) return false;
  uint16_t addr = slot * SLOT_SIZE;
  return (addr + SLOT_SIZE) <= EEPROM.length();
}

// Write a UID to the given slot
// Return value is whether it was successful
bool writeRFIDtoEEPROM(uint16_t slot, const uint8_t* uid, uint8_t uidLen) {
  if (!validSlot(slot)) return false;
  if (uidLen == 0 || uidLen > MAX_UID_LEN) return false;

  uint16_t base = slot * SLOT_SIZE;
  uint8_t checksum = computeChecksum(uid, uidLen);

  // Write length
  EEPROM.update(base + 0, uidLen);

  // Write bytes (pad remaining with 0)
  for (uint8_t i = 0; i < MAX_UID_LEN; ++i) {
    uint8_t b = (i < uidLen) ? uid[i] : 0;
    EEPROM.update(base + 1 + i, b);
  }

  // Write checksum
  EEPROM.update(base + 1 + MAX_UID_LEN, checksum);

  return true;
}

// Read a UID from a slot
// Return value is whether it was successful
bool readRFIDFromEEPROM(uint16_t slot, uint8_t* outUid, uint8_t* outLen) {
  if (!validSlot(slot)) return false;

  uint16_t base = slot * SLOT_SIZE;
  uint8_t len = EEPROM.read(base + 0);
  if (len == 0 || len > MAX_UID_LEN) {
    // 0 => empty slot or invalid length
    return false;
  }

  // Read UID
  for (uint8_t i = 0; i < len; ++i) {
    outUid[i] = EEPROM.read(base + 1 + i);
  }

  // zero out the rest (optional)
  for (uint8_t i = len; i < MAX_UID_LEN; ++i) outUid[i] = 0;

  uint8_t storedCs = EEPROM.read(base + 1 + MAX_UID_LEN);
  uint8_t calcCs = computeChecksum(outUid, len);
  if (storedCs != calcCs) {
    // Checksum invalid => corrupted UID
    return false;
  }

  *outLen = len;
  return true;
}
