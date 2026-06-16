import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from dash import html, dcc, Input, Output, callback
from components import story_classificacao

# =============================================================================
# CONFIGURAÇÃO VISUAL — 3 CLASSES
# =============================================================================
CLASSE_CONFIG = {
    1: {
        "label":    "Bestseller",
        "cor":      "#F59E0B",
        "desc":     "Obras com alto volume de leitores (≥ 10.000 avaliações).",
        "badge_bg": "#FFFBEB",
        "arquivo":  "shap_beeswarm_classe1_bestseller.parquet",
        "seta_neg": "← Não é Bestseller",
        "seta_pos": "Bestseller →",
    },
    2: {
        "label":    "Média Popularidade",
        "cor":      "#6366F1",
        "desc":     "Obras com popularidade intermediária (≥ 1.000 avaliações).",
        "badge_bg": "#EEF2FF",
        "arquivo":  "shap_beeswarm_classe2_media.parquet",
        "seta_neg": "← Não é Média Pop.",
        "seta_pos": "Média Pop. →",
    },
    3: {
        "label":    "Nicho",
        "cor":      "#10B981",
        "desc":     "Obras especializadas com público menor mas fiel (< 1.000 avaliações).",
        "badge_bg": "#ECFDF5",
        "arquivo":  "shap_beeswarm_classe3_nicho.parquet",
        "seta_neg": "← Não é Nicho",
        "seta_pos": "Nicho →",
    },
}

# Métricas reais do conjunto de TESTE (RF Otimizado)
METRICAS_TESTE = {
    "Acurácia Global":       "65.6%",
    "F1-Score (Macro)":      "0.49",
    "Recall (Bestseller)":   "54.0%",
    "Precisão (Nicho)":      "91.0%",
}

# =============================================================================
# DADOS BRUTOS DA TABELA COMPARATIVA DOS MODELOS
# =============================================================================
DADOS_TABELA_MODELOS = [
    {"modelo": "RL", "linhas": [
        ["Precisão", "0,140", "0,330", "0,910", "0,460", "0,760"],
        ["Recall",   "0,570", "0,410", "0,680", "0,550", "0,620"],
        ["F1-Score", "0,220", "0,360", "0,780", "0,450", "0,670"],
        ["Suporte",  "731",   "3299",  "12372", "16402", "16402"],
        ["Acurácia", "-",     "-",     "-",     "0,622", "-"],
    ]},
    {"modelo": "XGBOOST", "linhas": [
        ["Precisão", "0,210", "0,380", "0,920", "0,500", "0,780"],
        ["Recall",   "0,530", "0,580", "0,710", "0,610", "0,680"],
        ["F1-Score", "0,300", "0,460", "0,800", "0,520", "0,710"],
        ["Suporte",  "731",   "3299",  "12372", "16402", "16402"],
        ["Acurácia", "-",     "-",     "-",     "0,676", "-"],
    ]},
    {"modelo": "RF", "linhas": [
        ["Precisão", "0,180", "0,350", "0,910", "0,480", "0,760"],
        ["Recall",   "0,540", "0,480", "0,710", "0,580", "0,660"],
        ["F1-Score", "0,270", "0,400", "0,800", "0,490", "0,690"],
        ["Suporte",  "1106",  "4995",  "18493", "24594", "-"],
        ["Acurácia", "-",     "-",     "-",     "0,656", "-"],
    ]},
    {"modelo": "KNN + UNDERSMPL.", "linhas": [
        ["Precisão", "0,130", "0,330", "0,910", "0,460", "0,760"],
        ["Recall",   "0,580", "0,430", "0,650", "0,550", "0,600"],
        ["F1-Score", "0,210", "0,370", "0,760", "0,450", "0,660"],
        ["Suporte",  "1106",  "4995",  "18501", "24602", "24602"],
        ["Acurácia", "-",     "-",     "-",     "0,604", "-"],
    ]}
]


