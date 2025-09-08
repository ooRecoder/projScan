import json
import os
from typing import Any, Dict
from utils import Singleton
from core.logging import AppLogger

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
        
        # Garante que o arquivo de configuração existe
        self._ensure_config_file_exists()
        self._load_config()
        
        self.logger.info("AppConfig Inicializado")
    
    def _ensure_config_file_exists(self) -> None:
        """Garante que o arquivo de configuração existe, criando-o se necessário"""
        if not self.file_manager:
            return
            
        config_path = self.file_manager.get_file_path(self.config_file)
        
        try:
            # Cria o diretório pai se não existir
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            # Se o arquivo não existe, cria com configuração padrão
            if not os.path.exists(config_path):
                self.logger.warning(f"Arquivo de configuração {config_path} não encontrado. Criando configuração padrão.")
                self._create_default_config(config_path)
                
        except Exception as e:
            self.logger.error(f"Erro ao verificar/criar arquivo de configuração: {e}")
            raise
    
    def _create_default_config(self, config_path: str) -> None:
        """Cria um arquivo de configuração padrão"""
        default_config = {
            "THEME": "dark"
        }
        
        try:
            with open(config_path, 'w', encoding='utf-8') as file:
                json.dump(default_config, file, indent=4, ensure_ascii=False)
            self.config_data = default_config
            self.logger.info(f"Arquivo de configuração padrão criado: {config_path}")
        except Exception as e:
            self.logger.error(f"Erro ao criar arquivo de configuração padrão: {e}")
            raise
    
    def _load_config(self) -> None:
        """Carrega as configurações do arquivo JSON"""
        if not self.file_manager:
            return
            
        config_path = self.file_manager.get_file_path(self.config_file)
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as file:
                    self.config_data = json.load(file)
                self.logger.info(f"Configurações carregadas do arquivo: {config_path}")
            else:
                # Este caso não deveria acontecer mais devido ao _ensure_config_file_exists()
                self.logger.warning(f"Arquivo de configuração {config_path} não encontrado após verificação.")
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Erro ao decodificar JSON do arquivo de configuração: {e}")
            # Recria o arquivo se estiver corrompido
            self._create_default_config(config_path)
        except Exception as e:
            self.logger.error(f"Erro ao carregar configurações: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtém um valor de configuração"""
        return self.config_data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Define um valor de configuração e salva no arquivo"""
        self.config_data[key] = value
        self._save_config()
    
    def _save_config(self) -> None:
        """Salva as configurações no arquivo JSON"""
        if not self.file_manager:
            return
            
        config_path = self.file_manager.get_file_path(self.config_file)
        try:
            # Garante que o diretório existe antes de salvar
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as file:
                json.dump(self.config_data, file, indent=4, ensure_ascii=False)
            self.logger.info(f"Configurações salvas no arquivo: {config_path}")
        except Exception as e:
            self.logger.error(f"Erro ao salvar configurações: {e}")
    
    def reload(self) -> None:
        """Recarrega as configurações do arquivo"""
        self.logger.info("Recarregando configurações...")
        self._load_config()