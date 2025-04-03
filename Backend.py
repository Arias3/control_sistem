import csv
import os
from websocket_server import WebsocketServer

# Archivo CSV donde se almacenarán los datos
CSV_FILE = "data.csv"

# Crear el archivo CSV si no existe
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Nivel", "Potencia"])  # Encabezados del archivo

# Función que se ejecuta cuando un cliente se conecta
def new_client(client, server):
    print(f"Cliente conectado: {client['id']}")

# Función que se ejecuta cuando se recibe un mensaje
def message_received(client, server, message):
    
    try:
        # Procesar el mensaje recibido (formato esperado: [nivel, potencia])
        data = eval(message)  # Convertir el mensaje en una lista
        if len(data) == 2:
            nivel, potencia = data

            # Leer los datos existentes del archivo CSV
            rows = []
            if os.path.exists(CSV_FILE):
                with open(CSV_FILE, mode="r") as file:
                    reader = csv.reader(file)
                    rows = list(reader)

            # Eliminar encabezados y mantener solo los últimos 100 datos
            if len(rows) > 1:
                rows = rows[1:]  # Eliminar encabezados
            if len(rows) >= 100:
                rows.pop(0)  # Eliminar el dato más antiguo

            # Agregar el nuevo dato al final
            rows.append([nivel, potencia])

            # Escribir los datos actualizados en el archivo CSV
            with open(CSV_FILE, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Nivel", "Potencia"])  # Encabezados
                writer.writerows(rows)  # Escribir los datos actualizados
        else:
            print("Formato de mensaje inválido")
    except Exception as e:
        print(f"Error al procesar el mensaje: {e}")

# Crear el servidor WebSocket
server = WebsocketServer(host="0.0.0.0", port=8765)
server.set_fn_new_client(new_client)
server.set_fn_message_received(message_received)

print("Servidor WebSocket corriendo en 0.0.0.0:8765")
server.run_forever()