import streamlit as st
import asyncio
import websockets
import threading
from streamlit_autorefresh import st_autorefresh
import base64


# ================================
# Sección BACKEND: Lógica y WebSocket
# ================================

# Contenedor persistente para el último mensaje recibido.
@st.cache_resource
def get_last_message_container():
    return {"message": "Esperando datos..."}

container = get_last_message_container()

# Función asíncrona que maneja las conexiones entrantes del WebSocket.
async def websocket_handler(websocket):
    print("Cliente conectado")
    try:
        async for message in websocket:
            container["message"] = message  # Actualizamos el último mensaje recibido
            print("Mensaje recibido:", message)
    except websockets.exceptions.ConnectionClosed:
        print("Cliente desconectado")

# Función asíncrona para iniciar el servidor WebSocket.
async def start_websocket_server():
    server = await websockets.serve(websocket_handler, "0.0.0.0", 8765)
    print("Servidor WebSocket corriendo en 0.0.0.0:8765")
    await server.wait_closed()

# Función para ejecutar el servidor en un hilo de fondo.
def run_server():
    asyncio.run(start_websocket_server())

# Iniciar el servidor WebSocket (únicamente una vez).
if "server_started" not in st.session_state:
    threading.Thread(target=run_server, daemon=True).start()
    st.session_state.server_started = True

# ================================
# Sección FRONTEND: Interfaz de Usuario
# ================================

# --- Leer y codificar la imagen (logo) ---
with open("Media/logo.svg", "rb") as image_file:
    logo_bytes = image_file.read()
logo_base64 = base64.b64encode(logo_bytes).decode("utf-8")
logo_data = f"data:image/svg+xml;base64,{logo_base64}"

def render_ui():
    # 1. Inyectar CSS para el fondo y el header
    st.markdown(
        """
        <style>
        [data-testid="stHeader"] {
            display: none;
        }

        /* Quitar el fondo predeterminado de Streamlit y eliminar márgenes */
        .stApp {
            background-color: #525a80 !important;
            margin: 0;
            padding: 0;
        }
        
        /* Header personalizado */
        .custom-header {
            background-color: #5271ff;
            padding: 1rem;
            border-radius: 0 0 30px 30px; /* mayor redondeo en la parte inferior */
            color: white;
            font-size: 1.0rem;
            font-weight: bold;
            display: flex;
            align-items: center;
            justify-content: space-between; /* Separa la sección izquierda y derecha */
            position: fixed;
            top: 50px;
            left: 0;
            width: 100%;
            z-index: 10;
        }
        
        /* Sección izquierda del header (logo + texto) */
        .header-left {
            display: flex;
            align-items: center;
        }
        
        .header-text {
            font-size: 2.5rem; /* Ajusta el tamaño según lo necesites */
            font-family: 'Montserrat', sans-serif; /* Cambia la fuente si lo deseas */
            margin-left: 10px;
        }
        
        .custom-header img {
            width: 50px; /* Ajusta el tamaño del logo según necesites */
            margin-right: 5px;
        }
        
        /* Sección de botones del header */
        .header-buttons {
            display: flex;
            gap: 0.5rem;
        }
        
        .icon-button {
            background: none;
            border: none;
            cursor: pointer;
            font-size: 2rem;
            color: white;
        }
        
        .icon-button:hover {
            opacity: 0.8;
        }
        
        /* Agregar margen superior al contenido para que no quede tapado por el header */
        .main-content {
            margin-top: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 2. Insertar el header con HTML (usando f-string para interpolar logo_data)
    st.markdown(
        f"""
        <div class="custom-header">
                <div class="header-left">
                    <img src="{logo_data}" alt="Logo Level Sense"/>
                    <span class="header-text">Level Sense</span>
            </div>
            <div class="header-buttons">
                <button class="icon-button" title="Editar">✏️</button>
                <button class="icon-button" title="Agregar">➕</button>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Contenido principal (con margen superior para no quedar oculto por el header)
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    st.title("Monitor de Nivel de Líquido 🚰")
    st.write("Recibiendo datos desde el ESP32 en tiempo real.")

    # Forzar la actualización de la interfaz cada 2 segundos.
    st_autorefresh(interval=2000, limit=0, key="datarefresh")

    st.subheader("Nivel Actual:")
    st.write("📊 Valor del sensor aquí")  # Aquí se mostrará el dato recibido
    st.markdown('</div>', unsafe_allow_html=True)

# Ejecutar la función de la interfaz.
render_ui()