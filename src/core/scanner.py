from core import AppLogger
from utils import Singleton
from .configManager import ConfigManager
from .machines import ComputerManager
import importlib.util
import time
from typing import Dict, Any, Optional
from datetime import datetime

@Singleton
class Scanner:
    def __init__(self):
        instance_logger = AppLogger.instance
        instance_configm = ConfigManager.instance
        instance_compm = ComputerManager.instance
        
        if not instance_configm or not instance_logger or not instance_compm:
            raise ImportError("Logging ou ConfigManager ou ComputerManager não foi inicializado")
        
        self.config_manager = instance_configm
        self.computer_manager = instance_compm
        self.logger = instance_logger.get_logger(__name__)
        
        # Inicializa GitHubUploader se configurado
        self.github_uploader = None
        self._init_github_uploader()
        
        self.logger.info("Scanner inicializado")
    
    def _init_github_uploader(self):
        """Inicializa o GitHubUploader se as configurações estiverem disponíveis"""
        try:
            # Tenta importar e inicializar o GitHubUploader
            from utils import GitHubUploader
            self.github_uploader = GitHubUploader.instance
        except ImportError as e:
            self.logger.warning(f"GitHubUploader não disponível: {e}")
        except ValueError as e:
            self.logger.warning(f"Configuração do GitHub incompleta: {e}")
        except Exception as e:
            self.logger.error(f"Erro ao inicializar GitHubUploader: {e}")
        
    def run(self, save=True, upload_to_github: Optional[bool] = None) -> Dict[str, Any]:
        from utils import FilePathManager
        fm = FilePathManager.instance
        
        if not fm:
            raise ImportError("FilePathManager não foi inicializado")
        
        results = {}
        enabled_services = self.config_manager.list_services()
        
        if not enabled_services:
            self.logger.warning("Nenhum serviço habilitado para escanear")
            return results

        self.logger.info(f"Iniciando scan de {len(enabled_services)} serviços: {', '.join(enabled_services)}")

        for service_name in enabled_services:
            try:
                # Construir caminho para o módulo do serviço
                service_path = fm.get_file_path(f"services/{service_name}.py")
                
                # Importar o módulo do serviço
                spec = importlib.util.spec_from_file_location(service_name, service_path)
                if spec is None:
                    self.logger.error(f"Falha ao carregar especificação do serviço: {service_name}")
                    continue
                    
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)  # type: ignore
                
                # Obter a classe do serviço (assumindo que o nome da classe é o mesmo do serviço em maiúsculas)
                service_class = getattr(module, service_name.upper(), None)
                if service_class is None:
                    self.logger.error(f"Classe {service_name.upper()} não encontrada no módulo {service_name}")
                    continue
                
                # Obter configurações do serviço
                options = self.config_manager.get_service_config(service_name)
                
                # Inicializar o serviço com as opções configuradas
                service_instance = service_class(**options)
                
                # Iniciar timer e executar coleta
                start_time = time.time()
                scan_result = service_instance.collect()
                end_time = time.time()
                
                execution_time = end_time - start_time
                execution_date = datetime.now().isoformat()
                
                # Armazenar resultados
                results[service_name] = {
                    'data': scan_result,
                    'execution_time': execution_time,
                    'execution_date': execution_date,
                    'success': True
                }
                
                self.logger.info(f"Serviço {service_name} executado com sucesso em {execution_time:.2f}s")
                
                # Salvar resultados se solicitado
                if save and scan_result:
                    self._save_service_results(service_name, scan_result, execution_date)
                    
            except ImportError as e:
                self.logger.error(f"Erro ao importar serviço {service_name}: {e}")
                results[service_name] = {
                    'data': {},
                    'error': str(e),
                    'success': False
                }
            except AttributeError as e:
                self.logger.error(f"Erro de atributo no serviço {service_name}: {e}")
                results[service_name] = {
                    'data': {},
                    'error': str(e),
                    'success': False
                }
            except Exception as e:
                self.logger.error(f"Erro inesperado no serviço {service_name}: {e}")
                results[service_name] = {
                    'data': {},
                    'error': str(e),
                    'success': False
                }
        
        # Upload para GitHub se configurado e solicitado
        if (upload_to_github or (upload_to_github is None and self.github_uploader)) and results:
            self._upload_to_github(results)
        
        self.logger.info(f"Scan concluído. Resultados: {len([r for r in results.values() if r['success']])}/{len(enabled_services)} serviços bem-sucedidos")
        return results
    
    def _save_service_results(self, service_name: str, data: Dict[str, Any], execution_date: str):
        """Salva os resultados do serviço no ComputerManager"""
        try:
            # Para cada computador encontrado no scan, salvar os dados
            for identifier, computer_data in data.items():
                if isinstance(computer_data, dict):
                    # Adicionar metadados de execução
                    computer_data_with_meta = {
                        **computer_data,
                        'last_scan': execution_date,
                        'service': service_name
                    }
                    
                    # Salvar no ComputerManager
                    self.computer_manager.add_computer(identifier, {
                        service_name: computer_data_with_meta
                    })
            
            self.logger.debug(f"Resultados do serviço {service_name} salvos com sucesso")
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar resultados do serviço {service_name}: {e}")
    
    def _upload_to_github(self, results: Dict[str, Any]):
        """Faz upload dos resultados para o GitHub"""
        if not self.github_uploader:
            self.logger.warning("GitHubUploader não disponível para upload")
            return False
        
        try:
            # Preparar dados para upload
            upload_data = {}
            
            # Criar arquivo consolidado com todos os resultados
            consolidated_data = {
                'scan_timestamp': datetime.now().isoformat(),
                'services_scanned': list(results.keys()),
                'results': results
            }
            upload_data['full_scan_results.json'] = consolidated_data
            
            # Criar arquivos individuais por serviço
            for service_name, service_data in results.items():
                if service_data['success']:
                    service_filename = f"{service_name}_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    upload_data[service_filename] = service_data
            
            # Fazer upload
            success = self.github_uploader.upload_multiple_files(upload_data)
            
            if success:
                self.logger.info("✅ Upload para GitHub concluído com sucesso")
            else:
                self.logger.error("❌ Falha no upload para GitHub")
                
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Erro durante upload para GitHub: {e}")
            return False
    
    def get_last_results(self) -> Dict[str, Any]:
        """Retorna os resultados da última execução do scanner"""
        # Esta implementação precisaria armazenar os resultados da última execução
        # Por enquanto retorna vazio - pode ser implementado com persistência
        return {}
    
    def get_service_status(self, service_name: str) -> Dict[str, Any]:
        """Retorna o status de um serviço específico"""
        try:
            service_config = self.config_manager.get_service_config(service_name)
            computers = self.config_manager.get_all_computers()
            
            # Contar computadores com dados deste serviço
            service_computers = 0
            for computer_data in computers.values():
                if service_name in computer_data:
                    service_computers += 1
            
            return {
                'configured': bool(service_config),
                'computers_found': service_computers,
                'last_scan': self._get_last_scan_date(service_name, computers),
                'enabled': service_name in self.config_manager.list_services(),
                'github_upload_available': self.github_uploader is not None
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao obter status do serviço {service_name}: {e}")
            return {'error': str(e)}
    
    def _get_last_scan_date(self, service_name: str, computers: Dict[str, Any]) -> str:
        """Obtém a data do último scan bem-sucedido para um serviço"""
        last_scan = None
        
        for computer_data in computers.values():
            if service_name in computer_data and 'last_scan' in computer_data[service_name]:
                scan_date = computer_data[service_name]['last_scan']
                if last_scan is None or scan_date > last_scan:
                    last_scan = scan_date
        
        return last_scan or "Nunca escaneado"
    
    def upload_to_github_manual(self, data: Optional[Dict[str, Any]] = None, filename: Optional[str] = None) -> bool:
        """
        Upload manual para GitHub opcional
        
        Args:
            data: Dados para upload (se None, usa últimos resultados)
            filename: Nome do arquivo (se None, usa nome automático)
        
        Returns:
            bool: True se o upload foi bem-sucedido
        """
        if not self.github_uploader:
            self.logger.error("GitHubUploader não disponível")
            return False
        
        try:
            if data is None:
                data = self.get_last_results() or {}
            
            if filename is None:
                filename = f"manual_upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            return self.github_uploader.upload_json_file(data, filename)
            
        except Exception as e:
            self.logger.error(f"Erro no upload manual para GitHub: {e}")
            return False