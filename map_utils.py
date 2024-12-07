# from altair import Point
from shapely.geometry import Point, shape, mapping
import requests
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import geopandas as gpd
import io
import base64
import logging
import traceback
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.patches import Patch, Rectangle
from matplotlib.lines import Line2D
from data_utils import get_area_name
from PIL import Image
import numpy as np


def optimize_marker_image(image_data):
    """Otimiza imagem do marcador."""
    try:
        # Configurações
        MAX_IMAGE_SIZE = (32, 32)  # Tamanho máximo do ícone
        MAX_FILE_SIZE = 5 * 1024  # 5 KB

        if not image_data:
            return None
            
        # Decodifica a imagem base64
        content_type, content_string = image_data.split(',')
        decoded = base64.b64decode(content_string)
        
        # Verifica tamanho do arquivo
        if len(decoded) > MAX_FILE_SIZE:
            # Abre e otimiza a imagem
            with Image.open(io.BytesIO(decoded)) as img:
                # Converte para RGBA se necessário
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # Redimensiona mantendo proporção
                img.thumbnail(MAX_IMAGE_SIZE, Image.LANCZOS)
                
                # Salva com otimização
                output = io.BytesIO()
                img.save(output, format='PNG', optimize=True, 
                        quality=85)
                output.seek(0)
                
                # Converte de volta para base64
                optimized = base64.b64encode(output.getvalue()).decode('utf-8')
                return f'data:image/png;base64,{optimized}'
                
        return image_data
        
    except Exception as e:
        logger.error(f"Erro ao otimizar imagem: {str(e)}")
        traceback.print_exc()
        return None

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_base_map():
    """Obtém o mapa base do Brasil."""
    try:
        url_br = "https://servicodados.ibge.gov.br/api/v3/malhas/paises/BR?intrarregiao=UF&formato=application/vnd.geo+json"
        logger.info(f"Requisitando mapa base: {url_br}")
        
        response = requests.get(url_br)
        if response.status_code != 200:
            logger.error(f"Erro ao carregar mapa base. Status: {response.status_code}")
            return None, "Erro ao carregar o mapa. Tente novamente mais tarde."
            
        data_br = response.json()
        gdf_br = gpd.GeoDataFrame.from_features(data_br['features'])
        return gdf_br, None
        
    except Exception as e:
        logger.error(f"Erro ao obter mapa base: {str(e)}")
        traceback.print_exc()
        return None, "Erro ao processar dados do mapa."

def generate_base_map(gdf, color_map='#044c6d', color_border='#ffffff', border_thickness=1, show_axes=False):
    """Gera um mapa base com as configurações especificadas."""
    try:
        fig, ax = plt.subplots(figsize=(15, 15), dpi=300)
        
        if border_thickness == 0:
            gdf.plot(ax=ax, color=color_map, edgecolor='none')
        else:
            gdf.plot(ax=ax, color=color_map, edgecolor=color_border, linewidth=border_thickness)
            
        if not show_axes:
            ax.set_axis_off()
        
        legend_ax = fig.add_axes([0.90, 0.15, 0.15, 0.70])
        legend_ax.set_axis_off()
        
        return fig, ax, legend_ax
        
    except Exception as e:
        logger.error(f"Erro ao gerar mapa base: {str(e)}")
        traceback.print_exc()
        return None, None, None

def save_fig_to_buffer(fig):
    """Salva a figura em um buffer e retorna como base64."""
    try:
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=300)
        buf.seek(0)
        encoded_image = base64.b64encode(buf.getvalue()).decode('ascii')
        plt.close(fig)
        return f'data:image/png;base64,{encoded_image}'
        
    except Exception as e:
        logger.error(f"Erro ao salvar figura: {str(e)}")
        traceback.print_exc()
        return None

