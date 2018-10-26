#include <DHT_U.h>
#include <DHT.h>

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

const char* ssid = "FooBar"; // replace with local wifi network ssid
const char* password = "enchilada"; // replace with local wifi network password
const char* deviceName = "nodeMCUSunroom"; // deviceName will be used as both a device hostname as well as identifying the device in the JSON body
const char* serverAddress = "http://192.168.40.231:5000"; // Flask server address
#define DHTTYPE DHT11
#define dht_dpin 2
DHT dht(dht_dpin, DHTTYPE);

//#define DHT11_PIN 2


void setup() {
  dht.begin();
  delay(1000);
  Serial.begin(115200);

}

void loop() {
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
//  Serial.print("IP Address is: ");
//  IPAddress ip = WiFi.localIP();
//  String ipString = String(ip[0]) + '.' + String(ip[1]) + '.' + String(ip[2]) + '.' + String(ip[3]);
//  String ipPhrase = "IP Address is: " + ipString;
//  Serial.println(ipPhrase);
  Serial.print("Temperature = ");
  Serial.println(dht.readHumidity());
  Serial.print("Humidity = ");
  Serial.println(dht.readTemperature());
  String body = "{\"name\": \"" + String(deviceName) + "\", \"data\": {\"temperature\": \"" + dht.readTemperature() + "\", \"humidity\": \"" + dht.readHumidity() + "\"}}";
  Serial.println(body);
//  if(WiFi.status() == WL_CONNECTED) {
//    HTTPClient http;
//    http.begin(serverAddress);
//    http.addHeader("Content-Type", "text/plain");
//    int httpCode = http.POST(body);
//    String payload = http.getString();
//
//    Serial.println(httpCode);
//    Serial.println(payload);
//    http.end();
//  }
  WiFi.disconnect();
  delay(900000);
}
