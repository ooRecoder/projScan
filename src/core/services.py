import json
from typing import Dict, Any, Optional, List
from utils import Singleton
from .logging import AppLogger
from dotenv import load_dotenv
import os

load_dotenv()

@Singleton
class ServiceManager:
    def __init__(self, json_file_path: Optional[str] = "data/services.json") -> None:
        self.logger = AppLogger().get_logger(__name__)
        from utils import FilePathManager
        self.file_manager = FilePathManager.instance
        
        if not self.file_manager:
            raise RuntimeError("❌ Instância de FilePathManager não existe")
        
        self.json_file_path = self.file_manager.get_file_path(json_file_path)
        self.logger.info(f"Inicializando ServiceManager com arquivo: {self.json_file_path}")
        
        # Garante que o arquivo existe antes de carregar
        self._ensure_file_exists()
        self.services_data: Dict[str, Dict[str, Any]] = self._load_services()
        self.logger.info(f"ServiceManager Inicializado")
    
    def _ensure_file_exists(self):
        """Garante que o arquivo de serviços existe, criando-o se necessário"""
        try:
            # Cria o diretório se não existir
            os.makedirs(os.path.dirname(self.json_file_path), exist_ok=True)
            
            # Se o arquivo não existe, cria com serviços padrão
            if not os.path.exists(self.json_file_path):
                self.logger.warning(f"Arquivo JSON não encontrado: {self.json_file_path}")
                default_services = self._get_default_services()
                with open(self.json_file_path, 'w', encoding='utf-8') as file:
                    json.dump(default_services, file, indent=2, ensure_ascii=False)
                self.logger.info(f"Arquivo de serviços padrão criado: {self.json_file_path}")
                
        except PermissionError:
            self.logger.error(f"Sem permissão para criar arquivo: {self.json_file_path}")
            raise
        except Exception as e:
            self.logger.error(f"Erro ao criar arquivo de serviços: {e}")
            raise

    def _load_services(self) -> Dict[str, Dict[str, Any]]:
        """Carrega os dados dos serviços do arquivo JSON"""
        try:
            if os.path.exists(self.json_file_path):
                with open(self.json_file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    if isinstance(data, dict):
                        self.logger.debug(f"Serviços carregados: {len(data)} serviços encontrados")
                        return data
            
            # Se chegou aqui, o arquivo não existe ou está vazio
            self.logger.warning("Arquivo JSON não encontrado ou vazio, usando serviços padrão")
            return self._get_default_services()
                    
        except json.JSONDecodeError as e:
            self.logger.error(f"Erro de decodificação JSON: {e}")
            # Recria o arquivo se estiver corrompido
            return self._recreate_services_file()
        except Exception as e:
            self.logger.error(f"Erro inesperado ao carregar JSON: {e}")
            return self._get_default_services()
    
    def _recreate_services_file(self) -> Dict[str, Dict[str, Any]]:
        """Recria o arquivo de serviços com a estrutura padrão"""
        try:
            default_services = self._get_default_services()
            with open(self.json_file_path, 'w', encoding='utf-8') as file:
                json.dump(default_services, file, indent=2, ensure_ascii=False)
            self.logger.info(f"Arquivo de serviços recriado: {self.json_file_path}")
            return default_services
        except Exception as e:
            self.logger.error(f"Erro ao recriar arquivo de serviços: {e}")
            return self._get_default_services()
    
    def _get_default_services(self) -> Dict[str, Dict[str, Any]]:
        """Retorna a estrutura padrão de serviços"""
        default_services = {
            "CPU": {
                "description": "Coleta informações sobre a CPU do sistema",
                "options": {
                    "usage": {
                        "type": "boolean",
                        "default": False,
                        "description": "Incluir o uso da CPU em porcentagem"
                    },
                    "cores": {
                        "type": "boolean",
                        "default": True,
                        "description": "Incluir o número de núcleos da CPU"
                    },
                    "details": {
                        "type": "boolean",
                        "default": True,
                        "description": "Incluir detalhes do processador (nome/modelo)"
                    }
                }
            },
            "DEVICE": {
                "description": "Coleta informações detalhadas do sistema Windows, incluindo fabricante, modelo, tipo de equipamento e baterias.",
                "options": {
                    "include_system": {
                        "type": "boolean",
                        "default": True,
                        "description": "Incluir informações do sistema, como fabricante, modelo, tipo de PC e usuário logado."
                    },
                    "include_battery": {
                        "type": "boolean",
                        "default": True,
                        "description": "Incluir informações sobre a(s) bateria(s) do dispositivo, se houver."
                    }
                }
            },
            "BIOS": {
                "description": "Serviço responsável por coletar informações da BIOS no Windows usando WMI."
            },
            "DISK": {
                "description": "Coleta informações sobre os discos do sistema, incluindo modelo, uso, estatísticas de I/O e saúde.",
                "options": {
                    "disk_model": {
                        "type": "boolean",
                        "default": True,
                        "description": "Incluir modelo e status do disco."
                    },
                    "details": {
                        "type": "boolean",
                        "default": True,
                        "description": "Incluir detalhes completos do disco (WMI)."
                    },
                    "io_stats": {
                        "type": "boolean",
                        "default": False,
                        "description": "Incluir estatísticas de I/O de cada disco."
                    },
                    "usage": {
                        "type": "boolean",
                        "default": True,
                        "description": "Incluir uso de disco (total, usado, livre e percentual)."
                    }
                }
            },
            "OS": {
                "description": "Coleta informações sobre o sistema operacional, incluindo nome, versão e release.",
                "options": {
                    "system": {
                        "type": "boolean",
                        "default": True,
                        "description": "Incluir o nome do sistema operacional (ex: Windows, Linux, macOS)."
                    },
                    "version": {
                        "type": "boolean",
                        "default": True,
                        "description": "Incluir a versão do sistema operacional."
                    },
                    "release": {
                        "type": "boolean",
                        "default": True,
                        "description": "Incluir o release do sistema operacional."
                    }
                }
            },
            "RAM": {
                "description": "Coleta informações sobre a memória RAM do sistema.",
                "options": {
                    "unit": {
                        "type": "string",
                        "default": "GB",
                        "options": ["MB", "GB", "TB"],
                        "description": "Unidade da memória (MB, GB ou TB)."
                    }
                }
            }
        }
        
        self.logger.info("Usando estrutura padrão de serviços")
        return default_services

    def save_services(self) -> None:
        """Salva os dados atualizados no arquivo JSON"""
        try:
            # Garante que o diretório existe
            directory = os.path.dirname(self.json_file_path)
            if directory:
                os.makedirs(directory, exist_ok=True)
            
            with open(self.json_file_path, 'w', encoding='utf-8') as file:
                json.dump(self.services_data, file, indent=2, ensure_ascii=False)
            self.logger.info(f"Serviços salvos em: {self.json_file_path}")
        except Exception as e:
            self.logger.error(f"Erro ao salvar JSON: {e}")
            raise
    
    def get_all_services(self) -> Dict[str, Dict[str, Any]]:
        """Retorna todos os serviços disponíveis"""
        return self.services_data
    
    def get_service(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Obtém um serviço específico pelo nome"""
        return self.services_data.get(service_name.upper())
    
    def service_exists(self, service_name: str) -> bool:
        """Verifica se um serviço existe"""
        return service_name.upper() in self.services_data
    
    def get_service_description(self, service_name: str) -> Optional[str]:
        """Obtém a descrição de um serviço"""
        service = self.get_service(service_name)
        return service.get('description') if service else None
    
    def get_service_options(self, service_name: str) -> Optional[Dict[str, Dict[str, Any]]]:
        """Obtém as opções de um serviço"""
        service = self.get_service(service_name)
        return service.get('options') if service else None
    
    def get_option_value(self, service_name: str, option_name: str) -> Optional[Any]:
        """Obtém o valor de uma opção específica"""
        options = self.get_service_options(service_name)
        if options and option_name in options:
            return options[option_name].get('default')
        return None
    
    def get_enabled_options(self, service_name: str) -> Dict[str, Dict[str, Any]]:
        """Obtém todas as opções habilitadas de um serviço"""
        options = self.get_service_options(service_name)
        if not options:
            return {}
        
        enabled_options = {}
        for option_name, option_data in options.items():
            if option_data.get('default', False):
                enabled_options[option_name] = option_data
        
        return enabled_options
    
    def add_service(self, service_name: str, description: str, 
                   options: Optional[Dict[str, Dict[str, Any]]] = None) -> bool:
        """Adiciona um novo serviço"""
        if self.service_exists(service_name):
            self.logger.warning(f"Tentativa de adicionar serviço existente: {service_name}")
            return False
        
        service_data: Dict[str, Any] = {
            'description': description
        }
        
        if options:
            service_data['options'] = options
        
        self.services_data[service_name.upper()] = service_data
        self.logger.info(f"Serviço adicionado: {service_name}")
        self.save_services()
        return True
    
    def remove_service(self, service_name: str) -> bool:
        """Remove um serviço"""
        if service_name.upper() in self.services_data:
            del self.services_data[service_name.upper()]
            self.logger.info(f"Serviço removido: {service_name}")
            self.save_services()
            return True
        return False
    
    def validate_configuration(self) -> bool:
        """Valida a configuração completa dos serviços"""
        try:
            for service_name, service_data in self.services_data.items():
                if 'description' not in service_data:
                    self.logger.error(f"Serviço sem descrição: {service_name}")
                    return False
                
                if 'options' in service_data:
                    for option_name, option_data in service_data['options'].items():
                        if 'type' not in option_data or 'default' not in option_data or 'description' not in option_data:
                            self.logger.error(f"Opção incompleta: {service_name}.{option_name}")
                            return False
            
            return True
        except (AttributeError, TypeError) as e:
            self.logger.error(f"Erro na validação: {e}")
            return False

    def get_service_names(self) -> List[str]:
        """Retorna uma lista com os nomes de todos os serviços"""
        return list(self.services_data.keys())
    
    def get_option_info(self, service_name: str, option_name: str) -> Optional[Dict[str, Any]]:
        """Obtém informações completas de uma opção específica"""
        options = self.get_service_options(service_name)
        return options.get(option_name) if options else None
    
    def get_option_choices(self, service_name: str, option_name: str) -> Optional[List[Any]]:
        """Obtém as escolhas disponíveis para uma opção"""
        options = self.get_service_options(service_name)
        if options and option_name in options:
            return options[option_name].get("options")
        return None

    def get_service_options_with_defaults(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Retorna os options com defaults para um serviço específico"""
        service = self.get_service(service_name)
        if not service or 'options' not in service:
            return None
        
        options_with_defaults = {}
        for option_name, option_data in service['options'].items():
            options_with_defaults[option_name] = option_data.get('default')
        
        return options_with_defaults
    
    def update_option_value(self, service_name: str, option_name: str, value: Any) -> bool:
        """Atualiza o valor de uma opção específica"""
        service = self.get_service(service_name)
        if not service or 'options' not in service or option_name not in service['options']:
            self.logger.warning(f"Tentativa de atualizar opção inexistente: {service_name}.{option_name}")
            return False
        
        service['options'][option_name]['default'] = value
        self.logger.debug(f"Opção atualizada: {service_name}.{option_name} = {value}")
        self.save_services()
        return True
    
    def reload_services(self) -> None:
        """Recarrega os serviços do arquivo JSON"""
        self.logger.info("Recarregando serviços do arquivo JSON")
        self.services_data = self._load_services()
        