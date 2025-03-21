import sys
import asyncio
import websockets
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout,QMessageBox, QHBoxLayout, QGraphicsDropShadowEffect, QProgressBar, QPushButton, QDialog, QLineEdit, QFormLayout
from PyQt5.QtGui import QPixmap, QFont, QColor
from PyQt5.QtGui import QDoubleValidator
import math
from PyQt5.QtCore import Qt, QTimer
import threading
import json

# ========================== BACKEND - WEBSOCKET ==========================
class WebSocketServer:
    def __init__(self, ui_callback):
        """Inicializa el servidor WebSocket en un hilo separado"""
        self.ui_callback = ui_callback  # Función para actualizar la UI
        self.thread = threading.Thread(target=self.run_server, daemon=True)
        self.thread.start()

    def run_server(self):
        """Ejecuta el servidor WebSocket en segundo plano"""
        asyncio.run(self.websocket_server())

    async def websocket_server(self):
        """Lógica de comunicación WebSocket"""
        async def websocket_handler(websocket):
            async for message in websocket:
                try:
                    parsed = json.loads(message)
                    altura = float(parsed[0]) if len(parsed) > 0 else 0.0
                except (json.JSONDecodeError, ValueError, IndexError):
                    altura = 0.0

                # Llama a la función de actualización de UI
                self.ui_callback(altura)

        server = await websockets.serve(websocket_handler, "0.0.0.0", 8765)
        print("Servidor WebSocket corriendo en 0.0.0.0:8765")
        await server.wait_closed()


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
                self.altura_maxima = altura
                self.diametro = diametro
                self.volumen_maximo = math.pi * ((diametro / 2) ** 2) * altura
                self.altura_error.setStyleSheet("color: green;")
                self.altura_error.setText("Valores guardados correctamente.")
                self.accept()
        except ValueError:
            self.altura_error.setText("Error: Ingrese solo números válidos.")
            self.diametro_error.setText("Error: Ingrese solo números válidos.")


class ModernWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.diametro = 0  # Definir atributo antes de usarlo
        self.altura_maxima = 0

        def abrir_dialogo(self):
            dialogo = CustomDialog(self.altura_maxima or 0, self.diametro or 0)
            if dialogo.exec_():  # Espera a que se cierre el diálogo
                self.diametro = dialogo.diametro
                self.altura_maxima = dialogo.altura_maxima
                print(f"Nuevos valores en ModernWindow: Altura={self.altura_maxima}, Diámetro={self.diametro}")
        abrir_dialogo(self)
        
        # Configuración de la ventana principal
        self.setWindowTitle("Level Sense IU")
        self.setMinimumSize(800, 600)
        self.resize(1200, 700)

        # Crear interfaz gráfica
        self.setup_ui()

        # Iniciar WebSocket en segundo plano
        self.websocket_server = WebSocketServer(self.update_values)
    
    def show_dialog(self):
        dialog = CustomDialog(self.altura_maxima, self.diametro)
        if dialog.exec_() == QDialog.Accepted:
            print(f"Nuevos valores recibidos: Altura={dialog.altura_maxima}, Diámetro={dialog.diametro}")
            self.altura_maxima = dialog.altura_maxima
            self.diametro = dialog.diametro
            self.actualizar_calculos()  # Asegura que la UI refleje los nuevos valores

    def update_values(self, altura):
        """Se llama cuando llega un nuevo valor desde WebSocket"""
        self.altura_actual = altura
        self.actualizar_calculos()  # Recalcula volumen y porcentaje

    def actualizar_calculos(self):
        self.volumen_maximo = math.pi * (self.diametro / 2) ** 2 * self.altura_maxima
        volumen_actual = math.pi * (self.diametro / 2) ** 2 * self.altura_actual
        porcentaje = (volumen_actual / self.volumen_maximo) * 100 if self.volumen_maximo > 0 else 0

        print(f"Actualizando UI: Volumen={volumen_actual}, Porcentaje={porcentaje}, Altura={self.altura_actual}")

        if hasattr(self, "labels") and all(k in self.labels for k in ["Volumen", "Porcentaje", "Altura"]):
            self.labels["Volumen"].setText(f"{volumen_actual:.1f} L")
            self.labels["Porcentaje"].setText(f"{porcentaje:.1f}%")
            self.labels["Altura"].setText(f"{self.altura_actual:.1f} cm")
            self.repaint()  # Forzar actualización de la UI
        
    def setup_ui(self):
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
                progress_container.addSpacing(10)
                progress_container.addLayout(empty_layout)
                
                block_layout.addLayout(progress_container)
            
            block.setLayout(block_layout)
            self.left_section.addWidget(block)

        left_widget = QWidget()
        left_widget.setLayout(self.left_section)

        # Sección derecha (70%)
        self.right_section = QWidget()
        self.right_section.setStyleSheet("background-color: #7886C7; border-radius: 10px;")
        right_layout = QVBoxLayout()

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 3)
        self.right_section.setGraphicsEffect(shadow)

        self.right_section.setLayout(right_layout)

        content_layout.addWidget(left_widget, 30)
        content_layout.addWidget(self.right_section, 70)

        main_layout.addStretch()

    def update_values(self, altura):
        """Calcula y actualiza la UI con los valores recibidos"""
        volumen = math.pi * (self.diametro / 2) ** 2 * altura
        porcentaje = (altura / self.altura_maxima) * 100

        self.labels["Volumen"].setText(f"{volumen:.2f} L")
        self.labels["Porcentaje"].setText(f"{porcentaje:.1f}%")
        self.labels["Altura"].setText(f"{altura:.1f} cm")

        QApplication.processEvents()  # Asegurar actualización en la UI
    
    def show_dialog(self):
        dialog = CustomDialog(self.altura_maxima, self.diametro)
        dialog.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernWindow()
    window.show()
    sys.exit(app.exec_())