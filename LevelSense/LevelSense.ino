#include <WiFi.h>
#include <WebSocketsClient.h>

#define TRIG_PIN 12  // Pin de disparo (Trig) del sensor ultrasónico
#define ECHO_PIN 14  // Pin de recepción (Echo) del sensor ultrasónico

// Configuración de la red WiFi
const char* ssid = "JA";
const char* password = "juanpro123";

// Configuración del servidor WebSocket
const char* websocket_server = "192.168.127.190";
const uint16_t websocket_port = 8765;

WebSocketsClient webSocket;

unsigned long previousMillis = 0;
const long interval = 500;  // Actualizar cada 1 segundo
const int actuatorPower = 100; // Valor constante para la potencia del actuador

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  switch(type) {
    case WStype_DISCONNECTED:
      Serial.println("Desconectado del WebSocket!");
      break;
    case WStype_CONNECTED:
      Serial.println("Conectado al WebSocket!");
      webSocket.sendTXT("ESP32 conectado");
      break;
    case WStype_TEXT:
      Serial.print("Mensaje recibido: ");
      Serial.println((char*)payload);
      break;
    case WStype_ERROR:
      Serial.println("Error en el WebSocket");
      break;
    default:
      break;
  }
}

void connectToWiFi() {
  Serial.print("Conectando a WiFi: ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("Conectado! IP: ");
  Serial.println(WiFi.localIP());
}

void setup() {
  Serial.begin(115200);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  connectToWiFi();
  webSocket.begin(websocket_server, websocket_port, "/");
  webSocket.setReconnectInterval(5000);
  webSocket.onEvent(webSocketEvent);
}

float medirDistancia() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH);
  float distance = (duration * 0.0343) / 2;
  return distance;
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi desconectado. Reintentando...");
    connectToWiFi();
  }
  webSocket.loop();

  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
    float distance = medirDistancia();
    Serial.print("Distancia medida: ");
    Serial.println(distance);

    // Enviar mensaje en formato JSON: [distancia, potencia]
    String mensaje = "[" + String(distance, 1) + "," + String(actuatorPower) + "]";
    Serial.print("Enviando: ");
    Serial.println(mensaje);
    if (webSocket.isConnected()) {
      webSocket.sendTXT(mensaje);
    } else {
      Serial.println("WebSocket no conectado, no se envía el mensaje.");
    }
  }
}