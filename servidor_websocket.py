from websocket_server import WebsocketServer

# Función que se ejecuta cuando un cliente se conecta
def new_client(client, server):
    print(f"Cliente conectado: {client['id']}")

# Función que se ejecuta cuando se recibe un mensaje
def message_received(client, server, message):
    print(f"Mensaje recibido: {message}")

# Crear el servidor WebSocket
server = WebsocketServer(host="0.0.0.0", port=8765)
server.set_fn_new_client(new_client)
server.set_fn_message_received(message_received)

print("Servidor WebSocket corriendo en 0.0.0.0:8765")
server.run_forever()