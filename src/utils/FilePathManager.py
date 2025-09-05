# file_path_manager.py
import os
import sys
import logging
from pathlib import Path
from typing import Optional

class FilePathManager:
    """Classe para gerenciar referências a arquivos com compatibilidade PyInstaller"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.is_production = self._check_environment()
        self.base_path = self._get_base_path()
        self.logger.info(f"FilePathManager inicializado - Ambiente: {'Produção' if self.is_production else 'Desenvolvimento'}")
        self.logger.info(f"Base path: {self.base_path}")
    
    def _check_environment(self) -> bool:
        """
        Verifica se está em ambiente de produção (PyInstaller) ou desenvolvimento
        Returns:
            bool: True se for produção, False se for desenvolvimento
        """
        # Verifica variável de ambiente personalizada
        env = os.environ.get('ENVIRONMENT', '').lower()
        if env in ['prod', 'production']:
            self.logger.debug("Ambiente detectado via variável ENVIRONMENT: Produção")
            return True
        if env in ['dev', 'development']:
            self.logger.debug("Ambiente detectado via variável ENVIRONMENT: Desenvolvimento")
            return False
        
        # Verifica se está executando como bundle do PyInstaller
        if getattr(sys, 'frozen', False):
            self.logger.debug("Ambiente detectado via sys.frozen: Produção (PyInstaller)")
            return True
        
        # Verifica se existe o diretório _internal (comum no PyInstaller)
        if hasattr(sys, '_MEIPASS'):
            self.logger.debug("Ambiente detectado via sys._MEIPASS: Produção (PyInstaller)")
            return True
        
        self.logger.debug("Ambiente padrão: Desenvolvimento")
        return False
    
    def _get_base_path(self) -> Path:
        """
        Retorna o caminho base dependendo do ambiente
        Returns:
            Path: Caminho base do projeto
        """
        if self.is_production:
            # Em produção, usa o diretório do executável
            if hasattr(sys, '_MEIPASS'):
                # PyInstaller cria um diretório temporário
                base_path = Path(sys._MEIPASS) # type: ignore
                self.logger.debug(f"Usando diretório _MEIPASS: {base_path}")
            else:
                base_path = Path(sys.executable).parent
                self.logger.debug(f"Usando diretório do executável: {base_path}")
            return base_path
        else:
            # Em desenvolvimento, usa o diretório do script atual
            base_path = Path(__file__).parent.parent
            self.logger.debug(f"Usando diretório do script: {base_path}")
            return base_path
    
    def get_file_path(self, relative_path: str) -> str:
        """
        Retorna o caminho absoluto do arquivo considerando o ambiente
        Args:
            relative_path (str): Caminho relativo do arquivo
        Returns:
            str: Caminho absoluto do arquivo
        """
        self.logger.debug(f"Buscando arquivo: {relative_path}")
        absolute_path = self.base_path / relative_path
        
        # Verifica se o arquivo existe
        if not absolute_path.exists():
            self.logger.warning(f"Arquivo não encontrado no caminho primário: {absolute_path}")
            
            # Tenta encontrar em subdiretórios comuns
            possible_paths = [
                self.base_path / relative_path,
                self.base_path / "resources" / relative_path,
                self.base_path / "data" / relative_path,
                self.base_path / "assets" / relative_path,
                self.base_path / "src" / relative_path,
                self.base_path.parent / relative_path,
            ]
            
            for path in possible_paths:
                if path.exists():
                    self.logger.info(f"Arquivo encontrado em caminho alternativo: {path}")
                    return str(path)
            
            error_msg = f"Arquivo não encontrado em nenhum local: {relative_path}"
            self.logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        self.logger.debug(f"Arquivo encontrado: {absolute_path}")
        return str(absolute_path)
    
    def get_resource_path(self, relative_path: str) -> str:
        """
        Método específico para recursos (compatibilidade com PyInstaller)
        Args:
            relative_path (str): Caminho relativo do recurso
        Returns:
            str: Caminho absoluto do recurso
        """
        self.logger.debug(f"Buscando recurso: {relative_path}")
        
        if self.is_production and hasattr(sys, '_MEIPASS'):
            # Em produção com PyInstaller
            base_path = Path(sys._MEIPASS) # type: ignore
            self.logger.debug(f"Usando _MEIPASS para recurso: {base_path}")
        else:
            # Em desenvolvimento ou produção sem _MEIPASS
            base_path = self.base_path
            self.logger.debug(f"Usando base path para recurso: {base_path}")
        
        return str(base_path / relative_path)
    
    def ensure_directory_exists(self, directory_path: str) -> None:
        """
        Garante que um diretório existe
        Args:
            directory_path (str): Caminho do diretório
        """
        try:
            path = Path(directory_path)
            path.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Diretório garantido: {directory_path}")
        except Exception as e:
            self.logger.error(f"Erro ao criar diretório {directory_path}: {e}")
            raise
    
    def is_file_internal(self) -> bool:
        """
        Verifica se um arquivo está no diretório _internal
        Returns:
            bool: True se estiver no diretório _internal
        """
        internal_dir = self.base_path / "_internal"
        exists = internal_dir.exists() and internal_dir.is_dir()
        self.logger.debug(f"Diretório _internal existe: {exists}")
        return exists
    
    def find_file(self, filename: str, search_dirs: Optional[list] = None) -> Optional[str]:
        """
        Busca um arquivo em múltiplos diretórios
        Args:
            filename: Nome do arquivo a ser buscado
            search_dirs: Lista de diretórios para buscar (opcional)
        Returns:
            Caminho do arquivo encontrado ou None
        """
        self.logger.debug(f"Buscando arquivo '{filename}' em múltiplos diretórios")
        
        if search_dirs is None:
            search_dirs = [
                self.base_path,
                self.base_path / "resources",
                self.base_path / "data",
                self.base_path / "assets",
                self.base_path / "config",
                self.base_path.parent,
            ]
        
        for directory in search_dirs:
            path = Path(directory) / filename
            if path.exists():
                self.logger.info(f"Arquivo '{filename}' encontrado em: {path}")
                return str(path)
        
        self.logger.warning(f"Arquivo '{filename}' não encontrado em nenhum diretório de busca")
        return None

# Função factory para facilitar o uso
def get_file_manager() -> FilePathManager:
    """Retorna uma instância do FilePathManager"""
    return FilePathManager()