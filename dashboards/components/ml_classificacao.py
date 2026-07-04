import os
import joblib
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from dash import html, dcc, Input, Output, callback, State
from components import storytelling

# config padrao do visual
CLASSE_CONFIG = {
    1: {
        "label":    "Bestseller",
        "cor":      "#F59E0B",
        "desc":     "Obras com alto volume de leitores (≥ 10.000 avaliações).",
        "badge_bg": "#FFFBEB",
        "arquivo":  "shap_beeswarm_classe1_bestseller.parquet",
        "seta_neg": "← Afasta de Bestseller",
        "seta_pos": "Aproxima de Bestseller →",
    },
    2: {
        "label":    "Média Popularidade",
        "cor":      "#6366F1",
        "desc":     "Obras com popularidade intermediária (≥ 1.000 avaliações).",
        "badge_bg": "#EEF2FF",
        "arquivo":  "shap_beeswarm_classe2_media.parquet",
        "seta_neg": "← Afasta de Média Pop.",
        "seta_pos": "Aproxima de Média Pop. →",
    },
    3: {
        "label":    "Nicho",
        "cor":      "#10B981",
        "desc":     "Obras especializadas com público menor mas fiel (< 1.000 avaliações).",
        "badge_bg": "#ECFDF5",
        "arquivo":  "shap_beeswarm_classe3_nicho.parquet",
        "seta_neg": "← Afasta de Nicho",
        "seta_pos": "Aproxima de Nicho →",
    },
}

# metricas do conjunto de TESTE
METRICAS_TESTE = {
    "Acurácia Global":       "65.6%",
    "F1-Score (Macro)":      "0.49",
    "Recall (Bestseller)":   "54.0%",
    "Precisão (Nicho)":      "91.0%",
}

# formato do cards para o layout
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
            html.Div(valor, style={"fontWeight": "700", "fontSize": "26px", "color": "#0C111B", "letterSpacing": "-0.5px"}),
            html.Div(titulo, style={"fontSize": "12px", "color": "#40444D", "marginTop": "6px", "fontWeight": "500", "textTransform": "uppercase", "letterSpacing": "0.05em"}),
        ],
    )

# grafico comparativo de métricas (Precisão, Sensibilidade e F1-Score)
def _build_grafico_escolha_modelo() -> html.Div:
    """Constrói o Gráfico de Barras agrupadas com foco na Classe 1 (conforme a imagem)."""
    dados = []
    
    # Valores extraídos para a Classe 1
    precisao = [0.180, 0.210, 0.140, 0.130]
    recall   = [0.540, 0.500, 0.570, 0.570]
    f1_score = [0.270, 0.300, 0.220, 0.210]
    
    modelos = ['Random Forest', 'XGBoost', 'Regressão Logística', 'KNN']
    cores = ['#4285F4', '#A855F7', "#FB7324", '#FDE047'] 
    
    for i, modelo in enumerate(modelos):
        dados.append({'Modelo': modelo, 'Métrica': 'Precisão', 'Desempenho': precisao[i]})
        dados.append({'Modelo': modelo, 'Métrica': 'Recall', 'Desempenho': recall[i]})
        dados.append({'Modelo': modelo, 'Métrica': 'F1-Score', 'Desempenho': f1_score[i]})
        
    df_plot = pd.DataFrame(dados)
    
    fig = px.bar(
        df_plot,
        x='Métrica',
        y='Desempenho',
        color='Modelo',
        barmode='group',
        text='Desempenho',
        color_discrete_sequence=cores
    )
    
    fig.update_traces(texttemplate='%{text:.3f}', textposition='outside')
    
    fig.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font_family="Poppins, sans-serif",
        font_color="#1A1E25",
        legend_title_text='',
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="center", x=0.5, font=dict(size=20)),
        xaxis=dict(title="", showgrid=False, zeroline=False, tickfont=dict(size=16)),
        yaxis=dict(title="", showgrid=True, gridcolor="#F3F4F6", zeroline=False, range=[0, 0.65]),
        margin=dict(l=20, r=20, t=60, b=40),
        height=450
    )

    return html.Div(
        style={"background": "#FFFFFF", "borderRadius": "16px", "padding": "24px", "boxShadow": "0 2px 12px rgba(0,0,0,.07)", "marginBottom": "32px"},
        children=[
            html.H3("Como o melhor modelo foi escolhido?", style={"marginTop": "0", "fontSize": "20px", "color": "#111827", "marginBottom": "6px", "fontWeight": "bold"}),
            html.P("Comparativo de desempenho focado exclusivamente na capacidade de detectar Bestsellers (Classe 1).", style={"fontSize": "14px", "color": "#40444D", "marginBottom": "20px"}),
            dcc.Graph(figure=fig, config={"displayModeBar": False})
        ]
    )