def add_legend(legend_ax, area_name, marker_style=None, marker_color=None, layer_name=None, 
               marker_image=None, color_map='#044c6d', show_legend=True, show_compass=True):
    """Adiciona legenda ao mapa."""
    if not show_legend:
        legend_ax.clear()
        legend_ax.set_axis_off()
        return

    try:
        handles = []
        labels = []
        
        handles.append(Patch(facecolor=color_map, edgecolor='none'))
        labels.append(area_name)
        
        if marker_image:
            content_type, content_string = marker_image.split(',')
            img_data = base64.b64decode(content_string)
            img = plt.imread(io.BytesIO(img_data), format='png')
            img_handle = Rectangle((0, 0), 1, 1, fc="none", ec="none")
            labels.append(layer_name)
            handles.append(img_handle)
            
            imagebox = OffsetImage(img, zoom=0.1)
            ab = AnnotationBbox(imagebox, (0.5, 0.5), frameon=False, box_alignment=(0.5, 0.5))
            legend_ax.add_artist(ab)
        elif marker_style and marker_color and layer_name:
            handles.append(Line2D([0], [0], marker=marker_style, color='w', 
                                markerfacecolor=marker_color, markersize=10))
            labels.append(layer_name)
        
        legend = legend_ax.legend(handles, labels, title='Legenda', loc='center',
                                fontsize=14, frameon=True, fancybox=True,
                                shadow=True, title_fontsize=14)
        
        if show_compass:
            try:
                compass_rose = plt.imread('assets/compass_rose.png')
                compass_ax = legend_ax.inset_axes([0.3, 0.0, 0.5, 0.3], transform=legend_ax.transAxes)
                compass_ax.imshow(compass_rose)
                compass_ax.axis('off')
            except Exception as e:
                logger.error(f"Erro ao adicionar rosa dos ventos: {str(e)}")
                
    except Exception as e:
        logger.error(f"Erro ao adicionar legenda: {str(e)}")
        traceback.print_exc()

def generate_specific_map(url):
    """Gera mapa específico a partir de uma URL."""
    try:
        logger.info(f"Requisitando mapa: {url}")
        response = requests.get(url)
        
        if response.status_code != 200:
            logger.error(f"Erro na requisição. Status: {response.status_code}")
            return None, f"Erro ao carregar o mapa. Status: {response.status_code}"
            
        data = response.json()
        if not data.get('features'):
            logger.error("Dados recebidos não contêm features")
            return None, "Dados do mapa inválidos"
            
        # Criar GeoDataFrame com CRS explícito
        gdf = gpd.GeoDataFrame.from_features(data['features'])
        gdf.set_crs("EPSG:4326", inplace=True)
        
        if len(gdf) == 0:
            logger.error("GeoDataFrame vazio")
            return None, "Dados do mapa vazios"
            
        return gdf, None
        
    except Exception as e:
        logger.error(f"Erro ao gerar mapa específico: {str(e)}")
        traceback.print_exc()
        return None, str(e)

def generate_brazil_map(color_map='#044c6d', color_border='#ffffff', border_thickness=1,
                       show_axes=False, show_legend=True, show_compass=True):
    """Gera mapa do Brasil."""
    try:
        logger.info("Gerando mapa do Brasil")
        gdf_br, error = get_base_map()
        
        if error:
            return error, None
            
        fig, ax, legend_ax = generate_base_map(gdf_br, color_map, color_border,
                                             border_thickness, show_axes)
                                             
        if fig is None:
            return None, None
            
        add_legend(legend_ax, 'Brasil', color_map=color_map,
                  show_legend=show_legend, show_compass=show_compass)
                  
        return save_fig_to_buffer(fig), gdf_br
        
    except Exception as e:
        logger.error(f"Erro ao gerar mapa do Brasil: {str(e)}")
        traceback.print_exc()
        return None, None

def generate_region_map(region_id, color_map='#044c6d', color_border='#ffffff',
                       border_thickness=1, show_axes=False, show_legend=True, show_compass=True):
    """Gera mapa de região."""
    try:
        url_region = f"https://servicodados.ibge.gov.br/api/v3/malhas/regioes/{region_id}?intrarregiao=UF&formato=application/vnd.geo+json"
        gdf_region, error = generate_specific_map(url_region)
        
        if error:
            return error, None
            
        fig, ax, legend_ax = generate_base_map(gdf_region, color_map, color_border,
                                             border_thickness, show_axes)
                                             
        if fig is None:
            return None, None
            
        region_name = get_area_name('region', region_id)
        add_legend(legend_ax, region_name, color_map=color_map,
                  show_legend=show_legend, show_compass=show_compass)
                  
        return save_fig_to_buffer(fig), gdf_region
        
    except Exception as e:
        logger.error(f"Erro ao gerar mapa da região: {str(e)}")
        traceback.print_exc()
        return None, None

def generate_uf_with_municipios_map(uf_id, color_map='#044c6d', color_border='#ffffff',
                                  border_thickness=1, show_axes=False, show_legend=True,
                                  show_compass=True):
    """Gera mapa de UF com municípios."""
    try:
        url_uf = f"https://servicodados.ibge.gov.br/api/v3/malhas/estados/{uf_id}?intrarregiao=municipio&formato=application/vnd.geo+json"
        gdf_uf, error = generate_specific_map(url_uf)
        
        if error:
            return error, None
            
        fig, ax, legend_ax = generate_base_map(gdf_uf, color_map, color_border,
                                             border_thickness, show_axes)
                                             
        if fig is None:
            return None, None
            
        uf_name = get_area_name('uf', uf_id)
        add_legend(legend_ax, uf_name, color_map=color_map,
                  show_legend=show_legend, show_compass=show_compass)
                  
        return save_fig_to_buffer(fig), gdf_uf
        
    except Exception as e:
        logger.error(f"Erro ao gerar mapa da UF: {str(e)}")
        traceback.print_exc()
        return None, None

