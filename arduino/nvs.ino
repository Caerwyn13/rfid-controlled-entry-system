// This is to be flashed in order to safely secure the Wi-Fi SSID and Password into the in-built NVS

#include <Preferences.h>

Preferences prefs;

void setup() {
  Serial.begin(115200);

  prefs.begin("rfid_keys", false);   // IMPORTANT: same namespace as main sketch

  // Actual ssid and password not given here for obvious reasons :)
  prefs.putString("wifi_ssid", "WiFiName");
  prefs.putString("wifi_pass", "WiFiPassword");

  Serial.println("WiFi credentials saved to NVS.");

  prefs.end();
}

void loop() {}
