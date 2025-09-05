import json
import os
from typing import Any, Dict
from utils import Singleton
from core.logging import AppLogger
from dotenv import load_dotenv

# Carrega variáveis do .env
load_dotenv()

@Singleton
class AppConfig:
    def __init__(self, config_file: str = "config.json") -> None:
        from utils import FilePathManager
        instance_logger = AppLogger.instance
        self.file_manager = FilePathManager.instance
        
        if not instance_logger or not self.file_manager:
            raise RuntimeError("As instâncias File e Logging não foram inicializadas")
        
        self.logger = instance_logger.get_logger(__name__)
        
        self.config_file = config_file
        self.config_data: Dict[str, Any] = {}
        self._load_config()
        
        self.logger.info("AppConfig Inicializado")
    
    def _load_config(self) -> None:
        """Carrega as configurações do arquivo JSON"""
        if not self.file_manager: return None
        config_path = self.file_manager.get_file_path("config.json")
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as file:
                    self.config_data = json.load(file)
                self.logger.info(f"Configurações carregadas do arquivo: {config_path}")
            else:
                self.logger.warning(f"Arquivo de configuração {config_path} não encontrado. Criando configuração padrão.")
                self._create_default_config()
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Erro ao decodificar JSON do arquivo de configuração: {e}")
        except Exception as e:
            self.logger.error(f"Erro ao carregar configurações: {e}")
    
    def _create_default_config(self) -> None:
        """Cria um arquivo de configuração padrão com GitHub"""
        default_config = {
            "THEME": "dark"
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as file:
                json.dump(default_config, file, indent=4, ensure_ascii=False)
            self.config_data = default_config
            self.logger.info(f"Arquivo de configuração padrão criado: {self.config_file}")
        except Exception as e:
            self.logger.error(f"Erro ao criar arquivo de configuração padrão: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtém um valor de configuração"""
        return self.config_data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Define um valor de configuração e salva no arquivo"""
        self.config_data[key] = value
        self._save_config()
    
    def _save_config(self) -> None:
        """Salva as configurações no arquivo JSON"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as file:
                json.dump(self.config_data, file, indent=4, ensure_ascii=False)
            self.logger.info(f"Configurações salvas no arquivo: {self.config_file}")
        except Exception as e:
            self.logger.error(f"Erro ao salvar configurações: {e}")
    
    def reload(self) -> None:
        """Recarrega as configurações do arquivo"""
        self.logger.info("Recarregando configurações...")
        self._load_config()
        