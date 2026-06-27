from dash import html, Input, Output

# dicionario com todas as storytellings do dashboard
STORY_DATA = {
    "hipoteses": {
        "title": "O que o formato de um livro revela sobre suas caracteristicas",
        "subtitle": "Booklog · Notebook 03",
        "badge": "Dados: Kaggle · não generalizável",
        "badge_bg": "#EAF3DE", "badge_color": "#3B6D11",
        "sections": [
            {"label": "O que queríamos entender", "text": "Se existe diferença real na quantidade de páginas entre os principais formatos físicos — Paperback e Hardcover — e o digital (ebook). A hipótese era que o formato poderia influenciar o tamanho da obra."},
            {"label": "Formato não define tamanho", "text": "Os três principais formatos convergem para a mesma faixa: Paperback com pico em 298 páginas, Hardcover em 310 e ebook em 283. A diferença entre o formato mais curto e o mais longo é de apenas 27 páginas — o formato não determina o tamanho do livro."},
            {"label": "A hegemonia da brochura", "text": "O Paperback domina 18 dos 20 maiores gêneros do acervo e representa 61,5% do volume filtrado. Novas editoras podem seguir essas metricas para começar no mercado, como um guia seguro."},
            {"label": "O que ainda não sabemos", "text": "Se esse padrão é uma característica do mercado global ou um viés do dataset do Kaggle."},
        ]
    },
    "comunidade": {
        "title": "Comportamento, Autores e Leitores",
        "subtitle": "Booklog · Comunidade",
        "badge": "Engajamento na plataforma",
        "badge_bg": "#E8F0FE", "badge_color": "#1A73E8",
        "sections": [
            {"label": "O que queríamos entender", "text": "Como o catálogo do Booklog se comporta, quais formatos e gêneros dominam a plataforma, e de que forma a comunidade de leitores realmente interage, gerando valor e debate."},
            {"label": "Insight 1: O Formato não Define o Tamanho", "text": "Descobrimos que o formato físico não dita a extensão da obra: de e-books a edições em capa dura, a distribuição de páginas é equivalente. No entanto, o formato Brochura (paperback) é o verdadeiro motor do catálogo, dominando 18 dos 20 maiores gêneros."},
            {"label": "Insight 2: Estrelinhas vs. Longas Conversas", "text": "O catálogo é concentrado em poucos gêneros, mas os dados revelam que os livros mais votados não são os mais discutidos. Há obras que recebem avaliações rápidas (apenas notas) e outras que despertam uma necessidade real de diálogo, gerando resenhas longas e debates."},
            {"label": "Valor Prático: Editoras e Usuários", "text": "Para as editoras, mapear esse comportamento ajuda a identificar quais livros criam comunidades leais e engajadas. Para o usuário do Booklog, o sistema ganha inteligência para personalizar o feed: recomendando livros que estimulam conversas para quem gosta de debater, ou títulos de sucesso garantido para quem busca leituras rápidas."}
        ]
    },
    "clustering": {
        "title": "A Personalidade das Tribos Literárias",
        "subtitle": "Booklog · Clusterização",
        "badge": "Machine Learning · K-Means",
        "badge_bg": "#F3E5F5", "badge_color": "#6A1B9A",
        "sections": [
            {"label": "O Que Queríamos Entender", "text": "Como os leitores se comportam e se agrupam organicamente na plataforma. A ideia era ir além das divisões tradicionais de gênero e usar Machine Learning para descobrir 'tribos' com base em hábitos reais de leitura, volume de avaliações e tamanho das obras."},
            {"label": "Universo Geek e Fantasia Pop (Cluster 0)", "text": "Representando 18.5% do catálogo, o Cluster 0 concentra os leitores mais vorazes e apaixonados. São extremamente vocais e lideram absolutamente a popularidade de resenhas. Consomem em peso mundos fantásticos, magia, aventura e ficção científica."},
            {"label": "Literatura Sênior e Ensaios (Cluster 1)", "text": "O Cluster 1 (23.9%) revela um público exigente e focado em densidade. Eles preferem biografias, história, ensaios e clássicos literários. São leitores que valorizam a profundidade intelectual e não se intimidam com calhamaços complexos."},
            {"label": "Não-Ficção de Nicho e Lazer (Cluster 2)", "text": "A maior tribo da plataforma (35.6%) é o Cluster 2. Buscam livros práticos sobre carreiras, estilo de vida e autodesenvolvimento. Um dado curioso: eles dão notas muito altas, mas são uma comunidade silenciosa, com um perfil de exposição muito menor nas resenhas escritas."},
            {"label": "Romances Mainstream e Dramas (Cluster 3)", "text": "O Cluster 3 (22.0%) é a casa dos devoradores de sucessos comerciais. Preferem romances e dramas com narrativas fluidas e de leitura rápida. Possuem uma altíssima identificação comunitária, consumindo os títulos que estão em alta nas discussões."},
            {"label": "O Que Isso Significa na Prática", "text": "O modelo provou que recomendar livros apenas por gênero é ineficiente. Leitores de fantasia (vocalizados) engajam de forma totalmente diferente dos leitores de guias práticos (silenciosos). Entender essas personalidades permite criar recomendações hiper-direcionadas."}
        ]
    },
    "classificacao": {
        "title": "O DNA do Sucesso Literário",
        "subtitle": "Booklog · Classificação",
        "badge": "Machine Learning · Random Forest",
        "badge_bg": "#F3E5F5", "badge_color": "#6A1B9A",
        "sections": [
            {"label": "O Propósito do Modelo", "text": "O objetivo da classificação supervisionada foi provar que é possível antecipar o potencial de popularidade de uma obra (Bestseller, Média Popularidade ou Nicho) antes mesmo de o livro interagir com o público. O pipeline testou algoritmos para comprovar que metadados estruturais de pré-lançamento (páginas, gênero e autor) possuem sinal estatístico autossuficiente para prever o engajamento futuro."},
            {"label": "Insight 1: O Efeito Divisor da Ficção (Filtro Brutal)", "text": "Mapeado pela análise SHAP, o gênero de Ficção atua como o maior redutor de entropia do catálogo. O algoritmo identificou que a natureza ficcional funciona como um divisor de águas: ela direciona a obra para um ecossistema de consumo totalmente diferente da não-ficção, sendo a principal locomotiva de hype e formação de comunidades ativas dentro do aplicativo."},
            {"label": "Insight 2: A Grife do Autor como Multiplicador", "text": "Ao abrir a 'caixa-preta' do modelo via valores de Shapley, descobriu-se que a frequência histórica com que um autor publica títulos é a variável individual que mais empurra a previsão em direção à classe Bestseller. Os dados provam que o comportamento de arrasto na plataforma é ditado pela assinatura e consistência do escritor, atuando como um forte preditor de retenção."},
            {"label": "Insight 3: O Paradoxo do Erro Comercial (RF vs XGBoost)", "text": "Embora o XGBoost tenha vencido na eficiência matemática global, a avaliação cega revelou um paradoxo de negócio: a Random Forest foi superior na tarefa mais crítica do produto, alcançando o maior índice de Sensibilidade (Recall de 0.54 na classe Bestseller). Para o Booklog, o custo de ignorar um fenômeno editorial (falso negativo) é muito maior do que inflar uma obra média, justificando a RF."},
            {"label": "Conclusão para o Sistema Booklog", "text": "Os dados comprovam que o sucesso comercial pode ser rastreado na origem estrutural do livro. O motor preditivo baseado em Random Forest deve ser integrado nativamente ao backend para rotular automaticamente novos títulos cadastrados. Isso permitirá que o sistema molde o feed do usuário de forma proativa."}
        ]
    }
}

