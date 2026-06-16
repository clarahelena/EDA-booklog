from dash import html, dcc, Input, Output

STORY_SECTIONS = [
    {
        "label": "O Propósito do K-Means",
        "text": (
            "O objetivo da clusterização foi provar que a divisão tradicional por 'Gênero' "
            "é insuficiente para sistemas de recomendação. O algoritmo agrupou o catálogo "
            "com base na correlação entre características físicas (páginas) e "
            "o comportamento real dos usuários (notas médias e volume de avaliações)."
        ),
    },
    {
        "label": "Insight 1: O Paradoxo da Não-Ficção (Cluster 2)",
        "text": (
            "Este é o maior grupo do catálogo (35.6%), dominado por livros práticos e de "
            "autodesenvolvimento. O insight primário: existe uma relação inversamente "
            "proporcional entre nota e engajamento. Eles possuem as maiores notas médias, "
            "porém o menor volume absoluto de resenhas. É um consumo de alta satisfação, mas baixo debate."
        ),
    },
    {
        "label": "Insight 2: O Peso do Engajamento na Fantasia (Cluster 0)",
        "text": (
            "Representando apenas 18.5% do catálogo, as obras de Fantasia e Ficção Científica "
            "concentram os maiores picos na escala logarítmica de popularidade. "
            "Estatisticamente, é o cluster que sustenta o engajamento social da plataforma, "
            "gerando volumes massivos de avaliações."
        ),
    },
    {
        "label": "Insight 3: O Efeito Calhamaço no Cluster 1",
        "text": (
            "O agrupamento de Literatura Sênior e História isolou obras mais longas e densas. "
            "O cruzamento de dados quebra um viés comum: livros com alta contagem de páginas "
            "não sofrem penalização nas notas. A média se mantém estável mesmo em obras acima "
            "de 600 páginas, indicando um público altamente resiliente."
        ),
    },
    {
        "label": "Conclusão para o Sistema Booklog",
        "text": (
            "Os dados comprovam que o engajamento varia pelo cluster, não apenas pela nota. "
            "Um livro do Cluster 2 com nota 4.8 pode gerar zero discussão, enquanto um "
            "livro do Cluster 0 com nota 4.1 pode viralizar. O sistema do "
            "aplicativo deve ponderar essas diferenças para o feed do usuario."
        ),
    },
]

# ── Estilos inline ────────────────────────────────────────────────────────────

SIDEBAR_W = "360px"

STYLE_OVERLAY = {
    "position": "fixed", "top": 0, "left": 0, "width": "100vw", "height": "100vh",
    "background": "rgba(0,0,0,0.35)", "zIndex": 998, "cursor": "pointer",
}

STYLE_SIDEBAR = {
    "position": "fixed", "top": 0, "right": 0, "width": SIDEBAR_W, "height": "100vh",
    "background": "#FAFAF8", "borderLeft": "1px solid #E5E3DC", "zIndex": 999,
    "overflowY": "auto", "padding": "2rem 1.75rem 3rem",
    "fontFamily": "'Georgia', 'Times New Roman', serif",
    "boxShadow": "-8px 0 32px rgba(0,0,0,0.12)",
    "transition": "transform 0.35s cubic-bezier(.4,0,.2,1)",
}

STYLE_BTN = {
    "position": "fixed", "top": "1.25rem", "right": "1.25rem", "zIndex": 1000,
    "background": "#2C3E50", "color": "#fff", "border": "none", "borderRadius": "8px",
    "padding": "0.55rem 1.1rem", "fontSize": "13px", "fontFamily": "'Georgia', serif",
    "letterSpacing": "0.03em", "cursor": "pointer", "display": "flex",
    "alignItems": "center", "gap": "6px", "boxShadow": "0 2px 8px rgba(0,0,0,0.18)",
}

STYLE_CLOSE = {
    "background": "none", "border": "none", "cursor": "pointer", "fontSize": "20px",
    "color": "#888", "float": "right", "marginTop": "-4px", "lineHeight": 1,
}

