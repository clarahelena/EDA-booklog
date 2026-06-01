import os
import pandas as pd
import numpy as np
from dash import Dash, html, dcc, Input, Output
from components import scatter_relacao, barras_generos, rosca_formatos, visao_geral, analise_hipoteses, analise_comunidade, ml_clustering, ml_classificacao

# função para converter a string do parquet em uma lista
def extrair_generos(x):
    if pd.isna(x): return []
    if isinstance(x, str):
        x = x.replace('[', '').replace(']', '').replace("'", "")
        return [g.strip() for g in x.split(',') if g.strip()]
    if isinstance(x, (list, np.ndarray)):
        return [str(g).strip() for g in x if str(g).strip()]
    return []

# carregamento dos dados do dataset
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, '..', 'datasets', 'books.parquet')

try:
    df = pd.read_parquet(DATASET_PATH)
except FileNotFoundError:
    df = pd.read_parquet(os.path.join(BASE_DIR, 'datasets', 'books.parquet'))

df['generos_lista'] = df['genre'].apply(extrair_generos) 
external_stylesheets = ['https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap']
# iniciamento do dashboard
app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=external_stylesheets)

layout_analise = scatter_relacao.render(app, df)
layout_barras  = barras_generos.render(app, df)
layout_visao   = visao_geral.render(app, df)
layout_rosca = rosca_formatos.render(app, df)
layout_hipoteses = analise_hipoteses.render(app, df)
layout_comunidade = analise_comunidade.render(app, df)
layout_ml = ml_clustering.render(app, df)
layout_ml_class = ml_classificacao.render(app, df)

# layout Global
app.layout = html.Div(
    style={'backgroundColor': '#E9ECEF', 'color': "#252525", 'minHeight': '100vh', 'fontFamily': 'Poppins, sans-serif'},
    children=[
        dcc.Location(id='url', refresh=False),

        html.Div(
            style={'backgroundColor': '#FFFFFF', 'padding': '16px 40px',
                   'display': 'flex', 'gap': '32px', 'align  ': 'center',
                   'borderBottom': '2px solid #E3E3E3'},
            children=[
                html.Span("Booklog", style={'color': '#252525', 'fontWeight': '700', 'fontSize': '20px'}),
                dcc.Link("Visão Geral", href="/",
                    style={'color': '#252525', 'textDecoration': 'none', 'fontSize': '16px', 'fontWeight': '600'}),
                dcc.Link("Insight 1", href="/hipoteses",
                    style={'color': '#252525', 'textDecoration': 'none', 'fontSize': '16px', 'fontWeight': '600'}),
                dcc.Link("Insight 2", href="/comunidade",
                    style={'color': '#252525', 'textDecoration': 'none', 'fontSize': '16px', 'fontWeight': '600'}),
                dcc.Link("ML Clusterização", href="/ml",
                    style={'color': '#252525', 'textDecoration': 'none', 'fontSize': '16px', 'fontWeight': '600'}),
                dcc.Link("ML Classificação", href="/ml-classificacao",
                    style={'color': '#252525', 'textDecoration': 'none', 'fontSize': '16px', 'fontWeight': '600'}),
            ]
        ),

        html.Div(id='page-content', style={'padding': '20px 40px'})
    ]
)
 
@app.callback(Output('page-content', 'children'), Input('url', 'pathname'))
def render_page(pathname):
    
    # path insight 1
    if pathname == '/hipoteses':
        return layout_hipoteses
        
    # path insight 2
    elif pathname == '/comunidade':
        return layout_comunidade
    
    # path ML 1
    elif pathname == '/ml':
        return layout_ml
    
    elif pathname == '/ml-classificacao':
        return layout_ml_class
            
    # path da home
    return html.Div([
        html.H1("Visão Geral & Análise", style={'textAlign': 'center', 'marginBottom': '32px', 'color': '#252525', 'fontWeight': 'bold'}),
        
        layout_visao,
        layout_analise,
        html.Div(
            style={'display': 'flex', 'gap': '20px', 'width': '100%', 'height': '450px', 'alignItems': 'stretch', 'marginTop': '24px'},
            children=[
                html.Div(layout_barras, style={'width': '75%', 'height': '100%'}),
                html.Div(layout_rosca, style={'width': '25%', 'height': '100%'})
            ]
        )
    ])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8050)), debug=False)