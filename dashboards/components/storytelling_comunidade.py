from dash import html, dcc, Input, Output

# Conteúdo do Datastorytelling da Comunidade
STORY_SECTIONS = [
    {
        "label": "O que queríamos entender",
        "text": "Como o catálogo do Booklog se comporta, quais livros, autores e gêneros dominam a plataforma, e o que a comunidade de leitores realmente valoriza e discute."
    },
    {
        "label": "O domínio dos gêneros",
        "text": "A plataforma é dominada por poucos gêneros muito populares. Romance, Fantasy e Fiction concentram a grande maioria dos livros catalogados, enquanto centenas de outros gêneros dividem o restante. Isso mostra que a base de leitores tem preferências bem definidas e consistentes."
    },
    {
        "label": "Avaliações vs. Debates",
        "text": "Os livros mais avaliados não são necessariamente os mais debatidos. Alguns títulos acumulam milhões de avaliações mas poucas reviews escritas, enquanto outros geram muito mais discussão do que popularidade, revelando dois perfis distintos de engajamento."
    },
    {
        "label": "Quantidade vs. Qualidade",
        "text": "Os autores mais produtivos raramente são os mais bem avaliados. Autores com dezenas de livros tendem a ter notas médias menores do que autores com poucos títulos mas muito impacto. Quantidade e qualidade percebida caminham em direções opostas."
    },
    {
        "label": "O que isso significa na prática",
        "text": "Entender quais livros geram mais conversa versus mais avaliações ajuda a plataforma a criar experiências mais ricas, como destacar títulos que estimulam debate nas seções sociais, ou valorizar autores de alto impacto mesmo com poucos títulos no catálogo."
    }
]

STYLE_OVERLAY = {"position": "fixed", "top": 0, "left": 0, "width": "100vw", "height": "100vh", "background": "rgba(0,0,0,0.35)", "zIndex": 998, "cursor": "pointer"}
STYLE_SIDEBAR = {"position": "fixed", "top": 0, "right": 0, "width": "360px", "height": "100vh", "background": "#FAFAF8", "borderLeft": "1px solid #E5E3DC", "zIndex": 999, "overflowY": "auto", "padding": "2rem 1.75rem 3rem", "fontFamily": "'Georgia', 'Times New Roman', serif", "boxShadow": "-8px 0 32px rgba(0,0,0,0.12)", "transition": "transform 0.35s cubic-bezier(.4,0,.2,1)"}
STYLE_BTN = {"position": "fixed", "top": "1.25rem", "right": "1.25rem", "zIndex": 1000, "background": "#2C3E50", "color": "#fff", "border": "none", "borderRadius": "8px", "padding": "0.55rem 1.1rem", "fontSize": "13px", "fontFamily": "'Georgia', serif", "letterSpacing": "0.03em", "cursor": "pointer", "display": "flex", "alignItems": "center", "gap": "6px", "boxShadow": "0 2px 8px rgba(0,0,0,0.18)"}
STYLE_CLOSE = {"background": "none", "border": "none", "cursor": "pointer", "fontSize": "20px", "color": "#888", "float": "right", "marginTop": "-4px", "lineHeight": 1}
STYLE_TITLE = {"fontSize": "17px", "fontWeight": "bold", "color": "#1a1a1a", "marginBottom": "0.25rem", "marginTop": "0.5rem", "lineHeight": 1.3}
STYLE_SUBTITLE = {"fontSize": "12px", "color": "#999", "letterSpacing": "0.06em", "textTransform": "uppercase", "marginBottom": "2rem", "borderBottom": "1px solid #E5E3DC", "paddingBottom": "1rem"}
STYLE_SECTION_LABEL = {"fontSize": "11px", "fontWeight": "bold", "color": "#2C3E50", "textTransform": "uppercase", "letterSpacing": "0.07em", "marginBottom": "0.35rem", "display": "flex", "alignItems": "center", "gap": "6px"}
STYLE_SECTION_TEXT = {"fontSize": "14px", "color": "#3a3a3a", "lineHeight": 1.75, "marginBottom": "1.5rem", "paddingBottom": "1.5rem", "borderBottom": "1px solid #EDEBE4"}
STYLE_BADGE = {"display": "inline-block", "background": "#E8F0FE", "color": "#1A73E8", "fontSize": "11px", "padding": "2px 10px", "borderRadius": "20px", "marginTop": "1.25rem", "fontFamily": "monospace"}

def storytelling_layout():
    sections = []
    for i, s in enumerate(STORY_SECTIONS):
        is_last = i == len(STORY_SECTIONS) - 1
        sections.append(
            html.Div([
                html.Div([html.Span(s, style={"fontSize": "14px"}), s["label"]], style=STYLE_SECTION_LABEL),
                html.P(s["text"], style={**STYLE_SECTION_TEXT, **({"borderBottom": "none", "marginBottom": 0} if is_last else {})}),
            ])
        )

    return html.Div([
        # IDs exclusivos com "com-" = comunidade data storytelling
        html.Button(["📖 ", "Data Storytelling"], id="story-com-btn-open", style=STYLE_BTN, n_clicks=0),
        html.Div(id="story-com-overlay", style={**STYLE_OVERLAY, "display": "none"}, n_clicks=0),
        html.Div(id="story-com-sidebar", style={**STYLE_SIDEBAR, "transform": "translateX(100%)"}, children=[
            html.Button("✕", id="story-com-btn-close", style=STYLE_CLOSE, n_clicks=0),
            html.Div("Datastorytelling", style=STYLE_SUBTITLE),
            html.Div("Comportamento, Autores e Leitores", style=STYLE_TITLE),
            html.Div("Booklog · Comunidade", style={**STYLE_SUBTITLE, "marginTop": "0.5rem"}),
            *sections,
            html.Div("Engajamento na plataforma", style=STYLE_BADGE),
        ]),
    ])

def register_callbacks(app):
    @app.callback(
        Output("story-com-sidebar", "style"),
        Output("story-com-overlay", "style"),
        Input("story-com-btn-open", "n_clicks"),
        Input("story-com-btn-close", "n_clicks"),
        Input("story-com-overlay", "n_clicks"),
        prevent_initial_call=True,
    )
    def toggle_sidebar(open_clicks, close_clicks, overlay_clicks):
        from dash import ctx
        trigger = ctx.triggered_id
        if trigger == "story-com-btn-open":
            return {**STYLE_SIDEBAR, "transform": "translateX(0)"}, {**STYLE_OVERLAY, "display": "block"}
        return {**STYLE_SIDEBAR, "transform": "translateX(100%)"}, {**STYLE_OVERLAY, "display": "none"}