def _build_shap_beeswarm(caminho_parquet: str, classe_id: int) -> go.Figure:
    """Constrói o gráfico SHAP detalhado para observar a distribuição."""
    cfg = CLASSE_CONFIG[classe_id]

    try:
        df_shap = pd.read_parquet(caminho_parquet)
    except FileNotFoundError:
        return go.Figure().update_layout(title=f"Arquivo {cfg['arquivo']} não encontrado.", paper_bgcolor="#FFFFFF")

    if hasattr(df_shap['Feature'], 'cat') and df_shap['Feature'].cat.ordered:
        ordered_features = list(df_shap['Feature'].cat.categories)
    else:
        ordered_features = (df_shap.assign(_abs=df_shap['SHAP_Value'].abs()).groupby('Feature')['_abs'].mean().sort_values(ascending=True).index.tolist())

    feat_to_y = {f: i for i, f in enumerate(ordered_features)}
    df_shap['Feature_Str'] = df_shap['Feature'].astype(str)

    np.random.seed(42)
    y_base = df_shap['Feature_Str'].map(feat_to_y).astype(float)
    df_shap['Y_Jitter'] = y_base + np.random.uniform(-0.35, 0.35, size=len(df_shap))
    df_shap['Feature_Value'] = df_shap['Feature_Value'].clip(0, 1)

    fig = px.scatter(
        df_shap, x='SHAP_Value', y='Y_Jitter', color='Feature_Value',
        color_continuous_scale=['#377eb8', '#e41a1c'], range_color=[0, 1],
        labels={'SHAP_Value': 'Impacto na Saída do Modelo (Valor SHAP)', 'Feature_Value': 'Valor da Variável'},
    )
    
    fig.update_traces(marker=dict(size=4, opacity=0.65, line=dict(width=0)))

    x_max = max(df_shap['SHAP_Value'].abs().max() * 1.1, 0.05)

    fig.update_layout(
        title=dict(text="Distribuição de Explicabilidade (SHAP Beeswarm)", font=dict(size=15, color="#0C121D")),
        paper_bgcolor="#FFFFFF", plot_bgcolor="#F9FAFB", font_family="Poppins, sans-serif", font_color="#232933", margin=dict(l=20, r=30, t=50, b=60),
        xaxis=dict(showgrid=True, gridcolor="#EBEBEB", zeroline=True, zerolinecolor="#1D1D1D", zerolinewidth=1.5, range=[-x_max, x_max], title_font=dict(size=17)),
        yaxis=dict(showgrid=True, gridcolor="#EBEBEB", zeroline=False, tickmode='array', tickvals=list(feat_to_y.values()), ticktext=list(feat_to_y.keys()), title="", tickfont=dict(size=15)),
        height=max(500, 60 * len(ordered_features)),
        coloraxis_colorbar=dict(title=dict(text="Valor da<br>Variável", font=dict(size=11)), tickvals=[0, 0.5, 1], ticktext=["Baixo", "Médio", "Alto"], thickness=14, len=0.6, y=0.5),
        annotations=[
            dict(x=-x_max * 0.97, y=-0.10, xref="x", yref="paper", text=cfg["seta_neg"], showarrow=False, font=dict(size=15, color="#6e0560"), xanchor="left"),
            dict(x=x_max * 0.97, y=-0.10, xref="x", yref="paper", text=cfg["seta_pos"], showarrow=False, font=dict(size=15, color="#0c8f13"), xanchor="right"),
        ],
    )
    return fig


