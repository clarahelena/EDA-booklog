import itertools
from collections import Counter
import pandas as pd
import plotly.express as px
from dash import dcc, html
from components import vg_callbacks

BG_CARD  = '#1e293b'
ACCENT   = '#a3e635'
TEXT     = '#f8fafc'
MUTED    = '#94a3b8'
TEMPLATE = 'plotly_dark'
TRANSP   = 'rgba(0,0,0,0)'

CARD_STYLE = {
    'backgroundColor': BG_CARD,
    'padding': '24px',
    'borderRadius': '12px',
    'border': '1px solid #334155',
}

# render – função chamada pelo app.py
def render(app, df: pd.DataFrame):
    df_valido = df[(df['pages'] > 0) & (df['rating'] > 0)].copy()

    todos_generos = list(itertools.chain.from_iterable(df['generos_lista']))
    top_generos   = [g for g, _ in Counter(todos_generos).most_common(100)]
    lista_autores = sorted(df['author'].dropna().unique())
    min_paginas = int(df_valido['pages'].min())
    max_paginas = int(df_valido['pages'].max())
    min_nota    = 0.0
 
    # registra os callbacks
    vg_callbacks.registrar(app, df, df_valido, top_generos, lista_autores, min_paginas, max_paginas, min_nota)

    # layout da página
    layout = html.Div(
        style={'color': TEXT},
        children=[
            # cabeçalho
            html.H1("🌐 Visão Geral da Plataforma",
                    style={'textAlign': 'center', 'marginBottom': '8px', 'color': ACCENT}),
            html.P("Explore o catálogo usando os filtros abaixo.",
                   style={'textAlign': 'center', 'color': MUTED, 'marginBottom': '28px', 'fontSize': '15px'}),
            
            # painel de filtros
            html.Div(
                style={**CARD_STYLE, 'marginBottom': '28px', 'overflowX': 'auto'},
                children=[
                    html.H3("🔍 Filtros", style={'color': ACCENT, 'marginBottom': '16px', 'fontSize': '16px'}),
                    html.Div(
                        style={'display': 'flex', 'gap': '16px', 'flexWrap': 'wrap', 'alignItems': 'flex-end'},
                        children=[
                            html.Div([
                                html.Label("Gênero:", style={'display': 'block', 'marginBottom': '5px', 'fontSize': '13px', 'color': MUTED}),
                                dcc.Dropdown(id='vg-genre', placeholder="Todos os gêneros",
                                    options=[{'label': g, 'value': g} for g in top_generos],
                                    clearable=True, style={'width': '200px', 'color': '#000'})
                            ]),
                            html.Div([
                                html.Label("Autor:", style={'display': 'block', 'marginBottom': '5px', 'fontSize': '13px', 'color': MUTED}),
                                dcc.Dropdown(id='vg-author', placeholder="Todos os autores",
                                    options=[], searchable=True, clearable=True,
                                    style={'width': '220px', 'color': '#000'})
                            ]),
                            html.Div([
                                html.Label("Páginas:", style={'display': 'block', 'marginBottom': '5px', 'fontSize': '13px', 'color': MUTED}),
                                html.Div([
                                    dcc.Input(id='vg-min-pages', type='number', placeholder='Mín',
                                        value=min_paginas, min=min_paginas, max=max_paginas,
                                        style={'width': '120px', 'padding': '4px 8px', 'height': '42px', 'borderRadius': '4px', 'color': '#000', 'fontSize': '14px', 'boxSizing': 'border-box', 'marginRight': '6px'}),
                                    dcc.Input(id='vg-max-pages', type='number', placeholder='Máx',
                                        value=max_paginas, min=min_paginas, max=max_paginas,
                                        style={'width': '150px', 'padding': '4px 8px', 'height': '42px', 'borderRadius': '4px', 'color': '#000', 'fontSize': '14px', 'boxSizing': 'border-box'}),
                                ], style={'display': 'flex'})
                            ]),
                            html.Div([
                                html.Label("Nota:", style={'display': 'block', 'marginBottom': '5px', 'fontSize': '13px', 'color': MUTED}),
                                html.Div([
                                    dcc.Input(id='vg-min-rating', type='number', placeholder='Mín',
                                        value=min_nota, min=0, max=5, step=0.1,
                                        style={'width': '100px', 'padding': '4px 8px', 'height': '42px', 'borderRadius': '4px', 'color': '#000', 'fontSize': '14px', 'boxSizing': 'border-box', 'marginRight': '6px'}),
                                    dcc.Input(id='vg-max-rating', type='number', placeholder='Máx',
                                        value=5.0, min=0, max=5, step=0.1,
                                        style={'width': '100px', 'padding': '4px 8px', 'height': '42px', 'borderRadius': '4px', 'color': '#000', 'fontSize': '14px', 'boxSizing': 'border-box'}),
                                ], style={'display': 'flex'})
                            ]),
                            html.Div([
                                html.Button("✕ Limpar filtros", id='vg-clear', n_clicks=0,
                                    style={'padding': '9px 16px', 'backgroundColor': '#334155',
                                           'color': TEXT, 'border': 'none', 'borderRadius': '6px',
                                           'cursor': 'pointer', 'fontSize': '13px'})
                            ], style={'alignSelf': 'flex-end'}),
                        ]
                    )
                ]
            ),


            # KPI cards
            html.Div(id='vg-kpi-row',
                style={'display': 'flex', 'gap': '16px', 'flexWrap': 'wrap', 'marginBottom': '32px'}),

            # linha 1: histograma + rosca
            html.Div(
                style={'display': 'flex', 'gap': '20px', 'marginBottom': '24px', 'flexWrap': 'wrap'},
                children=[
                    html.Div(style={**CARD_STYLE, 'flex': '1', 'minWidth': '320px'},
                             children=[dcc.Graph(id='vg-hist')]),
                ]
            ),
            
            # linha 2: scatter comunidade
            html.Div(
                style={'display': 'flex', 'gap': '20px', 'marginBottom': '24px', 'flexWrap': 'wrap'},
                children=[
                    html.Div(style={**CARD_STYLE, 'flex': '2', 'minWidth': '320px'},
                             children=[
                                 html.P("💡 Clique em um livro para ver detalhes",
                                        style={'color': MUTED, 'fontSize': '12px', 'marginBottom': '4px'}),
                                 dcc.Graph(id='vg-rosca'),
                             ]),
                ]
            ),

            # linha 3: scatter autores
            html.Div(
                style={'display': 'flex', 'gap': '20px', 'flexWrap': 'wrap'},
                children=[
                    html.Div(style={**CARD_STYLE, 'flex': '1', 'minWidth': '320px'},
                             children=[
                                 html.P("💡 Clique em um autor para filtrar os gráficos",
                                        style={'color': MUTED, 'fontSize': '12px', 'marginBottom': '4px'}),
                                 dcc.Graph(id='vg-autores')
                                 ]),
                ]
            ),
            
            # linha 4: livros barra
            html.Div(
                style={'display': 'flex', 'gap': '20px', 'flexWrap': 'wrap'},
                children=[
                    html.Div(style={**CARD_STYLE, 'flex': '2', 'minWidth': '320px'},
                             children=[
                                 html.P("💡 Clique em um livro para ver detalhes",
                                        style={'color': MUTED, 'fontSize': '12px', 'marginBottom': '4px'}),
                                 dcc.Graph(id='vg-top-livros'),
                             ]),
                    html.Div(id='vg-book-card',
                        style={**CARD_STYLE, 'flex': '1', 'minWidth': '260px',
                               'overflowY': 'auto', 'maxHeight': '650px'},
                        children=[
                            html.P("Clique em um livro no gráfico para ver os detalhes.",
                                   style={'textAlign': 'center', 'color': '#64748b',
                                          'marginTop': '60px', 'fontSize': '14px'})
                        ]),
                ]
            ),
        ]
    )
    
    
    return layout