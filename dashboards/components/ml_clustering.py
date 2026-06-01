import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from dash import html, dcc, Input, Output, dash_table

# Paleta e nomes das tribos
TRIBO_CONFIG = {
    0: {
        "nome":   "Blockbusters Populares",
        "cor":    "#E76F51",
        "desc":   "Os livros que todo mundo está lendo. Alto volume de avaliações e presença mainstream.",
        "generos": "Romance · Ficção · Fantasia",
    },
    1: {
        "nome":   "Nichos e Leituras Rápidas",
        "cor":    "#2A9D8F",
        "desc":   "Tesouros escondidos e leituras de fim de semana. Menor alcance, públicos específicos.",
        "generos": "Romance · Infantil · Quadrinhos / Mangás",
    },
    2: {
        "nome":   "Acadêmicos e Históricos",
        "cor":    "#457B9D",
        "desc":   "Calhamaços sérios para leitores maduros. Maior nota média e foco em conhecimento.",
        "generos": "Não-ficção · História · Religião",
    },
}

STATS_CONFIG = {
    0: {"paginas": 262,  "nota": 3.86, "avaliacoes": 7498},
    1: {"paginas": 232,  "nota": 3.72, "avaliacoes": 90},
    2: {"paginas": 295,  "nota": 3.95, "avaliacoes": 410},
}

# Loader do parquet
def _carregar_df_clusters(base_dir: str) -> pd.DataFrame | None:
    caminho_correto = os.path.abspath(os.path.join(base_dir, '..', '..', 'Machine Learning', 'data', 'processed', 'livros_com_clusters.parquet'))
    
    if os.path.exists(caminho_correto):
        return pd.read_parquet(caminho_correto)
        
    return None


# Card de tribo
def _card_tribo(cluster_id: int, n_livros: int | None = None) -> html.Div:
    cfg  = TRIBO_CONFIG[cluster_id]
    stat = STATS_CONFIG[cluster_id]
    cor  = cfg["cor"]

    contagem = f"{n_livros:,} livros" if n_livros else "—"

    return html.Div(
        style={
            "background":    "#FFFFFF",
            "borderRadius":  "16px",
            "padding":       "24px",
            "flex":          "1",
            "borderTop":     f"5px solid {cor}",
            "boxShadow":     "0 2px 12px rgba(0,0,0,.07)",
            "minWidth":      "220px",
        },
        children=[
            html.Div(
                style={"display": "flex", "alignItems": "center", "gap": "10px", "marginBottom": "8px"},
                children=[
                    html.Span(cfg["nome"],  style={"fontWeight": "700", "fontSize": "15px", "color": "#252525"}),
                ],
            ),
            html.P(cfg["desc"],    style={"fontSize": "13px", "color": "#464A53", "marginBottom": "12px", "lineHeight": "1.5"}),
            html.P(f"Gêneros: {cfg['generos']}", style={"fontSize": "12px", "color": cor, "fontWeight": "600", "marginBottom": "14px"}),
            html.Div(
                style={"display": "flex", "gap": "10px", "flexWrap": "wrap"},
                children=[
                    _mini_stat("Páginas",    f"{stat['paginas']}",         cor),
                    _mini_stat("Nota",        f"{stat['nota']}",            cor),
                    _mini_stat("Avaliações",  f"{stat['avaliacoes']:,}",    cor),
                    _mini_stat("Catálogo",    contagem,                     cor),
                ],
            ),
        ],
    )


def _mini_stat(label: str, valor: str, cor: str) -> html.Div:
    return html.Div(
        style={
            "background":   f"{cor}12",
            "borderRadius": "8px",
            "padding":      "6px 10px",
            "textAlign":    "center",
            "minWidth":     "80px",
        },
        children=[
            html.Div(valor, style={"fontWeight": "700", "fontSize": "14px", "color": cor}),
            html.Div(label, style={"fontSize": "10px",  "color": "#9CA3AF"}),
        ],
    )


