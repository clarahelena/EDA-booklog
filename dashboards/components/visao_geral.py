"""
visao_geral.py  –  Página "Visão Geral da Plataforma" do Booklog Dashboard
Autora: (seu nome)

Gráficos desta página:
  1. KPI Cards: números rápidos da base de livros
  2. Distribuição de Notas (histograma): como as notas se distribuem
  3. Top Autores: quem tem mais livros e melhores médias
  4. Formatos de Leitura (pizza/sunburst): proporção dos formatos
  5. Livros mais bem avaliados (tabela/bar horizontal): ranking de títulos
"""

import itertools
from collections import Counter

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, dcc, html

# ─────────────────────────────────────────────────────────────
# paleta e estilo compartilhados com o restante do dashboard
# ─────────────────────────────────────────────────────────────
BG_CARD  = '#1e293b'
BG_PAGE  = '#0f172a'
ACCENT   = '#a3e635'
TEXT     = '#f8fafc'
MUTED    = '#94a3b8'
TEMPLATE = 'plotly_dark'
TRANSP   = 'rgba(0,0,0,0)'

CARD_STYLE = {
    'backgroundColor': BG_CARD,
    'padding': '24px',
    'borderRadius': '12px',
    'border': f'1px solid #334155',
}


# ─────────────────────────────────────────────────────────────
# helpers
# ─────────────────────────────────────────────────────────────
def _fmt_num(n: int | float) -> str:
    """Formata número grande com separador de milhar."""
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(int(n))


def _kpi_card(titulo: str, valor: str, icone: str, cor: str = ACCENT):
    return html.Div(
        style={**CARD_STYLE, 'textAlign': 'center', 'flex': '1', 'minWidth': '160px'},
        children=[
            html.Div(icone, style={'fontSize': '32px', 'marginBottom': '8px'}),
            html.Div(valor, style={'fontSize': '28px', 'fontWeight': 'bold', 'color': cor}),
            html.Div(titulo, style={'fontSize': '13px', 'color': MUTED, 'marginTop': '4px'}),
        ]
    )


