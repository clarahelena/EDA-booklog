import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from scipy.stats import gaussian_kde
from collections import Counter
from dash import dcc, html, Input, Output
from components import storytelling

# --- ESTILOS GLOBAIS ---
BG_CARD  = '#FFFFFF'
ACCENT   = '#252525'
TEXT     = '#252525'
MUTED    = '#64748b'
TEMPLATE = 'plotly_white'

CARD_STYLE = {
    'backgroundColor': BG_CARD,
    'padding': '24px',
    'borderRadius': '12px',
    'border': '1px solid #E2E8F0',
    'boxShadow': '0px 4px 8px rgba(0, 0, 0, 0.05)',
    'marginBottom': '24px'
}

# --- REGRAS DO NOTEBOOK 03 ---
STOP_GENRES = {'Fiction', 'Literature', 'Books', 'Audiobook', 'Audiobooks', 'Nonfiction'}
PARETO_CUTOFF = 0.80
KDE_FORMAT_MIN_N = 50
PALETTE_PLOTLY = px.colors.qualitative.Prism

def processar_dados_hipoteses(df_bruto: pd.DataFrame):
    # Limpeza e deduplicação iguais ao notebook 03
    df_hip = df_bruto.dropna(subset=['isbn']).copy()
    df_hip = df_hip.drop_duplicates(subset=['isbn'])
    
    for col in ['pages', 'rating', 'reviews', 'totalratings']:
        df_hip[col] = pd.to_numeric(df_hip[col], errors='coerce')
        
    df_hip = df_hip.dropna(subset=['rating', 'totalratings', 'genre', 'bookformat'])
    
    # Tratamento da lista de gêneros (removendo Stop Genres)
    df_hip['genre_list'] = (
        df_hip['genre']
        .apply(lambda x: [g.strip() for g in str(x).split(',') if g.strip()])
        .apply(lambda x: list(dict.fromkeys(g for g in x if g not in STOP_GENRES)))
    )
    
    # Princípio de Pareto para pegar os gêneros mais relevantes
    all_genres = [g for sublist in df_hip['genre_list'] for g in sublist]
    genre_counts = Counter(all_genres)
    pareto_df = pd.DataFrame.from_dict(genre_counts, orient='index', columns=['Frequencia']).sort_values('Frequencia', ascending=False)
    pareto_df['Pct_Cumulativa'] = pareto_df['Frequencia'].cumsum() / pareto_df['Frequencia'].sum()
    
    top_genres = pareto_df[pareto_df['Pct_Cumulativa'] <= PARETO_CUTOFF].index.tolist()
    
    # Cálculo do limite de páginas via IQR e log_pages
    Q1_pages = df_hip['pages'].quantile(0.25)
    Q3_pages = df_hip['pages'].quantile(0.75)
    IQR_pages = Q3_pages - Q1_pages
    pages_min = max(1, int(Q1_pages - 1.5 * IQR_pages))
    pages_max = int(df_hip['pages'].quantile(0.99))
    
    df_hip['log_pages'] = np.where(
        df_hip['pages'].between(pages_min, pages_max),
        np.log10(df_hip['pages']),
        np.nan
    )
    
    # Formatos válidos para o KDE
    fmt_counts = df_hip['bookformat'].value_counts()
    formatos_validos = fmt_counts[fmt_counts >= KDE_FORMAT_MIN_N].index.tolist()
    
    return df_hip, top_genres, formatos_validos

