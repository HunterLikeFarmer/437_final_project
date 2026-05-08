#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

const char* ssid = "2.4 207WRIG-U203";
const char* password = "CXNK0080A813";
const char* mqtt_server = "192.168.10.56";
const int port_num = 1883;

WiFiClient espClient;
PubSubClient client(espClient);

int lock_state = 0;

void sendData() {
  StaticJsonDocument<256> doc;

  doc["node_id"] = "lock_1";
  doc["status"] = "ok";

  JsonObject data = doc.createNestedObject("data");
  data["lock_value"] = lock_state;

  char payload[256];
  serializeJson(doc, payload);

  client.publish("smart_toddler/lock/status", payload);
}

void getData(char* topic, byte* payload, unsigned int length) {
  String message;
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }

  Serial.println("Lock State: " + message);

  StaticJsonDocument<256> doc;
  deserializeJson(doc, message);
  
  if (doc.containsKey("command")) {
    const char* cmd = doc["command"];
    if (strcmp(cmd, "lock") == 0) {
      lock_state = 1;
    }
    if (strcmp(cmd, "unlock") == 0) {
      lock_state = 0;
    } 
  }

}

void setup() {
  Serial.begin(115200);

  WiFi.begin(ssid, password);

  while(WiFi.status() != WL_CONNECTED)
    delay(500);

  Serial.println("Wifi Connected");

  client.setServer(mqtt_server, port_num);
  client.setCallback(getData);

  while(!client.connected()) {
    client.connect("lock_1");
    client.subscribe("smart_toddler/lock/command");
    delay(500);
  }
    

  Serial.println("Client Connected");

}

void loop() {

  if (!client.connected()) {
      Serial.println(("Disconnected from server"));
      client.connect("lock_1");
      client.subscribe("smart_toddler/lock/command");
      delay(3000);
    }

    client.loop();

    sendData();

    delay(500);
}
