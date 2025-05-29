import csv
import os

# Archivo CSV donde se almacenarán los datos simulados
CSV_FILE = "data.csv"

# Crear el archivo CSV con encabezados si no existe
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Nivel", "Potencia"])  # Encabezados

# Simular llenado y vaciado del recipiente
nivel = 0.0
potencia = -100
direction = 1  # 1 = subiendo, -1 = bajando

try:
    data = []

    while len(data) < 1000:  # Generar exactamente 1000 datos
        # Redondear la potencia a un decimal
        potencia = round(potencia, 1)

        # Agregar el nuevo dato
        data.append([nivel, potencia])

        # Actualizar nivel y potencia
        nivel += direction * 1.0
        potencia = -100 + (nivel / 30.0) * 200  # Escalar potencia de -100 a 100

        if nivel >= 30.0:
            nivel = 30.0
            direction = -1
        elif nivel <= 0.0:
            nivel = 0.0
            direction = 1

    # Escribir los datos generados en el archivo CSV
    with open(CSV_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Nivel", "Potencia"])  # Encabezados
        writer.writerows(data)  # Escribir los datos generados

    print(f"Generación completada: {len(data)} datos almacenados en '{CSV_FILE}'")

except Exception as e:
    print(f"Error durante la generación de datos: {e}")