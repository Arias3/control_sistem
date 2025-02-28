import streamlit as st
import asyncio
import websockets
import threading
import base64
import pandas as pd
import numpy as np
from streamlit_autorefresh import st_autorefresh

st.set_page_config(layout="wide", page_title="Level Sense")

# ================================
# Sección BACKEND: Lógica y WebSocket
# ================================

@st.cache_resource
def get_last_message_container():
    return {"message": "Esperando datos..."}

container = get_last_message_container()

async def websocket_handler(websocket):
    print("Cliente conectado")
    try:
        async for message in websocket:
            container["message"] = message
            print("Mensaje recibido:", message)
    except websockets.exceptions.ConnectionClosed:
        print("Cliente desconectado")

async def start_websocket_server():
    server = await websockets.serve(websocket_handler, "0.0.0.0", 8765)
    print("Servidor WebSocket corriendo en 0.0.0.0:8765")
    await server.wait_closed()

def run_server():
    asyncio.run(start_websocket_server())

if "server_started" not in st.session_state:
    threading.Thread(target=run_server, daemon=True).start()
    st.session_state.server_started = True

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
# Inyección de CSS
# ================================
st.markdown(
    """
    <style>
    html, body {
        overflow: hidden !important;
    }
    [data-testid="stHeader"] {
        display: none;
    }
    .stApp {
        background-color: #525a80 !important;
        margin: 0;
        padding: 0;
    }
    /* Header personalizado */
    .custom-header {
        background-color: #5271ff;
        padding: 1rem;
        border-radius: 0 0 30px 30px;
        color: white;
        font-size: 1.0rem;
        font-weight: bold;
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
    .main-content {
        margin-top: 20px;
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
    .section3-container {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        margin-bottom: 1rem;
    }
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
    /* Estilos para el contenedor del botón personalizado */
    #custom-btn-container {
        text-align: center; /* Centra su contenido */
        margin-bottom: 1rem; /* Opcional: espacio inferior */
    }
    /* Estilos específicos para el botón dentro de ese contenedor */
    #custom-btn-container button {
        background-color: #007BFF !important; /* Azul; ajusta el tono si lo deseas */
        color: white !important;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ================================
# Sección FRONTEND: Interfaz de Usuario
# ================================

# Definir el diálogo (modal) con un formulario de edición para las dimensiones del recipiente cilíndrico
@st.dialog("Editar Configuración")
def editar_dialog():
    st.write("Por favor, ingresa las dimensiones del recipiente cilíndrico en centimetros:")
    altura_maxima = st.number_input("Altura máxima del recipiente:", value=100.0, step=1.0, key="dialog_altura", help="Ingresa la altura máxima del recipiente")
    diametro = st.number_input("Diámetro del recipiente:", value=50.0, step=1.0, key="dialog_diametro", help="Ingresa el diámetro del recipiente")
    if st.button("Guardar"):
        st.session_state.edited_config = {"altura_maxima": altura_maxima, "diametro": diametro}
        st.success("Configuración actualizada")
        st.session_state["dialog_open"] = False  # Cerrar el diálogo
        st.rerun()


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
                <!-- Aquí podríamos mostrar un icono, pero el botón para editar será un componente Streamlit -->
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    

    # Contenido principal
    st.markdown('<div class="main-content">', unsafe_allow_html=True)

    # División en dos columnas
    left_col, right_col = st.columns([1, 2])

    with left_col:
        # Sección 1: Tres rectángulos informativos
        # Botón de edición en la sección 1 de la columna izquierda
        st.markdown("<div id='custom-btn-container'>", unsafe_allow_html=True)
        if st.button("✏️ Editar Configuración", key="editar_btn"):
            st.session_state["dialog_open"] = True
            editar_dialog()
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            """
            <div class="outer-container">
                <div class="mini-box">
                    <div class="mini-box-label">Volumen</div>
                    <div class="mini-box-value">500 L</div>
                </div>
                <div class="mini-box">
                    <div class="mini-box-label">Porcentaje</div>
                    <div class="mini-box-value">75%</div>
                </div>
                <div class="mini-box">
                    <div class="mini-box-label">Altura</div>
                    <div class="mini-box-value">1.2 m</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


        # Sección 2: Dos rectángulos para barra de progreso
        st.markdown("### Potencia de Actuadores")
        progress_vaciado = 0
        progress_llenado = 100
        col_vaciado, col_llenado = st.columns(2)
        with col_vaciado:
            st.markdown(
                """
                <div class="section2-box">
                    <div class="section2-label">Vaciado</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.progress(progress_vaciado)
        with col_llenado:
            st.markdown(
                """
                <div class="section2-box">
                    <div class="section2-label">Llenado</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.progress(progress_llenado)

        # Sección 3: Contenedor blanco para inputs
        
        st.markdown("<div class='section3-label'>Inserta un nuevo nivel:</div>", unsafe_allow_html=True)
        col_input, col_dropdown = st.columns([2, 1])
        with col_input:
            nuevo_nivel = st.number_input("", value=0, step=1, key="nuevo_nivel", label_visibility="hidden")
        with col_dropdown:
            unidad = st.selectbox("", options=["L", "%", "cm"], key="unidad", label_visibility="hidden")        
        if st.button("✅ Enviar Nueva Consigna", key="enviar_btn"):
            editar_dialog()
        st.markdown("</div>", unsafe_allow_html=True)

    with right_col:
        st.header("Panel Derecho")
        st.write("Aquí se puede mostrar un gráfico o datos históricos.")
        
        # Selector para elegir la variable a mostrar
        variable = st.selectbox("Selecciona la variable a mostrar:", 
                                ["Volumen", "Porcentaje", "Altura (m)"])
        
        # Simulación de datos históricos según la variable seleccionada
        if variable == "Volumen":
            # Ejemplo: Volumen en litros
            data = pd.DataFrame(np.random.randn(20, 1) * 50 + 500, columns=["Volumen (L)"])
        elif variable == "Porcentaje":
            # Ejemplo: Porcentaje (0 a 100)
            data = pd.DataFrame(np.random.rand(20, 1) * 100, columns=["Porcentaje (%)"])
        elif variable == "Altura (m)":
            # Ejemplo: Altura en metros (0 a 2)
            data = pd.DataFrame(np.random.rand(20, 1) * 2, columns=["Altura (m)"])
        
        # Mostrar la gráfica de área
        st.area_chart(data)


    # Llamar a autorefresh solo si NO se está editando
    if not st.session_state.get("dialog_open", False):
        st_autorefresh(interval=2000, limit=0, key="datarefresh")

render_ui()
