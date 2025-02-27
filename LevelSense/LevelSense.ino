#include <WiFi.h>
#include <WebSocketsClient.h>

// Configuración de la red WiFi
const char* ssid = "JA";              // Nombre de la red (SSID)
const char* password = "juanpro123";  // Contraseña de la red

// Configuración del servidor WebSocket
const char* websocket_server = "192.168.14.190";  // IP del servidor
const uint16_t websocket_port = 8765;          // Puerto del servidor

WebSocketsClient webSocket;

// Manejo de eventos del WebSocket
void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  switch (type) {
    case WStype_DISCONNECTED:
      Serial.println("Desconectado del WebSocket!");
      break;
    case WStype_CONNECTED:
      Serial.println("Conectado al WebSocket!");
      // Enviar mensaje inicial al conectarse
      webSocket.sendTXT("ESP32 conectado");
      break;
    case WStype_TEXT:
      Serial.printf("Mensaje recibido: %s\n", payload);
      // Si se recibe el comando "RESET", reiniciar el ESP32
      if (strcmp((char*)payload, "RESET") == 0) {
        Serial.println("Reiniciando ESP32...");
        ESP.restart();
      }
      break;
    case WStype_ERROR:
      Serial.println("Error en el WebSocket");
      break;
    default:
      break;
  }
}

// Función para conectar a la red WiFi
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

unsigned long previousMillis = 0;
const long interval = 1000;  // Envío de datos cada 1 segundo

void setup() {
  Serial.begin(115200);
  // Conectar a WiFi
  connectToWiFi();

  // Inicializar conexión WebSocket
  webSocket.begin(websocket_server, websocket_port, "/");
  // Configura reconexión automática cada 5 segundos si se pierde
  webSocket.setReconnectInterval(5000);
  webSocket.onEvent(webSocketEvent);
}

void loop() {
  // Verificar que WiFi siga conectado, y reconectar en caso contrario
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi desconectado. Reintentando conexión...");
    connectToWiFi();
  }

  // Procesar eventos del WebSocket
  webSocket.loop();

  // Enviar datos simulados cada segundo
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
    int nivel_liquido = random(0, 101);  // Nivel simulado entre 0 y 100%
    String mensaje = "Nivel: " + String(nivel_liquido) + "%";
    Serial.println("Enviando: " + mensaje);
    
    if (webSocket.isConnected()) {
      webSocket.sendTXT(mensaje);
    } else {
      Serial.println("WebSocket no conectado, no se envía el mensaje.");
    }
  }
}

