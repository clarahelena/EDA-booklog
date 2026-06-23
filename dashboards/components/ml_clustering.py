import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from dash import html, dcc, Input, Output, dash_table
from components import storytelling

# ── paleta e nomes das tribos(clusters)
TRIBO_CONFIG = {
    0: {"nome": "Cluster 0 (Universo Geek & Fantasia)",   "cor": "#e41a1c"},
    1: {"nome": "Cluster 1 (Literatura Sênior & Ensaios)", "cor": "#377eb8"},
    2: {"nome": "Cluster 2 (Não-Ficção de Nicho & Lazer)","cor": "#4daf4a"},
    3: {"nome": "Cluster 3 (Romances Mainstream & Dramas)", "cor": "#ff7f00"},
}

# carregamento do parquet com os clusters
def _carregar_df_clusters(base_dir: str) -> pd.DataFrame | None:
    caminho_parquet = os.path.abspath(os.path.join(base_dir, '..', '..', 'Machine Learning', 'data', 'processed', 'livros_com_clusters.parquet'))
    if os.path.exists(caminho_parquet):
        return pd.read_parquet(caminho_parquet)
        
    caminho_csv = os.path.abspath(os.path.join(base_dir, '..', '..', 'Machine Learning', 'data', 'processed', 'livros_com_clusters.csv'))
    if os.path.exists(caminho_csv):
        return pd.read_csv(caminho_csv)
        
    return None

# ── Gráfico 0: Scatter plot Espacial SVD 
def _build_scatter(df_clusters: pd.DataFrame) -> go.Figure:
    df_sample = df_clusters.sample(min(10000, len(df_clusters)), random_state=42).copy()
    df_sample['Cluster_Nome'] = df_sample['Cluster'].map({k: v["nome"] for k, v in TRIBO_CONFIG.items()})
    cores_map = {v["nome"]: v["cor"] for k, v in TRIBO_CONFIG.items()}

    fig = px.scatter(
        df_sample, x='svd_x', y='svd_y', color='Cluster_Nome',
        hover_name='title', hover_data=['author', 'rating', 'pages'],
        category_orders={'Cluster_Nome': list(cores_map.keys())},
        color_discrete_map=cores_map,
        labels={'svd_x': 'Componente de Projeção SVD 1', 'svd_y': 'Componente de Projeção SVD 2'}
    )
    fig.update_traces(marker=dict(size=4, opacity=0.6, line=dict(width=0.2, color='DarkSlateGrey')))
    fig.update_layout(
        paper_bgcolor="#FFFFFF", plot_bgcolor="#F9FAFB", font_family="Poppins, sans-serif",
        legend=dict(title_text=None, orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=12, color="#1A1A1A", weight="bold")),
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(showgrid=True, gridcolor="#EBEBEB", zeroline=False, title_font=dict(color="#252525", size=12)),
        yaxis=dict(showgrid=True, gridcolor="#EBEBEB", zeroline=False, title_font=dict(color="#252525", size=12)),
        height=480,
    )
    return fig

