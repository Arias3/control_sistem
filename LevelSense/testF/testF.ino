// Sensor ultrasónico
#define TRIGGER_PIN 14
#define ECHO_PIN    13

// Puente H
#define IN1     25  // Dirección bomba de vaciado
#define IN2     27  // Dirección bomba de llenado
#define PWM1    33  // PWM bomba de vaciado
#define PWM2    26  // PWM bomba de llenado

long duration;
float distance;
float containerHeight = 22.0; // Altura máxima del recipiente (cm)
float waterLevel = 0.0;       // Nivel actual del líquido (cm)
float targetLevel = 0.0;      // Nivel deseado del líquido (cm)
float hysteresis = 1.0;       // Histeresis de 1 cm

void setup() {
  Serial.begin(115200);

  // Pines sensor
  pinMode(TRIGGER_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  // Pines motores
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(PWM1, OUTPUT);
  pinMode(PWM2, OUTPUT);

  Serial.println("Iniciando sistema...");
  Serial.println("Ingrese el nivel deseado (en cm) por consola serial:");
}

void loop() {
  // Leer el nivel deseado desde la consola serial
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    targetLevel = input.toFloat();
    Serial.print("Nivel deseado actualizado a: ");
    Serial.print(targetLevel);
    Serial.println(" cm");
  }

  // Leer el nivel actual del líquido
  readWaterLevel();

  // Controlar las bombas para alcanzar el nivel deseado con histeresis
  if (waterLevel < targetLevel - hysteresis) {
    // Llenar el recipiente
    Serial.println("Llenando el recipiente...");
    digitalWrite(IN1, LOW);  // Apagar bomba de vaciado
    digitalWrite(IN2, HIGH); // Activar bomba de llenado
    analogWrite(PWM2, 150);  // Velocidad moderada
  } else if (waterLevel > targetLevel + hysteresis) {
    // Vaciar el recipiente
    Serial.println("Vaciando el recipiente...");
    digitalWrite(IN1, HIGH); // Activar bomba de vaciado
    digitalWrite(IN2, LOW);  // Apagar bomba de llenado
    analogWrite(PWM1, 150);  // Velocidad moderada
  } else {
    // Apagar ambas bombas si el nivel está dentro del rango deseado
    Serial.println("Nivel dentro del rango deseado. Apagando bombas.");
    analogWrite(PWM1, 0);
    analogWrite(PWM2, 0);
  }

  delay(500); // Esperar antes de la siguiente iteración
}

// ==== Función para leer el nivel de agua ====
void readWaterLevel() {
  digitalWrite(TRIGGER_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIGGER_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIGGER_PIN, LOW);

  duration = pulseIn(ECHO_PIN, HIGH);
  distance = duration * 0.034 / 2;  // Convertir duración a distancia en cm

  // Calcular la altura del líquido
  waterLevel = containerHeight - distance;
  if (waterLevel < 0) waterLevel = 0;  // Asegurarse de que no sea negativo
  if (waterLevel > containerHeight) waterLevel = containerHeight;  // Limitar al máximo

  Serial.print("Nivel actual del líquido: ");
  Serial.print(waterLevel);
  Serial.println(" cm");
}