#include <WiFi.h>
#include <WebSocketsClient.h>

// Configuración de la red WiFi
const char* ssid = "JUANET";
const char* password = "5241856500";

// Configuración del servidor WebSocket
const char* websocket_server = "192.168.0.100";
const uint16_t websocket_port = 8765;

WebSocketsClient webSocket;

// Variables de configuración del recipiente (en cm)
float containerHeight = 30.0;   // Altura máxima del recipiente (valor inicial predeterminado)
float containerDiameter = 10.0; // Diámetro del recipiente (valor inicial predeterminado)

// Variables de simulación
float waterLevel = 0.0;  // Nivel actual de agua (cm)
int direction = 1;       // 1 = subiendo, -1 = bajando
int actuatorPower = 0;   // Potencia del actuador (-100 a 100)

unsigned long previousMillis = 0;
const long interval = 500;  // Actualizar cada 500 ms

// Manejo de eventos del WebSocket
void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  String msg = String((char*)payload);
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
      Serial.println(msg);

      // Manejar mensaje de configuración (c:<altura>,<diámetro>)
      if (msg.startsWith("c:")) {
        String configStr = msg.substring(2); // Extraer el valor después de "c:"
        int commaIndex = configStr.indexOf(",");
        if (commaIndex != -1) {
          String heightStr = configStr.substring(0, commaIndex);
          String diameterStr = configStr.substring(commaIndex + 1);

          // Actualizar dimensiones sin validación adicional
          containerHeight = heightStr.toFloat();
          containerDiameter = diameterStr.toFloat();
          Serial.print("Nueva altura máxima: ");
          Serial.println(containerHeight);
          Serial.print("Nuevo diámetro: ");
          Serial.println(containerDiameter);
        } else {
          Serial.println("Error: Formato de configuración inválido. Use c:<altura>,<diámetro>");
        }
      }
      // Manejar mensaje de setpoint (s:<altura>)
      else if (msg.startsWith("s:")) {
        String setpointStr = msg.substring(2); // Extraer el valor después de "s:"
        waterLevel = setpointStr.toFloat();    // Actualizar el nivel de agua directamente
        Serial.print("Nuevo setpoint recibido: ");
        Serial.println(waterLevel);
      }
      // Mensaje no reconocido
      else {
        Serial.println("Error: Comando no reconocido.");
      }
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
  connectToWiFi();

  webSocket.begin(websocket_server, websocket_port, "/");
  webSocket.setReconnectInterval(5000);
  webSocket.onEvent(webSocketEvent);
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

    // Simular cambios en el nivel de agua
    waterLevel += direction * 1.0;
    if (waterLevel >= containerHeight) {
      waterLevel = containerHeight;
      direction = -1;
    } else if (waterLevel <= 0) {
      waterLevel = 0;
      direction = 1;
    }

    actuatorPower = (direction == 1) ? 100 : -100;

    // Enviar mensaje en formato JSON: [nivel, potencia]
    String mensaje = "[" + String(waterLevel, 1) + "," + String(actuatorPower) + "]";
    Serial.print("Enviando: ");
    Serial.println(mensaje);
    if (webSocket.isConnected()) {
      webSocket.sendTXT(mensaje);
    } else {
      Serial.println("WebSocket no conectado, no se envía el mensaje.");
    }
  }
}