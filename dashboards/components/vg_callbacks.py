import plotly.express as px
from dash import Input, Output, html

BG_CARD  = '#1e293b'
ACCENT   = '#a3e635'
TEXT     = '#f8fafc'
MUTED    = '#94a3b8'
TEMPLATE = 'plotly_dark'
TRANSP   = 'rgba(0,0,0,0)'

CARD_STYLE = {
    'backgroundColor': BG_CARD,
    'padding': '24px',
    'borderRadius': '12px',
    'border': '1px solid #334155',
}


def _fmt_num(n):
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000:     return f"{n/1_000:.1f}K"
    return str(int(n))


def _kpi_card(titulo, valor, icone, cor=ACCENT):
    from dash import html
    return html.Div(
        style={**CARD_STYLE, 'textAlign': 'center', 'flex': '1', 'minWidth': '160px'},
        children=[
            html.Div(icone, style={'fontSize': '32px', 'marginBottom': '8px'}),
            html.Div(valor, style={'fontSize': '28px', 'fontWeight': 'bold', 'color': cor}),
            html.Div(titulo, style={'fontSize': '13px', 'color': MUTED, 'marginTop': '4px'}),
        ]
    )


def registrar(app, df, df_valido, top_generos, lista_autores,
              min_paginas, max_paginas, min_nota):

    # opções de autor via busca
    @app.callback(Output('vg-author', 'options'), Input('vg-author', 'search_value'))
    def update_author_opts(search):
        if not search:
            return [{'label': a, 'value': a} for a in lista_autores[:50]]
        matches = [a for a in lista_autores if search.lower() in a.lower()]
        return [{'label': a, 'value': a} for a in matches[:50]]

    # opções de livro via busca
    @app.callback(
        Output('vg-author', 'value'), 
        Input('vg-autores', 'clickData'), 
        prevent_initial_call=True
    )
    def autor_click_para_filtro(clickData):
        if clickData is None:
            return None
        return clickData['points'][0]['hovertext']

    # limpar filtros
    @app.callback(
        Output('vg-genre', 'value'),   
        Output('vg-author', 'value', allow_duplicate=True),
        Output('vg-min-pages', 'value'), Output('vg-max-pages', 'value'),
        Output('vg-min-rating', 'value'), Output('vg-max-rating', 'value'),
        Input('vg-clear', 'n_clicks'), 
        prevent_initial_call=True
    )
    def clear_filters(_):
        return None,  None, min_paginas, max_paginas, min_nota, 5.0

    # atualiza KPIs e gráficos
    @app.callback(
        Output('vg-kpi-row',    'children'),
        Output('vg-hist',       'figure'),
        Output('vg-rosca',      'figure'),
        Output('vg-autores',    'figure'),
        Output('vg-top-livros', 'figure'),
        Input('vg-genre',      'value'),
        Input('vg-author',     'value'),
        Input('vg-min-pages',  'value'),
        Input('vg-max-pages',  'value'),
        Input('vg-min-rating', 'value'),
        Input('vg-max-rating', 'value'),
    )
    def update_all(genre, author, min_p, max_p, min_r, max_r):
        if min_p is None: min_p = min_paginas
        if max_p is None: max_p = max_paginas
        if min_r is None: min_r = min_nota
        if max_r is None: max_r = 5.0

        fdf = df_valido[
            (df_valido['pages']  >= min_p) & (df_valido['pages']  <= max_p) &
            (df_valido['rating'] >= min_r) & (df_valido['rating'] <= max_r)
        ].copy()

        if genre:  fdf = fdf[fdf['generos_lista'].apply(lambda x: genre in x)]
        if author: fdf = fdf[fdf['author'] == author]

        # KPIs
        kpis = html.Div(
            style={'display': 'flex', 'gap': '16px', 'flexWrap': 'wrap', 'width': '100%'},
            children=[
                _kpi_card("Livros",         _fmt_num(len(fdf)),                        "📚"),
                _kpi_card("Autores",         _fmt_num(fdf['author'].nunique()),         "✍️"),
                _kpi_card("Nota média",      f"{fdf['rating'].mean():.2f} ★" if len(fdf) else "—", "⭐", '#facc15'),
                _kpi_card("Avaliações",      _fmt_num(fdf['totalratings'].sum()),       "💬", '#38bdf8'),
                _kpi_card("Média páginas",   f"{int(fdf['pages'].mean())} pgs" if len(fdf) else "—", "📄", '#f472b6'),
            ]
        )

        if fdf.empty:
            vazio = px.bar(title="Nenhum resultado para os filtros selecionados", template=TEMPLATE)
            vazio.update_layout(paper_bgcolor=TRANSP, plot_bgcolor=TRANSP)
            return kpis, vazio, vazio, vazio, vazio

        # histograma de notas
        media = fdf['rating'].mean()
        fig_hist = px.histogram(fdf, x='rating', nbins=40,
            title='Distribuição das Notas', template=TEMPLATE,
            color_discrete_sequence=[ACCENT])
        fig_hist.update_layout(paper_bgcolor=TRANSP, plot_bgcolor=TRANSP,
            xaxis_title='Nota', yaxis_title='Qtd', bargap=0.05)
        fig_hist.add_vline(x=media, line_dash='dash', line_color='#facc15',
            annotation_text=f' Média: {media:.2f}', annotation_font_color='#facc15')

        # rosca formatos
        fmt = fdf['bookformat'].value_counts().reset_index()
        fmt.columns = ['Formato', 'Qtd']
        fmt.loc[fmt['Qtd'] < fmt['Qtd'].sum() * 0.02, 'Formato'] = 'Outros'
        fmt = fmt.groupby('Formato', as_index=False)['Qtd'].sum()
        fig_rosca = px.pie(fmt, names='Formato', values='Qtd',
            title='Formatos de Leitura', template=TEMPLATE,
            color_discrete_sequence=px.colors.sequential.Viridis, hole=0.4)
        fig_rosca.update_traces(textposition='inside', textinfo='percent+label')
        fig_rosca.update_layout(paper_bgcolor=TRANSP, showlegend=True, height=450)

        # scatter autores
        autor_stats = (fdf.groupby('author')
            .agg(qtd_livros=('title','count'), media_nota=('rating','mean'),
                 total_ratings=('totalratings','sum'))
            .reset_index())
        top_autores = autor_stats[autor_stats['qtd_livros'] >= 2].nlargest(15, 'total_ratings')
        fig_autores = px.scatter(top_autores, x='qtd_livros', y='media_nota',
            size='total_ratings', color='media_nota', hover_name='author',
            title='Top Autores: Produtividade × Nota', template=TEMPLATE,
            color_continuous_scale='Turbo', size_max=60, range_color=[0, 5],
            labels={'qtd_livros': 'Livros', 'media_nota': 'Nota média'})
        fig_autores.update_layout(paper_bgcolor=TRANSP, plot_bgcolor=TRANSP)

        # top 10 livros
        top = fdf[fdf['totalratings'] > 0].nlargest(10, 'totalratings').copy()
        top['titulo_curto'] = top['title'].str[:45] + top['title'].apply(lambda x: '…' if len(x) > 45 else '')
        fig_top = px.bar(top, x='totalratings', y='titulo_curto', orientation='h',
            color='rating', color_continuous_scale='Turbo', range_color=[0, 5],
            hover_name='title', title='Top 10 Livros Mais Avaliados', template=TEMPLATE,
            labels={'totalratings': 'Total avaliações', 'titulo_curto': '', 'rating': 'Nota'})
        fig_top.update_layout(yaxis={'categoryorder': 'array', 
            'categoryarray': top.sort_values('rating', ascending=True)['titulo_curto'].tolist()
            }, 
            paper_bgcolor=TRANSP, 
            plot_bgcolor=TRANSP
        )

        return kpis, fig_hist, fig_rosca, fig_autores, fig_top
    # card de detalhes ao clicar no top livros
    @app.callback(
        Output('vg-book-card', 'children'),
        Input('vg-top-livros', 'clickData'),
        prevent_initial_call=True
    )
    def book_card(clickData):
        if clickData is None:
            return [html.P("Clique em um livro no gráfico para ver os detalhes.",
                           style={'textAlign': 'center', 'color': '#64748b',
                                  'marginTop': '60px', 'fontSize': '14px'})]
        try:
            titulo_clicado = clickData['points'][0]['hovertext']
            livro = df[df['title'] == titulo_clicado].iloc[0]
 
            img_url  = livro.get('img', livro.get('image_url', ''))
            titulo   = livro.get('title', 'Título Indisponível')
            autor    = livro.get('author', '')
            descricao = livro.get('desc', livro.get('description', 'Sem descrição disponível.'))
 
            generos = livro.get('genres', livro.get('genre', ''))
            if isinstance(generos, list):
                generos_texto = ", ".join(generos)
            else:
                generos_texto = str(generos).replace('[','').replace(']','').replace("'","")
 
            return [
                html.H3(titulo, style={'color': ACCENT, 'fontSize': '16px', 'fontWeight': 'bold',
                                       'textAlign': 'center', 'marginBottom': '8px'}),
                html.P(f"✍️ {autor}", style={'textAlign': 'center', 'color': MUTED,
                                              'fontSize': '13px', 'marginBottom': '16px'}),
                html.Div(style={'textAlign': 'center', 'marginBottom': '16px'}, children=[
                    html.Img(src=img_url, style={'maxWidth': '100%', 'maxHeight': '180px',
                                                  'borderRadius': '8px'})
                ] if img_url else [html.P("📷 Sem Imagem", style={'color': '#475569', 'fontStyle': 'italic'})]),
                html.Div(style={'marginBottom': '12px'}, children=[
                    html.Span("Gêneros: ", style={'color': ACCENT, 'fontWeight': 'bold', 'fontSize': '13px'}),
                    html.Span(generos_texto, style={'color': '#cbd5e1', 'fontSize': '13px'}),
                ]),
                html.Hr(style={'borderColor': '#334155', 'margin': '12px 0'}),
                html.P("Sinopse:", style={'color': ACCENT, 'fontWeight': 'bold', 'fontSize': '13px', 'marginBottom': '5px'}),
                html.P(descricao, style={'color': '#94a3b8', 'fontSize': '12px',
                                         'textAlign': 'justify', 'lineHeight': '1.5'}),
            ]
        except Exception as e:
            return [html.P(f"Erro: {str(e)}", style={'color': '#ef4444', 'fontSize': '12px'})]    