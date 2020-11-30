#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include "configuracionWIFI.h"
#include <ArduinoJson.h>
#define DHTPIN 4   
#define DHTTYPE DHT21   // DHT 21 (AM2301)

DHT dht(DHTPIN, DHTTYPE);

WiFiClient espClient;
PubSubClient client(espClient);
long lastMsg = 0;
int value = 0;

#define BUTTON_BUILTIN 0

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
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Mensaje recibido [");
  Serial.print(topic);
  Serial.print("] ");
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();

}

void reconnect() {
  // Bucle hasta reconectar MQTT
  while (!client.connected()) {
    Serial.print("Intentado la conexion MQTT...");
    String clientId = WiFi.macAddress();
    // Se intenta conectar
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
      // Una vez conectado, publicar un mensaje...
      client.publish("sensor/data/id", "hello world");
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
  Serial.begin(115200);
  Serial.println("DHTxx test!");
  dht.begin();
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
  
  // Se obtiene los valores de los sensores
  float temp = dht.readTemperature(); // Recoge la temperatura ambiental
  float hum = dht.readHumidity();     // Recoge la humedad ambiental
  int valor = analogRead(A0);         // Recoge la humedad terrestre, valores de 0 a 1024
  int soil =  map(valor, 0, 1023, 100, 0); // Se convierte los valores a escala 0 a 100
  
  // Serializamos los valores en un formato JSON
  const size_t capacity = JSON_OBJECT_SIZE(6);
  DynamicJsonDocument doc(capacity);
  doc["id"] = WiFi.macAddress(); // Se añade un nuevo campo llamado id que identifica al sensor, este se compone de la mac del sensor
  doc["temp"] = temp;
  doc["hum"] = hum;
  doc["soil"] = soil;
  serializeJson(doc, Serial);

  //Se envia mediante MQTT el json, antes se debe convertir a un array de char
  char buffer[256];
  size_t n = serializeJson(doc, buffer);
  Serial.println();
  boolean exito = client.publish(topic_mqtt, buffer,n);
  digitalWrite(BUILTIN_LED, LOW);
  Serial.println("\n");
  delay(100);
  digitalWrite(BUILTIN_LED, HIGH);
  if(exito){
    Serial.println("Modo ESP8266 deep sleep durante 30 segundos");
    ESP.deepSleep(900e6); // 60e6 es 60.000.000 microsegundos
  } else{
    delay(10); // Solo se ejecuta si falla el envio de mqtt
  }
}
