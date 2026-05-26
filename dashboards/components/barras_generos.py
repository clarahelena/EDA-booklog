import plotly.express as px
import pandas as pd
from dash import dcc, html, Input, Output
import itertools
from collections import Counter

def render(app, df):
    # lauyout exclusivo desse componente
    layout = html.Div([
        dcc.Graph(id='genre-bar-chart')
    ], style={'backgroundColor': '#1e293b', 'padding': '20px', 'borderRadius': '12px'})

    @app.callback(
        Output('genre-bar-chart', 'figure'),
        [Input('author-select', 'value'),
         Input('genre-select', 'value'),
         Input('min-ratings-input', 'value'),
         Input('max-ratings-input', 'value'),
         Input('min-pages-input', 'value'),
         Input('max-pages-input', 'value')]
    )

    
    def update_bar(selected_author, focus_genre, min_ratings, max_ratings, min_p, max_p):
        if min_ratings is None: min_ratings = 0
        if max_ratings is None: max_ratings = float('inf')
        if min_p is None: min_p = 0
        if max_p is None: max_p = float('inf')

        # aplica as mesmas regras de limite numérico
        filtered_df = df[
            (df['totalratings'] >= min_ratings) & (df['totalratings'] <= max_ratings) &
            (df['pages'] >= min_p) & (df['pages'] <= max_p)
        ]

        if selected_author:
            filtered_df = filtered_df[filtered_df['author'] == selected_author]
        
        # se os filtros zerar os livros
        if filtered_df.empty:
            vazio = px.bar(title="Nenhum livro atende a esses filtros", template='plotly_dark')
            vazio.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            return vazio

        # aplica a regra do Gênero
        if focus_genre:
            mask = filtered_df['generos_lista'].apply(lambda x: focus_genre in x)
            filtered_df = filtered_df[mask]
            titulo_barras = f"Gêneros que mais acompanham '{focus_genre}'"
        else:
            titulo_barras = "Top 10 Gêneros Mais Frequentes (Filtro Atual)"

        # contar os gêneros
        todos_generos_filtrados = list(itertools.chain.from_iterable(filtered_df['generos_lista']))
        
        if focus_genre:
            todos_generos_filtrados = [g for g in todos_generos_filtrados if g != focus_genre]

        contagem = Counter(todos_generos_filtrados).most_common(10)
        df_barras = pd.DataFrame(contagem, columns=['Gênero', 'Frequência'])

        if df_barras.empty:
            vazio = px.bar(title="Sem dados suficientes", template='plotly_dark')
            vazio.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            return vazio


        max_freq = df_barras['Frequência'].max()
        # grafico de barras dos generos
        fig_bar = px.bar(
            df_barras, x='Frequência', y='Gênero', orientation='h',
            title=titulo_barras, template='plotly_dark',
            color='Frequência', color_continuous_scale=["#8a094a", "#ba0c63", "#c9442b", "#338a57", "#4ca6a6"],
            range_color=[0, max_freq]
        )
        
        fig_bar.update_layout(
            yaxis={'categoryorder':'total ascending'},
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            font_family="Poppins"
        )
        
        return fig_bar

    return layout