from dash import html, dcc, Input, Output

# ── Conteúdo do Datastorytelling
STORY_SECTIONS = [
    {
        "label": "O Propósito do Modelo",
        "text": (
            "O objetivo da classificação supervisionada foi provar que é possível antecipar o "
            "potencial de popularidade de uma obra (Bestseller, Média Popularidade ou Nicho) "
            "antes mesmo de o livro interagir com o público. O pipeline testou algoritmos para "
            "comprovar que metadados estruturais de pré-lançamento (páginas, gênero e autor) "
            "possuem sinal estatístico autossuficiente para prever o engajamento futuro."
        ),
    },
    {
        "label": "Insight 1: O Efeito Divisor da Ficção (Filtro Brutal)",
        "text": (
            "Mapeado pela análise SHAP, o gênero de Ficção atua como o maior redutor de "
            "entropia do catálogo. O algoritmo identificou que a natureza ficcional funciona "
            "como um divisor de águas: ela direciona a obra para um ecossistema de consumo "
            "totalmente diferente da não-ficção, sendo a principal locomotiva de hype e "
            "formação de comunidades ativas dentro do aplicativo."
        ),
    },
    {
        "label": "Insight 2: A Grife do Autor como Multiplicador",
        "text": (
            "Ao abrir a 'caixa-preta' do modelo via valores de Shapley, descobriu-se que a "
            "frequência histórica com que um autor publica títulos é a variável individual que "
            "mais empurra a previsão em direção à classe Bestseller. Os dados provam que o "
            "comportamento de arrasto na plataforma é ditado pela assinatura e consistência "
            "do escritor, atuando como um forte preditor de retenção."
        ),
    },
    {
        "label": "Insight 3: O Paradoxo do Erro Comercial (RF vs XGBoost)",
        "text": (
            "Embora o XGBoost tenha vencido na eficiência matemática global, a avaliação "
            "cega revelou um paradoxo de negócio: a Random Forest foi superior na tarefa "
            "mais crítica do produto, alcançando o maior índice de Sensibilidade (Recall de 0.59 "
            "na classe Bestseller). Para o Booklog, o custo de ignorar um fenômeno editorial "
            "(falso negativo) é muito maior do que inflar uma obra média, justificando a RF."
        ),
    },
    {
        "label": "Conclusão para o Sistema Booklog",
        "text": (
            "Os dados comprovam que o sucesso comercial pode ser rastreado na origem "
            "estrutural do livro. O motor preditivo baseado em Random Forest deve ser integrado "
            "nativamente ao backend para rotular automaticamente novos títulos cadastrados. "
            "Isso permitirá que o sistema molde o feed do usuário de forma proativa."
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
    Retorna o botão, overlay e o painel lateral com IDs exclusivos para ML Classificação.
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
            id="story-class-btn-open",
            style=STYLE_BTN,
            n_clicks=0,
        ),

        # overlay escurecido (clicável para fechar)
        html.Div(
            id="story-class-overlay",
            style={**STYLE_OVERLAY, "display": "none"},
            n_clicks=0,
        ),

        # painel lateral
        html.Div(
            id="story-class-sidebar",
            style={**STYLE_SIDEBAR, "transform": "translateX(100%)"},
            children=[
                html.Button("✕", id="story-class-btn-close", style=STYLE_CLOSE, n_clicks=0),
                html.Div("Datastorytelling", style=STYLE_SUBTITLE),
                html.Div("O DNA do Sucesso Literário", style=STYLE_TITLE),
                html.Div("Booklog · Notebook 08", style={**STYLE_SUBTITLE, "marginTop": "0.5rem"}),
                *sections,
                html.Div("Machine Learning · Random Forest", style=STYLE_BADGE),
            ],
        ),

    ])

# ── Callbacks ─────────────────────────────────────────────────────────────────

def register_callbacks(app):
    """
    Registra os callbacks de abrir/fechar o painel de classificação.
    """
    @app.callback(
        Output("story-class-sidebar", "style"),
        Output("story-class-overlay", "style"),
        Input("story-class-btn-open", "n_clicks"),
        Input("story-class-btn-close", "n_clicks"),
        Input("story-class-overlay", "n_clicks"),
        prevent_initial_call=True,
    )
    def toggle_sidebar(open_clicks, close_clicks, overlay_clicks):
        from dash import ctx
        trigger = ctx.triggered_id

        if trigger == "story-class-btn-open":
            sidebar = {**STYLE_SIDEBAR, "transform": "translateX(0)"}
            overlay = {**STYLE_OVERLAY, "display": "block"}
        else:
            sidebar = {**STYLE_SIDEBAR, "transform": "translateX(100%)"}
            overlay = {**STYLE_OVERLAY, "display": "none"}

        return sidebar, overlay