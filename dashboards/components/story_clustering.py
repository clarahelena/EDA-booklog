from dash import html, dcc, Input, Output

STORY_SECTIONS = [
    {
        "label": "O Que Queríamos Entender",
        "text": (
            "Como os leitores se comportam e se agrupam organicamente na plataforma. "
            "A ideia era ir além das divisões tradicionais de gênero e usar Machine Learning "
            "para descobrir 'tribos' com base em hábitos reais de leitura, volume de "
            "avaliações e tamanho das obras."
        ),
    },
    {
        "label": "Universo Geek e Fantasia Pop (Cluster 0)",
        "text": (
            "Representando 18.5% do catálogo, o Cluster 0 concentra os leitores mais vorazes "
            "e apaixonados. São extremamente vocais e lideram absolutamente a popularidade "
            "de resenhas. Consomem em peso mundos fantásticos, magia, aventura e ficção científica."
        ),
    },
    {
        "label": "Literatura Sênior e Ensaios (Cluster 1)",
        "text": (
            "O Cluster 1 (23.9%) revela um público exigente e focado em densidade. "
            "Eles preferem biografias, história, ensaios e clássicos literários. São "
            "leitores que valorizam a profundidade intelectual e não se intimidam com "
            "calhamaços complexos."
        ),
    },
    {
        "label": "Não-Ficção de Nicho e Lazer (Cluster 2)",
        "text": (
            "A maior tribo da plataforma (35.6%) é o Cluster 2. Buscam livros práticos sobre "
            "carreiras, estilo de vida e autodesenvolvimento. Um dado curioso: eles dão notas "
            "muito altas, mas são uma comunidade silenciosa, com um perfil de exposição muito "
            "menor nas resenhas escritas."
        ),
    },
    {
        "label": "Romances Mainstream e Dramas (Cluster 3)",
        "text": (
            "O Cluster 3 (22.0%) é a casa dos devoradores de sucessos comerciais. Preferem "
            "romances e dramas com narrativas fluidas e de leitura rápida. Possuem uma altíssima "
            "identificação comunitária, consumindo os títulos que estão em alta nas discussões."
        ),
    },
    {
        "label": "O Que Isso Significa na Prática",
        "text": (
            "O modelo provou que recomendar livros apenas por gênero é ineficiente. Leitores de "
            "fantasia (vocalizados) engajam de forma totalmente diferente dos leitores de guias "
            "práticos (silenciosos). Entender essas personalidades permite criar recomendações "
            "hiper-direcionadas."
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