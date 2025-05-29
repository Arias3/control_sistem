import csv
import os
from websocket_server import WebsocketServer
import threading

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
            if len(rows) >= 1000:
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

# Función para enviar un mensaje al ESP
def enviar_mensaje(mensaje):
    """Envía un mensaje al ESP a través del servidor WebSocket."""
    try:
        if server.clients:
            for client in server.clients:
                server.send_message(client, mensaje)
                print(f"Mensaje enviado al cliente {client['id']}: {mensaje}")
        else:
            print("No hay clientes conectados para enviar el mensaje.")
    except Exception as e:
        print(f"Error al enviar el mensaje: {e}")

# Crear el servidor WebSocket
server = WebsocketServer(host="0.0.0.0", port=8765)
server.set_fn_new_client(new_client)
server.set_fn_message_received(message_received)

# Ejemplo: Enviar un mensaje al ESP
def enviar_comandos():
    """Función para enviar comandos al ESP desde la consola."""
    print("Servidor WebSocket corriendo en 0.0.0.0:8765")
    try:
        while True:
            comando = input("Ingrese el comando a enviar (formato: 's:25.0' o 'c:50.0,10.0', SALIR para salir): ").strip()
            if comando.lower().startswith(("s:", "c:")):
                enviar_mensaje(comando)  # Llamar a enviar_mensaje directamente
            elif comando.upper() == "SALIR":
                print("Cerrando el servidor...")
                server.shutdown()
                break
            else:
                print("Comando no reconocido. Use 's:<altura>', 'c:<altura>,<diámetro>' o 'SALIR'.")
    except KeyboardInterrupt:
        print("\nServidor detenido manualmente.")
    finally:
        server.shutdown()

# Ejecutar el servidor WebSocket en un hilo separado
def start_websocket_server():
    print("Iniciando servidor WebSocket...")
    server.run_forever()

# Ejecutar enviar_comandos en un hilo separado
def start_enviar_comandos():
    print("Iniciando consola de comandos...")
    enviar_comandos()

# Iniciar ambos hilos
websocket_thread = threading.Thread(target=start_websocket_server)
websocket_thread.daemon = True
websocket_thread.start()

comandos_thread = threading.Thread(target=start_enviar_comandos)
comandos_thread.daemon = True
comandos_thread.start()