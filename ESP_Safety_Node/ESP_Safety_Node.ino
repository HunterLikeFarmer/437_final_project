#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include "DFRobot_C4001.h"

#define RX 5
#define TX 18
#define LED 19
#define BUZZER 23

//Wifi Parameters
const char* ssid = "2.4 207WRIG-U203";
const char* password = "CXNK0080A813";
const char* mqtt_server = "192.168.10.56";
const int port_num = 1883;

WiFiClient espClient;
PubSubClient client(espClient);

//Radar Parameters
int target;
DFRobot_C4001_UART radar(&Serial1, 9600, RX, TX);

void sendData() {
  StaticJsonDocument<256> doc;

  doc["node_id"] = "safety_1";
  doc["status"] = "ok";

  JsonObject data = doc.createNestedObject("data");
  data["kids_close"] = target;

  char payload[256];
  serializeJson(doc, payload);

  client.publish("smart_toddler/safety/status", payload);
}

void setup() {
  Serial.begin(115200);

  delay(1000);
  while(!Serial);

  WiFi.begin(ssid, password);

  while(WiFi.status() != WL_CONNECTED)
    delay(500);

  Serial.println("Wifi Connected");

  client.setServer(mqtt_server, port_num);

  while(!client.connected()) {
    client.connect("safety_1");
    delay(500);
  }
    

  Serial.println("Client Connected");

  while (!radar.begin()) {
    Serial.println("Radar not connected");
    delay(1000);
  }
  Serial.println("Device connected!");


  //Set Radar Sensor Parameters
  radar.setSensorMode(eSpeedMode);

  sSensorStatus_t data;
  data = radar.getStatus();

  Serial.print("work status  = ");
  Serial.println(data.workStatus);

  Serial.print("work mode  = ");
  Serial.println(data.workMode);

  Serial.print("init status = ");
  Serial.println(data.initStatus);
  Serial.println();

  if (radar.setDetectThres(/*min*/ 40, /*max*/ 1200, /*thres*/ 130)) { //was thres=10 and min=11, 40
    Serial.println("set detect threshold successfully");
  }

  radar.setFrettingDetection(eON);

  //Send Parameters for Radar Sensor
  Serial.print("min range = ");
  Serial.println(radar.getTMinRange());
  Serial.print("max range = ");
  Serial.println(radar.getTMaxRange());
  Serial.print("threshold range = ");
  Serial.println(radar.getThresRange());
  Serial.print("fretting detection = ");
  Serial.println(radar.getFrettingDetection());

  pinMode(BUZZER, OUTPUT);
  pinMode(LED, OUTPUT);
}

void loop() {
  target = radar.getTargetNumber();

  //If target detected, turn on LED and BUZZER
  if (target > 0) {
    tone(BUZZER, 2700);
    digitalWrite(LED, HIGH);
  } else {
    noTone(BUZZER);
    digitalWrite(LED, LOW);
  }

  if (!client.connected()) {
    Serial.println(("Disconnected from server"));
    client.connect("safety_1");
    delay(3000);
  }

  client.loop();
  sendData();
  delay(800);
}
