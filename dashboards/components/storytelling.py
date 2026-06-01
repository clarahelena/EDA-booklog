from dash import html, dcc, Input, Output, callback

# ── Conteúdo do datastorytelling 1

STORY_SECTIONS = [
    {
        "label": "O que queríamos entender",
        "text": (
            "Se o formato de um livro — brochura, capa dura, ebook — tem "
            "alguma relação com a quantidade de paginas que ele vai ter. "
            "E se o gênero literário influencia essa escolha de formato."
        ),
    },
    {
        "label": "Formato não define tamanho",
        "text": (
            "Paperback, Hardcover e Ebook se concentram todos na mesma faixa — "
            "em torno de 300 páginas. A ideia de que ebooks tendem a ser mais "
            "curtos ou que capas duras existem só para livros grandes não se "
            "sustenta nos dados."
        ),
    },
    {
        "label": "A hegemonia da brochura",
        "text": (
            "O Paperback domina 18 dos 20 maiores gêneros do acervo. "
            "Não é liderança — é quase monopólio. Ignorar esse peso "
            "esmagador ao planejar a distribuição ou aquisição de novos títulos significa "
            "otimizar para um mercado que simplesmente não existe."
        ),
    },
    {
        "label": "O que ainda não sabemos",
        "text": (
            "Se esse padrão é uma característica do mercado global ou um viés "
            "do dataset do Kaggle."
        ),
    },
]

# Estilos inline

SIDEBAR_W = "360px"

STYLE_OVERLAY = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "width": "100vw",
    "height": "100vh",
    "background": "rgba(0,0,0,0.35)",
    "zIndex": 998,
    "cursor": "pointer",
}

STYLE_SIDEBAR = {
    "position": "fixed",
    "top": 0,
    "right": 0,
    "width": SIDEBAR_W,
    "height": "100vh",
    "background": "#FAFAF8",
    "borderLeft": "1px solid #E5E3DC",
    "zIndex": 999,
    "overflowY": "auto",
    "padding": "2rem 1.75rem 3rem",
    "fontFamily": "'Georgia', 'Times New Roman', serif",
    "boxShadow": "-8px 0 32px rgba(0,0,0,0.12)",
    "transition": "transform 0.35s cubic-bezier(.4,0,.2,1)",
}

STYLE_BTN = {
    "position": "fixed",
    "top": "1.25rem",
    "right": "1.25rem",
    "zIndex": 1000,
    "background": "#2C3E50",
    "color": "#fff",
    "border": "none",
    "borderRadius": "8px",
    "padding": "0.55rem 1.1rem",
    "fontSize": "13px",
    "fontFamily": "'Georgia', serif",
    "letterSpacing": "0.03em",
    "cursor": "pointer",
    "display": "flex",
    "alignItems": "center",
    "gap": "6px",
    "boxShadow": "0 2px 8px rgba(0,0,0,0.18)",
}

STYLE_CLOSE = {
    "background": "none",
    "border": "none",
    "cursor": "pointer",
    "fontSize": "20px",
    "color": "#888",
    "float": "right",
    "marginTop": "-4px",
    "lineHeight": 1,
}

STYLE_TITLE = {
    "fontSize": "17px",
    "fontWeight": "bold",
    "color": "#1a1a1a",
    "marginBottom": "0.25rem",
    "marginTop": "0.5rem",
    "lineHeight": 1.3,
}

STYLE_SUBTITLE = {
    "fontSize": "12px",
    "color": "#999",
    "letterSpacing": "0.06em",
    "textTransform": "uppercase",
    "marginBottom": "2rem",
    "borderBottom": "1px solid #E5E3DC",
    "paddingBottom": "1rem",
}

STYLE_SECTION_LABEL = {
    "fontSize": "11px",
    "fontWeight": "bold",
    "color": "#2C3E50",
    "textTransform": "uppercase",
    "letterSpacing": "0.07em",
    "marginBottom": "0.35rem",
    "display": "flex",
    "alignItems": "center",
    "gap": "6px",
}

STYLE_SECTION_TEXT = {
    "fontSize": "14px",
    "color": "#3a3a3a",
    "lineHeight": 1.75,
    "marginBottom": "1.5rem",
    "paddingBottom": "1.5rem",
    "borderBottom": "1px solid #EDEBE4",
}

STYLE_BADGE = {
    "display": "inline-block",
    "background": "#EAF3DE",
    "color": "#3B6D11",
    "fontSize": "11px",
    "padding": "2px 10px",
    "borderRadius": "20px",
    "marginTop": "1.25rem",
    "fontFamily": "monospace",
}


# layout

def storytelling_layout():
    """
    Retorna o botão, overlay e o painel lateral.
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
            id="story-btn-open",
            style=STYLE_BTN,
            n_clicks=0,
        ),

        # overlay escurecido (clicável para fechar)
        html.Div(
            id="story-overlay",
            style={**STYLE_OVERLAY, "display": "none"},
            n_clicks=0,
        ),

        # painel lateral
        html.Div(
            id="story-sidebar",
            style={**STYLE_SIDEBAR, "transform": "translateX(100%)"},
            children=[
                html.Button("✕", id="story-btn-close", style=STYLE_CLOSE, n_clicks=0),
                html.Div("Datastorytelling", style=STYLE_SUBTITLE),
                html.Div("O que o formato de um livro revela sobre suas caracteristicas", style=STYLE_TITLE),
                html.Div("Booklog · Notebook 03", style={**STYLE_SUBTITLE, "marginTop": "0.5rem"}),
                *sections,
                html.Div("Dados: Kaggle · não generalizável", style=STYLE_BADGE),
            ],
        ),

    ])


# ── Callbacks ─────────────────────────────────────────────────────────────────

def register_callbacks(app):
    """
    Registra os callbacks de abrir/fechar o painel.
    """
    @app.callback(
        Output("story-sidebar", "style"),
        Output("story-overlay", "style"),
        Input("story-btn-open", "n_clicks"),
        Input("story-btn-close", "n_clicks"),
        Input("story-overlay", "n_clicks"),
        prevent_initial_call=True,
    )
    def toggle_sidebar(open_clicks, close_clicks, overlay_clicks):
        from dash import ctx
        trigger = ctx.triggered_id

        if trigger == "story-btn-open":
            sidebar = {**STYLE_SIDEBAR, "transform": "translateX(0)"}
            overlay = {**STYLE_OVERLAY, "display": "block"}
        else:
            sidebar = {**STYLE_SIDEBAR, "transform": "translateX(100%)"}
            overlay = {**STYLE_OVERLAY, "display": "none"}

        return sidebar, overlay