# =============================================================================
# HELPERS DE LAYOUT
# =============================================================================
def _stat_card(titulo: str, valor: str) -> html.Div:
    return html.Div(
        style={
            "background":   "#FFFFFF",
            "borderRadius": "16px",
            "padding":      "24px 20px",
            "flex":         "1",
            "minWidth":     "160px",
            "border":       "1px solid #F3F4F6",
            "boxShadow":    "0 10px 25px rgba(0,0,0,0.08)", 
            "textAlign":    "center",
            "transition":   "transform 0.2s ease"
        },
        children=[
            html.Div(valor, style={"fontWeight": "700", "fontSize": "26px", "color": "#111827", "letterSpacing": "-0.5px"}),
            html.Div(titulo, style={"fontSize": "12px", "color": "#6B7280", "marginTop": "6px", "fontWeight": "500", "textTransform": "uppercase", "letterSpacing": "0.05em"}),
        ],
    )

def _build_tabela_comparativa() -> html.Div:
    headers = ["Modelo", "Métrica", "Classe 1", "Classe 2", "Classe 3", "Média", "Média Ponderada"]
    table_rows = []
    
    for mod in DADOS_TABELA_MODELOS:
        for i, linha in enumerate(mod["linhas"]):
            row_cells = []
            
            # Célula principal do Nome do Modelo (Mesclada verticalmente nas 5 linhas)
            if i == 0:
                row_cells.append(html.Td(
                    mod["modelo"], 
                    rowSpan=5, 
                    style={
                        "fontWeight": "700", "verticalAlign": "middle", "textAlign": "center",
                        "borderBottom": "2px solid #E5E7EB", "backgroundColor": "#F9FAFB", "padding": "10px"
                    }
                ))

            # Percorre os valores (Precisão, Recall, etc.)
            for j, val in enumerate(linha):
                # Estilização das linhas e colunas
                estilo_celula = {
                    "padding": "10px 16px",
                    "borderBottom": "2px solid #E5E7EB" if i == 4 else "1px solid #F3F4F6",
                    "textAlign": "left" if j == 0 else "center",
                    "fontWeight": "500" if j == 0 else "400"
                }

                # 💡 Destaque para o Recall da RF na Classe 1 (Justificativa de negócio)
                if mod["modelo"] == "RF" and linha[0] == "Recall" and j == 1:
                    estilo_celula.update({
                        "backgroundColor": "#FEF3C7", 
                        "fontWeight": "700", 
                        "color": "#B45309",
                        "borderRadius": "4px"
                    })

                row_cells.append(html.Td(val, style=estilo_celula))

            table_rows.append(html.Tr(row_cells))

    return html.Div(
        style={
            "background": "#FFFFFF", "borderRadius": "16px", "padding": "24px",
            "boxShadow": "0 2px 12px rgba(0,0,0,.07)", "marginBottom": "32px", "overflowX": "auto"
        },
        children=[
            html.H3("Arena de Modelos: Comparativo de Desempenho", style={"marginTop": "0", "fontSize": "18px", "color": "#111827", "marginBottom": "6px"}),
            html.P("Resultados dos treinamentos iniciais que basearam a escolha da Random Forest devido ao seu pico de Sensibilidade na Classe 1.", style={"fontSize": "13px", "color": "#6B7280", "marginBottom": "20px"}),
            html.Table(
                style={"width": "100%", "borderCollapse": "collapse", "fontSize": "13px", "color": "#4B5563"},
                children=[
                    html.Thead(
                        html.Tr([
                            html.Th(h, style={"padding": "12px", "borderBottom": "2px solid #D1D5DB", "color": "#374151", "fontWeight": "600", "textAlign": "center"}) for h in headers
                        ])
                    ),
                    html.Tbody(table_rows)
                ]
            )
        ]
    )