#  Scatter plot
def _build_scatter(df_clusters: pd.DataFrame, tribo_ativa: int | None = None) -> go.Figure:
    fig = go.Figure()

    amostra = df_clusters.sample(min(5000, len(df_clusters)), random_state=42)

    for cid, cfg in TRIBO_CONFIG.items():
        mask   = amostra["Cluster"] == cid
        subset = amostra[mask]
        opacidade = 0.75 if (tribo_ativa is None or tribo_ativa == cid) else 0.10

        fig.add_trace(go.Scatter(
            x    = subset["svd_x"],
            y    = subset["svd_y"],
            mode = "markers",
            name = cfg["nome"],
            marker=dict(color=cfg["cor"], size=5, opacity=opacidade,
                        line=dict(width=0.3, color="white")),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "%{customdata[1]}<br>"
                "Nota: %{customdata[2]:.2f}<extra></extra>"
            ),
            customdata=subset[["title", "author", "rating"]].values,
        ))

    fig.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor ="#F9FAFB",
        font_family  ="Poppins, sans-serif",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(size=14, color="#1A1A1A")),
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(showgrid=True, gridcolor="#EBEBEB", zeroline=False, title="Componente SVD 1"),
        yaxis=dict(showgrid=True, gridcolor="#EBEBEB", zeroline=False, title="Componente SVD 2"),
        height=440,
    )
    return fig


# Tabela de livros 
def _build_tabela(df_clusters: pd.DataFrame, cluster_id: int) -> dash_table.DataTable:
    cfg  = TRIBO_CONFIG[cluster_id]
    cols = ["title", "author", "rating", "pages", "Cluster"]
    df_f = df_clusters[df_clusters["Cluster"] == cluster_id][cols].head(50)

    return dash_table.DataTable(
        data    = df_f.to_dict("records"),
        columns = [
            {"name": "Título",   "id": "title"},
            {"name": "Autor",    "id": "author"},
            {"name": "Nota",     "id": "rating"},
            {"name": "Páginas",  "id": "pages"},
        ],
        page_size    = 10,
        sort_action  = "native",
        filter_action= "native",
        style_table  = {"overflowX": "auto"},
        style_header = {
            "backgroundColor": cfg["cor"],
            "color":           "#FFFFFF",
            "fontWeight":      "700",
            "fontSize":        "13px",
            "border":          "none",
            "padding":         "10px 14px",
        },
        style_cell = {
            "fontFamily":        "Poppins, sans-serif",
            "fontSize":          "13px",
            "padding":           "9px 14px",
            "border":            "1px solid #F0F0F0",
            "backgroundColor":   "#FFFFFF",
            "color":             "#374151",
            "maxWidth":          "260px",
            "overflow":          "hidden",
            "textOverflow":      "ellipsis",
        },
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": "#FAFAFA"},
        ],
    )


