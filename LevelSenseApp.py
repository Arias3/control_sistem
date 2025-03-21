import streamlit as st
import asyncio
import websockets
import threading
import base64
import pandas as pd
import numpy as np
import json
import math
import time
import altair as alt
from streamlit_autorefresh import st_autorefresh

st.set_page_config(layout="wide", page_title="Level Sense")

# Definir un event loop global para el WebSocket
ws_loop = asyncio.new_event_loop()

# ================================
# SECCIÓN BACKEND: Lógica y WebSocket
# ================================
@st.cache_resource
def get_last_message_container():
    return {"message": "[]"}  # Inicializamos con una cadena JSON vacía

container = get_last_message_container()

# Función asíncrona que maneja la conexión y guarda el objeto websocket
async def websocket_handler(websocket):
    print("Cliente conectado")
    st.session_state.ws_connection = websocket  # Guardar la conexión para enviar mensajes
    try:
        async for message in websocket:
            # Se espera que el mensaje sea algo como "[x, y]"
            container["message"] = message
            print("Mensaje recibido:", message)
    except websockets.exceptions.ConnectionClosed:
        print("Cliente desconectado")
        st.session_state.ws_connection = None

async def start_websocket_server():
    server = await websockets.serve(websocket_handler, "0.0.0.0", 8765)
    print("Servidor WebSocket corriendo en 0.0.0.0:8765")
    await server.wait_closed()

def run_server():
    asyncio.set_event_loop(ws_loop)
    ws_loop.run_until_complete(start_websocket_server())

# Inicializar ws_connection en session_state si no existe
if "ws_connection" not in st.session_state:
    st.session_state.ws_connection = None

if "server_started" not in st.session_state:
    threading.Thread(target=run_server, daemon=True).start()
    st.session_state.server_started = True

# Función asíncrona para enviar el nuevo setpoint al ESP en el mismo loop
async def send_command(new_height):
    if st.session_state.ws_connection is None:
        st.error("No hay conexión WebSocket disponible.")
    else:
        try:
            await st.session_state.ws_connection.sendTXT("NEW_HEIGHT:" + str(new_height))
            st.success("Nueva consigna enviada: " + str(new_height) + " cm")
        except Exception as e:
            st.error("Error al enviar nueva consigna: " + str(e))

# ================================
# Cachear el logo para evitar relecturas
# ================================
@st.cache_resource
def load_logo():
    with open("Media/logo.svg", "rb") as image_file:
        logo_bytes = image_file.read()
    logo_base64 = base64.b64encode(logo_bytes).decode("utf-8")
    return f"data:image/svg+xml;base64,{logo_base64}"

logo_data = load_logo()