# montagem do layout html
def render(app, df_books: pd.DataFrame) -> html.Div:
    storytelling.register_callbacks(app, "classificacao")
    base_modelos = os.path.join(os.path.dirname(__file__), "..", "..", "Machine Learning", "models")
    base_shap = os.path.join(os.path.dirname(__file__), '..', '..', 'Machine Learning', 'data', 'processed')

    modelo = joblib.load(os.path.join(base_modelos, "RF_popularidade.pkl"))
    autor_frequencia = joblib.load(os.path.join(base_modelos, "autor_frequencia_RF.pkl"))

    macro_generos = [
    "Artes, Lazer e Estilo de Vida",
    "Fantasia e Ficção Científica",
    "Ficção Geral e Literatura",
    "História e Biografia",
    "Infantojuvenil e Quadrinhos",
    "Mistério, Thriller e Terror",
    "Não-Ficção e Autodesenvolvimento",
    "Outros",
    "Romance"
    ]

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
                id=f"btn-classe-{classe_id}", n_clicks=0,
                style={"background": "#FFFFFF", "border": "1px solid #E5E7EB", "borderRadius": "12px", "padding": "10px 16px", "cursor": "pointer", "textAlign": "left", "flex": "1", "gap": "10","minWidth": "200px", "boxShadow": "0 2px 4px rgba(0,0,0,0.04)", "transition": "box-shadow 0.2s, transform 0.2s"},
            )
            for classe_id, cfg in CLASSE_CONFIG.items()
        ]
    )

    layout = html.Div([
        storytelling.create_layout("classificacao"),
        html.H2("Machine Learning · Random Forest", style={"fontWeight": "700", "fontSize": "28px", "color": "#252525", "marginTop": "32px"}),
        html.P("Desempenho final do modelo e explicabilidade (SHAP) do processo decisório. Como o algoritmo entende o impacto contextual de cada variável na popularidade.", style={"fontSize": "16px", "color": "#2E3238", "marginBottom": "24px"}),
        
        # KPIs
        html.H3("Métricas de Teste", style={"marginTop": "0", "fontSize": "18px", "color": "#111827", "marginBottom": "16px"}),
        cards_metricas,
        
        html.H3("Simulador Potencial do Mercado", style={"marginTop": "0", "fontSize": "18px", "color": "#111827", "marginBottom": "16px"}),
        
        html.Div(
            style={
                "background": "#FFFFFF",
                "borderRadius": "16px",
                "padding": "24px",
                "boxShadow": "0 2px 12px rgba(0,0,0,.07)",
                "marginBottom": "40px",
            },
            children=[
                html.Div(
                    style={
                        "display": "flex",
                        "gap": "15px",
                        "marginTop": "20px",
                        "alignItems": "flex-end"
                    },
                    children=[
                        # 1. Coluna do Autor
                        html.Div(
                            style={"flex": "2"},
                            children=[
                                html.Label("Autor:", style={'display': 'block', 'marginBottom': '8px', 'fontWeight': 'bold'}),
                                dcc.Input(
                                    id="autor-input",
                                    placeholder="Ex: Agatha Christie",
                                    type="text",
                                    style={"width": "100%"}
                                )
                            ]
                        ),
                        # 2. Coluna do N° de Páginas
                        html.Div(
                            style={"width": "150px"},  # <--- Define um tamanho fixo ideal para números
                            children=[
                                html.Label("N° de Páginas:", style={'display': 'block', 'marginBottom': '8px', 'fontWeight': 'bold'}),
                                dcc.Input(
                                    id="pages-input",
                                    placeholder="Ex: 156",
                                    type="number",
                                    style={"width": "100%"}
                                )
                            ]
                        ),
                        # 3. Coluna do Macrogênero
                        html.Div(
                            style={"flex": "2"},
                            children=[
                                html.Label("Macrogênero:", style={'display': 'block', 'marginBottom': '8px', 'fontWeight': 'bold'}),
                                dcc.Dropdown(
                                    id="genero-input",
                                    options=[{"label": g, "value": g} for g in macro_generos],
                                    placeholder="Ex: Romance",
                                    style={"width": "100%"}
                                )
                            ]
                        ),
                        # 4. Botão Predizer
                        html.Button(
                            "Predizer",
                            id="btn-predizer",
                            n_clicks=0,
                            style={
                                "backgroundColor": "#E9ECEF",
                                "color": "#0E0E0E",
                                "cursor": "pointer",
                                "border": "none",
                                "borderRadius": "6px",
                                "height": "36px",
                                "transition": "background-color 0.2s"
                            }
                        )

                    ]
                ),

                html.Br(),
                html.Div(id="classe-prevista"),

                dcc.Graph(
                    id="grafico-probabilidades",
                    config={"displayModeBar": False}
                )
            ]
        ),        

        html.Div([
            html.P("Selecione a classe que deseja analisar:", style={"fontSize": "14px", "fontWeight": "600", "color": "#374151", "marginBottom": "10px"}),
            seletor_classe,
        ]),
        html.Div(id="shap-classe-badge", style={"marginBottom": "16px"}),

        # Gráfico SHAP Beeswarm
        html.H3("Comportamento e Distribuição (SHAP)", style={"marginTop": "0", "fontSize": "18px", "color": "#111827", "marginBottom": "16px"}),
        html.Div(
            style={"background": "#FFFFFF", "borderRadius": "16px", "padding": "24px", "boxShadow": "0 2px 12px rgba(0,0,0,.07)", "marginBottom": "40px"},
            children=[dcc.Graph(id="shap-beeswarm-graph", config={"displayModeBar": False})]
        ),

        # Gráfico de Decisão do Modelo
        _build_grafico_escolha_modelo(),

        dcc.Store(id="shap-classe-selecionada", data=1),
    ])

    # ── Callbacks que atualizam os graficos

    @callback(
        Output("shap-classe-selecionada", "data"),
        Input("btn-classe-1", "n_clicks"), Input("btn-classe-2", "n_clicks"), Input("btn-classe-3", "n_clicks"),
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
    def _atualizar_graficos(classe_id):
        cfg = CLASSE_CONFIG[classe_id]
        caminho_shap = os.path.join(base_shap, cfg["arquivo"])
        
        fig_shap = _build_shap_beeswarm(caminho_shap, classe_id)
        
        badge = html.Span(
            f"Analisando Classe: {cfg['label']}",
            style={"background": cfg["badge_bg"], "color": cfg["cor"], "border": f"1px solid {cfg['cor']}", "borderRadius": "20px", "padding": "6px 16px", "fontSize": "13px", "fontWeight": "600"}
        )
        return fig_shap, badge
    
    @callback(
        Output("classe-prevista","children"),
        Output("grafico-probabilidades","figure"),

        Input("btn-predizer","n_clicks"),

        State("autor-input","value"),
        State("pages-input","value"),
        State("genero-input","value"),

        prevent_initial_call=True
    )
    def _prever(n, autor, paginas, genero):
        if not autor or paginas is None or genero is None:
            return (
                html.Div(
                    "Preencha todos os campos.",
                    style={
                        "color": "red",
                        "fontWeight": "600"
                    }
                ),
                go.Figure()
            )

        author_frequency = autor_frequencia.get(autor,0)

        entrada = {}

        for coluna in modelo.feature_names_in_:

            entrada[coluna]=0

        entrada["pages"]=paginas
        entrada["author_frequency"]=author_frequency

        entrada = dict.fromkeys(modelo.feature_names_in_, 0)

        entrada["pages"] = paginas
        entrada["author_frequency"] = author_frequency

        if genero:
            entrada[genero] = 1

        X = pd.DataFrame([entrada])

        classe = modelo.predict(X)[0]

        probabilidades = modelo.predict_proba(X)[0]

        nomes = {
            1:"Bestseller",
            2:"Média Popularidade",
            3:"Nicho"
        }

        fig = go.Figure()

        cores = [
            "#C5A059",
            "#2E5A88",
            "#4A5568"
        ]

        fig.add_trace(
            go.Bar(
                x=[
                    "Bestseller",
                    "Média Popularidade",
                    "Nicho"
                ],
                y=probabilidades,
                text=[f"{p:.1%}" for p in probabilidades],
                textposition="outside",
                marker_color=cores
            )
        )

        fig.update_layout(
            title="Segmentação Comercial Estimada: ",
            paper_bgcolor="white",
            plot_bgcolor="white",
            yaxis=dict(
                title="Probabilidade",
                range=[0,1]
            ),
            xaxis_title="Classe",
            height=350
        )

        fig.update_layout(
            yaxis_range=[0,1],
            height=320,
            paper_bgcolor="white",
            plot_bgcolor="white",
            margin=dict(l=20,r=20,t=30,b=20)
        )

        texto = html.Div(

            [
                html.H3(
                    f"Classe prevista: {nomes[classe]}",
                    style={"color":"#000000"}
                )
            ]

        )

        return texto, fig

    # Injeta o estado Inicial
    cfg_init = CLASSE_CONFIG[1]
    
    layout.children[-3].children[0].figure = _build_shap_beeswarm(os.path.join(base_shap, cfg_init["arquivo"]), 1) 
    #layout.children[-5].children = html.Span(
    #    f"Analisando Classe: {cfg_init['label']}",
    #    style={"background": cfg_init["badge_bg"], "color": cfg_init["cor"], "border": f"1px solid {cfg_init['cor']}", "borderRadius": "20px", "padding": "6px 16px", "fontSize": "13px", "fontWeight": "600"}
    #)
    return layout