# Render principal 
def render(app, df_books: pd.DataFrame) -> html.Div:
    base_dir      = os.path.dirname(os.path.abspath(__file__))
    df_clusters   = _carregar_df_clusters(base_dir)
    tem_svd       = df_clusters is not None and {"svd_x", "svd_y"}.issubset(df_clusters.columns)

    # Contagem real de livros por cluster
    contagens: dict[int, int] = {}
    if df_clusters is not None:
        for cid in range(3):
            contagens[cid] = int((df_clusters["Cluster"] == cid).sum())

    # Cards das tribos 
    cards = html.Div(
        style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "24px"},
        children=[_card_tribo(i, contagens.get(i)) for i in range(3)],
    )

    # Scatter plot
    if tem_svd:
        scatter_section = html.Div(
            style={
                "background":   "#FFFFFF",
                "borderRadius": "16px",
                "padding":      "24px",
                "boxShadow":    "0 2px 12px rgba(0,0,0,.07)",
                "marginBottom": "24px",
            },
            children=[
                html.H3("Mapa das Tribos Literárias",
                        style={"fontWeight": "700", "fontSize": "16px",
                               "color": "#252525", "marginBottom": "4px"}),
                html.P("Cada ponto é um livro posicionado pelo SVD — uma técnica que reduz dezenas de características dos textos em apenas 2 eixos principais de semelhança. "
                       "Clique numa tribo na legenda para destacá-la.",
                       style={"fontSize": "13px", "color": "#1a1a1a", "marginBottom": "16px"}),
                dcc.Graph(
                    id    ="scatter-tribos",
                    figure=_build_scatter(df_clusters),
                    config={"displayModeBar": False},
                ),
            ],
        )
    else:
        scatter_section = html.Div(
            style={
                "background":   "#FFF8F0",
                "borderRadius": "12px",
                "padding":      "20px 24px",
                "marginBottom": "24px",
                "border":       "1px dashed #E76F51",
            },
            children=[
                html.P("Aviso: Scatter plot indisponível.",
                       style={"fontWeight": "700", "color": "#E76F51", "marginBottom": "4px"}),
                html.P("O arquivo livros_com_clusters.csv não foi encontrado ou não contém as colunas svd_x / svd_y. "
                       "Verifique se o arquivo está na pasta 'Machine Learning/data/processed/'.",
                       style={"fontSize": "13px", "color": "#92400E"}),
            ],
        )

    # Seção de exploração por tribo
    opcoes_tribo = [
        {"label": f"{TRIBO_CONFIG[i]['nome']}", "value": i}
        for i in range(3)
    ]

    explorar_section = html.Div(
        style={
            "background":   "#FFFFFF",
            "borderRadius": "16px",
            "padding":      "24px",
            "boxShadow":    "0 2px 12px rgba(0,0,0,.07)",
        },
        children=[
            html.H3("Explorar Livros por Tribo",
                    style={"fontWeight": "700", "fontSize": "16px",
                           "color": "#252525", "marginBottom": "4px"}),
            html.P("Selecione uma tribo para ver os livros que o modelo agrupou nela.",
                   style={"fontSize": "13px", "color": "#6B7280", "marginBottom": "16px"}),

            dcc.Dropdown(
                id      ="dropdown-tribo",
                options =opcoes_tribo,
                value   =0,
                clearable=False,
                style   ={"fontFamily": "Poppins, sans-serif", "marginBottom": "16px",
                           "fontSize": "14px"},
            ),

            html.Div(id="tabela-tribo-container"),
        ],
    )

    # callbacks
    if df_clusters is not None:
        @app.callback(
            Output("tabela-tribo-container", "children"),
            Input("dropdown-tribo", "value"),
        )
        def atualizar_tabela(cluster_id):
            if cluster_id is None:
                return html.P("Selecione uma tribo acima.", style={"color": "#9CA3AF"})
            return _build_tabela(df_clusters, int(cluster_id))

    else:
        @app.callback(
            Output("tabela-tribo-container", "children"),
            Input("dropdown-tribo", "value"),
        )
        def atualizar_tabela_sem_dados(_):
            return html.P(
                "Tabela indisponível: livros_com_clusters.csv não encontrado.",
                style={"color": "#9CA3AF", "fontStyle": "italic"},
            )

    # Layout final 
    return html.Div(
        children=[
            html.H2(
                "Machine Learning · Clusterização K-Means++",
                style={"fontWeight": "700", "fontSize": "22px",
                       "color": "#252525", "marginBottom": "6px"},
            ),
            html.P(
                "O algoritmo K-Means++ analisou os 84.054 livros do catálogo e os agrupou em 3 Tribos Literárias "
                "com base em gênero, nota, páginas e popularidade. Silhouette Score: 0.6015.",
                style={"fontSize": "14px", "color": "#34373D", "marginBottom": "24px", "lineHeight": "1.6"},
            ),
            cards,
            scatter_section,
            explorar_section,
        ]
    )