# estilos de cada item que compoem a seção do datastorytelling
STYLE_OVERLAY = {"position": "fixed", "top": 0, "left": 0, "width": "100vw", "height": "100vh", "background": "rgba(0,0,0,0.35)", "zIndex": 998, "cursor": "pointer"}
STYLE_SIDEBAR = {"position": "fixed", "top": 0, "right": 0, "width": "360px", "height": "100vh", "background": "#FAFAF8", "borderLeft": "1px solid #E5E3DC", "zIndex": 999, "overflowY": "auto", "padding": "2rem 1.75rem 3rem", "fontFamily": "'Poppins', 'Times New Roman', serif", "boxShadow": "-8px 0 32px rgba(0,0,0,0.12)", "transition": "transform 0.35s cubic-bezier(.4,0,.2,1)"}
STYLE_BTN = {"position": "fixed", "top": "1.25rem", "right": "1.25rem", "zIndex": 1000, "background": "#1A3550", "color": "#fff", "border": "none", "borderRadius": "8px", "padding": "0.55rem 1.1rem", "fontSize": "13px", "fontFamily": "'Georgia', serif", "letterSpacing": "0.03em", "cursor": "pointer", "display": "flex", "alignItems": "center", "gap": "6px", "boxShadow": "0 2px 8px rgba(0,0,0,0.18)"}
STYLE_CLOSE = {"background": "none", "border": "none", "cursor": "pointer", "fontSize": "20px", "color": "#888", "float": "right", "marginTop": "-4px", "lineHeight": 1}
STYLE_TITLE = {"fontSize": "17px", "fontWeight": "bold", "color": "#1a1a1a", "marginBottom": "0.25rem", "marginTop": "0.5rem", "lineHeight": 1.3, "fontFamily": "'Poppins', sans-serif", "fontSize": "17px", "fontWeight": "bold", "color": "#1a1a1a"}
STYLE_SUBTITLE = {"fontSize": "12px", "color": "#2C3E50", "letterSpacing": "0.06em", "textTransform": "uppercase", "marginBottom": "2rem", "borderBottom": "1px solid #E5E3DC", "paddingBottom": "1rem"}
STYLE_SECTION_LABEL = {"fontSize": "16px", "fontWeight": "bold", "color": "#15202B", "letterSpacing": "0.07em", "marginBottom": "0.35rem", "display": "flex", "alignItems": "center", "gap": "6px"}
STYLE_SECTION_TEXT = {"fontSize": "14px", "color": "#3a3a3a", "lineHeight": 1.75, "marginBottom": "1.5rem", "paddingBottom": "1.5rem", "borderBottom": "1px solid #EDEBE4"}