def generate_municipio_map(municipio_id, color_map='#044c6d', color_border='#ffffff',
                         border_thickness=1, show_axes=False, show_legend=True,
                         show_compass=True):
    """Gera mapa de município."""
    try:
        url_municipio = f"https://servicodados.ibge.gov.br/api/v3/malhas/municipios/{municipio_id}?formato=application/vnd.geo+json"
        gdf_municipio, error = generate_specific_map(url_municipio)
        
        if error:
            return error, None
            
        fig, ax, legend_ax = generate_base_map(gdf_municipio, color_map, color_border,
                                             border_thickness, show_axes)
                                             
        if fig is None:
            return None, None
            
        municipio_name = get_area_name('municipio', municipio_id)
        add_legend(legend_ax, municipio_name, color_map=color_map,
                  show_legend=show_legend, show_compass=show_compass)
                  
        return save_fig_to_buffer(fig), gdf_municipio
        
    except Exception as e:
        logger.error(f"Erro ao gerar mapa do município: {str(e)}")
        traceback.print_exc()
        return None, None

def filter_points_by_area(latitudes, longitudes, gdf_area):
    """Filtra pontos pela área do mapa."""
    try:
        # Converter para arrays numpy se não forem
        latitudes = np.array(latitudes)
        longitudes = np.array(longitudes)
        
        # Criar pontos geométricos
        points = [Point(float(lon), float(lat)) for lon, lat in zip(longitudes, latitudes)]
        
        # Criar GeoSeries com CRS definido (WGS84)
        points_gdf = gpd.GeoSeries(points, crs="EPSG:4326")
        
        # Se gdf_area não tem CRS definido, definir como WGS84
        if gdf_area.crs is None:
            gdf_area.set_crs("EPSG:4326", inplace=True)
            
        # Filtrar pontos
        mask = points_gdf.within(gdf_area.unary_union)
        return latitudes[mask], longitudes[mask]
        
    except Exception as e:
        logger.error(f"Erro ao filtrar pontos: {str(e)}")
        traceback.print_exc()
        # Em caso de erro, retornar todos os pontos
        return latitudes, longitudes

def add_points_to_map(gdf_base, latitudes, longitudes, marker_style, color_map='#044c6d',
                     color_border='#ffffff', color_marker='#f9b347', marker_size=1,
                     border_thickness=1, show_axes=False, layer_name='Pontos',
                     marker_image=None, area_name='Área', show_legend=True,
                     show_compass=True):
    """Adiciona pontos ao mapa."""
    try:
        fig, ax, legend_ax = generate_base_map(gdf_base, color_map, color_border,
                                             border_thickness, show_axes)
                                             
        if fig is None:
            return None
        
        if marker_image:
            content_type, content_string = marker_image.split(',')
            img_data = base64.b64decode(content_string)
            img = plt.imread(io.BytesIO(img_data), format='png')
            
            # Calcular zoom baseado no tamanho do mapa
            bounds = gdf_base.total_bounds
            map_width = bounds[2] - bounds[0]  # longitude
            
            # Ajustar zoom base no tamanho do mapa
            base_zoom = map_width / 100  # Fator de escala base
            icon_zoom = marker_size * base_zoom  # Ajuste pelo slider
            
            for lon, lat in zip(longitudes, latitudes):
                imagebox = OffsetImage(img, zoom=icon_zoom)
                ab = AnnotationBbox(imagebox, (lon, lat), frameon=False,
                                  box_alignment=(0.5, 0.5),  # Centralizar
                                  pad=0)  # Sem padding
                ax.add_artist(ab)
        elif len(latitudes) > 0 and len(longitudes) > 0:
            ax.scatter(longitudes, latitudes, c=color_marker,
                      s=(marker_size * 10)**2, marker=marker_style)
        
        add_legend(legend_ax, area_name, marker_style, color_marker,
                  layer_name, marker_image, color_map=color_map,
                  show_legend=show_legend, show_compass=show_compass)
                  
        return save_fig_to_buffer(fig)
        
    except Exception as e:
        logger.error(f"Erro ao adicionar pontos ao mapa: {str(e)}")
        traceback.print_exc()
        return None
