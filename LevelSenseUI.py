import sys
import math
import random
import json
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QMessageBox, QHBoxLayout,
    QGraphicsDropShadowEffect, QProgressBar, QPushButton, QDialog, QLineEdit, QFormLayout, QComboBox
)
from PyQt5.QtGui import QPixmap, QFont, QColor, QDoubleValidator
from PyQt5.QtCore import Qt, QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from websocket_server import WebsocketServer
import threading

# ========================== BACKEND - WEBSOCKET ==========================


# Función que se ejecuta cuando un cliente se conecta
def new_client(client, server):
    print(f"Cliente conectado: {client['id']}")

# Función que se ejecuta cuando se recibe un mensaje
def message_received(client, server, message):
    print(f"R: {message}")

# Crear el servidor WebSocket
def start_websocket_server():
    server = WebsocketServer(host="0.0.0.0", port=8765)
    server.set_fn_new_client(new_client)
    server.set_fn_message_received(message_received)
    print("Servidor WebSocket corriendo en 0.0.0.0:8765")
    server.run_forever()

# Iniciar el servidor WebSocket en un hilo separado
websocket_thread = threading.Thread(target=start_websocket_server, daemon=True)
websocket_thread.start()


# ========================== FRONTEND - INTERFAZ GRÁFICA ==========================

class CustomDialog(QDialog):
    def __init__(self, altura_maxima, diametro):
        super().__init__()
        self.setWindowTitle("Modificar Contenedor")
        self.setFixedSize(400, 280)
        self.setStyleSheet("background-color: #435585; border-radius: 10px;")
        
        self.altura_maxima = altura_maxima
        self.diametro = diametro
        
        layout = QVBoxLayout()
        form_layout = QFormLayout()
        
        label_style = "font-weight: bold; font-size: 14px; color: white;"
        input_style = "background-color: white; border-radius: 8px; padding: 6px; font-size: 14px;"
        button_style = "background-color: #2D336B; color: white; border-radius: 8px; padding: 10px; font-size: 16px;"
        error_style = "color: red; font-size: 12px;"
        success_style = "color: green; font-size: 12px;"
        
        # Altura
        self.altura_label = QLabel("Altura Máxima (cm):")
        self.altura_label.setStyleSheet(label_style)
        self.altura_input = QLineEdit(str(self.altura_maxima))
        self.altura_input.setStyleSheet(input_style)
        self.altura_error = QLabel("")
        self.altura_error.setStyleSheet(error_style)
        
        # Diámetro
        self.diametro_label = QLabel("Diámetro (cm):")
        self.diametro_label.setStyleSheet(label_style)
        self.diametro_input = QLineEdit(str(self.diametro))
        self.diametro_input.setStyleSheet(input_style)
        self.diametro_error = QLabel("")
        self.diametro_error.setStyleSheet(error_style)
        
        # Agregar widgets
        form_layout.addRow(self.altura_label, self.altura_input)
        form_layout.addRow("", self.altura_error)
        form_layout.addRow(self.diametro_label, self.diametro_input)
        form_layout.addRow("", self.diametro_error)
        
        # Botón
        self.submit_button = QPushButton("Guardar")
        self.submit_button.setStyleSheet(button_style)
        self.submit_button.clicked.connect(self.guardar_valores)
        
        layout.addLayout(form_layout)
        layout.addWidget(self.submit_button)
        self.setLayout(layout)
    
    def guardar_valores(self):
        altura_text = self.altura_input.text()
        diametro_text = self.diametro_input.text()
        
        
        try:
            altura = float(altura_text)
            diametro = float(diametro_text)
            
            if not (0 < altura <= 500):
                self.altura_error.setText("Error: Altura fuera de rango (0-500 cm)")
            else:
                self.altura_error.setText("")
            
            if not (0 < diametro <= 200):
                self.diametro_error.setText("Error: Diámetro fuera de rango (0-200 cm)")
            else:
                self.diametro_error.setText("")
            
            if 0 < altura <= 500 and 0 < diametro <= 200:
                # Calcular el volumen máximo
                self.volumen_maximo = math.pi * ((diametro / 2) ** 2) * altura / 1000  # Convertir de cm³ a L
                self.altura_maxima = altura
                self.diametro = diametro

                 # Imprimir los valores calculados en la consola
                print(f"Altura máxima: {self.altura_maxima} cm")
                print(f"Diámetro: {self.diametro} cm")
                print(f"Volumen máximo: {self.volumen_maximo:.2f} L")
                
                # Mostrar mensaje de éxito
                self.altura_error.setStyleSheet("color: green;")
                self.altura_error.setText("Valores guardados correctamente.")
                self.accept()
        except ValueError:
            self.altura_error.setText("Error: Ingrese solo números válidos.")
            self.diametro_error.setText("Error: Ingrese solo números válidos.")


class ModernWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.diametro = 0
        self.altura_maxima = 0
        self.volumen_maximo = 0

        # Configuración de la ventana principal
        self.setWindowTitle("Level Sense IU")
        self.setMinimumSize(800, 600)
        self.resize(1200, 700)

        # Crear interfaz gráfica
        self.setup_ui()

        # Ejecutar diálogo inicial
        self.abrir_dialogo()

    def abrir_dialogo(self):
        """Abre el diálogo para configurar el contenedor."""
        dialogo = CustomDialog(self.altura_maxima or 0, self.diametro or 0)
        if dialogo.exec_():  # Espera a que se cierre el diálogo
            self.diametro = dialogo.diametro
            self.altura_maxima = dialogo.altura_maxima
            self.volumen_maximo = dialogo.volumen_maximo
            print(f"Nuevos valores en ModernWindow: Altura={self.altura_maxima}, Diámetro={self.diametro}, Volumen={self.volumen_maximo}")

    def show_dialog(self):
        """Muestra el diálogo para editar los valores del contenedor."""
        dialog = CustomDialog(self.altura_maxima, self.diametro)
        if dialog.exec_() == QDialog.Accepted:
            # Actualizar los valores máximos desde el diálogo
            self.altura_maxima = dialog.altura_maxima
            self.diametro = dialog.diametro
            self.volumen_maximo = (math.pi * ((self.diametro / 2) ** 2) * self.altura_maxima) / 1000  # Convertir de cm³ a L
            print(f"Nuevos valores recibidos: Altura={self.altura_maxima} cm, Diámetro={self.diametro} cm, Volumen Máximo={self.volumen_maximo:.2f} L")

    def setup_ui(self):
        pass  # Mantener el método setup_ui como está en el código original
        """Configura la interfaz gráfica"""
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: #435585;")  
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        central_widget.setLayout(main_layout)

        # Header
        self.header = QWidget()
        self.header.setFixedHeight(80)
        self.header.setStyleSheet("background-color: #363062; border-radius: 10px;")

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 3)
        self.header.setGraphicsEffect(shadow)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 10, 20, 10)
        self.header.setLayout(header_layout)

        # Logo
        self.logo = QLabel()
        pixmap = QPixmap("./Media/logo.png").scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.logo.setPixmap(pixmap)
        self.logo.setFixedSize(60, 60)

        # Título
        self.title = QLabel("Level Sense")
        self.title.setFont(QFont("Roboto", 26, QFont.Bold))
        self.title.setStyleSheet("color: #D8DEE9;")

        # Botón para abrir el diálogo
        self.open_dialog_button = QPushButton("Editar")
        self.open_dialog_button.setFont(QFont("roboto", 16))
        self.open_dialog_button.setFixedSize(100, 60)
        self.open_dialog_button.setStyleSheet("""
            background-color: #2D336B;
            color: white;
            border: 3px solid #1E2749;
            border-radius: 10px;
        """)
        self.open_dialog_button.clicked.connect(self.show_dialog)
        # Agregar elementos al header
        header_layout.addWidget(self.logo)
        header_layout.addSpacing(10)
        header_layout.addWidget(self.title)
        header_layout.addStretch()
        header_layout.addWidget(self.open_dialog_button)

        # Agregar header al layout principal
        main_layout.addWidget(self.header)
        main_layout.addSpacing(20)  # Espacio entre header y contenido

        # Layout de contenido
        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)

        # Sección izquierda (30%)
        self.left_section = QVBoxLayout()

        for i in range(3):
            block = QWidget()
            block.setStyleSheet("background-color: #7886C7; border-radius: 10px;")
            block_layout = QVBoxLayout()

            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(10)
            shadow.setColor(QColor(0, 0, 0, 150))
            shadow.setOffset(0, 3)
            block.setGraphicsEffect(shadow)

            if i == 0:
                inner_layout = QHBoxLayout()

                # Inicializar valores
                self.values = {
                    "Volumen": "0 L",
                    "Porcentaje": "0%",
                    "Altura": "0 cm"
                }

                self.labels = {}

                for title in self.values:
                    sub_block = QWidget()
                    sub_block.setStyleSheet("background-color: #B0B7E3; border-radius: 10px;")
                    sub_layout = QVBoxLayout()

                    label_title = QLabel(title)
                    label_title.setFont(QFont("Roboto", 12))
                    label_title.setStyleSheet("color: black;")

                    label_value = QLabel(self.values[title])
                    label_value.setFont(QFont("Roboto", 18, QFont.Bold))
                    label_value.setStyleSheet("color: black;")

                    self.labels[title] = label_value  

                    sub_layout.addWidget(label_title, alignment=Qt.AlignCenter)
                    sub_layout.addWidget(label_value, alignment=Qt.AlignCenter)
                    sub_block.setLayout(sub_layout)

                    inner_layout.addWidget(sub_block)

                block_layout.addLayout(inner_layout)
            elif i == 1:
                # Contenedor de barras de progreso
                progress_container = QHBoxLayout()
                
                # Contenedor de llenado
                fill_layout = QVBoxLayout()
                self.label_llenando = QLabel("Llenando")
                self.label_llenando.setFont(QFont("Roboto", 12))
                self.label_llenando.setStyleSheet("color: black;")
                self.fill_progress = QProgressBar()
                self.fill_progress.setStyleSheet("""
                    QProgressBar {
                        border: 2px solid black;
                        border-radius: 5px;
                        background-color: gray;
                        text-align: center;
                    }
                    QProgressBar::chunk {
                        background-color: #2D336B;
                        width: 20px;
                    }
                """)
                fill_layout.addWidget(self.label_llenando, alignment=Qt.AlignCenter)
                fill_layout.addWidget(self.fill_progress)
                
                # Contenedor de vaciado
                empty_layout = QVBoxLayout()
                self.label_vaciando = QLabel("Vaciando")
                self.label_vaciando.setFont(QFont("Roboto", 12))
                self.label_vaciando.setStyleSheet("color: black;")
                self.empty_progress = QProgressBar()
                self.empty_progress.setInvertedAppearance(True)
                self.empty_progress.setStyleSheet("""
                    QProgressBar {
                        border: 2px solid black;
                        border-radius: 5px;
                        background-color: gray;
                        text-align: center;
                    }
                    QProgressBar::chunk {
                        background-color: #2D336B;
                        width: 20px;
                    }
                """)
                empty_layout.addWidget(self.label_vaciando, alignment=Qt.AlignCenter)
                empty_layout.addWidget(self.empty_progress)
                
                progress_container.addLayout(fill_layout)
                progress_container.addSpacing(30)
                progress_container.addLayout(empty_layout)
                
                block_layout.addLayout(progress_container)
            elif i == 2:  # Bloque vacío
                # Crear un QLabel para el bloque vacío
                empty_label = QLabel("Ingrese un nuevo nivel de llenado")
                empty_label.setFont(QFont("Roboto", 12))
                empty_label.setStyleSheet("color: Black;")
                empty_label.setAlignment(Qt.AlignCenter)
                block_layout.addWidget(empty_label)

                # Crear un layout horizontal para el input y el selector
                input_selector_layout = QHBoxLayout()
                input_selector_layout.setContentsMargins(20, 0, 20, 0)  # Espaciado interno

                # Crear el input numérico
                self.numeric_input = QLineEdit()
                self.numeric_input.setPlaceholderText("Nivel de llenado")
                self.numeric_input.setValidator(QDoubleValidator())  # Solo permite números
                self.numeric_input.setStyleSheet("""
                    QLineEdit {
                        background-color: white;
                        border: 2px solid #000;
                        border-radius: 10px;
                        padding: 5px;
                        font-size: 14px;
                    }
                """)
                input_selector_layout.addWidget(self.numeric_input)

                # Crear el selector con 3 opciones
                self.selector = QComboBox()
                self.selector.addItem("     ▼")
                self.selector.addItems(["     L", "     cm", "     %"])
                self.selector.setItemData(0, 0, Qt.UserRole - 1)  # Deshabilitar la primera opción
                self.selector.setStyleSheet("""
                QComboBox {
                    background-color: white;
                    border: 2px solid #000;
                    border-radius: 10px;
                    padding: 5px;
                    font-size: 14px;
                }
                QComboBox::drop-down {
                    border: none;
                    background-color: transparent;
                }
                QComboBox QAbstractItemView {
                    background-color: white;
                    border: 1px solid black;
                    selection-background-color: #D3D3D3;
                    selection-color: black;
                }
            """)
                input_selector_layout.addWidget(self.selector)

                # Agregar el layout horizontal al bloque
                block_layout.addLayout(input_selector_layout)

                # Crear el botón de enviar
                send_button = QPushButton("Enviar")
                send_button.setStyleSheet("""
                    QPushButton {
                        background-color: #435585;
                        color: black;
                        border-radius: 10px;
                        padding: 10px;
                        font-size: 16px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #5a6a9c;
                    }
                """)
                block_layout.addWidget(send_button, alignment=Qt.AlignCenter)

                # Conectar el botón a la función enviar_datos
                send_button.clicked.connect(self.enviar_datos)

            block.setLayout(block_layout)
            self.left_section.addWidget(block)
            # Agregar espaciado vertical entre los bloques
            if i < 2:  # No agregar espaciado después del último bloque
                self.left_section.addSpacing(30)  # Ajusta el valor para más o menos espaciado

        left_widget = QWidget()
        left_widget.setLayout(self.left_section)

        # Sección derecha (70%)
        self.right_section = QVBoxLayout()

        # Crear un contenedor para la gráfica similar a los bloques de la izquierda
        graph_block = QWidget()
        graph_block.setStyleSheet("background-color: #7886C7; border-radius: 10px;")
        graph_block_layout = QVBoxLayout()

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 3)
        graph_block.setGraphicsEffect(shadow)

        # Crear un layout horizontal para el título y el menú
        title_menu_layout = QHBoxLayout()

        # Crear un label como título para la gráfica
        self.dynamic_title_label = QLabel("Altura")
        self.dynamic_title_label.setFont(QFont("Roboto", 16, QFont.Bold))
        self.dynamic_title_label.setStyleSheet("color: white;")
        self.dynamic_title_label.setAlignment(Qt.AlignLeft)

        # Crear un menú de selección (QComboBox)
        unit_menu = QComboBox()
        unit_menu.addItems(["cm", "L", "%"])
        unit_menu.setStyleSheet("""
            QComboBox {
            background-color: white;
            border: 2px solid #000;
            border-radius: 10px;
            padding: 5px;
            font-size: 14px;
            }
            QComboBox::drop-down {
            border: none;
            background-color: transparent;
            }
            QComboBox QAbstractItemView {
            background-color: white;
            border: 1px solid black;
            selection-background-color: #D3D3D3;
            selection-color: black;
            }
        """)

        # Conectar el cambio de selección del menú al cambio de texto del título
        def actualizar_titulo(index):
            opciones = ["Altura", "Volumen", "Porcentaje"]
            self.dynamic_title_label.setText(opciones[index])

        unit_menu.currentIndexChanged.connect(actualizar_titulo)

        # Agregar el título y el menú al layout horizontal
        title_menu_layout.addWidget(self.dynamic_title_label, alignment=Qt.AlignLeft)
        title_menu_layout.addStretch()  # Agregar espacio flexible entre el título y el menú
        title_menu_layout.addWidget(unit_menu, alignment=Qt.AlignRight)

        # Agregar el layout horizontal al bloque de la gráfica
        graph_block_layout.addLayout(title_menu_layout)

        # Crear la gráfica
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlim(-100, 0)  # Tiempo en el eje X
        self.ax.set_ylim(0, 1)  # Se ajustará dinámicamente
        self.ax.set_xlabel("Tiempo (s)")
        self.ax.set_ylabel("Altura (cm)")
        self.line, = self.ax.plot([], [], color="blue", alpha=0.6)
        self.fill = self.ax.fill_between([], [], color="cyan", alpha=0.3)

        # Inicializar datos para la gráfica
        self.data = {
            "time": np.linspace(-100, 0, 100),
            "values": np.zeros(100)
        }

        # Agregar la gráfica al bloque
        graph_layout = QVBoxLayout()
        graph_layout.setContentsMargins(0, 0, 0, 0)  # Eliminar márgenes
        graph_layout.addWidget(self.canvas)
        graph_block_layout.addLayout(graph_layout)

        # Establecer el layout del bloque de la gráfica
        graph_block.setLayout(graph_block_layout)

        # Agregar el bloque de la gráfica a la sección derecha
        self.right_section.addWidget(graph_block)

        # Conectar el cambio de selección del menú al cambio de gráfica
        unit_menu.currentIndexChanged.connect(self.actualizar_grafica)

        # Iniciar un temporizador para actualizar la gráfica cada segundo
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.actualizar_grafica(unit_menu.currentText().strip()))
        self.timer.start(1000)  # Actualizar cada segundo

        # Agregar las secciones izquierda y derecha al layout de contenido
        content_layout.addWidget(left_widget, 30)
        content_layout.addLayout(self.right_section, 70)
        main_layout.addStretch()

    def actualizar_grafica(self, unidad):
        """Actualiza la gráfica y los valores según la unidad seleccionada"""
        # Ajustar el eje Y según la unidad seleccionada
        if unidad == "cm":  # Altura
            if self.altura_maxima > 0:
                self.ax.set_ylim(0, self.altura_maxima)
            else:
                self.ax.set_ylim(0, 1)  # Valor predeterminado
            self.ax.set_ylabel("Altura (cm)")
        elif unidad == "L":  # Volumen
            if self.volumen_maximo > 0:
                self.ax.set_ylim(0, self.volumen_maximo)
            else:
                self.ax.set_ylim(0, 1)  # Valor predeterminado
            self.ax.set_ylabel("Volumen (L)")
        elif unidad == "%":  # Porcentaje
            self.ax.set_ylim(0, 100)
            self.ax.set_ylabel("Porcentaje (%)")

        # Generar un nuevo valor para la variable mensaje
        mensaje = self.generar_valor_mensaje()

        # Convertir el valor de mensaje según la unidad seleccionada
        if unidad == "L":  # Convertir volumen a altura
            nuevo_valor = (mensaje * 1000) / (math.pi * ((self.diametro / 2) ** 2))
        elif unidad == "%":  # Convertir porcentaje a altura
            nuevo_valor = (mensaje / 100) * self.altura_maxima
        else:  # Altura directamente
            nuevo_valor = mensaje

        # Actualizar los valores de la gráfica
        self.data["values"] = np.roll(self.data["values"], -1)  # Desplazar los datos
        self.data["values"][-1] = nuevo_valor  # Agregar el nuevo valor al final

        # Actualizar los datos de la gráfica
        self.line.set_data(self.data["time"], self.data["values"])
        if self.fill:
            self.fill.remove()  # Eliminar el área anterior si existe
        self.fill = self.ax.fill_between(self.data["time"], self.data["values"], color="cyan", alpha=0.3)

        # Redibujar la gráfica
        self.canvas.draw()
        
    def generar_valor_mensaje(self):
            """Genera un valor aleatorio para la variable mensaje"""
            if self.selector.currentText().strip() == "cm":  # Altura
                return random.uniform(0, self.altura_maxima)
            elif self.selector.currentText().strip() == "L":  # Volumen
                return random.uniform(0, self.volumen_maximo)
            elif self.selector.currentText().strip() == "%":  # Porcentaje
                return random.uniform(0, 100)
            return 0.0   
    
    # Función para manejar el evento del botón
    def enviar_datos(self):
        # Obtener el valor del input numérico
        nivel_text = self.numeric_input.text()
        # Obtener la opción seleccionada del selector
        unidad = self.selector.currentText().strip()

        # Validar que se haya ingresado un nivel
        if not nivel_text:
            QMessageBox.warning(self, "Error", "Por favor, ingrese un nivel de llenado.")
            return

        try:
            # Convertir el nivel a un número flotante
            nivel = float(nivel_text)

            # Validar que el nivel no sea negativo
            if nivel < 0:
                QMessageBox.warning(self, "Error", "El nivel de llenado no puede ser negativo.")
                return

            # Validar según la unidad seleccionada
            if unidad == "L":  # Volumen
                if nivel > self.volumen_maximo:
                    QMessageBox.warning(
                        self,
                        "Error",
                        f"El volumen no puede exceder el máximo permitido ({self.volumen_maximo:.1f} L)."
                    )
                    return
                altura_calculada = (nivel * 1000) / (math.pi * ((self.diametro / 2) ** 2))

            elif unidad == "cm":  # Altura
                if nivel > self.altura_maxima:
                    QMessageBox.warning(
                        self,
                        "Error",
                        f"La altura no puede exceder la altura máxima del contenedor ({self.altura_maxima:.1f} cm)."
                    )
                    return
                altura_calculada = nivel
            elif unidad == "%":  # Porcentaje
                if nivel > 100:
                    QMessageBox.warning(
                        self,
                        "Error",
                        "El porcentaje no puede exceder el 100%."
                    )
                    return
                altura_calculada = (nivel / 100) * self.altura_maxima
            else:
                QMessageBox.warning(self, "Error", "Por favor, seleccione una unidad válida.")
                return
            # Imprimir la altura calculada en la consola
            print(f"Altura calculada: {altura_calculada:.2f} cm")

        except ValueError:
            QMessageBox.warning(self, "Error", "Por favor, ingrese un número válido.")
            return

        # Procesar los datos (puedes personalizar esta parte)
        QMessageBox.information(self, "Datos enviados", f"Nuevo Nivel: {altura_calculada:.2f} cm", QMessageBox.Ok, QMessageBox.Ok)
        print(f"Altura calculada enviada: {altura_calculada:.2f} cm")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernWindow()
    window.show()
    sys.exit(app.exec_())