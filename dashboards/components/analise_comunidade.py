import pandas as pd
import plotly.express as px
import itertools
from collections import Counter
from dash import dcc, html, Input, Output
from components import storytelling_comunidade

# --- ESTILOS GLOBAIS ---
BG_CARD  = '#FFFFFF'
ACCENT   = '#252525'
TEXT     = '#252525'
MUTED    = '#64748b'
TEMPLATE = 'plotly_white'

CARD_STYLE = {
    'backgroundColor': BG_CARD,
    'padding': '24px',
    'borderRadius': '12px',
    'border': '1px solid #E2E8F0',
    'boxShadow': '0px 4px 8px rgba(0, 0, 0, 0.05)',
    'marginBottom': '24px'
}

def render(app, df: pd.DataFrame):
    # Registrar o painel lateral da comunidade
    storytelling_comunidade.register_callbacks(app)
    
    df_valido = df[(df['totalratings'] > 0)].copy()
    
    # Preparar gêneros para os filtros
    todos_generos = list(itertools.chain.from_iterable(df_valido['generos_lista']))
    top_generos = [g for g, _ in Counter(todos_generos).most_common(50)]
    
    # callback de atualizacao dos graficos
    @app.callback(
        Output('com-rev-ava', 'figure'),
        Output('com-autores', 'figure'),
        Output('com-top-livros', 'figure'),
        Input('com-genre-filter', 'value'),
        Input('com-min-ratings', 'value'),
        Input('com-min-rating', 'value'),
        Input('com-max-rating', 'value')
    )
    def atualizar_graficos(genre, min_ratings, min_rating, max_rating):
        # Tratamento de Nones (caso o usuário apague o campo)
        if min_ratings is None: min_ratings = 0
        if min_rating is None: min_rating = 0.0
        if max_rating is None: max_rating = 5.0

        fdf = df_valido[
            (df_valido['totalratings'] >= min_ratings) &
            (df_valido['rating'] >= min_rating) &
            (df_valido['rating'] <= max_rating)].copy()
        
        if genre: 
            fdf = fdf[fdf['generos_lista'].apply(lambda x: genre in x)]

        if fdf.empty:
            vazio = px.scatter(title="Nenhum dado encontrado para estes filtros", template=TEMPLATE)
            vazio.update_layout(paper_bgcolor='#ffffff', plot_bgcolor='#ffffff', font=dict(color=TEXT))
            return vazio, vazio, vazio

        # Debate da Comunidade
        rev_x_ava_stats = px.scatter(
            fdf.nlargest(500, 'totalratings'),
            x='totalratings', y='reviews',
            color='rating', color_continuous_scale='Turbo_r', range_color=[0, 5],
            hover_name='title', size='rating', size_max=20,
            title='Debate da Comunidade: Avaliações × Reviews', template=TEMPLATE,
            labels={'totalratings': 'Total de avaliações', 'reviews': 'Reviews escritas', 'rating': 'Nota'}
        )       
        rev_x_ava_stats.update_layout(
            title_font=dict(weight=600), paper_bgcolor='#ffffff', plot_bgcolor='#ffffff',
            font=dict(color=TEXT), xaxis=dict(gridcolor='#e0e0e0'), yaxis=dict(gridcolor='#e0e0e0'), height=450
        )

        # Top Autores
        autor_stats = (fdf.groupby('author')
            .agg(qtd_livros=('title','count'), media_nota=('rating','mean'), total_ratings=('totalratings','sum'))
            .reset_index())
        top_autores = autor_stats[autor_stats['qtd_livros'] >= 2].nlargest(15, 'total_ratings')
        
        fig_autores = px.scatter(top_autores, x='qtd_livros', y='media_nota',
            size='total_ratings', color='media_nota', hover_name='author',
            title='Top Autores: Produtividade × Nota', template=TEMPLATE,
            color_continuous_scale='Turbo_r', size_max=60, range_color=[0, 5],
            labels={'qtd_livros': 'Livros', 'media_nota': 'Nota média'})
        fig_autores.update_layout(
            title_font=dict(weight=600), paper_bgcolor='#ffffff', plot_bgcolor='#ffffff',
            font=dict(color=TEXT), xaxis=dict(gridcolor='#e0e0e0'), yaxis=dict(gridcolor='#e0e0e0')
        )

        # Top 10 Livros
        top = fdf.nlargest(10, 'totalratings').copy()
        top['titulo_curto'] = top['title'].str[:45] + top['title'].apply(lambda x: '…' if len(str(x)) > 45 else '')
        fig_top = px.bar(top, x='totalratings', y='titulo_curto', orientation='h',
            color='rating', color_continuous_scale='Turbo_r', range_color=[0, 5],
            hover_name='title', title='Top 10 Livros Mais Avaliados', template=TEMPLATE,
            labels={'totalratings': 'Total avaliações', 'titulo_curto': '', 'rating': 'Nota'})
        fig_top.update_layout(
            title_font=dict(weight=600), paper_bgcolor='#ffffff', plot_bgcolor='#ffffff',
            yaxis={'categoryorder': 'array', 'categoryarray': top.sort_values('rating', ascending=True)['titulo_curto'].tolist()},
            font=dict(color=TEXT), xaxis=dict(gridcolor='#e0e0e0')
        )

        return rev_x_ava_stats, fig_autores, fig_top

    # --- LAYOUT DA PÁGINA ---
    layout = html.Div(style={'color': TEXT}, children=[
        storytelling_comunidade.storytelling_layout(),
        
        html.H1("Comunidade e Engajamento", style={'textAlign': 'center', 'marginBottom': '8px', 'color': ACCENT, 'fontWeight': 'bold'}),
        html.P("Descubra o que os leitores realmente debatem, quem são os autores de maior impacto e os títulos favoritos.",
               style={'textAlign': 'center', 'color': MUTED, 'marginBottom': '28px', 'fontSize': '15px'}),
        

        # Filtros Técnicos
        html.Div(style=CARD_STYLE, children=[
            html.H3("Parâmetros de Análise", style={'color': ACCENT, 'marginBottom': '16px', 'fontSize': '16px', 'fontWeight': 'bold'}),
            html.Div(style={'display': 'flex', 'gap': '32px', 'flexWrap': 'wrap', 'alignItems': 'flex-end'}, children=[
                
                # Filtro de Gênero
                html.Div([
                    html.Label("Gênero Literário:", style={'display': 'block', 'marginBottom': '6px', 'fontSize': '13px', 'fontWeight': '500', 'color': MUTED}),
                    dcc.Dropdown(
                        id='com-genre-filter', options=[{'label': g, 'value': g} for g in top_generos],
                        placeholder="Todos os gêneros...", clearable=True,
                        style={'width': '260px', 'color': '#000'}
                    )
                ]),
                
                # Filtro de Significância
                html.Div([
                    html.Label("Corte de Significância (Mín. Avaliações):", style={'display': 'block', 'marginBottom': '6px', 'fontSize': '13px', 'fontWeight': '500', 'color': MUTED}),
                    dcc.Input(
                        id='com-min-ratings', type='number', placeholder='Ex: 1000',
                        value=0, min=0, step=500,
                        style={'width': '260px', 'padding': '8px 12px', 'borderRadius': '4px', 'border': '1px solid #cccccc', 'color': '#000', 'fontSize': '14px'}
                    )
                ]),

                # Filtro de Faixa de Nota
                html.Div([
                    html.Label("Faixa de Nota (Isolar perfis):", style={'display': 'block', 'marginBottom': '6px', 'fontSize': '13px', 'fontWeight': '500', 'color': MUTED}),
                    html.Div(style={'display': 'flex', 'gap': '8px'}, children=[
                        dcc.Input(id='com-min-rating', type='number', placeholder='Mín', value=0.0, min=0.0, max=5.0, step=0.1,
                                  style={'width': '100px', 'padding': '8px 12px', 'borderRadius': '4px', 'border': '1px solid #cccccc', 'color': '#000'}),
                        dcc.Input(id='com-max-rating', type='number', placeholder='Máx', value=5.0, min=0.0, max=5.0, step=0.1,
                                  style={'width': '100px', 'padding': '8px 12px', 'borderRadius': '4px', 'border': '1px solid #cccccc', 'color': '#000'})
                    ])
                ])
                
            ])
        ]),

        # Gráficos
        html.Div(style=CARD_STYLE, children=[
            dcc.Graph(id='com-rev-ava')
        ]),
        
        html.Div(style={'display': 'flex', 'gap': '24px', 'flexWrap': 'wrap'}, children=[
            html.Div(style={**CARD_STYLE, 'flex': '1 1 600px', 'minWidth': '400px'}, children=[
                dcc.Graph(id='com-autores')
            ]),
            html.Div(style={**CARD_STYLE, 'flex': '1 1 600px', 'minWidth': '400px'}, children=[
                dcc.Graph(id='com-top-livros')
            ])
        ])
    ])
    
    return layout