from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QApplication, QFrame)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
import sys

class CustomMessageBox(QDialog):
    def __init__(self, title="Aviso", message="", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | 
                            Qt.WindowType.Dialog |
                            Qt.WindowType.CustomizeWindowHint |
                            Qt.WindowType.WindowTitleHint)
        self.setModal(True)
        self.setFixedSize(400, 200)  # Reduzido pois não tem mais ícone
        
        self.setup_ui(message)
        self.setStyleSheet(self.get_stylesheet())
        
        # Auto-close após 5 segundos
        self.timer = QTimer()
        self.timer.timeout.connect(self.accept)
        self.timer.start(5000)
    
    def setup_ui(self, message):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        title_label = QLabel(self.windowTitle())
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            color: #2c3e50;
            font-size: 16px;
            font-weight: bold;
            padding: 5px;
        """)
        
        # Mensagem
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setStyleSheet("""
            color: #34495e;
            font-size: 14px;
            padding: 10px;
            background-color: #f8f9fa;
            border-radius: 5px;
        """)
        
        # Botão OK
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.setFixedSize(100, 40)
        ok_button.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addStretch()
        
        layout.addWidget(title_label)
        layout.addWidget(message_label)
        layout.addStretch()
        layout.addLayout(button_layout)
    
    def get_stylesheet(self):
        return """
            QDialog {
                background-color: #ffffff;
                border: 2px solid #bdc3c7;
                border-radius: 10px;
            }
            
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            
            QPushButton:hover {
                background-color: #2980b9;
            }
            
            QPushButton:pressed {
                background-color: #21618c;
            }
        """
    
    def show_message(self):
        self.exec()
    
    def closeEvent(self, event):
        # Para o timer quando a janela é fechada
        self.timer.stop()
        super().closeEvent(event)

def show_custom_message(title, message, parent=None):
    """Função auxiliar para exibir a mensagem personalizada"""
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    
    msg_box = CustomMessageBox(title, message, parent)
    msg_box.show_message()

# Exemplo de uso
if __name__ == "__main__":
    app = QApplication(sys.argv)
    show_custom_message("Sucesso", "Operação concluída com êxito!")
    sys.exit(app.exec())