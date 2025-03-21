#define TRIG_PIN 12  // Pin de disparo (Trig) del sensor ultrasónico
#define ECHO_PIN 14  // Pin de recepción (Echo) del sensor ultrasónico

void setup() {
    Serial.begin(115200);  // Inicia la comunicación serie
    pinMode(TRIG_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);
}

void loop() {
    // Enviar un pulso de 10µs al pin Trig
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);

    // Medir el tiempo que tarda en llegar el eco
    long duration = pulseIn(ECHO_PIN, HIGH);
    
    // Calcular la distancia en centímetros
    float distance = (duration * 0.0343) / 2;

    // Mostrar el resultado en el Monitor Serie
    Serial.print("Distancia: ");
    Serial.print(distance);
    Serial.println(" cm");

    delay(500);  // Pequeña pausa antes de la siguiente medición
}