def render(app, df_bruto: pd.DataFrame):
    df_hip, top_genres, formatos_validos = processar_dados_hipoteses(df_bruto)
    storytelling.register_callbacks(app)
    
    # selecao inicial para não carregar vazio
    formatos_iniciais = ['Paperback', 'Hardcover', 'ebook', 'Audio CD']
    formatos_iniciais = [f for f in formatos_iniciais if f in formatos_validos]
    if not formatos_iniciais: formatos_iniciais = formatos_validos[:4]
    
    @app.callback(
        Output('hip-kde-plot', 'figure'),
        Output('hip-stacked-bar', 'figure'),
        Input('hip-format-filter', 'value'),
        Input('hip-genre-filter', 'value')
    )
    def atualizar_graficos(formatos_selecionados, generos_selecionados):
        if not formatos_selecionados: formatos_selecionados = formatos_iniciais
        if not generos_selecionados: generos_selecionados = top_genres[:15]
        
        # grafico densidade por formato
        df_kde = df_hip[df_hip['bookformat'].isin(formatos_selecionados) & df_hip['log_pages'].notna()]
        
        fig_kde = go.Figure()
        if not df_kde.empty:
            x_range = np.linspace(df_kde['log_pages'].min(), df_kde['log_pages'].max(), 500)
            tickvals = [50, 100, 200, 300, 500, 1000, 2000]
            
            for i, fmt in enumerate(formatos_selecionados):
                subset = df_kde[df_kde['bookformat'] == fmt]['log_pages'].dropna()
                if len(subset) > 1:
                    try:
                        kde = gaussian_kde(subset, bw_method='scott')
                        y = kde(x_range)
                        color_line = PALETTE_PLOTLY[i % len(PALETTE_PLOTLY)]
                        
                        if color_line.startswith('rgb'):
                            color_fill = color_line.replace('rgb', 'rgba').replace(')', ', 0.15)')
                        else:
                            color_fill = px.colors.label_rgb(px.colors.hex_to_rgb(color_line) + (0.15,))
                        
                        fig_kde.add_trace(go.Scatter(
                            x=10**x_range, y=y, mode='lines', fill='tozeroy',
                            fillcolor=color_fill, line=dict(color=color_line, width=2),
                            name=f'{fmt} (n={len(subset):,})', opacity=0.9
                        ))
                    except Exception:
                        pass
                        
            fig_kde.update_layout(
                title='<b>Distribuição de páginas por formato — Densidade Relativa</b>',
                title_font=dict(weight=600),
                xaxis=dict(type='log', tickvals=tickvals, ticktext=[str(v) for v in tickvals], title='Páginas (Log)', gridcolor='#e0e0e0'),
                yaxis=dict(title='Densidade Relativa', showticklabels=False, gridcolor='#e0e0e0'),
                template=TEMPLATE, paper_bgcolor='#ffffff', plot_bgcolor='#ffffff',
                font=dict(color=TEXT), hovermode='x unified', legend=dict(title='Formato')
            )

        # Gráfico  Formatos por Gênero
        df_exploded = df_hip.explode('genre_list')
        df_exploded = df_exploded[df_exploded['genre_list'].isin(generos_selecionados)]
        
        if not df_exploded.empty:
            pivot = df_exploded.groupby(['genre_list', 'bookformat']).size().unstack(fill_value=0)
            pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100
            
            # Ordenar com base no formato mais frequente globalmente
            dominant_fmt = pivot_pct.sum(axis=0).idxmax()
            pivot_pct = pivot_pct.sort_values(dominant_fmt, ascending=True)
            
            fig_bar = go.Figure()
            for i, fmt in enumerate(pivot_pct.columns):
                fig_bar.add_trace(go.Bar(
                    name=fmt, x=pivot_pct[fmt].values, y=pivot_pct.index, orientation='h',
                    marker_color=PALETTE_PLOTLY[i % len(PALETTE_PLOTLY)],
                    hovertemplate='%{y}<br>' + fmt + ': %{x:.1f}%<extra></extra>'
                ))
                
            fig_bar.update_layout(
                barmode='stack',
                title='<b>Mix de formato por gênero</b>',
                title_font=dict(weight=600),
                xaxis=dict(title='Proporção (%)', range=[0, 100], ticksuffix='%', gridcolor='#e0e0e0'),
                yaxis=dict(title='', tickfont=dict(size=12), automargin=True),
                template=TEMPLATE, paper_bgcolor='#ffffff', plot_bgcolor='#ffffff',
                font=dict(color=TEXT), legend=dict(title='Formato', traceorder='normal'),
                margin=dict(l=150)
            )
        else:
            fig_bar = px.bar(title="Sem dados suficientes")

        return fig_kde, fig_bar

    # --- LAYOUT ---
    layout = html.Div(style={'color': TEXT}, children=[
        storytelling.storytelling_layout(),
        html.H1("Análise de Hipóteses", style={'textAlign': 'center', 'marginBottom': '8px', 'color': ACCENT, 'fontWeight': 'bold'}),
        html.P("Explorando a relação entre formatos físicos/digitais, tamanho das obras e preferências por gênero.",
               style={'textAlign': 'center', 'color': MUTED, 'marginBottom': '28px', 'fontSize': '15px'}),
        
        # Filtros
        html.Div(style=CARD_STYLE, children=[
            html.H3("Filtros Interativos", style={'color': ACCENT, 'marginBottom': '16px', 'fontSize': '16px', 'fontWeight': 'bold'}),
            html.Div(style={'display': 'flex', 'gap': '24px', 'flexWrap': 'wrap'}, children=[
                html.Div(style={'flex': '1', 'minWidth': '300px'}, children=[
                    html.Label("Comparar formatos (Gráfico KDE):", style={'display': 'block', 'marginBottom': '8px', 'fontWeight': 500}),
                    dcc.Dropdown(
                        id='hip-format-filter',
                        options=[{'label': f, 'value': f} for f in formatos_validos],
                        value=formatos_iniciais,
                        multi=True,
                        style={'color': '#000'}
                    )
                ]),
                html.Div(style={'flex': '1', 'minWidth': '300px'}, children=[
                    html.Label("Analisar gêneros (Mix 100%):", style={'display': 'block', 'marginBottom': '8px', 'fontWeight': 500}),
                    dcc.Dropdown(
                        id='hip-genre-filter',
                        options=[{'label': g, 'value': g} for g in top_genres],
                        value=top_genres[:15],
                        multi=True,
                        style={'color': '#000'}
                    )
                ])
            ])
        ]),
        
        # Gráficos
        html.Div(style=CARD_STYLE, children=[
            html.P("O formato dita o tamanho do livro?", style={'fontWeight': 'bold', 'marginBottom': '4px'}),
            html.P("O eixo de páginas utiliza escala logarítmica para conseguir mostrar livros pequenos e gigantes no mesmo gráfico de forma nítida e sem distorções.", style={'fontSize': '13px', 'color': MUTED, 'marginBottom': '16px'}),
            dcc.Graph(id='hip-kde-plot', style={'height': '500px'})
        ]),
        
        html.Div(style=CARD_STYLE, children=[
            html.P("O gênero dita a forma de consumo?", style={'fontWeight': 'bold', 'marginBottom': '4px'}),
            html.P("Proporção 100% empilhada confirmando a predominância da Brochura (Paperback).", style={'fontSize': '13px', 'color': MUTED, 'marginBottom': '16px'}),
            dcc.Graph(id='hip-stacked-bar', style={'height': '600px'})
        ])
    ])
    
    return layout