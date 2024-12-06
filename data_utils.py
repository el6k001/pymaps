import requests
import pandas as pd
import io
import base64

def get_regions():
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/regioes"
    response = requests.get(url)
    regions = response.json()
    return [{'label': region['nome'], 'value': region['id']} for region in regions]

def get_ufs():
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"
    response = requests.get(url)
    ufs = response.json()
    return [{'label': uf['nome'], 'value': uf['id']} for uf in ufs]

def get_ufs_by_region(region_id):
    url = f"https://servicodados.ibge.gov.br/api/v1/localidades/regioes/{region_id}/estados"
    response = requests.get(url)
    ufs = response.json()
    return [{'label': uf['nome'], 'value': uf['id']} for uf in ufs]

def get_all_municipios():
    url = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
    response = requests.get(url)
    municipios = response.json()
    return [{'label': municipio['nome'], 'value': municipio['id']} for municipio in municipios]

def get_municipios_by_uf(uf_id):
    url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf_id}/municipios"
    response = requests.get(url)
    municipios = response.json()
    return [{'label': municipio['nome'], 'value': municipio['id']} for municipio in municipios]

def load_data_from_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            return None
    except Exception as e:
        print(f"Error loading file: {e}")
        return None
    return df

def get_area_name(area_type, area_id):
    if area_type == 'region':
        url = f"https://servicodados.ibge.gov.br/api/v1/localidades/regioes/{area_id}"
    elif area_type == 'uf':
        url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{area_id}"
    elif area_type == 'municipio':
        url = f"https://servicodados.ibge.gov.br/api/v1/localidades/municipios/{area_id}"
    else:
        return "Área desconhecida"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['nome']
    else:
        return "Nome não encontrado"