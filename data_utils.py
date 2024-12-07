import requests
import pandas as pd
import io
import base64
import cachetools
from typing import Dict, List, Optional, Tuple, Any
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache para dados da API (1 hora)
API_CACHE = cachetools.TTLCache(maxsize=100, ttl=3600)

# Configurações
MAX_FILE_SIZE = 10 * 1024  # 10 KB
MAX_ROWS = 1000  # Máximo de linhas para processamento

def get_cached_api_data(url: str) -> Optional[List[Dict]]:
    """Obtém dados da API com cache."""
    if url in API_CACHE:
        return API_CACHE[url]
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        API_CACHE[url] = data
        return data
    except Exception as e:
        logger.error(f"Erro ao acessar API: {e}")
        return None

def get_regions() -> List[Dict]:
    """Obtém lista de regiões."""
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/regioes"
    data = get_cached_api_data(url)
    if not data:
        return []
    return [{'label': region['nome'], 'value': region['id']} for region in data]

def get_ufs() -> List[Dict]:
    """Obtém lista de UFs."""
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"
    data = get_cached_api_data(url)
    if not data:
        return []
    return [{'label': uf['nome'], 'value': uf['id']} for uf in data]

def get_ufs_by_region(region_id: int) -> List[Dict]:
    """Obtém UFs por região."""
    url = f"https://servicodados.ibge.gov.br/api/v1/localidades/regioes/{region_id}/estados"
    data = get_cached_api_data(url)
    if not data:
        return []
    return [{'label': uf['nome'], 'value': uf['id']} for uf in data]

def get_all_municipios() -> List[Dict]:
    """Obtém todos os municípios."""
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
    data = get_cached_api_data(url)
    if not data:
        return []
    return [{'label': municipio['nome'], 'value': municipio['id']} for municipio in data]

def get_municipios_by_uf(uf_id: int) -> List[Dict]:
    """Obtém municípios por UF."""
    url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf_id}/municipios"
    data = get_cached_api_data(url)
    if not data:
        return []
    return [{'label': municipio['nome'], 'value': municipio['id']} for municipio in data]

def load_data_from_contents(contents: str, filename: str) -> Optional[pd.DataFrame]:
    """
    Carrega e valida dados de um arquivo enviado.
    Limita tamanho do arquivo e número de linhas.
    """
    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        
        # Verifica tamanho do arquivo
        if len(decoded) > MAX_FILE_SIZE:
            raise ValueError(f"Arquivo muito grande. Máximo permitido: 10 KB. Tamanho atual: {len(decoded)/1024:.1f} KB")
        
        # Carrega dados baseado na extensão
        if 'csv' in filename.lower():
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename.lower():
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            raise ValueError("Formato de arquivo não suportado. Use CSV ou Excel.")
        
        # Limita número de linhas
        if len(df) > MAX_ROWS:
            logger.warning(f"Arquivo truncado de {len(df)} para {MAX_ROWS} linhas")
            df = df.head(MAX_ROWS)
        
        return df
    
    except Exception as e:
        logger.error(f"Erro ao carregar arquivo: {e}")
        return None

def get_area_name(area_type: str, area_id: int) -> str:
    """Obtém nome da área geográfica."""
    url_mapping = {
        'region': f"https://servicodados.ibge.gov.br/api/v1/localidades/regioes/{area_id}",
        'uf': f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{area_id}",
        'municipio': f"https://servicodados.ibge.gov.br/api/v1/localidades/municipios/{area_id}"
    }
    
    url = url_mapping.get(area_type)
    if not url:
        return "Área desconhecida"
    
    data = get_cached_api_data(url)
    return data['nome'] if data else "Nome não encontrado"
