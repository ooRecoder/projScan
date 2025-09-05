from ast import Dict
from core import AppLogger
import time
from datetime import datetime
from typing import Dict
from utils import Singleton
from .configManager import ConfigManager
from .machines import ComputerManager

@Singleton
class Scanner:
    def __init__(self):
        instance_logger = AppLogger.instance
        instance_cm = ComputerManager.instance
        
        if not instance_cm or not instance_logger:
            raise ImportError("Loggging ou ComputerManager não foi inicializado")
        
        self.config_manager = instance_cm
        self.logger = instance_logger.get_file_path(__name__)
        
    def run(self, save=True):
        from utils import FilePathManager
        fm = FilePathManager.instance
        
        if not fm:
            raise ImportError("FilePathManager não foi inicializado")
        
        results = {}
        enabled_services = self.config_manager.list_services()

        for service_name in enabled_services:
            # pasta dos serviços: services
            # Da para encontrar usando fm.get_file_path("services"): Retorna o caminho absoluto para a pasta 
            # Ou pode referenciar ao serviço logo com fm.get_file_path(f"services/{service_name}")
            
            # Importa o serviço habilitado
            # Pega a classe dentro dele getattr(module, service_name.upper())
            # Pega as opções configuradas com self.config_manager.get_service_config(service_name)
            
            # Passa as options para a classe classe(**options)
            
            # Inicia timer
            # Executa função collect() presente em todo classe de serviço e armazena o resultado que sempre será um dict
            # dict = value: Dict 
            # Finaliza timer
            
            # Calcula tempo de execução
            # Quando foi executada
            # Nome do serviço
            # Retorno de collect
            continue

        return results