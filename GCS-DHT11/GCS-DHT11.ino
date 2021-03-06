/**
 * Greenview Climate Sensor will collect temperature and humidity data and send it to a flask server.
 * Connects to wifi once every 15 minutes, sends data, disconnects.
 **/

#include <DHT_U.h>
#include <DHT.h>
#include <ArduinoJson.h>

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

const char* ssid = "network"; // replace with local wifi network ssid
const char* password = "password"; // replace with local wifi network password
const char* deviceName = "device name"; // deviceName will be used as both a device hostname as well as identifying the device in the JSON body
const char* host = "https://example.com"; // Flask server that we will be POSTing data to
const char* fingerprint = "BF CC A9 BE 47 44 C0 54 62 53 81 E3 05 5E DD D4 A1 BC DE 94"; // SHA1 fingerprint of flask server SSL certificate
const int httpsPort = 443;
#define DHTTYPE DHT11
#define dht_dpin 2
DHT dht(dht_dpin, DHTTYPE);

void setup() {
  dht.begin();
  delay(1000);
  Serial.begin(115200);
}

void loop() {
  WiFi.mode(WIFI_STA);
  WiFi.hostname(deviceName);
  WiFi.begin(ssid, password);

  Serial.println();
  Serial.print("Connecting");
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }
  Serial.println("success!");
  if(WiFi.status() == WL_CONNECTED) {
    StaticJsonBuffer<300> JSONbuffer;
    JsonObject& root = JSONbuffer.createObject();
    root["name"] = String(deviceName);
    JsonObject& JsonData = root.createNestedObject("JsonData");
    JsonData["temperature"] = dht.readTemperature();
    JsonData["humidity"] = dht.readHumidity();
    char JSONmessageBuffer[300];
    root.prettyPrintTo(JSONmessageBuffer, sizeof(JSONmessageBuffer));
    Serial.println(JSONmessageBuffer);

    HTTPClient http;

    http.begin(host, fingerprint);
    http.addHeader("Content-Type", "application/json");

    int httpCode = http.POST(JSONmessageBuffer);
    String payload = http.getString();
    Serial.println(httpCode);
    Serial.println(payload);
    http.end();
  
  } else {
    Serial.println("connection failed");
    delay(3000);
    return;
  }
  WiFi.disconnect();
  delay(900000); // defines time between the end of a read interval, and the start of the next
}