STYLE_TITLE = {
    "fontSize": "17px", "fontWeight": "bold", "color": "#1a1a1a",
    "marginBottom": "0.25rem", "marginTop": "0.5rem", "lineHeight": 1.3,
}

STYLE_SUBTITLE = {
    "fontSize": "12px", "color": "#999", "letterSpacing": "0.06em",
    "textTransform": "uppercase", "marginBottom": "2rem",
    "borderBottom": "1px solid #E5E3DC", "paddingBottom": "1rem",
}

STYLE_SECTION_LABEL = {
    "fontSize": "11px", "fontWeight": "bold", "color": "#2C3E50",
    "textTransform": "uppercase", "letterSpacing": "0.07em",
    "marginBottom": "0.35rem", "display": "flex", "alignItems": "center", "gap": "6px",
}

STYLE_SECTION_TEXT = {
    "fontSize": "14px", "color": "#3a3a3a", "lineHeight": 1.75,
    "marginBottom": "1.5rem", "paddingBottom": "1.5rem",
    "borderBottom": "1px solid #EDEBE4",
}

STYLE_BADGE = {
    "display": "inline-block", "background": "#F3E5F5", "color": "#6A1B9A",
    "fontSize": "11px", "padding": "2px 10px", "borderRadius": "20px",
    "marginTop": "1.25rem", "fontFamily": "monospace",
}

# ── Layout ────────────────────────────────────────────────────────────────────

def storytelling_layout():
    """
    Retorna o botão, overlay e o painel lateral com IDs exclusivos para ML cluster.
    """
    sections = []
    for i, s in enumerate(STORY_SECTIONS):
        is_last = i == len(STORY_SECTIONS) - 1
        sections.append(
            html.Div([
                html.Div([
                    s["label"],
                ], style=STYLE_SECTION_LABEL),
                html.P(
                    s["text"],
                    style={**STYLE_SECTION_TEXT, **({"borderBottom": "none", "marginBottom": 0} if is_last else {})},
                ),
            ])
        )

    return html.Div([

        # botão flutuante
        html.Button(
            "Data Storytelling",
            id="story-clus-btn-open",
            style=STYLE_BTN,
            n_clicks=0,
        ),

        # overlay escurecido (clicável para fechar)
        html.Div(
            id="story-clus-overlay",
            style={**STYLE_OVERLAY, "display": "none"},
            n_clicks=0,
        ),

        # painel lateral
        html.Div(
            id="story-clus-sidebar",
            style={**STYLE_SIDEBAR, "transform": "translateX(100%)"},
            children=[
                html.Button("✕", id="story-clus-btn-close", style=STYLE_CLOSE, n_clicks=0),
                html.Div("Datastorytelling", style=STYLE_SUBTITLE),
                html.Div("A Personalidade das Tribos Literárias", style=STYLE_TITLE),
                html.Div("Booklog · Notebook 05", style={**STYLE_SUBTITLE, "marginTop": "0.5rem"}),
                *sections,
                html.Div("Machine Learning · K-Means", style=STYLE_BADGE),
            ],
        ),

    ])

# ── Callbacks ─────────────────────────────────────────────────────────────────

def register_callbacks(app):
    """
    Registra os callbacks de abrir/fechar o painel de clusterização.
    """
    @app.callback(
        Output("story-clus-sidebar", "style"),
        Output("story-clus-overlay", "style"),
        Input("story-clus-btn-open", "n_clicks"),
        Input("story-clus-btn-close", "n_clicks"),
        Input("story-clus-overlay", "n_clicks"),
        prevent_initial_call=True,
    )
    def toggle_sidebar(open_clicks, close_clicks, overlay_clicks):
        from dash import ctx
        trigger = ctx.triggered_id

        if trigger == "story-clus-btn-open":
            sidebar = {**STYLE_SIDEBAR, "transform": "translateX(0)"}
            overlay = {**STYLE_OVERLAY, "display": "block"}
        else:
            sidebar = {**STYLE_SIDEBAR, "transform": "translateX(100%)"}
            overlay = {**STYLE_OVERLAY, "display": "none"}

        return sidebar, overlay