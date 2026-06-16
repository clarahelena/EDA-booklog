import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from dash import html, dcc, Input, Output, State, dash_table
from components import story_classificacao

# Configuração visual
CLASSE_CONFIG = {
    0: {
        "label":    "Nicho",
        "cor":      "#6366F1",
        "desc":     "Obras com perfil especializado, público menor mas fiel.",
        "badge_bg": "#EEF2FF",
    },
    1: {
        "label":    "Alta Popularidade",
        "cor":      "#F59E0B",
        "desc":     "Obras com apelo amplo e alto volume de leitores.",
        "badge_bg": "#FFFBEB",
    },
}

# ── Loader do parquet
def _carregar_df_pop(base_dir: str) -> pd.DataFrame | None:
    caminho_correto = os.path.abspath(
        os.path.join(
            base_dir, '..', '..', 'Machine Learning',
            'data', 'processed', 'livros_com_popularidade_dashboard.parquet'
        )
    )
    if os.path.exists(caminho_correto):
        return pd.read_parquet(caminho_correto)
    return None


# ── Helpers de layout
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


def _build_shap_beeswarm(caminho_parquet: str) -> go.Figure:
    """
    Constrói o gráfico beeswarm SHAP com direção correta dos valores.

    O parquet deve conter as colunas:
        - Feature       : nome da variável (str ou Categorical ordenado)
        - SHAP_Value    : valor SHAP da classe 1 (Alta Popularidade), com sinal
        - Feature_Value : valor normalizado [0,1] da variável original (para cor)

    Positivo → empurra para Alta Popularidade
    Negativo → empurra para Nicho
    """
    try:
        df_shap = pd.read_parquet(caminho_parquet)
    except FileNotFoundError:
        return go.Figure().update_layout(
            title="Arquivo shap_beeswarm.parquet não encontrado.",
            paper_bgcolor="#FFF8F0"
        )

    # ── 1. Preserva a ordem de importância vinda do parquet (Categorical ordenado)
    #       Se a coluna não for Categorical, ordena pela média absoluta dos SHAP values
    if hasattr(df_shap['Feature'], 'cat') and df_shap['Feature'].cat.ordered:
        # Ordem já gravada no parquet (menor → maior importância, de baixo pra cima)
        ordered_features = list(df_shap['Feature'].cat.categories)
    else:
        # Fallback: calcula a ordem aqui mesmo
        ordered_features = (
            df_shap
            .assign(_abs=df_shap['SHAP_Value'].abs())
            .groupby('Feature')['_abs']
            .mean()
            .sort_values(ascending=True)   # menor importância primeiro → ficará embaixo
            .index.tolist()
        )

    # ── 2. Mapeia feature → posição numérica no eixo Y
    feat_to_y = {f: i for i, f in enumerate(ordered_features)}
    df_shap['Feature_Str'] = df_shap['Feature'].astype(str)

    # ── 3. Jitter vertical para evitar sobreposição (beeswarm effect)
    np.random.seed(42)
    y_base = df_shap['Feature_Str'].map(feat_to_y).astype(float)
    df_shap['Y_Jitter'] = y_base + np.random.uniform(-0.35, 0.35, size=len(df_shap))

    # ── 4. Clipa o Feature_Value entre 0 e 1 para evitar artefatos de cor
    df_shap['Feature_Value'] = df_shap['Feature_Value'].clip(0, 1)

    # ── 5. Constrói o scatter
    fig = px.scatter(
        df_shap,
        x='SHAP_Value',
        y='Y_Jitter',
        color='Feature_Value',
        # Azul = valor baixo da feature → Vermelho = valor alto (padrão SHAP)
        color_continuous_scale=['#377eb8', '#e41a1c'],
        range_color=[0, 1],
        labels={
            'SHAP_Value':    'Impacto na Saída do Modelo (Valor SHAP)',
            'Feature_Value': 'Valor da Variável',
        },
    )

    fig.update_traces(marker=dict(size=4, opacity=0.65, line=dict(width=0)))

    # ── 6. Layout — linha zero bem visível, nomes das features no eixo Y
    x_max = df_shap['SHAP_Value'].abs().max() * 1.1   # margem simétrica
    x_max = max(x_max, 0.05)                           # garante mínimo

    fig.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#F9FAFB",
        font_family="Poppins, sans-serif",
        font_color="#374151",
        margin=dict(l=20, r=30, t=50, b=40),

        # Eixo X simétrico em torno de zero para mostrar direção
        xaxis=dict(
            showgrid=True,
            gridcolor="#EBEBEB",
            zeroline=True,
            zerolinecolor="#252525",
            zerolinewidth=1.5,
            range=[-x_max, x_max],
            title_font=dict(size=12),
        ),

        # Eixo Y: nomes das features nas posições corretas
        yaxis=dict(
            showgrid=True,
            gridcolor="#EBEBEB",
            zeroline=False,
            tickmode='array',
            tickvals=list(feat_to_y.values()),
            ticktext=list(feat_to_y.keys()),
            title="",
            tickfont=dict(size=12),
        ),

        height=max(400, 45 * len(ordered_features)),  # altura proporcional ao nº de features

        # Barra de cor com legenda clara
        coloraxis_colorbar=dict(
            title=dict(text="Valor da<br>Variável", font=dict(size=11)),
            tickvals=[0, 0.5, 1],
            ticktext=["Baixo", "Médio", "Alto"],
            thickness=14,
            len=0.6,
            y=0.5,
        ),

        # Anotações de direção (← Nicho | Alta Popularidade →)
        annotations=[
            dict(
                x=-x_max * 0.97, y=-0.12,
                xref="x", yref="paper",
                text="← Nicho",
                showarrow=False,
                font=dict(size=11, color="#6366F1"),
                xanchor="left",
            ),
            dict(
                x=x_max * 0.97, y=-0.12,
                xref="x", yref="paper",
                text="Alta Popularidade →",
                showarrow=False,
                font=dict(size=11, color="#F59E0B"),
                xanchor="right",
            ),
        ],
    )

    return fig


# ── Renderização do Layout Principal
def render(app, df_books: pd.DataFrame) -> html.Div:
    caminho_shap = os.path.join(
        os.path.dirname(__file__), '..', '..',
        'Machine Learning', 'data', 'processed', 'shap_beeswarm.parquet'
    )

    return html.Div([
        story_classificacao.storytelling_layout(),
        html.H2(
            "Machine Learning · Explicabilidade do Modelo (SHAP)",
            style={"fontWeight": "700", "fontSize": "22px", "color": "#252525"},
        ),
        html.P(
            "Como o modelo Random Forest 'pensa'. Analisamos o impacto de cada "
            "característica na decisão de classificar um livro como Popular ou de Nicho. "
            "Valores positivos empurram para Alta Popularidade; negativos, para Nicho.",
            style={"fontSize": "14px", "color": "#6B7280"},
        ),

        html.Div(
            style={
                "background":   "#FFFFFF",
                "borderRadius": "16px",
                "padding":      "24px",
                "boxShadow":    "0 2px 12px rgba(0,0,0,.07)",
                "marginTop":    "24px",
            },
            children=[
                dcc.Graph(
                    figure=_build_shap_beeswarm(caminho_shap),
                    config={"displayModeBar": False},
                )
            ],
        ),
    ])