# =============================================================================
# GRÁFICO SHAP BEESWARM
# =============================================================================
def _build_shap_beeswarm(caminho_parquet: str, classe_id: int) -> go.Figure:
    cfg = CLASSE_CONFIG[classe_id]

    try:
        df_shap = pd.read_parquet(caminho_parquet)
    except FileNotFoundError:
        return go.Figure().update_layout(
            title=f"Arquivo {cfg['arquivo']} não encontrado.",
            paper_bgcolor="#FFFFFF"
        )

    if hasattr(df_shap['Feature'], 'cat') and df_shap['Feature'].cat.ordered:
        ordered_features = list(df_shap['Feature'].cat.categories)
    else:
        ordered_features = (
            df_shap
            .assign(_abs=df_shap['SHAP_Value'].abs())
            .groupby('Feature')['_abs']
            .mean()
            .sort_values(ascending=True)
            .index.tolist()
        )

    feat_to_y = {f: i for i, f in enumerate(ordered_features)}
    df_shap['Feature_Str'] = df_shap['Feature'].astype(str)

    np.random.seed(42)
    y_base = df_shap['Feature_Str'].map(feat_to_y).astype(float)
    df_shap['Y_Jitter'] = y_base + np.random.uniform(-0.35, 0.35, size=len(df_shap))
    df_shap['Feature_Value'] = df_shap['Feature_Value'].clip(0, 1)

    fig = px.scatter(
        df_shap,
        x='SHAP_Value',
        y='Y_Jitter',
        color='Feature_Value',
        color_continuous_scale=['#377eb8', '#e41a1c'],
        range_color=[0, 1],
        labels={
            'SHAP_Value':    'Impacto na Saída do Modelo (Valor SHAP)',
            'Feature_Value': 'Valor da Variável',
        },
    )

    fig.update_traces(marker=dict(size=4, opacity=0.65, line=dict(width=0)))

    x_max = max(df_shap['SHAP_Value'].abs().max() * 1.1, 0.05)

    fig.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#F9FAFB",
        font_family="Poppins, sans-serif",
        font_color="#374151",
        margin=dict(l=20, r=30, t=20, b=50),
        xaxis=dict(
            showgrid=True, gridcolor="#EBEBEB", zeroline=True,
            zerolinecolor="#252525", zerolinewidth=1.5,
            range=[-x_max, x_max], title_font=dict(size=12),
        ),
        yaxis=dict(
            showgrid=True, gridcolor="#EBEBEB", zeroline=False,
            tickmode='array', tickvals=list(feat_to_y.values()),
            ticktext=list(feat_to_y.keys()), title="", tickfont=dict(size=12),
        ),
        height=max(400, 45 * len(ordered_features)),
        coloraxis_colorbar=dict(
            title=dict(text="Valor da<br>Variável", font=dict(size=11)),
            tickvals=[0, 0.5, 1], ticktext=["Baixo", "Médio", "Alto"],
            thickness=14, len=0.6, y=0.5,
        ),
        annotations=[
            dict(
                x=-x_max * 0.97, y=-0.10, xref="x", yref="paper",
                text=cfg["seta_neg"], showarrow=False,
                font=dict(size=11, color="#6366F1"), xanchor="left",
            ),
            dict(
                x=x_max * 0.97, y=-0.10, xref="x", yref="paper",
                text=cfg["seta_pos"], showarrow=False,
                font=dict(size=11, color=cfg["cor"]), xanchor="right",
            ),
        ],
    )

    return fig


