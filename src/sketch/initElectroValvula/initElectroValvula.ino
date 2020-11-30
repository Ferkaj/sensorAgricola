#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include "configuracionWIFI.h"
#include <ArduinoJson.h>


WiFiClient espClient;
PubSubClient client(espClient);
long lastMsg = 0;
int value = 0;

#define BUTTON_BUILTIN 0
#define pinRele 4

void setup_wifi() {
  digitalWrite(BUILTIN_LED, HIGH);
  delay(10);
  // Primero establecemos la conexion WIFI
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  randomSeed(micros());

  Serial.println("");
  Serial.println("conexion WIFI establecida");
  Serial.println("direccion IP: ");
  Serial.println(WiFi.localIP());
  Serial.println("direccion MAC: ");
  Serial.println(WiFi.macAddress());
}

void callback(char* topic, byte* payload, unsigned int length) {
  String mensaje = "";

  for (int i = 0; i < length; i++) {
    mensaje =String(mensaje + (char)payload[i]);
  }
  Serial.println();

  DynamicJsonDocument doc(1024);
  DeserializationError error = deserializeJson(doc, mensaje);
  
  if (error) {
    Serial.print("deserializeMsgPack() failed: ");
    Serial.println(error.f_str());
    return;
  } else {
    const String mac = doc["id"];

    if (mac == WiFi.macAddress()){
      boolean estado = doc["estado"];
      Serial.println(estado);
      //ejecutar orden
      if( estado == HIGH){
        Serial.println("activar");
        activarRele();
      } else if( estado == LOW){
        Serial.println("desactivar");
        desactivarRele();
      }
    }
  }
  
  
}

void reconnect() {
  // Bucle hasta reconectar MQTT
  while (!client.connected()) {
    Serial.print("Intentado la conexion MQTT...");
    String clientId = WiFi.macAddress();
    // Se intenta conectar
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      client.subscribe("leaf/server/data");
    } else {
      Serial.print("fallo, rc=");
      Serial.print(client.state());
      Serial.println(" se intentara de nuevo en 5 segundos");
      // Espera 5 segundos antes de reintentarlo
      delay(5000);
    }
  }
}
void setup() {
  pinMode(BUILTIN_LED, OUTPUT);    
  pinMode(BUTTON_BUILTIN, INPUT);
  pinMode(pinRele, OUTPUT);
  testRele();
  
  Serial.begin(115200);
  Serial.println("Electrovalvula iniciada!");
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  
  digitalWrite(BUILTIN_LED, HIGH);
}

void loop() {

  if (!client.connected()) {
    reconnect();
  }
  client.loop();

}

void activarRele(){
  digitalWrite(pinRele, HIGH);
}

void desactivarRele(){
  digitalWrite(pinRele, LOW);
}

void testRele(){
  digitalWrite(LED_BUILTIN, HIGH);
  digitalWrite(pinRele, HIGH);  
  delay(500);
  digitalWrite(LED_BUILTIN, LOW);
  digitalWrite(pinRele, LOW);  
  delay(100);                      
}
