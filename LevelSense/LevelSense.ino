#include <WiFi.h>
#include <WebSocketsClient.h>

// Configuración de la red WiFi
const char* ssid = "JUANET";
const char* password = "5241856500";

// Configuración del servidor WebSocket
const char* websocket_server = "192.168.0.101";
const uint16_t websocket_port = 8765;

WebSocketsClient webSocket;

// Sensor ultrasónico
#define TRIGGER_PIN 14
#define ECHO_PIN    13

// Puente H
#define IN1     25
#define IN2     27
#define PWM1    33
#define PWM2    26
//NIVEL MINIMO DE LA BOMBA DE LLENADO ES 65 PWM. 
// NIVEL MINIMO DE LA BOMBA DE VACIADO ES 60 PWM.
// Variables del sistema
float containerHeight = 22.0;   // Altura máxima del recipiente (cm)
float containerDiameter = 10.0; // Diámetro del recipiente (cm)
float waterLevel = 0.0;         // Nivel actual del líquido (cm)
float setpoint = 0.0;          // Nivel deseado del líquido (cm)
float hysteresis = 1.0;         // Histeresis
float power=0.0; // potencia de los motores


// Variables del sensor ultrasónico
long duration;
float distance;

// --- PID ---
float Kp = 0.15;
float Ki = 0.02;
float Kd = 0.05;
float integral = 0.0;
float prev_error = 0.0;
unsigned long last_time = 0;
int bomba_estado = 0; // 0=apagada, 1=llenando, -1=vaciando

// ==== Función de conexión WiFi ====
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

// ==== Función de conexión WebSocket ====
void connectToWebSocket() {
  webSocket.begin(websocket_server, websocket_port, "/");
  webSocket.setReconnectInterval(5000);
  webSocket.onEvent(webSocketEvent);
}

// ==== Función de lectura del sensor ultrasónico ====
void readUltrasonicSensor() {
  digitalWrite(TRIGGER_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIGGER_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIGGER_PIN, LOW);

  duration = pulseIn(ECHO_PIN, HIGH);
  distance = duration * 0.034 / 2;  // Convertir duración a distancia en cm

  // Calcular la altura del líquido en el contenedor
  waterLevel = containerHeight - distance*1.04;
  if (waterLevel < 0) waterLevel = 0;  // Asegurarse de que no sea negativo
  if (waterLevel > containerHeight) waterLevel = containerHeight;  // Limitar al máximo

  Serial.print("Distancia medida: ");
  Serial.print(distance);
  Serial.println(" cm");

  Serial.print("Altura del líquido: ");
  Serial.print(waterLevel);
  Serial.println(" cm");
}

void controlMotors() {
  float error = setpoint - waterLevel;
  unsigned long now = millis();
  float dt = 0.1; // 100 ms en segundos

  // Integral y derivada
  integral += error * dt;
  float derivative = (error - prev_error) / dt;

  // Ley de control PID
  float u = Kp * error + Ki * integral + Kd * derivative;

  // Saturación de la señal de control
  if (u > 1.0) u = 1.0;
  if (u < -1.0) u = -1.0;

  // --- HISTERESIS ---
  float upper = setpoint + hysteresis / 2.0;
  float lower = setpoint - hysteresis / 2.0;

  if (waterLevel < lower) {
    bomba_estado = 1; // Llenar
  } else if (waterLevel > upper) {
    bomba_estado = -1; // Vaciar
  } // Si está dentro de la banda, mantiene el último estado

  if (bomba_estado == 1 && u > 0.01) {
    // Llenar
    int pwm = (int)(u * 255.0);
    if (pwm < 65) pwm = 65;
    if (pwm > 255) pwm = 255;
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    analogWrite(PWM1, pwm);
    analogWrite(PWM2, 0);
    power = u * 100.0;
    Serial.println("PID: Llenando");
  } else if (bomba_estado == -1 && u < -0.01) {
    // Vaciar
    int pwm = (int)(-u * 255.0);
    if (pwm < 65) pwm = 65;
    if (pwm > 255) pwm = 255;
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
    analogWrite(PWM1, 0);
    analogWrite(PWM2, pwm);
    power = u * 100.0;
    Serial.println("PID: Vaciando");
  } else {
    // Apagar ambas bombas
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, LOW);
    analogWrite(PWM1, 0);
    analogWrite(PWM2, 0);
    power = 0;
    Serial.println("PID: Apagando bombas");
  }

  prev_error = error;
}

// ==== Manejo de eventos del WebSocket ====
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
      if (msg.startsWith("s:")) {
        String setpointStr = msg.substring(2); // Extraer el valor después de "s:"
        setpoint = setpointStr.toFloat();      // Actualizar el setpoint
        Serial.print("Nuevo setpoint recibido: ");
        Serial.println(setpoint);
      }
      break;
    case WStype_ERROR:
      Serial.println("Error en el WebSocket");
      break;
    default:
      break;
  }
}

void setup() {
  Serial.begin(115200);

  // Configurar pines del sensor ultrasónico
  pinMode(TRIGGER_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  // Configurar pines de las bombas
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(PWM1, OUTPUT);
  pinMode(PWM2, OUTPUT);

  // Conectar a WiFi y WebSocket
  connectToWiFi();
  connectToWebSocket();

  // Establecer el setpoint por defecto
  setpoint = 0.0;
  Serial.print("Setpoint inicial: ");
  Serial.println(setpoint);
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi desconectado. Reintentando...");
    connectToWiFi();
  }
  webSocket.loop();

  // Leer el sensor ultrasónico
  readUltrasonicSensor();

  // Controlar las bombas
  controlMotors();

  // Enviar datos al servidor WebSocket
  //float mappedOutput = 255 / 255.0 * 100.0; // Mapear output de -255 a 255 a -100 a 100
  String mensaje = "[" + String(waterLevel, 1) + "," + String(power, 1) + "]";
  Serial.print("Enviando: ");
  Serial.println(mensaje);
  if (webSocket.isConnected()) {
    webSocket.sendTXT(mensaje);
  } else {
    Serial.println("WebSocket no conectado, no se envía el mensaje.");
  }

  delay(100);  // Ejecutar el control cada 100 ms
}