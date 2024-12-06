import requests
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
import io
import base64
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.patches import Patch, Rectangle
from matplotlib.lines import Line2D
from data_utils import get_area_name

def get_base_map():
    url_br = "https://servicodados.ibge.gov.br/api/v3/malhas/paises/BR?intrarregiao=UF&formato=application/vnd.geo+json"
    response_br = requests.get(url_br)
    if response_br.status_code != 200:
        return None, "Erro ao carregar o mapa. Tente novamente mais tarde."
    try:
        data_br = response_br.json()
    except requests.exceptions.JSONDecodeError:
        return None, "Erro ao decodificar a resposta da API. Verifique a conexão e tente novamente."
    gdf_br = gpd.GeoDataFrame.from_features(data_br['features'])
    return gdf_br, None


def generate_base_map(gdf, color_map='#044c6d', color_border='#ffffff', border_thickness=1, show_axes=False):
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

def save_fig_to_buffer(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=300)
    buf.seek(0)
    encoded_image = base64.b64encode(buf.getvalue()).decode('ascii')
    plt.close(fig)
    return f'data:image/png;base64,{encoded_image}'

def add_legend(legend_ax, area_name, marker_style=None, marker_color=None, layer_name=None, marker_image=None, color_map='#044c6d', show_legend=True, show_compass=True):
    if not show_legend:
        legend_ax.clear()
        legend_ax.set_axis_off()
        return

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
        handles.append(Line2D([0], [0], marker=marker_style, color='w', markerfacecolor=marker_color, markersize=10))
        labels.append(layer_name)
    
    legend = legend_ax.legend(handles, labels, title='Legenda', loc='center', fontsize=14, frameon=True,
                              fancybox=True, shadow=True, title_fontsize=14)
    
    frame = legend.get_frame()
    frame.set_facecolor('white')
    frame.set_edgecolor('gray')

    if show_compass:
        compass_rose = plt.imread('assets/compass_rose.png')
        compass_ax = legend_ax.inset_axes([0.3, 0.0, 0.5, 0.3], transform=legend_ax.transAxes)
        compass_ax.imshow(compass_rose)
        compass_ax.axis('off')

def generate_specific_map(url):
    response = requests.get(url)
    if response.status_code != 200:
        return None, "Erro ao carregar o mapa. Tente novamente mais tarde."
    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        return None, "Erro ao decodificar a resposta da API. Verifique a conexão e tente novamente."
    gdf = gpd.GeoDataFrame.from_features(data['features'])
    return gdf, None

def generate_brazil_map(color_map='#044c6d', color_border='#ffffff', border_thickness=1, show_axes=False, show_legend=True, show_compass=True):
    gdf_br, error = get_base_map()
    if error:
        return error, None
    fig, ax, legend_ax = generate_base_map(gdf_br, color_map, color_border, border_thickness, show_axes)
    add_legend(legend_ax, 'Brasil', color_map=color_map, show_legend=show_legend, show_compass=show_compass)
    return save_fig_to_buffer(fig), gdf_br

def generate_region_map(region_id, color_map='#044c6d', color_border='#ffffff', border_thickness=1, show_axes=False, show_legend=True, show_compass=True):
    url_region = f"https://servicodados.ibge.gov.br/api/v3/malhas/regioes/{region_id}?intrarregiao=UF&formato=application/vnd.geo+json"
    gdf_region, error = generate_specific_map(url_region)
    if error:
        return error, None
    fig, ax, legend_ax = generate_base_map(gdf_region, color_map, color_border, border_thickness, show_axes)
    region_name = get_area_name('region', region_id)
    add_legend(legend_ax, region_name, color_map=color_map, show_legend=show_legend, show_compass=show_compass)
    return save_fig_to_buffer(fig), gdf_region

def generate_uf_with_municipios_map(uf_id, color_map='#044c6d', color_border='#ffffff', border_thickness=1, show_axes=False, show_legend=True, show_compass=True):
    url_uf = f"https://servicodados.ibge.gov.br/api/v3/malhas/estados/{uf_id}?intrarregiao=municipio&formato=application/vnd.geo+json"
    gdf_uf, error = generate_specific_map(url_uf)
    if error:
        return error, None
    fig, ax, legend_ax = generate_base_map(gdf_uf, color_map, color_border, border_thickness, show_axes)
    uf_name = get_area_name('uf', uf_id)
    add_legend(legend_ax, uf_name, color_map=color_map, show_legend=show_legend, show_compass=show_compass)
    return save_fig_to_buffer(fig), gdf_uf

def generate_municipio_map(municipio_id, color_map='#044c6d', color_border='#ffffff', border_thickness=1, show_axes=False, show_legend=True, show_compass=True):
    url_municipio = f"https://servicodados.ibge.gov.br/api/v3/malhas/municipios/{municipio_id}?formato=application/vnd.geo+json"
    gdf_municipio, error = generate_specific_map(url_municipio)
    if error:
        return error, None
    fig, ax, legend_ax = generate_base_map(gdf_municipio, color_map, color_border, border_thickness, show_axes)
    municipio_name = get_area_name('municipio', municipio_id)
    add_legend(legend_ax, municipio_name, color_map=color_map, show_legend=show_legend, show_compass=show_compass)
    return save_fig_to_buffer(fig), gdf_municipio

def filter_points_by_area(latitudes, longitudes, gdf_area):
    points = gpd.GeoSeries([Point(lon, lat) for lon, lat in zip(longitudes, latitudes)])
    mask = points.within(gdf_area.unary_union)
    return latitudes[mask], longitudes[mask]

def add_points_to_map(gdf_base, latitudes, longitudes, marker_style, color_map='#044c6d', color_border='#ffffff', color_marker='#f9b347', marker_size=1, border_thickness=1, show_axes=False, layer_name='Pontos', marker_image=None, area_name='Área', show_legend=True, show_compass=True):
    fig, ax, legend_ax = generate_base_map(gdf_base, color_map, color_border, border_thickness, show_axes)
    
    if marker_image:
        content_type, content_string = marker_image.split(',')
        img_data = base64.b64decode(content_string)
        img = plt.imread(io.BytesIO(img_data), format='png')
        
        for lon, lat in zip(longitudes, latitudes):
            imagebox = OffsetImage(img, zoom=marker_size/20)
            ab = AnnotationBbox(imagebox, (lon, lat), frameon=False)
            ax.add_artist(ab)
    elif len(latitudes) > 0 and len(longitudes) > 0:
        ax.scatter(longitudes, latitudes, c=color_marker, s=(marker_size * 10)**2, marker=marker_style)
    
    add_legend(legend_ax, area_name, marker_style, color_marker, layer_name, marker_image, color_map=color_map, show_legend=show_legend, show_compass=show_compass)
    return save_fig_to_buffer(fig)