#include <DallasTemperature.h>
#include <OneWire.h>
#include <ArduinoJson.h>
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

const char* ssid = "network"; // replace with local wifi network ssid
const char* password = "password"; // replace with local wifi network password
const char* deviceName = "deviceName"; // deviceName will be used as both a device hostname as well as identifying the device in the JSON body
const char* host = "https://example.com"; // Flask server that we will be POSTing data to
const char* fingerprint = "BF CC A9 BE 47 44 C0 54 62 53 81 E3 05 5E DD D4 A1 BC DE 94"; // SHA1 fingerprint of flask server SSL certificate
const int httpsPort = 443;

#define ONE_WIRE_BUS 2
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire); 

void setup() {
    Serial.begin(115200);
    sensors.begin();
}
void loop(void) {
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
        sensors.requestTemperatures();
        Serial.println("Temperature is: ");
        Serial.println(sensors.getTempCByIndex(0));

        StaticJsonBuffer<300> JSONbuffer;
        JsonObject& root = JSONbuffer.createObject();
        root["name"] = String(deviceName);
        JsonObject& JsonData = root.createNestedObject("data");
        JsonData["temperature"] = sensors.getTempCByIndex(0);
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
    delay(10000); // defines time between the end of a read interval, and the start of the next
}