# construtor do Layout
def create_layout(page_id: str):
    data = STORY_DATA[page_id]
    
    sections_html = []
    for i, s in enumerate(data["sections"]):
        is_last = i == len(data["sections"]) - 1
        sections_html.append(html.Div([
            html.Div([s["label"]], style=STYLE_SECTION_LABEL),
            html.P(s["text"], style={**STYLE_SECTION_TEXT, **({"borderBottom": "none", "marginBottom": 0} if is_last else {})}),
        ]))

    return html.Div([
        # O ID recebe a tag da página para ser único (ex: btn-open-hipoteses)
        html.Button("Data Storytelling", id=f"btn-open-{page_id}", style=STYLE_BTN, n_clicks=0),
        html.Div(id=f"overlay-{page_id}", style={**STYLE_OVERLAY, "display": "none"}, n_clicks=0),
        
        html.Div(id=f"sidebar-{page_id}", style={**STYLE_SIDEBAR, "transform": "translateX(100%)"}, children=[
            html.Button("✕", id=f"btn-close-{page_id}", style=STYLE_CLOSE, n_clicks=0),
            html.Div("Datastorytelling", style=STYLE_SUBTITLE),
            html.Div(data["title"], style=STYLE_TITLE),
            html.Div(data["subtitle"], style={**STYLE_SUBTITLE, "marginTop": "0.5rem"}),
            *sections_html,
            html.Div(data["badge"], style={"display": "inline-block", "background": data["badge_bg"], "color": data["badge_color"], "fontSize": "11px", "padding": "2px 10px", "borderRadius": "20px", "marginTop": "1.25rem", "fontFamily": "monospace"}),
        ]),
    ])

# registrador de callbacks
def register_callbacks(app, page_id: str):
    @app.callback(
        Output(f"sidebar-{page_id}", "style"),
        Output(f"overlay-{page_id}", "style"),
        Input(f"btn-open-{page_id}", "n_clicks"),
        Input(f"btn-close-{page_id}", "n_clicks"),
        Input(f"overlay-{page_id}", "n_clicks"),
        prevent_initial_call=True,
    )
    def toggle_sidebar(open_clicks, close_clicks, overlay_clicks):
        from dash import ctx
        if ctx.triggered_id == f"btn-open-{page_id}":
            return {**STYLE_SIDEBAR, "transform": "translateX(0)"}, {**STYLE_OVERLAY, "display": "block"}
        return {**STYLE_SIDEBAR, "transform": "translateX(100%)"}, {**STYLE_OVERLAY, "display": "none"}
