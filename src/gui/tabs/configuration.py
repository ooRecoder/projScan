from PySide6.QtWidgets import QWidget, QHBoxLayout
from ..components import ServiceSidebar, ServiceContentArea

class ConfigTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
               
        # Create the main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(16)
        
        # Sidebar com serviços
        self.sidebar = ServiceSidebar()
        main_layout.addWidget(self.sidebar)
        
        # Área de conteúdo
        self.content_area = ServiceContentArea()
        main_layout.addWidget(self.content_area, 1)
        
        # Conectar sinais
        self.sidebar.serviceSelected.connect(self.content_area.show_service)