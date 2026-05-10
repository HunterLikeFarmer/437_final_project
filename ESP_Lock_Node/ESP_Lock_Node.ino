#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <SPI.h>
#include <MFRC522.h>

#define DEBUG

#define MOSI 15
#define MISO 16
#define CLK 17
#define RST 6
#define SDA 5

#define RED_LED 11
#define GREEN_LED 10

#define SERVO 9

const char* ssid = "2.4 207WRIG-U203";
const char* password = "CXNK0080A813";
const char* mqtt_server = "192.168.10.56";
const int port_num = 1883;

WiFiClient espClient;
PubSubClient client(espClient);

int lock_state = 0;

MFRC522 rfid(SDA, RST);

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

  #if defined(DEBUG)
    Serial.println("Lock State: " + message);
  #endif

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

  SPI.begin(17, 16, 15, 5);

  rfid.PCD_Init();
  Serial.println("RFID Intialized");

  //Intialize LEDs
  pinMode(RED_LED, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);

  //Intialize Servo
  ledcAttach(SERVO, 50, 14);

}

void loop() {

  if (!client.connected()) {
      Serial.println(("Disconnected from server"));
      client.connect("lock_1");
      client.subscribe("smart_toddler/lock/command");
      delay(3000);
    }

  ledcWrite(SERVO, 819);

  if (lock_state == 0) {
    //Unlocked State
    digitalWrite(GREEN_LED, HIGH);
    digitalWrite(RED_LED, LOW);
    ledcWrite(SERVO, 819);
    delay(2000);
  } else if (lock_state == 1) {
    //Locked State
    digitalWrite(GREEN_LED, LOW);
    digitalWrite(RED_LED, HIGH);
    ledcWrite(SERVO, 1638);
    delay(2000);
  }

  client.loop();

  sendData();

  if (rfid.PICC_IsNewCardPresent()) {
    if (rfid.PICC_ReadCardSerial()) {
      #if defined(DEBUG)
        Serial.println("Card Read");
      #endif

      //Hold card readings:
      rfid.PICC_HaltA();

      //Switch Lock State
      if (lock_state == 0)
        lock_state = 1;
      else if (lock_state == 1)
        lock_state = 0;
      
      #if defined(DEBUG)
        Serial.println("Lock State Switched");
      #endif
    }
  }

  delay(500);
}
