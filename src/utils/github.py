import requests
import json
import base64
import logging
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from utils import Singleton
from core import AppLogger  # assumindo que o AppLogger está em core/logger.py

# Carrega variáveis do .env
load_dotenv()


@Singleton
class GitHubUploader:
    def __init__(self):
        # Logger
        self.logger = AppLogger().get_logger(__name__)
        
        self.logger.debug("Inicializando GitHub")
        
        # Carrega configs direto do .env
        self.token = os.getenv("GITHUB_TOKEN")
        self.owner = os.getenv("GITHUB_REPOSITORY_OWNER")
        self.repo = os.getenv("GITHUB_REPOSITORY_NAME")
        self.branch = os.getenv("GITHUB_BRANCH", "main")
        self.file_path = os.getenv("GITHUB_FILE_PATH", "machines/")

        if not all([self.repo, self.owner, self.token]):
            raise ValueError("❌ Configuração do GitHub incompleta no .env")
        
        self.logger.info("GitHub Inicializado.")

    def upload_json_file(self, data: Any, filename: str) -> bool:
        """
        Faz upload direto de um arquivo JSON para o GitHub usando API
        """
        try:
            url = f"https://api.github.com/repos/{self.owner}/{self.repo}/contents/{self.file_path}{filename}"
            self.logger.debug(f"📤 Preparando upload do arquivo: {filename} para {url}")

            # Converte dados para JSON string
            json_content = json.dumps(data, indent=4, ensure_ascii=False)
            self.logger.debug(f"📄 Conteúdo convertido para JSON (tamanho {len(json_content)} bytes)")

            # Converte para base64
            content_base64 = base64.b64encode(json_content.encode('utf-8')).decode('utf-8')
            self.logger.debug(f"🔑 Conteúdo convertido para Base64")

            # Headers com autenticação
            headers = {
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json"
            }

            # Verifica se o arquivo já existe
            existing_file_sha = self._get_file_sha(url, headers)
            if existing_file_sha:
                self.logger.info(f"📝 Arquivo {filename} já existe, atualizando (SHA={existing_file_sha})")
            else:
                self.logger.info(f"➕ Arquivo {filename} será criado no repositório")

            payload = {
                "message": f"Adicionando/atualizando {filename}",
                "content": content_base64,
                "branch": self.branch
            }

            if existing_file_sha:
                payload["sha"] = existing_file_sha

            response = requests.put(url, headers=headers, json=payload)

            if response.status_code in [200, 201]:
                self.logger.info(f"✅ Arquivo {filename} enviado com sucesso para o GitHub")
                return True
            else:
                self.logger.error(f"❌ Erro ao enviar arquivo {filename}: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            self.logger.exception(f"❌ Erro no upload do arquivo {filename}: {e}")
            return False

    def _get_file_sha(self, url: str, headers: dict) -> Optional[str]:
        """Obtém o SHA do arquivo se ele já existir"""
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                sha = response.json().get("sha")
                self.logger.debug(f"🔍 SHA do arquivo encontrado: {sha}")
                return sha
            elif response.status_code == 404:
                self.logger.debug("📂 Arquivo não encontrado no repositório")
                return None
            else:
                self.logger.warning(f"⚠️ Não foi possível verificar SHA: {response.status_code}")
                return None
        except Exception as e:
            self.logger.error(f"⚠️ Erro ao tentar obter SHA: {e}")
            return None

    def upload_multiple_files(self, files_data: Dict[str, Any]) -> bool:
        """Faz upload de múltiplos arquivos"""
        success = True
        for filename, data in files_data.items():
            self.logger.info(f"🚀 Iniciando upload do arquivo: {filename}")
            if not self.upload_json_file(data, filename):
                success = False
        return success