# ─────────────────────────────────────────────────────────────
# render – função chamada pelo app.py
# ─────────────────────────────────────────────────────────────
def render(app, df: pd.DataFrame):
    """Monta o layout e registra os callbacks desta página."""

    # ── pré-processamento ──────────────────────────────────
    df_valido = df[(df['pages'] > 0) & (df['rating'] > 0)].copy()

    # top autores com pelo menos 5 livros
    autor_stats = (
        df_valido.groupby('author')
        .agg(qtd_livros=('title', 'count'), media_nota=('rating', 'mean'), total_ratings=('totalratings', 'sum'))
        .reset_index()
    )
    top_autores = autor_stats[autor_stats['qtd_livros'] >= 5].nlargest(15, 'total_ratings')

    # formatos de leitura (agrupa menores em "Outros")
    fmt_counts = df['bookformat'].value_counts().reset_index()
    fmt_counts.columns = ['Formato', 'Qtd']
    threshold = fmt_counts['Qtd'].sum() * 0.02
    fmt_counts.loc[fmt_counts['Qtd'] < threshold, 'Formato'] = 'Outros'
    fmt_counts = fmt_counts.groupby('Formato', as_index=False)['Qtd'].sum()

    # livros com mais avaliações (top 10)
    top_livros = (
        df_valido[df_valido['totalratings'] > 0]
        .nlargest(10, 'totalratings')[['title', 'author', 'rating', 'totalratings', 'genre']]
        .reset_index(drop=True)
    )
    # Trunca título longo para exibição
    top_livros['titulo_curto'] = top_livros['title'].str[:45] + top_livros['title'].apply(
        lambda x: '…' if len(x) > 45 else ''
    )

    # ── KPI cards ──────────────────────────────────────────
    total_livros   = len(df)
    total_autores  = df['author'].nunique()
    nota_media     = df_valido['rating'].mean()
    total_aval     = df['totalratings'].sum()
    paginas_media  = int(df_valido['pages'].mean())

    kpi_row = html.Div(
        style={'display': 'flex', 'gap': '16px', 'flexWrap': 'wrap', 'marginBottom': '32px'},
        children=[
            _kpi_card("Livros no catálogo", _fmt_num(total_livros),   "📚"),
            _kpi_card("Autores únicos",      _fmt_num(total_autores),  "✍️"),
            _kpi_card("Nota média geral",    f"{nota_media:.2f}",   "⭐", '#facc15'),
            _kpi_card("Total de avaliações", _fmt_num(total_aval),     "💬", '#38bdf8'),
            _kpi_card("Média de páginas",    f"{paginas_media} pgs",   "📄", '#f472b6'),
        ]
    )

    # ── gráfico 1 – Distribuição de Notas (histograma) ────
    fig_hist = px.histogram(
        df_valido, x='rating', nbins=40,
        title='Distribuição das Notas dos Livros',
        template=TEMPLATE,
        color_discrete_sequence=[ACCENT],
    )
    fig_hist.update_layout(
        paper_bgcolor=TRANSP, plot_bgcolor=TRANSP,
        xaxis_title='Nota', yaxis_title='Quantidade de livros',
        bargap=0.05,
    )
    fig_hist.add_vline(
        x=nota_media, line_dash='dash', line_color='#facc15',
        annotation_text=f' Média: {nota_media:.2f}',
        annotation_font_color='#facc15',
    )

    # ── gráfico 2 – Top Autores por popularidade ──────────
    fig_autores = px.scatter(
        top_autores,
        x='qtd_livros', y='media_nota',
        size='total_ratings', color='media_nota',
        hover_name='author',
        hover_data={'qtd_livros': True, 'media_nota': ':.2f', 'total_ratings': True},
        title='Top Autores: Produtividade × Nota Média',
        template=TEMPLATE,
        color_continuous_scale='Viridis',
        size_max=60,
        labels={'qtd_livros': 'Livros publicados', 'media_nota': 'Nota média', 'total_ratings': 'Total de avaliações'},
    )
    fig_autores.update_layout(paper_bgcolor=TRANSP, plot_bgcolor=TRANSP)

    # ── gráfico 3 – Formatos de Leitura (pizza) ───────────
    fig_rosca = px.pie(
        fmt_counts, names='Formato', values='Qtd',
        title='Proporção dos Formatos de Leitura',
        template=TEMPLATE,
        color_discrete_sequence=px.colors.sequential.Viridis,
        hole=0.4,
    )
    fig_rosca.update_traces(textposition='inside', textinfo='percent+label')
    fig_rosca.update_layout(paper_bgcolor=TRANSP, showlegend=True)

    # ── gráfico 4 – Top 10 livros mais avaliados ──────────
    fig_top = px.bar(
        top_livros, x='totalratings', y='titulo_curto',
        orientation='h',
        color='rating',
        color_continuous_scale='Viridis',
        range_color=[3.5, 5],
        hover_data={'author': True, 'rating': True, 'titulo_curto': False},
        hover_name='title',
        title='Top 10 Livros Mais Avaliados',
        template=TEMPLATE,
        labels={'totalratings': 'Total de avaliações', 'titulo_curto': '', 'rating': 'Nota'},
    )
    fig_top.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        paper_bgcolor=TRANSP, plot_bgcolor=TRANSP,
    )

    # ── layout da página ───────────────────────────────────
    layout = html.Div(
        style={'color': TEXT},
        children=[
            # cabeçalho
            html.H1("🌐 Visão Geral da Plataforma",
                    style={'textAlign': 'center', 'marginBottom': '8px', 'color': ACCENT}),
            html.P("Uma visão consolidada do catálogo de livros da plataforma Booklog.",
                   style={'textAlign': 'center', 'color': MUTED, 'marginBottom': '36px', 'fontSize': '15px'}),

            # KPIs
            kpi_row,

            # linha 1: histograma + pizza
            html.Div(
                style={'display': 'flex', 'gap': '20px', 'marginBottom': '24px', 'flexWrap': 'wrap'},
                children=[
                    html.Div(style={**CARD_STYLE, 'flex': '2', 'minWidth': '320px'},
                             children=[dcc.Graph(figure=fig_hist)]),
                    html.Div(style={**CARD_STYLE, 'flex': '1', 'minWidth': '680px'},
                             children=[dcc.Graph(figure=fig_rosca)]),
                ]
            ),

            # linha 2: scatter autores + bar top livros
            html.Div(
                style={'display': 'flex', 'gap': '20px', 'flexWrap': 'wrap'},
                children=[
                    html.Div(style={**CARD_STYLE, 'flex': '1', 'minWidth': '320px'},
                             children=[dcc.Graph(figure=fig_autores)]),
                    html.Div(style={**CARD_STYLE, 'flex': '1', 'minWidth': '320px'},
                             children=[dcc.Graph(figure=fig_top)]),
                ]
            ),
        ]
    )

    return layout