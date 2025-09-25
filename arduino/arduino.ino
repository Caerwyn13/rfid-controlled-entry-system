#include <ESP8266WiFi.h>

//TODO: Replace with actual SSID and Password
const char* ssid = "SSID";
const char* pass = "Password";

WifiClient client;
const char* host = "1.1.1.1";    // Replace with PC's IP
const uint16_t port = 12345;     // Replace with actual port

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, pass);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi!");
}

void loop() {
  if (client.connect(host, port)) {
    client.println("Hello!");    // Replace with data to send
  }
  delay(2000);    // Send data every 2 seconds
}
