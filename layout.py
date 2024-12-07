from dash import dcc, html
import dash_bootstrap_components as dbc
from data_utils import get_regions, get_all_municipios

# Componentes reutilizáveis
def create_error_alert(id_name):
    """Cria alerta de erro padronizado."""
    return dbc.Alert(
        id=id_name,
        is_open=False,
        duration=4000,
        color="danger",
        style={"position": "fixed", "top": 10, "right": 10, "zIndex": 1000}
    )

# Layout principal
app_layout = html.Div(className='dashboard-container', children=[
    # Navbar
    dbc.Navbar(
        dbc.Container([
            dbc.Row([
                dbc.Col(
                    html.A(
                        dbc.Row([
                            # Lazy loading para a logo
                            dbc.Col(
                                dcc.Loading(
                                    html.Img(src='assets/LogoSVG.svg', height="55px"),
                                    type="default"
                                ),
                                width="auto"
                            ),
                            dbc.Col(dbc.NavbarBrand("", className="ms-2"), width="auto"),
                        ],
                        align="center",
                        className="g-0"
                    ),
                    href="/",
                    style={"textDecoration": "none"},
                ),
                width="auto"
            ),
        ],
        justify="between",
        className="w-100",
        ),
    ], fluid=True),
    color="dark",
    dark=True,
    ),
    
    # Container principal
    dbc.Container([
        # Alertas de erro
        create_error_alert("upload-error"),
        create_error_alert("marker-upload-error"),
        create_error_alert("map-error"),
        
        dbc.Row([
            # Barra lateral
            dbc.Col([
                dbc.Accordion([
                    # Seleção de área
                    dbc.AccordionItem(
                        [
                            dbc.Row([
                                dbc.Col(
                                    dcc.Dropdown(
                                        id='pais-dropdown',
                                        options=[{'label': 'Brasil', 'value': 'Brasil'}],
                                        value='Brasil',
                                        placeholder='País',
                                        className='dropdown-selector'
                                    )
                                ),
                                dbc.Col(
                                    dcc.Dropdown(
                                        id='regiao-dropdown',
                                        options=get_regions(),
                                        placeholder='Região',
                                        className='dropdown-selector'
                                    )
                                ),
                            ], className="mb-3"),
                            dbc.Row([
                                dbc.Col(
                                    dcc.Dropdown(
                                        id='uf-dropdown',
                                        placeholder='UF',
                                        className='dropdown-selector'
                                    )
                                ),
                                dbc.Col(
                                    dcc.Dropdown(
                                        id='municipios-dropdown',
                                        options=get_all_municipios(),
                                        placeholder='Municípios',
                                        className='dropdown-selector'
                                    )
                                ),
                            ]),
                        ],
                        title="🗺️ Selecione a Área",
                        item_id="area-menu",
                    ),
                    
                    # Upload de dados
                    dbc.AccordionItem(
                        [
                            dbc.Alert([
                                html.Strong("Formatos aceitos:"),
                                html.Ul([
                                    html.Li("CSV, Excel (máx. 10 KB)"),
                                    html.Li("Máximo 1000 linhas"),
                                ]),
                            ], color="info", className="mb-3"),
                            
                            dcc.Upload(
                                id='upload-data',
                                children=dbc.Button(
                                    'Selecione ou arraste um arquivo',
                                    color="primary",
                                    className="w-100"
                                ),
                                className='upload-area mb-3'
                            ),
                            html.Div(id="upload-error-message", className="text-danger mb-2"),
                            
                            dcc.Store(id='uploaded-data-store'),
                            
                            html.Div([
                                html.Label("Colunas de Latitude e Longitude"),
                                dcc.Dropdown(
                                    id='latitude-column',
                                    placeholder='Latitude',
                                    className='mb-2'
                                ),
                                dcc.Dropdown(
                                    id='longitude-column',
                                    placeholder='Longitude',
                                    className='mb-2'
                                ),
                            ]),
                            
                            html.Div([
                                html.Label("Símbolo do marcador"),
                                dcc.Dropdown(
                                    id='marker-symbol',
                                    options=[
                                        {'label': 'Círculo', 'value': 'o'},
                                        {'label': 'Quadrado', 'value': 's'},
                                        {'label': 'Triângulo', 'value': '^'},
                                        {'label': 'Diamante', 'value': 'D'},
                                        {'label': 'Estrela', 'value': '*'}
                                    ],
                                    value='o',
                                    className='mb-2',
                                ),
                            ]),
                            
                            html.Div([
                                html.Label("Nome da camada de dados"),
                                dbc.Input(
                                    id='layer-name-input',
                                    type='text',
                                    placeholder='Nome da camada'
                                ),
                            ], className='mb-3'),
                            
                            html.Div([
                                html.Label("Ou faça upload de uma imagem para o marcador"),
                                dbc.Alert([
                                    "Requisitos da imagem:",
                                    html.Ul([
                                        html.Li("Formatos: PNG, JPG, GIF"),
                                        html.Li("Tamanho máximo: 32x32 pixels"),
                                        html.Li("Arquivo até 5 KB"),
                                    ]),
                                ], color="info", className="mb-2"),
                                
                                dcc.Upload(
                                    id='upload-marker-image',
                                    children=dbc.Button(
                                        'Selecione uma imagem',
                                        color="secondary",
                                        className="w-100"
                                    ),
                                    className='upload-area mb-3'
                                ),
                                html.Div(id="marker-upload-error", className="text-danger mb-2"),
                                dcc.Store(id='uploaded-marker-image-store'),
                            ]),
                            
                            dbc.Button(
                                'Adicionar pontos ao mapa',
                                id='add-points-button',
                                color='success',
                                className='w-100'
                            )
                        ],
                        title="📊 Adicione seus dados",
                    ),
                    
                    # Configurações
                    dbc.AccordionItem(
                        [
                            html.Label("Cores"),
                            dbc.Row([
                                dbc.Col(
                                    html.Div([
                                        html.Label("Mapa"),
                                        dbc.Input(
                                            type="color",
                                            id='color-map-picker',
                                            value='#044c6d'
                                        )
                                    ])
                                ),
                                dbc.Col(
                                    html.Div([
                                        html.Label("Bordas"),
                                        dbc.Input(
                                            type="color",
                                            id='color-border-picker',
                                            value='#ffffff'
                                        )
                                    ])
                                ),
                                dbc.Col(
                                    html.Div([
                                        html.Label("Marcadores"),
                                        dbc.Input(
                                            type="color",
                                            id='color-marker-picker',
                                            value='#f9b347'
                                        )
                                    ])
                                ),
                            ], className='mb-3'),
                            
                            html.Label("Tamanho do marcador"),
                            dcc.Slider(
                                id='marker-size-slider',
                                min=0.5,
                                max=5.0,
                                step=0.5,
                                value=1.0,
                                className='mb-3'
                            ),
                            
                            html.Label("Espessura das bordas"),
                            dcc.Slider(
                                id='border-thickness-slider',
                                min=0,
                                max=10,
                                step=0.5,
                                value=0.5,
                                className='mb-3'
                            ),
                            
                            dbc.Row([
                                dbc.Col([
                                    html.Label("Mostrar eixos"),
                                    dbc.Switch(id='toggle-axes', value=True),
                                ], width=4),
                                dbc.Col([
                                    html.Label("Mostrar legendas"),
                                    dbc.Switch(id='toggle-legends', value=True),
                                ], width=4),
                                dbc.Col([
                                    html.Label("Mostrar R. ventos"),
                                    dbc.Switch(id='toggle-compass', value=True),
                                ], width=4),
                            ], className='mb-3'),
                        ],
                        title="🎨 Configurações",
                    ),
                ], start_collapsed=True, always_open=True, active_item="area-menu"),
                
                # Informações do autor
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Autor", className="card-title"),
                        html.P("Carlos Alejandro Urzagasti"),
                        html.P([
                            "E-mail: ",
                            html.A(
                                "carlosalejandro.6k00@gmail.com",
                                href="mailto:carlosalejandro.6k00@gmail.com",
                                className="card-link"
                            )
                        ]),
                        html.A(
                            dcc.Loading(
                                html.Img(src="assets/linkedin.png", height="30px")
                            ),
                            href="https://www.linkedin.com/in/carlos-alejandro-u-023050144/",
                            target="_blank",
                            className="card-link"
                        ),
                    ])
                ], className="mt-3"),

                # Licenças
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Licenças e Atribuições", className="card-title"),
                        html.P([
                            "Dados: ",
                            html.A(
                                "IBGE",
                                href="https://www.ibge.gov.br/",
                                target="_blank"
                            ),
                            " (CC BY 4.0)"
                        ], className="mb-2"),
                        html.P([
                            "Desenvolvido com: ",
                            html.A(
                                "Python",
                                href="https://www.python.org/about/legal/",
                                target="_blank"
                            ),
                            " e ",
                            html.A(
                                "Dash",
                                href="https://plotly.com/dash/",
                                target="_blank"
                            ),
                            " (MIT)"
                        ], className="mb-0"),
                    ])
                ], className="mt-3"),

                # Doação
                dbc.Card([
                    dbc.CardBody([
                        html.H5("Apoie o Projeto", className="card-title"),
                        dcc.Loading(
                            html.Img(
                                src="assets/PIX.svg",
                                className="img-fluid mb-2",
                                style={"maxWidth": "85%", "width": "65%"}
                            )
                        ),
                        html.P(
                            "Ajude a manter este projeto online e gratuito!",
                            className="text-center"
                        ),
                    ])
                ], className="mt-3"),
            ], md=3),
        
            # Área do mapa
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        dcc.Loading(
                            html.Div([
                                html.Img(id='mapa', className="img-fluid")
                            ], className="map-container"),
                            type="default",
                            color="#044c6d"
                        ),
                        dbc.Button(
                            "BAIXAR MAPA",
                            id='download-map-link',
                            color="primary",
                            className="mt-3 w-100"
                        )
                    ])
                ])
            ], md=8)
        ])
    ], fluid=True, className="mt-3"),
    
    dcc.Download(id="download-map")
])
