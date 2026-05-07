#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <DHT11.h>

//#define DEBUG

#define DHT_PIN 12
#define PHOTO_PIN 15
#define MOTION_PIN 11
#define SOUND_PIN 13

const char* ssid = "2.4 207WRIG-U203";
const char* password = "CXNK0080A813";
const char* mqtt_server = "192.168.10.56";
const int port_num = 1883;

WiFiClient espClient;
PubSubClient client(espClient);

DHT11 temp_humid_sensor(DHT_PIN);
long slow_sense_time = 3000000;
unsigned long now = 0;
unsigned long last_sensed = 0;

int temp;
int humid;
float light_value;
float sound_value;
int motion_detected;

void sendData() {
  StaticJsonDocument<256> doc;

  doc["node_id"] = "environment_1";
  doc["status"] = "ok";

  JsonObject data = doc.createNestedObject("data");
  data["temperature"] = temp;
  data["humidity"] = humid;
  data["light_level"] = light_value;
  data["sound_level"] = sound_value;
  data["motion_detected"] = motion_detected;

  char payload[256];
  serializeJson(doc, payload);

  client.publish("smart_toddler/environment/status", payload);
}

void setup() {
  Serial.begin(115200);

  WiFi.begin(ssid, password);

  while(WiFi.status() != WL_CONNECTED)
    delay(500);

  Serial.println("Wifi Connected");

  client.setServer(mqtt_server, port_num);

  while(!client.connected()) {
    client.connect("environment_1");
    delay(500);
  }
    

  Serial.println("Client Connected");

  analogSetAttenuation(ADC_11db);
  pinMode(MOTION_PIN, INPUT);
}

void loop() {
  light_value = analogRead(PHOTO_PIN);
  sound_value = analogRead(SOUND_PIN);
  motion_detected = digitalRead(MOTION_PIN);

  now = micros();
  if (now - last_sensed >= slow_sense_time) {

    last_sensed = micros();

    #if defined(DEBUG)
      if (motion_detected == HIGH) {
        Serial.println("Motion detected");
      } else {
        Serial.println("No motion detected");
      }

      Serial.printf("Sound value: %f\n", sound_value);
    #endif

    if (temp_humid_sensor.readTemperatureHumidity(temp, humid) == 0) {
      #if defined(DEBUG)
        Serial.printf("Temperatured: %d, Humidity: %d\n", temp, humid);
      #endif
    }
      
    #if defined(DEBUG)
      Serial.printf("Light value: %f\n", light_value);
    #endif

    if (!client.connected()) {
      Serial.println(("Disconnected from server"));
      client.connect("environment_1");
      delay(3000000);
    }

    client.loop();

    sendData();
  }

}
