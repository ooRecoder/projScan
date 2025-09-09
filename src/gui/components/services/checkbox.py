from PySide6.QtWidgets import QCheckBox
from PySide6.QtCore import Signal

class ServiceCheckBox(QCheckBox):
    """Checkbox personalizado para serviços com sinal de foco"""
    focused = Signal(str)
    
    def enterEvent(self, event):
        self.focused.emit(self.text())
        super().enterEvent(event)