# ── Gráfico 1: Distribuição dos Livros
def _build_bar_distribuicao(df: pd.DataFrame, cluster_id='Todos') -> go.Figure:
    dist_df = df['Cluster'].value_counts().reset_index()
    dist_df.columns = ['Cluster', 'Quantidade']
    dist_df['Percentual'] = (dist_df['Quantidade'] / len(df)) * 100 # Dividido pelo total do dataframe original
    
    dist_df['Nome_Curto'] = dist_df['Cluster'].map({i: f"Cluster {i}" for i in range(4)})
    dist_df['Nome_Longo'] = dist_df['Cluster'].map({k: v["nome"] for k, v in TRIBO_CONFIG.items()})
    
    cores_map = {v["nome"]: v["cor"] for k, v in TRIBO_CONFIG.items()}

    # Lógica de Filtro
    if cluster_id != 'Todos':
        dist_df = dist_df[dist_df['Cluster'] == cluster_id]

    fig = px.bar(
        dist_df, x='Nome_Curto', y='Quantidade',
        text=dist_df['Percentual'].apply(lambda x: f"{x:.1f}%"),
        color='Nome_Longo', color_discrete_map=cores_map,
        category_orders={'Nome_Curto': ['Cluster 0', 'Cluster 1', 'Cluster 2', 'Cluster 3']},
        labels={'Quantidade': 'Número de Livros', 'Nome_Curto': 'Cluster Literário', 'Nome_Longo': 'Legenda'}
    )
    fig.update_traces(textposition='outside', cliponaxis=False)
    
    # Mantém o eixo Y fixo mesmo filtrando
    max_y = df['Cluster'].value_counts().max() * 1.15
    fig.update_yaxes(range=[0, max_y], showgrid=True, gridcolor="#EBEBEB")
    
    fig.update_layout(
        paper_bgcolor="#FFFFFF", plot_bgcolor="#F9FAFB", font_family="Poppins, sans-serif",
        height=350, margin=dict(t=20, b=20, l=20, r=20),
        showlegend=(cluster_id == 'Todos'), # Esconde legenda se for um só
        legend=dict(title_text=None, orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig


# ── Gráfico 2: Presença de Gêneros
def _build_bar_generos(df: pd.DataFrame, cluster_id='Todos') -> go.Figure:
    genre_cols = [
        'Artes, Lazer e Estilo de Vida', 'Fantasia e Ficção Científica',
        'Ficção Geral e Literatura', 'História e Biografia',
        'Infantojuvenil e Quadrinhos', 'Mistério, Thriller e Terror',
        'Não-Ficção e Autodesenvolvimento', 'Outros', 'Romance'
    ]
    cols_presentes = [c for c in genre_cols if c in df.columns]
    
    if not cols_presentes:
        return go.Figure().update_layout(title="⚠️ Colunas de gêneros não encontradas no dataset", paper_bgcolor="#FFF8F0")

    if cluster_id == 'Todos':
        proporcoes = df.groupby('Cluster')[cols_presentes].mean().reset_index()
        prop_melted = proporcoes.melt(id_vars='Cluster', var_name='Gênero', value_name='Proporção')
        prop_melted['Percentual'] = prop_melted['Proporção'] * 100
        prop_melted['Nome_Cluster'] = prop_melted['Cluster'].map(lambda x: TRIBO_CONFIG[x]['nome'])
        
        cores_map = {v["nome"]: v["cor"] for k, v in TRIBO_CONFIG.items()}

        fig = px.bar(
            prop_melted, x='Percentual', y='Gênero', color='Nome_Cluster', barmode='group',
            color_discrete_map=cores_map,
            labels={'Percentual': 'Presença no Cluster (%)', 'Gênero': 'Gênero Literário'}
        )
    else:
        # Se for apenas 1 cluster, desenha barras simples
        df_sub = df[df['Cluster'] == cluster_id]
        proporcoes = (df_sub[cols_presentes].mean() * 100).reset_index()
        proporcoes.columns = ['Gênero', 'Percentual']
        fig = px.bar(
            proporcoes, x='Percentual', y='Gênero', orientation='h',
            labels={'Percentual': 'Presença no Cluster (%)', 'Gênero': 'Gênero Literário'}
        )
        fig.update_traces(marker_color=TRIBO_CONFIG[cluster_id]['cor'])

    fig.update_layout(
        paper_bgcolor="#FFFFFF", plot_bgcolor="#F9FAFB", font_family="Poppins, sans-serif",
        height=400, yaxis={'categoryorder':'total ascending'}, margin=dict(t=20, b=20, l=20, r=20),
        showlegend=(cluster_id == 'Todos'),
        legend=dict(title_text=None, orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig


# ── Gráfico 3: Características Físicas e Pop.
def _build_boxplot_pop(df: pd.DataFrame, cluster_id='Todos') -> go.Figure:
    if 'totalratings' not in df.columns or 'pages' not in df.columns:
        return go.Figure().update_layout(title="Colunas necessárias não encontradas", paper_bgcolor="#FFF8F0")

    fig = make_subplots(
        rows=1, cols=3, 
        subplot_titles=('Nota Média em log(Rating)', 'Extensão (Páginas)', 'Popularidade (N.º Avaliações)')
    )

    df_plot = df.copy()
    
    # Lógica de Filtro
    clusters_to_plot = TRIBO_CONFIG.items() if cluster_id == 'Todos' else [(cluster_id, TRIBO_CONFIG[cluster_id])]

    for cid, config in clusters_to_plot:
        subset = df_plot[df_plot['Cluster'] == cid]
        cor = config["cor"]
        
        fig.add_trace(go.Box(y=subset['rating'], name=f"C{cid}", marker_color=cor, showlegend=False), row=1, col=1)
        fig.add_trace(go.Box(y=subset['pages'], name=f"C{cid}", marker_color=cor, showlegend=False), row=1, col=2)
        fig.add_trace(go.Box(y=subset['totalratings'] + 1, name=f"C{cid}", marker_color=cor, showlegend=False), row=1, col=3)

    fig.update_yaxes(range=[0.0, 5.5], row=1, col=1, showgrid=True, gridcolor="#EBEBEB")
    fig.update_yaxes(range=[0, 1000], row=1, col=2, showgrid=True, gridcolor="#EBEBEB")
    fig.update_yaxes(type="log", row=1, col=3, showgrid=True, gridcolor="#EBEBEB") 

    fig.update_layout(
        paper_bgcolor="#FFFFFF", plot_bgcolor="#F9FAFB", font_family="Poppins, sans-serif",
        height=350, margin=dict(t=40, b=20, l=20, r=20)
    )
    return fig


# ── Gráfico 4: Autores Líderes
def _build_bar_autores(df: pd.DataFrame, cluster_id='Todos') -> go.Figure:
    if 'totalratings' not in df.columns:
        return go.Figure().update_layout(title="Coluna 'totalratings' não encontrada", paper_bgcolor="#FFF8F0")

    if cluster_id == 'Todos':
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=[v["nome"] for k, v in TRIBO_CONFIG.items()],
            horizontal_spacing=0.35,  
            vertical_spacing=0.3      
        )

        for i, (cid, config) in enumerate(TRIBO_CONFIG.items()):
            row = (i // 2) + 1
            col = (i % 2) + 1
            
            top_authors = df[df['Cluster'] == cid].groupby('author')['totalratings'].sum().reset_index()
            top_authors = top_authors.sort_values(by='totalratings', ascending=True).tail(5)
            top_authors['author_short'] = top_authors['author'].apply(lambda x: x.split(',')[0][:18])
            
            fig.add_trace(
                go.Bar(
                    x=top_authors['totalratings'], y=top_authors['author_short'],
                    orientation='h', marker_color=config["cor"], showlegend=False
                ), row=row, col=col
            )
        height = 550
    else:
        # Se for apenas 1 cluster, desenha barras simples com os top 10
        top_authors = df[df['Cluster'] == cluster_id].groupby('author')['totalratings'].sum().reset_index()
        top_authors = top_authors.sort_values(by='totalratings', ascending=True).tail(10)
        top_authors['author_short'] = top_authors['author'].apply(lambda x: x.split(',')[0][:18])
        
        fig = px.bar(top_authors, x='totalratings', y='author_short', orientation='h')
        fig.update_traces(marker_color=TRIBO_CONFIG[cluster_id]["cor"])
        height = 400

    fig.update_xaxes(showgrid=True, gridcolor="#EBEBEB")
    fig.update_layout(
        paper_bgcolor="#FFFFFF", plot_bgcolor="#F9FAFB", font_family="Poppins, sans-serif",
        height=height, margin=dict(t=40, b=20, l=20, r=20)
    )
    return fig


# ── Gráfico 5: Efeito Calhamaço
def _build_bar_calhamaco(df: pd.DataFrame, cluster_id='Todos') -> go.Figure:
    if 'rating' not in df.columns or 'pages' not in df.columns:
        return go.Figure().update_layout(title="Colunas necessárias não encontradas", paper_bgcolor="#FFF8F0")

    df_size = df.copy()
    df_size['Tamanho'] = pd.cut(
        df_size['pages'], 
        bins=[-1, 150, 350, 600, 99999], 
        labels=['Curto (<150 pags)', 'Médio (150-350 pags)', 'Longo (350-600 pags)', 'Calhamaço (>600 pags)']
    )

    if cluster_id == 'Todos':
        df_size_grouped = df_size.groupby(['Cluster', 'Tamanho'], observed=False)['rating'].mean().reset_index()
        df_size_grouped['Nome_Cluster'] = df_size_grouped['Cluster'].map(lambda x: TRIBO_CONFIG[x]['nome'])
        
        cores_map = {v["nome"]: v["cor"] for k, v in TRIBO_CONFIG.items()}

        fig = px.bar(
            df_size_grouped, x='Tamanho', y='rating', color='Nome_Cluster', barmode='group',
            color_discrete_map=cores_map,
            labels={'rating': 'Nota Média', 'Tamanho': 'Extensão'}
        )
    else:
        df_size_grouped = df_size[df_size['Cluster'] == cluster_id].groupby('Tamanho', observed=False)['rating'].mean().reset_index()
        fig = px.bar(
            df_size_grouped, x='Tamanho', y='rating',
            labels={'rating': 'Nota Média', 'Tamanho': 'Extensão'}
        )
        fig.update_traces(marker_color=TRIBO_CONFIG[cluster_id]["cor"])

    fig.update_yaxes(range=[0.0, 5.5], showgrid=True, gridcolor="#EBEBEB")
    fig.update_layout(
        paper_bgcolor="#FFFFFF", plot_bgcolor="#F9FAFB", font_family="Poppins, sans-serif",
        height=350, margin=dict(t=20, b=20, l=20, r=20),
        showlegend=(cluster_id == 'Todos'),
        legend=dict(title_text=None, orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig


# ── molde para os cards do layout 
def _card_grafico(titulo: str, desc: str, component_id: str, figura: go.Figure) -> html.Div:
    return html.Div(
        style={"background": "#FFFFFF", "borderRadius": "16px", "padding": "20px", "boxShadow": "0 2px 10px rgba(0,0,0,.06)", "display": "flex", "flexDirection": "column", "height": "100%"},
        children=[
            html.H4(titulo, style={"fontWeight": "700", "fontSize": "15px", "color": "#252525", "marginBottom": "4px"}),
            html.P(desc, style={"fontSize": "13px", "color": "#404347", "marginBottom": "16px"}),
            html.Div(dcc.Graph(id=component_id, figure=figura, config={"displayModeBar": False}), style={"flexGrow": "1"})
        ]
    )


# validaçao de arquivos físicos, monta painéis de controle e gerencia o isolamento de dados
def render(app, df_books: pd.DataFrame) -> html.Div:
    storytelling.register_callbacks(app, "clustering")
    base_dir      = os.path.dirname(os.path.abspath(__file__))
    df_clusters   = _carregar_df_clusters(base_dir)
    tem_svd       = df_clusters is not None and {"svd_x", "svd_y"}.issubset(df_clusters.columns)

    if not tem_svd:
        return html.Div(style={"padding": "20px"}, children=[html.P("Aviso: Dados de Clusterização SVD indisponíveis.", style={"color": "#E76F51", "fontWeight": "bold"})])

    # painel de controles dos fitlros
    top_controls = html.Div(
        style={
            'backgroundColor': '#FFFFFF', 'padding': '24px', 'borderRadius': '12px',
            'border': '1px solid #E2E8F0', 'boxShadow': '0px 4px 8px rgba(0, 0, 0, 0.05)',
            'marginBottom': '24px', 'display': 'flex', 'gap': '32px', 'flexWrap': 'wrap'
        },
        children=[
            # Cross-Filtering, onde o filtro é aplicado em todos os graficos da pagina
            html.Div(
                style={'flex': '1', 'minWidth': '280px'},
                children=[
                    html.Label("Filtro de Clusters:", style={'fontSize': '13px', 'fontWeight': 'bold', 'color': '#252525', 'marginBottom': '8px', 'display': 'block'}),
                    dcc.Dropdown(
                        id='ml-dropdown-crossfilter',
                        options=[{'label': 'Todas as Tribos Literárias', 'value': 'Todos'}] + 
                                [{'label': v['nome'], 'value': k} for k, v in TRIBO_CONFIG.items()],
                        value='Todos',
                        clearable=False,
                        style={'fontFamily': 'Poppins, sans-serif'}
                    )
                ]
            ),
            # Filtro de Avaliação SVD
            html.Div(
                style={'flex': '1', 'minWidth': '320px'},
                children=[
                    html.Label("Nota média:", style={'fontSize': '13px', 'fontWeight': 'bold', 'color': '#252525', 'marginBottom': '8px', 'display': 'block'}),
                    dcc.RangeSlider(
                        id='ml-slider-nota',
                        min=0, max=5.0, step=0.1,
                        value=[0, 5.0],
                        marks={0: '0.0', 1: '1.0', 2: '2.0', 3: '3.0', 4: '4.0', 5: '5.0'},
                        tooltip={"placement": "bottom", "always_visible": True}
                    )
                ]
            )
        ]
    )

    # Seção 1: Scatter Espacial 
    scatter_section = html.Div(
        style={"background": "#FFFFFF", "borderRadius": "16px", "padding": "24px", "boxShadow": "0 2px 12px rgba(0,0,0,.07)", "marginBottom": "24px"},
        children=[
            html.H3("Mapa Espacial da Galáxia de Livros", style={"fontWeight": "700", "fontSize": "16px", "color": "#252525", "marginBottom": "4px"}),
            html.P("Amostra de 10.000 títulos renderizados via SVD. Uma técnica matemática que reduz características em eixos de semelhança.", style={"fontSize": "13px", "color": "#33363D", "marginBottom": "16px"}),
            dcc.Graph(id='ml-grafico-scatter-svd', figure=_build_scatter(df_clusters), config={"displayModeBar": False}),
        ],
    )

    # Seção 2: Graficos do notebook 05
    graficos_cluster = html.Div(
        style={"display": "flex", "flexDirection": "column", "gap": "24px", "marginBottom": "24px"},
        children=[
            html.Div(
                style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "24px"},
            ),
            # Linha 1
            _card_grafico("Distribuição do volume entre os Clusters", "Distribuição absoluta de livros catalogados em cada cluster.", 'ml-grafico-dist', _build_bar_distribuicao(df_clusters)),
            # Linha 2
            _card_grafico("Distribuição do Número de paginas e de Popularidade por Cluster", "Distribuição de avaliações, revelando tribos de nicho vs. mainstream.", 'ml-grafico-pop', _build_boxplot_pop(df_clusters)),
            # Linha 3
            _card_grafico("Presença de Gêneros por Cluster", "Domínio de cada gênero dentro dos agrupamentos.", 'ml-grafico-gen', _build_bar_generos(df_clusters)),
            # Linha 4
            _card_grafico("Autores Líderes de Engajamento por Cluster", "Os autores com maior volume acumulado de resenhas.", 'ml-grafico-aut', _build_bar_autores(df_clusters)),
            # Linha 5
            _card_grafico("Relação entre extensão de páginas e a nota média", "O Efeito Calhamaço.", 'ml-grafico-cal', _build_bar_calhamaco(df_clusters)),
        ]
    )

    # ── CALLBACKS INTERNOS 
    @app.callback(
        Output('ml-grafico-scatter-svd', 'figure'),
        Input('ml-slider-nota', 'value'),
        Input('ml-dropdown-crossfilter', 'value')
    )
    def update_scatter(nota_range, cluster_id):
        # Filtra pela nota (Slider)
        df_filtrado = df_clusters[
            (df_clusters['rating'] >= nota_range[0]) & 
            (df_clusters['rating'] <= nota_range[1])
        ]
        
        # Filtra pela Tribo Literária (Dropdown)
        if cluster_id != 'Todos':
            df_filtrado = df_filtrado[df_filtrado['Cluster'] == int(cluster_id)]
            
        # Prevenção de erros caso o filtro fique vazio
        if df_filtrado.empty:
            return go.Figure().update_layout(
                title="Nenhum livro encontrado com esses filtros.", 
                paper_bgcolor="#FFFFFF", plot_bgcolor="#F9FAFB", 
                xaxis=dict(visible=False), yaxis=dict(visible=False)
            )
            
        return _build_scatter(df_filtrado)

    @app.callback(
        Output('ml-grafico-dist', 'figure'),
        Output('ml-grafico-pop', 'figure'),
        Output('ml-grafico-gen', 'figure'),
        Output('ml-grafico-aut', 'figure'),
        Output('ml-grafico-cal', 'figure'),
        Input('ml-dropdown-crossfilter', 'value')
    )
    def update_cross_filters(cluster_id):
        cid = int(cluster_id) if cluster_id != 'Todos' else 'Todos'
        return (
            _build_bar_distribuicao(df_clusters, cid),
            _build_boxplot_pop(df_clusters, cid),
            _build_bar_generos(df_clusters, cid),
            _build_bar_autores(df_clusters, cid),
            _build_bar_calhamaco(df_clusters, cid)
        )

    return html.Div(
        children=[
            storytelling.create_layout("clustering"),
            html.H2("Machine Learning · Clusterização K-Means (k=4)", style={"fontWeight": "700", "fontSize": "22px", "color": "#252525", "marginBottom": "6px"}),
            html.P("O algoritmo segmentou o catálogo em 4 Tribos Literárias com base em comportamento de avaliações, gêneros e extensão de paginas.", style={"fontSize": "14px", "color": "#32353B", "marginBottom": "24px", "lineHeight": "1.6"}),
            top_controls,
            scatter_section,
            graficos_cluster,
        ]
    )