# ================================
# Inyección de CSS depurado
# ================================
st.markdown(
    """
    <style>
    html, body {
        overflow: hidden !important;
        margin: 0;
        padding: 0;
    }
    [data-testid="stHeader"] {
        display: none;
    }
    .stApp {
        background-color: #525a80 !important;
    }
    /* Header personalizado */
    .custom-header {
        background-color: #5271ff;
        padding: 1rem;
        border-radius: 0 0 30px 30px;
        color: white;
        display: flex;
        align-items: center;
        justify-content: space-between;
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        z-index: 10;
    }
    .header-left {
        display: flex;
        align-items: center;
    }
    .header-text {
        font-size: 2.5rem;
        font-family: 'Montserrat', sans-serif;
        margin-left: 10px;
    }
    .custom-header img {
        width: 50px;
        margin-right: 5px;
    }
    .header-buttons {
        display: flex;
        gap: 0.5rem;
    }
    /* Contenedor para el botón de edición en Sección 1 */
    #custom-btn-container {
        text-align: center;
        margin-bottom: 1rem;
    }
    /* Contenido principal */
    .main-content {
        margin-top: 100px;
        padding: 1rem;
    }
    /* Sección 1: Rectángulos informativos */
    .outer-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    .mini-box {
        background-color: #a0abdc;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        min-width: 80px;
    }
    .mini-box-label {
        font-size: 1rem;
        color: #333;
        margin-bottom: 0.5rem;
    }
    .mini-box-value {
        font-size: 1.5rem;
        color: #000;
    }
    /* Sección 2: Etiquetas para progreso */
    .section2-box {
        text-align: center;
    }
    .section2-label {
        font-size: 1rem;
        color: #333;
    }
    /* Sección 3: Contenedor blanco para inputs */
    
    .section3-label {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .section3-button {
        background-color: #5271ff;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-size: 1.2rem;
        cursor: pointer;
        margin-top: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ================================
# Diálogo de edición para dimensiones del recipiente
# ================================
@st.dialog("Editar Configuración")
def editar_dialog():
    st.write("Por favor, ingresa las dimensiones del recipiente cilíndrico en cm:")
    altura_maxima = st.number_input("Altura máxima del recipiente:", value=30.0, step=1.0, key="dialog_altura", help="Valor en cm")
    diametro = st.number_input("Diámetro del recipiente:", value=10.0, step=1.0, key="dialog_diametro", help="Valor en cm")
    if st.button("Guardar"):
        st.session_state.edited_config = {"altura_maxima": altura_maxima, "diametro": diametro}
        st.success("Configuración actualizada")
        st.session_state["dialog_open"] = False  # Cerrar el diálogo
        st.rerun()

# ================================
# Renderización de la interfaz principal
# ================================
def render_ui():
    # Header personalizado
    st.markdown(
        f"""
        <div class="custom-header">
            <div class="header-left">
                <img src="{logo_data}" alt="Logo Level Sense"/>
                <span class="header-text">Level Sense</span>
            </div>
            <div class="header-buttons">
                <!-- Se pueden agregar otros botones aquí si se desea -->
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Contenido principal
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    left_col, right_col = st.columns([1, 2])
    
    with left_col:
        # Sección 1: Rectángulos informativos con datos calculados
        try:
            parsed = json.loads(container["message"])
            water_level = float(parsed[0])
            actuator_power = float(parsed[1])
        except Exception as e:
            water_level = 0.0
            actuator_power = 0.0
        
        altura_maxima = st.session_state.get("edited_config", {}).get("altura_maxima", 30.0)
        diametro = st.session_state.get("edited_config", {}).get("diametro", 10.0)
        
        percentage = (water_level / altura_maxima * 100) if altura_maxima > 0 else 0
        volume_cm3 = math.pi * ((diametro / 2) ** 2) * water_level
        volume_liters = volume_cm3 / 1000
        
        st.markdown(
            f"""
            <div class="outer-container">
                <div class="mini-box">
                    <div class="mini-box-label">Volumen</div>
                    <div class="mini-box-value">{volume_liters:.1f} L</div>
                </div>
                <div class="mini-box">
                    <div class="mini-box-label">Porcentaje</div>
                    <div class="mini-box-value">{percentage:.1f} %</div>
                </div>
                <div class="mini-box">
                    <div class="mini-box-label">Altura</div>
                    <div class="mini-box-value">{water_level:.1f} cm</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
        # Botón de edición para modificar las dimensiones del recipiente (Sección 1)
        st.markdown("<div id='custom-btn-container'>", unsafe_allow_html=True)
        if st.button("✏️ Editar Configuración", key="editar_btn"):
            st.session_state["dialog_open"] = True
            editar_dialog()
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Sección 2: Actuador (barra de progreso)
        st.markdown("### Potencia de Actuadores")
        vaciado_power = abs(actuator_power) if actuator_power < 0 else 0
        llenado_power = actuator_power if actuator_power > 0 else 0
        col_vaciado, col_llenado = st.columns(2)
        with col_vaciado:
            st.markdown(
                """
                <div class="section2-box">
                    <div class="section2-label">Vaciado</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.progress(int(vaciado_power))
        with col_llenado:
            st.markdown(
                """
                <div class="section2-box">
                    <div class="section2-label">Llenado</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.progress(int(llenado_power))
        
        # Sección 3: Contenedor blanco para ingresar una nueva consigna
       
        st.markdown("<div class='section3-label'>Inserta un nuevo nivel:</div>", unsafe_allow_html=True)
        col_input, col_dropdown = st.columns([2, 1])
        with col_input:
            nuevo_nivel = st.number_input("Nivel", value=0, step=1, key="nuevo_nivel", label_visibility="hidden")
        with col_dropdown:
            unidad = st.selectbox("Unidad", options=["L", "%", "cm"], key="unidad", label_visibility="hidden")        
        if st.button("✅ Enviar Nueva Consigna", key="enviar_btn"):
            # Validar y calcular la nueva altura a enviar al ESP
            if unidad == "%":
                if nuevo_nivel < 0 or nuevo_nivel > 100:
                    st.error("El porcentaje debe estar entre 0 y 100.")
                else:
                    new_height = (nuevo_nivel / 100) * altura_maxima
                    st.info(f"Nueva altura calculada: {new_height:.1f} cm (Porcentaje)")
                    asyncio.run(send_command(new_height))
            elif unidad == "L":
                max_volume = (math.pi * ((diametro / 2.0) ** 2) * altura_maxima) / 1000.0
                if nuevo_nivel < 0 or nuevo_nivel > max_volume:
                    st.error(f"El volumen debe estar entre 0 y {max_volume:.1f} L.")
                else:
                    new_height = (nuevo_nivel * 1000) / (math.pi * ((diametro / 2.0) ** 2))
                    st.info(f"Nueva altura calculada: {new_height:.1f} cm (Volumen)")
                    asyncio.run(send_command(new_height))
            elif unidad == "cm":
                if nuevo_nivel < 0 or nuevo_nivel > altura_maxima:
                    st.error(f"La altura debe estar entre 0 y {altura_maxima} cm.")
                else:
                    new_height = nuevo_nivel
                    st.info(f"Nueva altura calculada: {new_height:.1f} cm (Directo)")
                    asyncio.run(send_command(new_height))
        st.markdown("</div>", unsafe_allow_html=True)
    
    with right_col:
        st.header("Nivel Actual")
        st.write("Histórico de valores:")
        
        if "history" not in st.session_state:
            st.session_state.history = pd.DataFrame(columns=["record_time", "water_level", "percentage", "volume"])
        
        try:
            parsed = json.loads(container["message"])
            water_level = float(parsed[0])
        except Exception as e:
            water_level = 0.0
        
        altura_maxima = st.session_state.get("edited_config", {}).get("altura_maxima", 30.0)
        diametro = st.session_state.get("edited_config", {}).get("diametro", 10.0)
        
        percentage = (water_level / altura_maxima * 100.0) if altura_maxima > 0 else 0
        volume_cm3 = math.pi * ((diametro / 2.0) ** 2) * water_level
        volume_liters = volume_cm3 / 1000.0
        
        current_ts = time.time()
        new_row = pd.DataFrame({
            "record_time": [current_ts],
            "water_level": [water_level],
            "percentage": [percentage],
            "volume": [volume_liters]
        })
        st.session_state.history = pd.concat([st.session_state.history, new_row], ignore_index=True)
        
        history = st.session_state.history.copy()
        history["relative_time"] = history["record_time"].astype(float) - current_ts
        history = history[history["relative_time"] >= -90]
        
        variable = st.selectbox("Selecciona la variable a mostrar:", 
                                ["Volumen", "Porcentaje", "Altura (cm)"])
        st.session_state.selected_variable = variable
        if variable == "Volumen":
            history["value"] = (math.pi * ((diametro / 2.0) ** 2) * history["water_level"]) / 1000.0
            y_label = "Volumen (L)"
            max_y = (math.pi * ((diametro / 2.0) ** 2) * altura_maxima) / 1000.0
        elif variable == "Porcentaje":
            history["value"] = (history["water_level"] / altura_maxima * 100.0) if altura_maxima > 0 else 0
            y_label = "Porcentaje (%)"
            max_y = 100
        else:
            history["value"] = history["water_level"]
            y_label = "Altura (cm)"
            max_y = altura_maxima
        
        history = history.sort_values("relative_time").set_index("relative_time")
        chart = alt.Chart(history.reset_index()).mark_area(opacity=0.5, interpolate='monotone').encode(
            x=alt.X('relative_time:Q', title='Tiempo (s)', scale=alt.Scale(domain=[-90, 0]),
                    axis=alt.Axis(labelAngle=0, format="d")),
            y=alt.Y('value:Q', title=y_label, scale=alt.Scale(domain=[0, max_y]))
        ).properties(
            width=600,
            height=300
        )
        st.altair_chart(chart, use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    if not st.session_state.get("dialog_open", False):
        st_autorefresh(interval=500, limit=0, key="datarefresh")

render_ui()