# =============================================================================
# LAYOUT PRINCIPAL
# =============================================================================
def render(app, df_books: pd.DataFrame) -> html.Div:

    base_shap = os.path.join(
        os.path.dirname(__file__), '..', '..',
        'Machine Learning', 'data', 'processed'
    )

    cards_metricas = html.Div(
        style={"display": "flex", "gap": "20px", "marginBottom": "32px", "flexWrap": "wrap"},
        children=[
            _stat_card("Acurácia Global",     METRICAS_TESTE["Acurácia Global"]),
            _stat_card("F1-Score (Macro)",    METRICAS_TESTE["F1-Score (Macro)"]),
            _stat_card("Recall (Bestseller)", METRICAS_TESTE["Recall (Bestseller)"]),
            _stat_card("Precisão (Nicho)",    METRICAS_TESTE["Precisão (Nicho)"]),
        ]
    )

    seletor_classe = html.Div(
        style={"display": "flex", "gap": "10px", "marginBottom": "20px", "flexWrap": "wrap"},
        children=[
            html.Button(
                children=[
                    html.Span(cfg["label"], style={"fontWeight": "600", "fontSize": "13px", "display": "block", "color": "#111827"}),
                    html.Span(cfg["desc"],  style={"fontSize": "11px", "color": "#6B7280", "display": "block", "marginTop": "2px"}),
                ],
                id=f"btn-classe-{classe_id}",
                n_clicks=0,
                style={
                    "background":   "#FFFFFF",
                    "border":       "1px solid #E5E7EB",
                    "borderRadius": "12px",
                    "padding":      "10px 16px",
                    "cursor":       "pointer",
                    "textAlign":    "left",
                    "flex":         "1",
                    "minWidth":     "200px",
                    "boxShadow":    "0 2px 4px rgba(0,0,0,0.04)",
                    "transition":   "box-shadow 0.2s, transform 0.2s",
                },
            )
            for classe_id, cfg in CLASSE_CONFIG.items()
        ]
    )

    layout = html.Div([
        story_classificacao.storytelling_layout(),

        html.H2(
            "Machine Learning · Seleção do Modelo e Explicabilidade",
            style={"fontWeight": "700", "fontSize": "22px", "color": "#252525", "marginTop": "32px"}
        ),
        
        # Inserção da nova tabela comparativa
        _build_tabela_comparativa(),

        html.P(
            "Desempenho final do modelo otimizado e explicabilidade (SHAP) do processo decisório. "
            "Selecione as abas abaixo para ver como as características empurram a decisão para cada classe.",
            style={"fontSize": "14px", "color": "#6B7280", "marginBottom": "24px"}
        ),

        cards_metricas,

        html.Div([
            html.P(
                "Selecione a classe para inspecionar a explicabilidade:",
                style={"fontSize": "13px", "fontWeight": "600", "color": "#374151", "marginBottom": "10px"}
            ),
            seletor_classe,
        ]),

        html.Div(id="shap-classe-badge", style={"marginBottom": "12px"}),

        html.Div(
            style={
                "background":   "#FFFFFF",
                "borderRadius": "16px",
                "padding":      "24px",
                "boxShadow":    "0 2px 12px rgba(0,0,0,.07)",
            },
            children=[
                dcc.Graph(id="shap-beeswarm-graph", config={"displayModeBar": False})
            ]
        ),

        dcc.Store(id="shap-classe-selecionada", data=1),
    ])

    # ── Callbacks ──────────────────────────────────────────────────────────────

    @callback(
        Output("shap-classe-selecionada", "data"),
        Input("btn-classe-1", "n_clicks"),
        Input("btn-classe-2", "n_clicks"),
        Input("btn-classe-3", "n_clicks"),
        prevent_initial_call=True,
    )
    def _atualizar_classe(n1, n2, n3):
        from dash import ctx
        return {"btn-classe-1": 1, "btn-classe-2": 2, "btn-classe-3": 3}.get(ctx.triggered_id, 1)

    @callback(
        Output("shap-beeswarm-graph", "figure"),
        Output("shap-classe-badge",   "children"),
        Input("shap-classe-selecionada", "data"),
    )
    def _atualizar_grafico(classe_id):
        cfg     = CLASSE_CONFIG[classe_id]
        caminho = os.path.join(base_shap, cfg["arquivo"])
        fig     = _build_shap_beeswarm(caminho, classe_id)

        badge = html.Span(
            f"Exibindo: {cfg['label']}",
            style={
                "background":   cfg["badge_bg"],
                "color":        cfg["cor"],
                "border":       f"1px solid {cfg['cor']}",
                "borderRadius": "20px",
                "padding":      "4px 14px",
                "fontSize":     "12px",
                "fontWeight":   "600",
            }
        )
        return fig, badge

    cfg_init    = CLASSE_CONFIG[1]
    fig_inicial = _build_shap_beeswarm(os.path.join(base_shap, cfg_init["arquivo"]), 1)

    layout.children[-2].children[0].figure = fig_inicial
    layout.children[-3].children = html.Span(
        f"Exibindo: {cfg_init['label']}",
        style={
            "background":   cfg_init["badge_bg"],
            "color":        cfg_init["cor"],
            "border":       f"1px solid {cfg_init['cor']}",
            "borderRadius": "20px",
            "padding":      "4px 14px",
            "fontSize":     "12px",
            "fontWeight":   "600",
        }
    )

    return layout