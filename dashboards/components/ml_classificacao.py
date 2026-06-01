import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from dash import html, dcc, Input, Output, State, dash_table

# Configuração visual
CLASSE_CONFIG = {
    0: {
        "label":  "Nicho",
        "cor":    "#6366F1",
        "desc":   "Obras com perfil especializado, público menor mas fiel.",
        "badge_bg": "#EEF2FF",
    },
    1: {
        "label":  "Alta Popularidade",
        "cor":    "#F59E0B",
        "desc":   "Obras com apelo amplo e alto volume de leitores.",
        "badge_bg": "#FFFBEB",
    },
}

# ── Loader do parquet
def _carregar_df_pop(base_dir: str) -> pd.DataFrame | None:
    caminho_correto = os.path.abspath(os.path.join(base_dir, '..', '..', 'Machine Learning', 'data', 'processed', 'livros_com_popularidade_dashboard.parquet'))

    if os.path.exists(caminho_correto):
        return pd.read_parquet(caminho_correto)
        
    return None


# Helpers de layout 
def _stat_card(titulo: str, valor: str, cor: str) -> html.Div:
    return html.Div(
        style={
            "background":   "#FFFFFF",
            "borderRadius": "14px",
            "padding":      "20px 24px",
            "flex":         "1",
            "minWidth":     "160px",
            "boxShadow":    "0 2px 10px rgba(0,0,0,.06)",
            "borderLeft":   f"5px solid {cor}",
        },
        children=[
            html.Div(valor, style={"fontWeight": "700", "fontSize": "22px", "color": "#252525"}),
            html.Div(titulo, style={"fontSize": "12px", "color": "#9CA3AF", "marginTop": "2px"}),
        ],
    )


def _input_field(label: str, field_id: str, placeholder: str, valor_padrao) -> html.Div:
    return html.Div(
        style={"flex": "1", "minWidth": "140px"},
        children=[
            html.Label(label, style={"fontSize": "13px", "fontWeight": "600",
                                     "color": "#374151", "marginBottom": "6px",
                                     "display": "block"}),
            dcc.Input(
                id          = field_id,
                type        = "number",
                placeholder = placeholder,
                value       = valor_padrao,
                debounce    = False,
                style={
                    "width":        "100%",
                    "padding":      "10px 14px",
                    "borderRadius": "10px",
                    "border":       "1.5px solid #E5E7EB",
                    "fontSize":     "14px",
                    "fontFamily":   "Poppins, sans-serif",
                    "outline":      "none",
                    "boxSizing":    "border-box",
                },
            ),
        ],
    )


#  Gráfico distribuição das classes 
def _build_bar_distribuicao(df: pd.DataFrame) -> go.Figure:
    contagens = df["classe_popularidade"].value_counts().sort_index()
    cores  = [CLASSE_CONFIG[i]["cor"] for i in contagens.index]
    labels = [CLASSE_CONFIG[i]['label'] for i in contagens.index]

    fig = go.Figure(go.Bar(
        x           = labels,
        y           = contagens.values,
        marker_color= cores,
        text        = [f"{v:,}<br>({v/len(df)*100:.1f}%)" for v in contagens.values],
        textposition= "outside",
        textfont    = dict(size=13, family="Poppins"),
    ))
    fig.update_layout(
        paper_bgcolor = "#FFFFFF",
        plot_bgcolor  = "#F9FAFB",
        font_family   = "Poppins, sans-serif",
        margin        = dict(l=20, r=20, t=20, b=20),
        yaxis         = dict(showgrid=True, gridcolor="#EBEBEB", title="Número de Livros"),
        xaxis         = dict(showgrid=False),
        height        = 300,
        showlegend    = False,
    )
    return fig


