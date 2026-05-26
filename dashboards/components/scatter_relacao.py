import plotly.express as px
from dash import dcc, html, Input, Output
import itertools
from collections import Counter

def render(app, df):
    coluna_autor = 'author'
    lista_autores = sorted(df[coluna_autor].dropna().unique())
    metrics = ['pages', 'totalratings', 'rating']

    todos_generos = list(itertools.chain.from_iterable(df['generos_lista']))
    top_generos = [g for g, c in Counter(todos_generos).most_common(100)]

    layout = html.Div([
        # linha 1 dropdowns
        html.Div(
            style={'display': 'flex', 'gap': '20px', 'justifyContent': 'center', 'alignItems': 'flex-end', 'marginBottom': '40px', 'flexWrap': 'wrap'},
            children=[
                html.Div([
                    html.Label("Métrica Eixo X:", style={'display': 'block', 'marginBottom': '5px'}),
                    dcc.Dropdown(id='x-axis-select', options=[{'label': m.replace('_', ' ').title(), 'value': m} for m in metrics], value='pages', clearable=False, style={'width': '160px', 'color': '#000'})
                ]),
                html.Div([
                    html.Label("Métrica Eixo Y:", style={'display': 'block', 'marginBottom': '5px'}),
                    dcc.Dropdown(id='y-axis-select', options=[{'label': m.replace('_', ' ').title(), 'value': m} for m in metrics], value='totalratings', clearable=False, style={'width': '160px', 'color': '#000'})
                ]),
                html.Div([
                    html.Label("Buscar Autor:", style={'display': 'block', 'marginBottom': '5px'}),
                    dcc.Dropdown(id='author-select', placeholder="Selecione um autor...", searchable=True, clearable=True, style={'width': '220px', 'color': '#000'})
                ]),
                html.Div([
                    html.Label("Foco por Gênero:", style={'display': 'block', 'marginBottom': '5px', 'color': '#a3e635', 'fontWeight': 'bold'}),
                    dcc.Dropdown(id='genre-select', options=[{'label': g, 'value': g} for g in top_generos], placeholder="Ex: Fantasy", searchable=True, clearable=True, style={'width': '220px', 'color': '#000'})
                ])
            ]
        ),

        # linha 2 inputs min e max
        html.Div(
            style={'display': 'flex', 'gap': '20px', 'justifyContent': 'center', 'flexWrap': 'wrap', 'marginBottom': '40px'},
            children=[
                html.Div([html.Label("Mín. Avaliações:", style={'display': 'block', 'marginBottom': '5px'}), dcc.Input(id='min-ratings-input', type='number', value=100, min=0, style={'width': '160px', 'padding': '8px', 'borderRadius': '4px', 'color': '#000000'})]),
                html.Div([html.Label("Máx. Avaliações:", style={'display': 'block', 'marginBottom': '5px'}), dcc.Input(id='max-ratings-input', type='number', value=500000, min=0, style={'width': '160px', 'padding': '8px', 'borderRadius': '4px', 'color': '#000000'})]),
                html.Div([html.Label("Mín. Páginas:", style={'display': 'block', 'marginBottom': '5px'}), dcc.Input(id='min-pages-input', type='number', value=0, min=0, style={'width': '160px', 'padding': '8px', 'borderRadius': '4px', 'color': '#000000', 'marginLeft': '20px'})]),
                html.Div([html.Label("Máx. Páginas:", style={'display': 'block', 'marginBottom': '5px'}), dcc.Input(id='max-pages-input', type='number', value=2000, min=0, style={'width': '160px', 'padding': '8px', 'borderRadius': '4px', 'color': '#000000'})])
            ]
        ),

        # linha 3 grafico + card
        html.Div(
            style={'display': 'flex', 'gap': '20px', 'width': '100%', 'marginBottom': '20px'},
            children=[
                html.Div(
                    style={'backgroundColor': '#1e293b', 'padding': '20px', 'borderRadius': '12px', 'width': '80%'},
                    children=[dcc.Graph(id='main-interactive-graph')]
                ),
                
                html.Div(
                    id='book-details-card',
                    style={
                        'backgroundColor': '#1e293b', 'padding': '25px', 'borderRadius': '12px', 
                        'width': '20%', 'color': '#f8fafc', 'display': 'block',
                        'overflowY': 'auto', 'maxHeight': '650px'
                    },
                    children=[
                        # mensagem padrão inicial antes do usuário clicar em algo
                        html.P("Clique em uma bolinha no gráfico para ver os detalhes do livro.", 
                               style={'textAlign': 'center', 'color': '#64748b', 'marginTop': '60px', 'fontSize': '14px'})
                    ]
                )
            ]
        )
    ])


    # callback de opçoes do autor
    @app.callback(
        Output('author-select', 'options'),
        [Input('author-select', 'search_value'), Input('author-select', 'value')]
    )
    def update_author_options(search_value, current_value):
        if not search_value:
            opcoes = lista_autores[:50]
            if current_value and current_value not in opcoes: opcoes.insert(0, current_value)
            return [{'label': autor, 'value': autor} for autor in opcoes]
        matches = [autor for autor in lista_autores if search_value.lower() in str(autor).lower()]
        opcoes_filtradas = matches[:50]
        if current_value and current_value not in opcoes_filtradas: opcoes_filtradas.insert(0, current_value)
        return [{'label': autor, 'value': autor} for autor in opcoes_filtradas]



    # Callback do grafico de dispersão
    @app.callback(
        Output('main-interactive-graph', 'figure'),
        [Input('x-axis-select', 'value'), Input('y-axis-select', 'value'),
         Input('author-select', 'value'), Input('genre-select', 'value'),
         Input('min-ratings-input', 'value'), Input('max-ratings-input', 'value'),
         Input('min-pages-input', 'value'), Input('max-pages-input', 'value')]
    )


    def update_graph(x_col, y_col, selected_author, focus_genre, min_ratings, max_ratings, min_p, max_p):
        if min_ratings is None: min_ratings = 0
        if max_ratings is None: max_ratings = float('inf')
        if min_p is None: min_p = 0
        if max_p is None: max_p = float('inf')

        filtered_df = df[
            (df['totalratings'] >= min_ratings) & (df['totalratings'] <= max_ratings) &
            (df['pages'] >= min_p) & (df['pages'] <= max_p)
        ]

        titulo_grafico = f"Relação Dinâmica: {x_col.title()} vs {y_col.title()}"
        if selected_author:
            filtered_df = filtered_df[filtered_df[coluna_autor] == selected_author]
            titulo_grafico += f" | Autor: {selected_author}"
            
        if focus_genre:
            mask = filtered_df['generos_lista'].apply(lambda x: focus_genre in x)
            filtered_df = filtered_df[mask]
            titulo_grafico += f" | Gênero: {focus_genre}"

        fig = px.scatter(
            filtered_df, x=x_col, y=y_col, color='rating',
            size='totalratings' if y_col != 'totalratings' else None, hover_name='title',
            log_y=True if y_col == 'totalratings' else False, template='plotly_dark',
            color_continuous_scale='Viridis', range_color=[0, 5], title=titulo_grafico
        )
        fig.update_layout(transition_duration=300, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        return fig


    # captura o clique no grafico e renderiza o card
    @app.callback(
        Output('book-details-card', 'children'),
        [Input('main-interactive-graph', 'clickData')]
    )

    def update_details_card(clickData):
        if clickData is None:
            return [html.P("Clique em uma bola no gráfico para ver os detalhes do livro.", 
                           style={'textAlign': 'center', 'color': '#64748b', 'marginTop': '60px', 'fontSize': '14px'})]
        
        try:
            # nome do livro clicado vem na propriedade 'hovertext'
            titulo_clicado = clickData['points'][0]['hovertext']
            
            # localizar a linha correspondente ao livro no DataFrame
            livro_info = df[df['title'] == titulo_clicado].iloc[0]
            
            # busca das colunas solicitadas
            img_url = livro_info.get('img', livro_info.get('image_url', ''))
            titulo = livro_info.get('title', 'Título Indisponível')
            descricao = livro_info.get('desc', livro_info.get('description', 'Nenhuma descrição detalhada disponível.'))
            
            # exibicao dos generos
            generos = livro_info.get('genres', livro_info.get('genre', ''))
            if isinstance(generos, list):
                generos_texto = ", ".join(generos)
            else:
                generos_texto = str(generos).replace('[', '').replace(']', '').replace("'", "")

            # estrutura html do card
            card_html = [
                # titulo
                html.H3(titulo, style={'color': '#a3e635', 'fontSize': '16px', 'fontWeight': 'bold', 'textAlign': 'center', 'marginBottom': '20px'}),
                
                # imagem
                html.Div(
                    style={'textAlign': 'center', 'marginBottom': '20px'},
                    children=[
                        html.Img(src=img_url, style={'maxWidth': '100%', 'maxHeight': '180px', 'borderRadius': '8px', 'boxShadow': '0 4px 10px rgba(0,0,0,0.5)'})
                    ] if img_url else [html.P("📷 Sem Imagem", style={'fontStyle': 'italic', 'color': '#475569'})]
                ),
                
                # generos
                html.Div(style={'marginBottom': '15px'}, children=[
                    html.Span("Gêneros: ", style={'color': '#a3e635', 'fontWeight': 'bold', 'fontSize': '13px'}),
                    html.Span(generos_texto, style={'color': '#cbd5e1', 'fontSize': '13px'})
                ]),
                
                html.Hr(style={'borderColor': '#334155', 'margin': '15px 0'}),
                
                # descriçao
                html.Div(children=[
                    html.P("Sinopse:", style={'color': '#a3e635', 'fontWeight': 'bold', 'fontSize': '13px', 'marginBottom': '5px'}),
                    html.P(descricao, style={'color': '#94a3b8', 'fontSize': '12px', 'textAlign': 'justify', 'lineHeight': '1.5'})
                ])
            ]
            return card_html
            
        except Exception as e:
            # caso ocorra algum erro de mapeamento, mostra o erro no card sem quebrar o app
            return [html.P(f"Erro ao carregar metadados: {str(e)}", style={'color': '#ef4444', 'fontSize': '12px'})]

    return layout