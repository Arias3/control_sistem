// Definir el pin del LED integrado (si tu placa lo tiene) o usa otro pin
#define LED_BUILTIN 2  // En muchas placas ESP32, el LED está en el pin 2

void setup() {
  pinMode(LED_BUILTIN, OUTPUT); // Configurar el pin como salida
}

void loop() {
  digitalWrite(LED_BUILTIN, HIGH); // Encender el LED
  delay(1000); // Esperar 1 segundo
  digitalWrite(LED_BUILTIN, LOW); // Apagar el LED
  delay(1000); // Esperar 1 segundo
}
