import os
import pandas as pd
import numpy as np
from dash import Dash, html, dcc, Input, Output
from components import scatter_relacao, barras_generos, visao_geral

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

# iniciamento do dashboard
app = Dash(__name__, suppress_callback_exceptions=True)

layout_analise = scatter_relacao.render(app, df)
layout_barras  = barras_generos.render(app, df)
layout_visao   = visao_geral.render(app, df)

# layout Global
app.layout = html.Div(
    style={'backgroundColor': '#0f172a', 'color': '#f8fafc', 'padding': '40px', 'minHeight': '100vh', 'fontFamily': 'system-ui, sans-serif'},
    children=[
        dcc.Location(id='url', refresh=False),

        html.Div(
            style={'backgroundColor': '#1e293b', 'padding': '16px 40px',
                   'display': 'flex', 'gap': '32px', 'alignItems': 'center',
                   'borderBottom': '2px solid #a3e635'},
            children=[
                html.Span("Booklog", style={'color': '#a3e635', 'fontWeight': 'bold', 'fontSize': '20px'}),
                dcc.Link("Visão Geral", href="/",
                    style={'color': '#94a3b8', 'textDecoration': 'none', 'fontSize': '15px'}),
                dcc.Link("Análise de Livros", href="/analise",
                    style={'color': '#94a3b8', 'textDecoration': 'none', 'fontSize': '15px'}),
            ]
        ),

        html.Div(id='page-content', style={'padding': '40px'})
    ]
)
 
@app.callback(Output('page-content', 'children'), Input('url', 'pathname'))
def render_page(pathname):
    if pathname == '/analise':
        return html.Div([
            html.H1("Análise de Livros", style={'textAlign': 'center', 'marginBottom': '40px', 'color': '#A3E635'}),
            layout_analise,
            layout_barras,
        ])
    return layout_visao


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8050)), debug=False)