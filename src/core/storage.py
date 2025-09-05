import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from utils import get_mac_address, FilePathManager

# Configura logger
logger = logging.getLogger(__name__)

fm = FilePathManager.instance
if not fm:
    logger.critical("❌ Instância de FilePathManager não existe")
    raise ImportError("❌ Instância de FilePathManager não existe")

DATA_FILE = Path(fm.get_file_path("data/machines.json"))
logger.info(f"Arquivo de dados configurado: {DATA_FILE}")

def load_data() -> Dict[str, Any]:
    """Carrega os dados do arquivo JSON."""
    try:
        if DATA_FILE.exists():
            logger.debug(f"Carregando dados do arquivo: {DATA_FILE}")
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                logger.info(f"Dados carregados com sucesso. {len(data)} máquina(s) encontrada(s)")
                return data
        else:
            logger.info("Arquivo de dados não existe. Retornando dicionário vazio")
            return {}
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao decodificar JSON do arquivo {DATA_FILE}: {e}")
        return {}
    except Exception as e:
        logger.error(f"Erro inesperado ao carregar dados: {e}")
        return {}

def save_data(data: Dict[str, Any]) -> None:
    """Salva os dados completos no JSON."""
    try:
        logger.debug(f"Salvando dados no arquivo: {DATA_FILE}")
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        logger.info(f"Dados salvos com sucesso. {len(data)} máquina(s) no arquivo")
    except Exception as e:
        logger.error(f"Erro ao salvar dados no arquivo {DATA_FILE}: {e}")
        raise

def update_machine_info(new_info: Dict[str, Any]) -> None:
    """
    Atualiza as informações da máquina atual no JSON.
    Se já existe, mescla os dados em vez de sobrescrever tudo.
    """
    try:
        mac = get_mac_address()
        logger.debug(f"Atualizando informações da máquina com MAC: {mac}")
        
        data = load_data()

        if mac not in data:
            logger.info(f"Nova máquina detectada. Adicionando MAC: {mac}")
            data[mac] = {}

        # Log das alterações
        old_keys = set(data[mac].keys())
        new_keys = set(new_info.keys())
        added_keys = new_keys - old_keys
        updated_keys = old_keys.intersection(new_keys)
        
        # Faz merge: sobrescreve apenas as chaves novas/alteradas
        data[mac].update(new_info)

        save_data(data)
        
        # Log detalhado das mudanças
        if added_keys:
            logger.info(f"Chaves adicionadas: {list(added_keys)}")
        if updated_keys:
            logger.info(f"Chaves atualizadas: {list(updated_keys)}")
        logger.info(f"Informações da máquina {mac} atualizadas com sucesso")
        
    except Exception as e:
        logger.error(f"Erro ao atualizar informações da máquina: {e}")
        raise

def get_machine_info(mac: Optional[str] = None) -> Dict[str, Any]:
    """
    Retorna as informações de uma máquina específica.
    Se não for passado MAC, retorna a máquina atual.
    """
    try:
        if mac is None:
            mac = get_mac_address()
            logger.debug(f"Buscando informações da máquina atual: {mac}")
        else:
            logger.debug(f"Buscando informações da máquina: {mac}")
        
        data = load_data()
        machine_info = data.get(mac, {})
        
        if machine_info:
            logger.info(f"Informações encontradas para MAC {mac}: {len(machine_info)} chaves")
        else:
            logger.warning(f"Nenhuma informação encontrada para MAC: {mac}")
            
        return machine_info
        
    except Exception as e:
        logger.error(f"Erro ao buscar informações da máquina {mac if mac else 'atual'}: {e}")
        return {}