import pandas as pd
from dash import Input, Output, html

CARD_STYLE = {
    'backgroundColor': '#FFFFFF',
    'padding': '24px',
    'borderRadius': '12px',
    'border': '1px solid #E2E8F0',
    'boxShadow': '0px 4px 8px rgba(0, 0, 0, 0.05)'
}

def _fmt_num(n):
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000:     return f"{n/1_000:.1f}K"
    return str(int(n))

def _kpi_card(titulo, valor, cor='#252525'):
    return html.Div(
        style={**CARD_STYLE, 'textAlign': 'center', 'flex': '1', 'minWidth': '160px', 'marginBottom': '0'},
        children=[
            html.Div(valor, style={'fontSize': '28px', 'fontWeight': 'bold', 'color': cor}),
            html.Div(titulo, style={'fontSize': '13px', 'color': '#252525', 'marginTop': '4px'}),
        ]
    )

def registrar(app, df, df_valido, *args):
    @app.callback(
        Output('vg-kpi-row', 'children'),
        [
            Input('genre-select', 'value'),
            Input('author-select', 'value'),
            Input('min-pages-input', 'value'),
            Input('max-pages-input', 'value'),
            Input('min-ratings-input', 'value'),
            Input('max-ratings-input', 'value')
        ]
    )
    def update_kpis(genre, author, min_p, max_p, min_ratings, max_ratings):
        # Tratamento de campos vazios, caso o usuário apague o número
        if min_p is None: min_p = 0
        if max_p is None: max_p = float('inf')
        if min_ratings is None: min_ratings = 0
        if max_ratings is None: max_ratings = float('inf')

        # Aplica os filtros numéricos (Páginas e Avaliações)
        fdf = df_valido[
            (df_valido['pages'] >= min_p) & 
            (df_valido['pages'] <= max_p) &
            (df_valido['totalratings'] >= min_ratings) & 
            (df_valido['totalratings'] <= max_ratings)
        ].copy()

        # Aplica os filtros de texto (Gênero e Autor)
        if genre:  
            fdf = fdf[fdf['generos_lista'].apply(lambda x: genre in x)]
        if author: 
            fdf = fdf[fdf['author'] == author]

        # Gera os Cards atualizados
        kpis = html.Div(
            style={'display': 'flex', 'gap': '16px', 'flexWrap': 'wrap', 'width': '100%'},
            children=[
                _kpi_card("Livros",          _fmt_num(len(fdf))),
                _kpi_card("Autores",         _fmt_num(fdf['author'].nunique())),
                _kpi_card("Nota média",      f"{fdf['rating'].mean():.2f}" if len(fdf) else "—"),
                _kpi_card("Avaliações",      _fmt_num(fdf['totalratings'].sum())),
                _kpi_card("Média páginas",   f"{int(fdf['pages'].mean())} pgs" if len(fdf) else "—"),
            ]
        )

        return kpis