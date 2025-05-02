// Pines del sensor ultrasónico
#define TRIGGER_PIN 14
#define ECHO_PIN    13

// Pines del puente H
#define IN1  25
#define IN2  27
#define PWM1 33  // Llenado
#define PWM2 26  // Vaciado

// Variables de estado
bool sensorActivo = false;
bool llenando = false;
bool vaciando = false;
int velocidadGeneral = 255;  // Velocidad compartida

// Calibración
float distanciaBase = 0.0;  // Distancia cuando nivel de agua = 0 cm

// SETUP
void setup() {
  Serial.begin(115200);

  pinMode(TRIGGER_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(PWM1, OUTPUT);
  pinMode(PWM2, OUTPUT);

  detenerMotores();

  Serial.println("Comandos disponibles:");
  Serial.println("s: activar/desactivar sensor ultrasónico");
  Serial.println("l: activar llenado");
  Serial.println("v: activar vaciado");
  Serial.println("x: detener motores");
  Serial.println("+: aumentar velocidad");
  Serial.println("-: disminuir velocidad");
  Serial.println("0: establecer nivel base (nivel = 0 cm)");
}

// LOOP PRINCIPAL
void loop() {
  if (Serial.available()) {
    char comando = Serial.read();

    switch (comando) {
      case 's':
        sensorActivo = !sensorActivo;
        Serial.println(sensorActivo ? "Sensor activado" : "Sensor desactivado");
        break;

      case 'l':
        llenando = true;
        vaciando = false;
        activarLlenado();
        Serial.println("Modo: LLENADO");
        break;

      case 'v':
        vaciando = true;
        llenando = false;
        activarVaciado();
        Serial.println("Modo: VACIADO");
        break;

      case 'x':
        llenando = false;
        vaciando = false;
        detenerMotores();
        Serial.println("Motores detenidos");
        break;

      case '+':
        velocidadGeneral++;
        if (velocidadGeneral > 255) velocidadGeneral = 255;
        Serial.print("Velocidad actual: ");
        Serial.println(velocidadGeneral);
        actualizarVelocidad();
        break;

      case '-':
        velocidadGeneral--;
        if (velocidadGeneral < 0) velocidadGeneral = 0;
        Serial.print("Velocidad actual: ");
        Serial.println(velocidadGeneral);
        actualizarVelocidad();
        break;

      case '0':  // Establecer nivel base (nivel = 0 cm)
        if (sensorActivo) {
          long duracion = medirDistancia();
          distanciaBase = duracion * 0.034 / 2;
          Serial.print("Distancia base establecida: ");
          Serial.print(distanciaBase);
          Serial.println(" cm");
        } else {
          Serial.println("Sensor no está activado. No se puede establecer nivel base.");
        }
        break;
    }
  }

  if (sensorActivo) {
    long duracion = medirDistancia();
    float distancia = duracion * 0.034 / 2;
    float nivelMedido = distanciaBase - distancia;

    if (distanciaBase > 0) {
      Serial.print("Nivel de agua (sin corrección): ");
      Serial.print(nivelMedido);
      Serial.println(" cm");
    } else {
      Serial.println("Esperando calibración con tecla '0'...");
    }

    delay(500);
  }
}

// FUNCIONES DE CONTROL DE MOTORES
void activarLlenado() {
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  analogWrite(PWM1, velocidadGeneral);
  analogWrite(PWM2, 0);
}

void activarVaciado() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  analogWrite(PWM1, 0);
  analogWrite(PWM2, velocidadGeneral);
}

void detenerMotores() {
  analogWrite(PWM1, 0);
  analogWrite(PWM2, 0);
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
}

void actualizarVelocidad() {
  if (llenando) activarLlenado();
  if (vaciando) activarVaciado();
}

// MEDICIÓN ULTRASÓNICA
long medirDistancia() {
  digitalWrite(TRIGGER_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIGGER_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIGGER_PIN, LOW);
  return pulseIn(ECHO_PIN, HIGH, 30000);  // timeout: 30ms
}
