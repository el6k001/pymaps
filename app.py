import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
from layout import app_layout
from data_utils import get_regions, get_ufs_by_region, get_all_municipios, get_municipios_by_uf, get_ufs, load_data_from_contents, get_area_name
from map_utils import generate_brazil_map, generate_region_map, generate_uf_with_municipios_map, generate_municipio_map, add_points_to_map, filter_points_by_area

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, '/assets/styles.css'])
app.layout = app_layout
server = app.server


@app.callback(
    Output('uf-dropdown', 'options'),
    [Input('regiao-dropdown', 'value')]
)
def update_uf_dropdown(region_id):
    if not region_id:
        return get_ufs()
    return get_ufs_by_region(region_id)

@app.callback(
    Output('regiao-dropdown', 'value'),
    [Input('uf-dropdown', 'value'),
     Input('municipios-dropdown', 'value')]
)
def clear_region_selection(uf_id, municipio_id):
    return None

@app.callback(
    Output('uf-dropdown', 'value'),
    [Input('municipios-dropdown', 'value')]
)
def clear_uf_selection(municipio_id):
    return None

@app.callback(
    Output('municipios-dropdown', 'options'),
    [Input('uf-dropdown', 'value')]
)
def update_municipios_dropdown(uf_id):
    if not uf_id:
        return get_all_municipios()
    return get_municipios_by_uf(uf_id)

@app.callback(
    [Output('uploaded-data-store', 'data'),
     Output('latitude-column', 'options'),
     Output('longitude-column', 'options')],
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')]
)
def store_uploaded_data(contents, filename):
    if contents is not None:
        df = load_data_from_contents(contents, filename)
        if df is None:
            return None, [], []
        options = [{'label': col, 'value': col} for col in df.columns]
        return df.to_dict('records'), options, options
    return None, [], []

@app.callback(
    Output('uploaded-marker-image-store', 'data'),
    [Input('upload-marker-image', 'contents')],
    [State('upload-marker-image', 'filename')]
)
def store_uploaded_marker_image(contents, filename):
    if contents is not None:
        return contents
    return None

@app.callback(
    Output('mapa', 'src'),
    [Input('pais-dropdown', 'value'),
     Input('regiao-dropdown', 'value'),
     Input('uf-dropdown', 'value'),
     Input('municipios-dropdown', 'value'),
     Input('uploaded-data-store', 'data'),
     Input('uploaded-marker-image-store', 'data'),
     Input('add-points-button', 'n_clicks'),
     Input('color-map-picker', 'value'),
     Input('color-border-picker', 'value'),
     Input('color-marker-picker', 'value'),
     Input('marker-size-slider', 'value'),
     Input('border-thickness-slider', 'value'),
     Input('toggle-axes', 'value'),
     Input('toggle-legends', 'value'),
     Input('toggle-compass', 'value')],
    [State('latitude-column', 'value'),
     State('longitude-column', 'value'),
     State('marker-symbol', 'value'),
     State('layer-name-input', 'value')]
)
def update_map(pais, region_id, uf_id, municipio_id, data, marker_image, n_clicks, color_map, color_border, color_marker, marker_size, border_thickness, show_axes, show_legends, show_compass, lat_col, lon_col, marker_style, layer_name):
    color_map_hex = color_map if color_map else '#044c6d'
    # color_map_hex = color_map
    color_border_hex = color_border
    color_marker_hex = color_marker

    if municipio_id:
        area_name = get_area_name('municipio', municipio_id)
        map_image, gdf_area = generate_municipio_map(municipio_id, color_map_hex, color_border_hex, border_thickness, show_axes, show_legends, show_compass)
    elif uf_id:
        area_name = get_area_name('uf', uf_id)
        map_image, gdf_area = generate_uf_with_municipios_map(uf_id, color_map_hex, color_border_hex, border_thickness, show_axes, show_legends, show_compass)
    elif region_id:
        area_name = get_area_name('region', region_id)
        map_image, gdf_area = generate_region_map(region_id, color_map_hex, color_border_hex, border_thickness, show_axes, show_legends, show_compass)
    else:
        area_name = 'Brasil'
        map_image, gdf_area = generate_brazil_map(color_map_hex, color_border_hex, border_thickness, show_axes, show_legends, show_compass)

    if data is not None and lat_col is not None and lon_col is not None:
        df = pd.DataFrame(data)
        latitudes = df[lat_col]
        longitudes = df[lon_col]

        filtered_latitudes, filtered_longitudes = filter_points_by_area(latitudes, longitudes, gdf_area)

        map_image = add_points_to_map(gdf_area, filtered_latitudes, filtered_longitudes, marker_style, color_map_hex, color_border_hex, color_marker_hex, marker_size, border_thickness, show_axes, layer_name, marker_image, area_name, show_legends, show_compass)

    return map_image

@app.callback(
    Output("download-map", "data"),
    Input("download-map-link", "n_clicks"),
    State("mapa", "src"),
    prevent_initial_call=True,
)
def download_map(n_clicks, src):
    if n_clicks is None:
        return None
    
    img_data = src.split(',')[1]
    
    return dict(content=img_data, filename="mapa.png", type="image/png", base64=True)

if __name__ == '__main__':
    app.run_server(debug=True)
