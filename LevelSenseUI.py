import sys
import asyncio
import websockets
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QGraphicsDropShadowEffect, QProgressBar
from PyQt5.QtGui import QPixmap, QFont, QColor
from PyQt5.QtCore import Qt

class ModernWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Configurar título
        self.setWindowTitle("Level Sense IU")
        
        # Ajustar tamaño inicial y permitir redimensionamiento
        self.setMinimumSize(800, 600)
        self.resize(1200, 700)
        
        # Widget central
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: #435585;")  # Cambiar color de fondo
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)  # Margen respecto a los bordes
        central_widget.setLayout(main_layout)
        
        # Crear Header
        self.header = QWidget()
        self.header.setFixedHeight(80)  # Altura del header
        self.header.setStyleSheet("""
            background-color: #363062;
            border-radius: 10px;
        """)
        
        # Sombra para el header
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 3)
        self.header.setGraphicsEffect(shadow)
        
        # Layout del header
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 10, 20, 10)
        self.header.setLayout(header_layout)
        
        # Logo
        self.logo = QLabel()
        pixmap = QPixmap("./Media/logo.png").scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.logo.setPixmap(pixmap)
        self.logo.setFixedSize(60, 60)
        
        # Texto del título
        self.title = QLabel("Level Sense")
        self.title.setFont(QFont("Roboto", 26, QFont.Bold))
        self.title.setStyleSheet("color: #D8DEE9;")
        
        # Agregar elementos al header
        header_layout.addWidget(self.logo)
        header_layout.addSpacing(10)
        header_layout.addWidget(self.title)
        header_layout.addStretch()
        
        # Agregar header al layout principal
        main_layout.addWidget(self.header)
        main_layout.addSpacing(20)  # Espacio entre header y contenido
        
        # Layout de contenido con dos secciones (30/70)
        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)
        
        # Sección izquierda (30%)
        self.left_section = QVBoxLayout()
        
        for i in range(3):
            block = QWidget()
            block.setStyleSheet("background-color: #7886C7; border-radius: 10px;")
            block_layout = QVBoxLayout()
            
            # Aplicar sombra
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(10)
            shadow.setColor(QColor(0, 0, 0, 150))
            shadow.setOffset(0, 3)
            block.setGraphicsEffect(shadow)
            
            if i == 0:
                inner_layout = QHBoxLayout()
                
                # Crear los tres bloques internos con valores iniciales en 0
                self.values = {
                    "Volumen": "0 L",
                    "Porcentaje": "0%",
                    "Altura": "0 m"
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
                    
                    self.labels[title] = label_value  # Guardar referencia
                    
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
        
        # Aplicar sombra
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(0, 3)
        self.right_section.setGraphicsEffect(shadow)
        
        self.right_section.setLayout(right_layout)
        
        content_layout.addWidget(left_widget, 30)
        content_layout.addWidget(self.right_section, 70)
        
        main_layout.addStretch()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernWindow()
    window.show()
    sys.exit(app.exec_())
