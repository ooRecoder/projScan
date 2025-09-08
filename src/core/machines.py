import json
import os
from typing import Any, Dict
from utils import Singleton
from core.logging import AppLogger
from typing import Optional

@Singleton
class ComputerManager:
    """
    Gerencia os computadores scanneados e suas informações por serviço.
    """

    def __init__(self, file_path: Optional[str] = "data/machines.json"):
        """
        Inicializa o gerenciador de computadores.
        """
        from utils import FilePathManager
        fm = FilePathManager.instance
        instance_logger = AppLogger.instance
        
        if not fm or not instance_logger:
            raise RuntimeError("Instância de FilePathManager ou Logging não inicializada")
        
        self.file_path = fm.get_file_path(file_path)
        self.logger = instance_logger.get_logger(__name__)
        self.computers: Dict[str, Dict[str, Any]] = {}
        self.logger.info(f"ComputerManager inicializado - Arquivo: {self.file_path}")
        self.load()

    def load(self):
        """Carrega os dados do arquivo JSON, se existir."""
        try:
            # Primeiro tenta carregar do arquivo do usuário
            if os.path.exists(self.file_path):
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        self.computers = data
                        self.logger.info(f"Dados carregados: {len(self.computers)} computadores")
                        return
                    else:
                        self.logger.warning("Estrutura JSON inválida no arquivo do usuário")
            
            self.computers = {}
            self.logger.info("Inicializando dados vazios")
                
        except json.JSONDecodeError:
            self.logger.error("Arquivo JSON corrompido, inicializando dados vazios")
            self.computers = {}
        except PermissionError:
            self.logger.error(f"Sem permissão para ler o arquivo: {self.file_path}")
            self.computers = {}
        except Exception as e:
            self.logger.error(f"Erro inesperado ao carregar dados: {e}")
            self.computers = {}

    def save(self):
        """Salva os dados atuais no arquivo JSON do usuário."""
        try:
            # Garante que o diretório existe
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.computers, f, indent=4, ensure_ascii=False)
            self.logger.info(f"Dados salvos em: {self.file_path} - {len(self.computers)} computadores")
                
        except PermissionError:
            self.logger.error(f"Sem permissão para escrever no arquivo: {self.file_path}")
        except Exception as e:
            self.logger.error(f"Erro ao salvar dados: {e}")

    def add_computer(self, identifier: str, data: Optional[Dict[str, Any]] = None):
        """
        Adiciona um computador pelo identificador (MAC, hostname, etc.)
        Se já existir, mantém os dados existentes ou atualiza se data for fornecido.
        """
        if data is None:
            data = {}
        
        if identifier not in self.computers:
            self.computers[identifier] = data
            self.logger.info(f"Computador adicionado: {identifier}")
        else:
            self.computers[identifier].update(data)
            self.logger.debug(f"Computador atualizado: {identifier}")
        
        self.save()

    def remove_computer(self, identifier: str):
        """Remove um computador pelo identificador."""
        if identifier in self.computers:
            del self.computers[identifier]
            self.logger.info(f"Computador removido: {identifier}")
            self.save()
        else:
            self.logger.warning(f"Tentativa de remover computador inexistente: {identifier}")

    def get_computer(self, identifier: str) -> Optional[Dict[str, Any]]:
        """Retorna os dados completos de um computador."""
        computer = self.computers.get(identifier)
        if computer:
            self.logger.debug(f"Dados recuperados para computador: {identifier}")
        else:
            self.logger.debug(f"Computador não encontrado: {identifier}")
        return computer

    def get_service_data(self, identifier: str, service_name: str) -> Optional[Dict[str, Any]]:
        """Retorna os dados de um serviço específico de um computador."""
        computer = self.get_computer(identifier)
        if computer:
            service_data = computer.get(service_name)
            if service_data:
                self.logger.debug(f"Dados do serviço '{service_name}' recuperados para: {identifier}")
            else:
                self.logger.debug(f"Serviço '{service_name}' não encontrado para: {identifier}")
            return service_data
        return None

    def list_computers(self) -> list[str]:
        """Retorna a lista de identificadores de computadores."""
        computers_list = list(self.computers.keys())
        self.logger.debug(f"Lista de computadores recuperada: {len(computers_list)} itens")
        return computers_list

    def update_service_data(self, identifier: str, service_name: str, service_data: Dict[str, Any]):
        """Atualiza ou adiciona dados de um serviço em um computador."""
        if identifier not in self.computers:
            self.computers[identifier] = {}
            self.logger.info(f"Novo computador criado para serviço: {identifier}")
        
        self.computers[identifier][service_name] = service_data
        self.logger.info(f"Serviço '{service_name}' atualizado para computador: {identifier}")
        self.save()

    def get_all_computers(self) -> Dict[str, Dict[str, Any]]:
        """Retorna todos os computadores."""
        self.logger.debug("Todos os computadores recuperados")
        return self.computers.copy()

    def clear_all(self):
        """Remove todos os computadores."""
        count = len(self.computers)
        self.computers.clear()
        self.logger.warning(f"Todos os computadores removidos: {count} itens")
        self.save()
        