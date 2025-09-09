from utils import Singleton
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QTabWidget

from gui.tabs import ConfigTab, ExecTab, ResTab

@Singleton
class App(QMainWindow):
    def __init__(self, titleApp = "App"):
        super().__init__()
        
        self.setWindowTitle(titleApp)
        self.setGeometry(100,100,1000,700)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(0)
        
         # Título principal
        title = QLabel("Configuração de Serviços")
        title.setObjectName("title")
        main_layout.addWidget(title)
        
        # Área principal com abas
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Aba de configuração
        self.config_tab = ConfigTab()
        self.tab_widget.addTab(self.config_tab, "Configuração")
              
        # Aba de verificação (placeholder)
        self.execution_tab = ExecTab()
        self.tab_widget.addTab(self.execution_tab, "Executar Serviços")
        
        # Aba de resultado
        self.result_tab = ResTab()
        self.tab_widget.addTab(self.result_tab, "Resultados")
        
        return