# Gráfico de dispersão: rating × reviews colorido por classe 
def _build_scatter_pop(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    amostra = df.sample(min(4000, len(df)), random_state=42)

    for cid, cfg in CLASSE_CONFIG.items():
        sub = amostra[amostra["classe_popularidade"] == cid]
        fig.add_trace(go.Scatter(
            x    = sub["rating"],
            y    = np.log1p(sub["reviews"]),
            mode = "markers",
            name = f"{cfg['label']}",
            marker= dict(color=cfg["cor"], size=5, opacity=0.65,
                         line=dict(width=0.3, color="white")),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Nota: %{x:.2f} | Resenhas: %{customdata[1]:,}<extra></extra>"
            ),
            customdata=sub[["title", "reviews"]].values,
        ))

    fig.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor ="#F9FAFB",
        font_family  ="Poppins, sans-serif",
        margin       =dict(l=20, r=20, t=20, b=20),
        xaxis        =dict(title="Nota Média (rating)", showgrid=True, gridcolor="#EBEBEB"),
        yaxis        =dict(title="Resenhas (escala log)", showgrid=True, gridcolor="#EBEBEB"),
        legend       =dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height       =320,
    )
    return fig


# Render principal 
def render(app, df_books: pd.DataFrame) -> html.Div:
    base_dir  = os.path.dirname(os.path.abspath(__file__))
    df        = _carregar_df_pop(base_dir)
    tem_dados = df is not None

    # Métricas gerais 
    if tem_dados:
        n_total   = len(df)
        n_pop     = int((df["classe_popularidade"] == 1).sum())
        n_nicho   = int((df["classe_popularidade"] == 0).sum())
        pct_pop   = f"{n_pop / n_total * 100:.1f}%"
        nota_media= f"{df['rating'].mean():.2f}"
    else:
        n_total = n_pop = n_nicho = 0
        pct_pop = nota_media = "—"

    stats_row = html.Div(
        style={"display": "flex", "gap": "14px", "flexWrap": "wrap", "marginBottom": "24px"},
        children=[
            _stat_card("Livros Analisados",   f"{n_total:,}",  "#252525"),
            _stat_card("Alta Popularidade",   f"{n_pop:,}",    CLASSE_CONFIG[1]["cor"]),
            _stat_card("Nicho",               f"{n_nicho:,}",  CLASSE_CONFIG[0]["cor"]),
            _stat_card("% Populares",          pct_pop,        "#10B981"),
            _stat_card("Nota Média Catálogo.",   nota_media,     "#6366F1"),
        ],
    )

    # Gráficos 
    if tem_dados:
        graficos = html.Div(
            style={"display": "flex", "gap": "20px", "flexWrap": "wrap", "marginBottom": "24px"},
            children=[
                html.Div(
                    style={"flex": "1", "minWidth": "280px", "background": "#FFFFFF",
                           "borderRadius": "16px", "padding": "20px",
                           "boxShadow": "0 2px 10px rgba(0,0,0,.06)"},
                    children=[
                        html.H4("Distribuição das Classes",
                                style={"fontWeight": "700", "fontSize": "14px",
                                       "color": "#252525", "marginBottom": "4px"}),
                        html.P("73.9% Nicho · 26.1% Alta Popularidade — dataset desbalanceado natural.",
                               style={"fontSize": "12px", "color": "#9CA3AF", "marginBottom": "12px"}),
                        dcc.Graph(figure=_build_bar_distribuicao(df),
                                  config={"displayModeBar": False}),
                    ],
                ),
                html.Div(
                    style={"flex": "2", "minWidth": "320px", "background": "#FFFFFF",
                           "borderRadius": "16px", "padding": "20px",
                           "boxShadow": "0 2px 10px rgba(0,0,0,.06)"},
                    children=[
                        html.H4("Nota vs. Resenhas por Classe",
                                style={"fontWeight": "700", "fontSize": "14px",
                                       "color": "#252525", "marginBottom": "4px"}),
                        html.P("Livros populares concentram-se em notas altas e mais resenhas. "
                               "Passe o mouse para ver o título.",
                               style={"fontSize": "12px", "color": "#9CA3AF", "marginBottom": "12px"}),
                        dcc.Graph(id    ="scatter-popularidade",
                                  figure=_build_scatter_pop(df),
                                  config={"displayModeBar": False}),
                    ],
                ),
            ],
        )
    else:
        graficos = html.Div(
            style={"background": "#FFF8F0", "borderRadius": "12px",
                   "padding": "20px 24px", "marginBottom": "24px",
                   "border": "1px dashed #F59E0B"},
            children=[
                html.P(" CSV não encontrado.",
                       style={"fontWeight": "700", "color": "#F59E0B"})
            ]
        )

    # Tabela explorável 
    if tem_dados:
        tabela_section = html.Div(
            style={
                "background":   "#FFFFFF",
                "borderRadius": "16px",
                "padding":      "24px",
                "boxShadow":    "0 2px 12px rgba(0,0,0,.07)",
            },
            children=[
                html.H3("Explorar Livros por Classe",
                        style={"fontWeight": "700", "fontSize": "16px",
                               "color": "#252525", "marginBottom": "4px"}),
                html.P("Filtre por classe e pesquise títulos diretamente na tabela.",
                       style={"fontSize": "13px", "color": "#6B7280", "marginBottom": "16px"}),

                dcc.Dropdown(
                    id       ="dropdown-classe-pop",
                    options  =[
                        {"label": "Alta Popularidade", "value": 1},
                        {"label": "Nicho",             "value": 0},
                        {"label": "Todos",             "value": -1},
                    ],
                    value    =-1,
                    clearable=False,
                    style    ={"fontFamily": "Poppins, sans-serif",
                               "fontSize": "14px", "marginBottom": "16px"},
                ),

                html.Div(id="tabela-pop-container"),
            ],
        )
    else:
        tabela_section = html.Div()


    # Callback 1: Tabela por classe
    if tem_dados:
        @app.callback(
            Output("tabela-pop-container", "children"),
            Input("dropdown-classe-pop", "value"),
        )
        def atualizar_tabela_pop(classe_val):
            if classe_val == -1:
                df_f = df
            else:
                df_f = df[df["classe_popularidade"] == classe_val]

            cols_show = [c for c in ["title", "author", "pages", "rating", "reviews", "totalratings"]
                         if c in df_f.columns]
            df_f = df_f[cols_show].head(100)

            cor = CLASSE_CONFIG[1]["cor"] if classe_val == 1 else (
                  CLASSE_CONFIG[0]["cor"] if classe_val == 0 else "#252525")

            col_labels = {
                "title": "Título", "author": "Autor", "pages": "Páginas",
                "rating": "Nota", "reviews": "Resenhas", "totalratings": "Total Aval.",
            }

            return dash_table.DataTable(
                data        = df_f.to_dict("records"),
                columns     = [{"name": col_labels.get(c, c), "id": c} for c in df_f.columns],
                page_size   = 10,
                sort_action = "native",
                filter_action="native",
                style_table ={"overflowX": "auto"},
                style_header={
                    "backgroundColor": cor,
                    "color":           "#FFFFFF",
                    "fontWeight":      "700",
                    "fontSize":        "13px",
                    "border":          "none",
                    "padding":         "10px 14px",
                },
                style_cell={
                    "fontFamily":      "Poppins, sans-serif",
                    "fontSize":        "13px",
                    "padding":         "9px 14px",
                    "border":          "1px solid #F0F0F0",
                    "backgroundColor": "#FFFFFF",
                    "color":           "#374151",
                    "maxWidth":        "240px",
                    "overflow":        "hidden",
                    "textOverflow":    "ellipsis",
                },
                style_data_conditional=[
                    {"if": {"row_index": "odd"}, "backgroundColor": "#FAFAFA"},
                ],
            )

    # Layout final 
    return html.Div(
        children=[
            html.H2(
                "Machine Learning · Classificação de Popularidade",
                style={"fontWeight": "700", "fontSize": "22px",
                       "color": "#252525", "marginBottom": "6px"},
            ),
            html.P(
                f"Modelo KNN supervisionado (k=5) treinado para classificar se um livro tem perfil de "
                f"Nicho (classe 0) ou Alta Popularidade (classe 1), com base em páginas, nota e resenhas. "
                f"Acurácia global: 92.01% | Acervo avaliado: {n_total:,} livros | Split de Treino original: 70/30.",
                style={"fontSize": "14px", "color": "#6B7280",
                       "marginBottom": "24px", "lineHeight": "1.6"},
            ),
            stats_row,
            graficos,
            tabela_section,
        ]
    )