#include <Arduino.h>
#include <Preferences.h>
#include <WiFi.h>
#include <MFRC522.h>
#include <SPI.h>

// == Pin definitions =========================================
#define SS_PIN    5
#define RST_PIN   27
#define GREEN_LED 26
#define RED_LED   25

// == UID / NVS storage constants =============================
#define MAX_UID_LEN  10
#define SLOT_SIZE    (1 + MAX_UID_LEN + 1)
#define MAX_SLOTS    50

// == Network configuration ===================================
const char* host = "192.168.1.50";   // Private server IP
const uint16_t port = 5000;         // Private API port

// == Objects =================================================
MFRC522     mfrc522(SS_PIN, RST_PIN);
WiFiClient  client;
Preferences prefs;

// WiFi credentials loaded from NVS
String ssid;
String pass;


// ============================================================
// setup()
// ============================================================
void setup() {
  Serial.begin(115200);

  SPI.begin();
  mfrc522.PCD_Init();

  pinMode(GREEN_LED, OUTPUT);
  pinMode(RED_LED, OUTPUT);

  prefs.begin("rfid_keys", false);

  // Load WiFi credentials from NVS
  ssid = prefs.getString("wifi_ssid", "");
  pass = prefs.getString("wifi_pass", "");

  if (ssid == "" || pass == "") {
    Serial.println("WiFi credentials not set in NVS!");
    Serial.println("Use prefs.putString(\"wifi_ssid\", \"yourSSID\") once to provision.");
    while (true) delay(1000);
  }

  WiFi.begin(ssid.c_str(), pass.c_str());
  Serial.print("Connecting to WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\nConnected!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
}


// ============================================================
// loop()
// ============================================================
void loop() {

  // Auto-reconnect WiFi
  if (WiFi.status() != WL_CONNECTED) {
    WiFi.reconnect();
    delay(1000);
    return;
  }

  digitalWrite(GREEN_LED, LOW);
  digitalWrite(RED_LED, LOW);

  if (!mfrc522.PICC_IsNewCardPresent()) return;
  if (!mfrc522.PICC_ReadCardSerial())   return;

  String content = "";
  for (byte i = 0; i < mfrc522.uid.size; i++) {
    if (mfrc522.uid.uidByte[i] < 0x10) content += "0";
    content += String(mfrc522.uid.uidByte[i], HEX);
  }
  content.toUpperCase();

  bool granted = isAuthorised(mfrc522.uid.uidByte, mfrc522.uid.size);

  if (granted) {
    Serial.println("Access granted");
    digitalWrite(GREEN_LED, HIGH);
  } else {
    Serial.println("Access denied");
    digitalWrite(RED_LED, HIGH);
  }

  sendAccessEvent(content, granted);

  mfrc522.PICC_HaltA();
  delay(2000);
}


// ============================================================
// sendAccessEvent()
// ============================================================
void sendAccessEvent(const String& uid, bool granted) {

  if (!client.connect(host, port)) {
    Serial.println("Server unreachable");
    return;
  }

  // UID, Granted(1/0), Timestamp, Device Token
  String payload = uid + "," +
                   String(granted ? 1 : 0) + "," +
                   String(millis()) + "," +
                   deviceToken + "\n";

  client.print(payload);
  client.stop();

  Serial.print("Sent: ");
  Serial.println(payload);
}


// ============================================================
// NVS helpers (unchanged)
// ============================================================

uint8_t computeChecksum(const uint8_t* data, uint8_t len) {
  uint8_t cs = len;
  for (uint8_t i = 0; i < len; ++i) cs ^= data[i];
  return cs;
}

bool validSlot(uint16_t slot) {
  return slot < MAX_SLOTS;
}

String slotKey(uint16_t slot) {
  return "slot_" + String(slot);
}

bool writeRFIDtoNVS(uint16_t slot, const uint8_t* uid, uint8_t uidLen) {
  if (!validSlot(slot)) return false;
  if (uidLen == 0 || uidLen > MAX_UID_LEN) return false;

  uint8_t blob[SLOT_SIZE] = {};
  blob[0] = uidLen;
  for (uint8_t i = 0; i < uidLen; ++i) blob[1 + i] = uid[i];
  blob[1 + MAX_UID_LEN] = computeChecksum(uid, uidLen);

  prefs.putBytes(slotKey(slot).c_str(), blob, SLOT_SIZE);
  return true;
}

bool readRFIDFromNVS(uint16_t slot, uint8_t* outUid, uint8_t* outLen) {
  if (!validSlot(slot)) return false;

  uint8_t blob[SLOT_SIZE] = {};
  size_t read = prefs.getBytes(slotKey(slot).c_str(), blob, SLOT_SIZE);
  if (read != SLOT_SIZE) return false;

  uint8_t len = blob[0];
  if (len == 0 || len > MAX_UID_LEN) return false;

  for (uint8_t i = 0; i < len; ++i) outUid[i] = blob[1 + i];

  uint8_t storedCs = blob[1 + MAX_UID_LEN];
  uint8_t calcCs   = computeChecksum(outUid, len);
  if (storedCs != calcCs) return false;

  *outLen = len;
  return true;
}

bool isAuthorised(const uint8_t* scannedUid, uint8_t scannedLen) {
  uint8_t storedUid[MAX_UID_LEN];
  uint8_t storedLen;

  for (uint16_t s = 0; s < MAX_SLOTS; ++s) {
    if (!readRFIDFromNVS(s, storedUid, &storedLen)) continue;
    if (storedLen != scannedLen) continue;
    if (memcmp(storedUid, scannedUid, scannedLen) == 0) return true;
  }
  return false;
}
