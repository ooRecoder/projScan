import json
import os
import sys
from typing import Any, Dict, Optional
from utils import Singleton
from core.logging import AppLogger

@Singleton
class ConfigManager:
    def __init__(self, config_file: Optional[str] = "data/config.json"):
        """
        Inicializa o gerenciador de configurações
        
        Args:
            config_file: Caminho opcional para o arquivo de configuração
        """
        from utils import FilePathManager
        fm = FilePathManager.instance
        instance_logger = AppLogger.instance
        
        if not fm or not instance_logger:
            raise RuntimeError("FilePathManager ou Logging não foi inicializado")
        
        self.logger = instance_logger.get_logger(__name__)
        self.config_file = fm.get_file_path(config_file)
        self.config: Dict[str, Any] = {}
        
        self.logger.info(f"ConfigManager inicializado - Arquivo: {self.config_file}")
        self.ensure_config_file_exists()  # Garante que o arquivo existe
        self.load()
    
    def ensure_config_file_exists(self):
        """Garante que o arquivo de configuração existe, criando-o se necessário"""
        try:
            # Cria o diretório se não existir
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            # Se o arquivo não existe, cria com configuração vazia
            if not os.path.exists(self.config_file):
                with open(self.config_file, "w", encoding="utf-8") as f:
                    json.dump({}, f, indent=4, ensure_ascii=False)
                self.logger.info(f"Arquivo de configuração criado: {self.config_file}")
                
        except PermissionError:
            self.logger.error(f"Sem permissão para criar arquivo: {self.config_file}")
            raise
        except Exception as e:
            self.logger.error(f"Erro ao criar arquivo de configuração: {e}")
            raise
    
    def load(self):
        """Carrega a configuração do arquivo JSON"""
        try:
            # Primeiro tenta carregar a configuração do usuário
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
                    if isinstance(self.config, dict):
                        self.logger.info(f"Configuração carregada: {len(self.config)} serviços")
                        return
                    
            self.config = {}
            self.logger.info("Inicializando configuração vazia")
                
        except json.JSONDecodeError:
            self.config = {}
            self.logger.error("Arquivo de configuração corrompido, usando configuração vazia")
        except FileNotFoundError:
            self.config = {}
            self.logger.warning("Arquivo de configuração não encontrado, usando configuração vazia")
        except PermissionError:
            self.config = {}
            self.logger.error(f"Sem permissão para ler o arquivo: {self.config_file}")
        except Exception as e:
            self.config = {}
            self.logger.error(f"Erro inesperado ao carregar configuração: {e}")
    
    def save(self):
        """Salva a configuração no arquivo JSON do usuário"""
        try:                
            # Garante que o diretório existe
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            
            self.logger.info(f"Configuração salva: {len(self.config)} serviços em {self.config_file}")
                
        except PermissionError:
            self.logger.error(f"Sem permissão para escrever no arquivo: {self.config_file}")
        except Exception as e:
            self.logger.error(f"Erro ao salvar configuração: {e}")
    
    def get_service_config(self, service_name: str) -> Dict[str, Any]:
        """Retorna a configuração de um serviço"""
        config = self.config.get(service_name, {})
        self.logger.debug(f"Configuração recuperada para serviço: {service_name}")
        return config
    
    def get_service_config_with_defaults(self, service_name: str, default_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Retorna a configuração de um serviço com valores padrão para opções faltantes.
        
        Args:
            service_name: Nome do serviço
            default_config: Configuração padrão para mesclar
        
        Returns:
            Configuração completa do serviço
        """
        if default_config is None:
            default_config = {}
        
        service_config = self.get_service_config(service_name)
        # Mescla as configurações, dando prioridade às do usuário
        merged_config = {**default_config, **service_config}
        
        self.logger.debug(f"Configuração com padrões recuperada para serviço: {service_name}")
        return merged_config

    def set_service_config(self, service_name: str, options: Dict[str, Any]):
        """Define a configuração completa de um serviço"""
        self.config[service_name] = options
        self.logger.info(f"Configuração definida para serviço: {service_name}")
        self.save()
        
    def remove_service(self, service_name: str):
        """Remove a configuração de um serviço"""
        if service_name in self.config:
            del self.config[service_name]
            self.logger.info(f"Serviço removido da configuração: {service_name}")
            self.save()
        else:
            self.logger.warning(f"Tentativa de remover serviço inexistente: {service_name}")

    def list_services(self) -> list[str]:
        """Retorna lista de serviços configurados"""
        services = list(self.config.keys())
        self.logger.debug(f"Lista de serviços recuperada: {len(services)} serviços")
        return services
    
    def get_all_configs(self) -> Dict[str, Any]:
        """Retorna todas as configurações"""
        self.logger.debug("Todas as configurações recuperadas")
        return self.config.copy()
    
    def update_service_option(self, service_name: str, option_name: str, value: Any):
        """Atualiza uma opção específica de um serviço"""
        if service_name not in self.config:
            self.config[service_name] = {}
        
        old_value = self.config[service_name].get(option_name)
        self.config[service_name][option_name] = value
        
        self.logger.info(f"Opção '{option_name}' atualizada para serviço '{service_name}': {old_value} -> {value}")
        self.save()
    
    def get_service_option(self, service_name: str, option_name: str, default: Any = None) -> Any:
        """Obtém o valor de uma opção específica de um serviço"""
        service_config = self.get_service_config(service_name)
        value = service_config.get(option_name, default)
        self.logger.debug(f"Opção '{option_name}' recuperada do serviço '{service_name}': {value}")
        return value
    
    def get_default_config_path(self) -> str:
        """Retorna o caminho do arquivo de configuração padrão (do pacote)"""
        self.logger.debug(f"Caminho padrão da configuração: {self.config_file}")
        return self.config_file
    
    def get_user_config_path(self) -> str:
        """Retorna o caminho do arquivo de configuração do usuário"""
        self.logger.debug(f"Caminho do usuário da configuração: {self.config_file}")
        return self.config_file
    