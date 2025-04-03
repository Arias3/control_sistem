import csv
import time

# Archivo CSV donde se almacenarán los datos simulados
CSV_FILE = "data.csv"

# Crear el archivo CSV con encabezados si no existe
try:
    with open(CSV_FILE, mode="r", newline="") as file:
        pass
except FileNotFoundError:
    with open(CSV_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Nivel", "Potencia"])

# Simular llenado y vaciado del recipiente
nivel = 0.0
potencia = -100
direction = 1  # 1 = subiendo, -1 = bajando

try:
    while True:
        # Leer los datos existentes del archivo CSV
        data = []
        try:
            with open(CSV_FILE, mode="r") as file:
                reader = csv.reader(file)
                data = list(reader)
        except FileNotFoundError:
            pass

        # Eliminar encabezados y mantener solo los últimos 50 datos
        if len(data) > 1:
            data = data[1:]  # Eliminar encabezados
        if len(data) >= 100:
            data.pop(0)  # Eliminar el dato más antiguo

        # Redondear la potencia a un decimal
        potencia = round(potencia, 1)

        # Agregar el nuevo dato
        data.append([nivel, potencia])

        # Escribir los datos actualizados en el archivo CSV
        with open(CSV_FILE, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Nivel", "Potencia"])  # Encabezados
            writer.writerows(data)  # Escribir los datos actualizados

        print(f"Datos simulados: Nivel={nivel}, Potencia={potencia}")

        # Actualizar nivel y potencia
        nivel += direction * 1.0
        potencia = -100 + (nivel / 30.0) * 200  # Escalar potencia de -100 a 100

        if nivel >= 30.0:
            nivel = 30.0
            direction = -1
        elif nivel <= 0.0:
            nivel = 0.0
            direction = 1

        # Esperar 1 segundo antes de la siguiente actualización
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\nEjecución interrumpida por el usuario. Saliendo del programa...")