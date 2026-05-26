import plotly.graph_objects as go
import pandas as pd
from dash import dcc, html, Input, Output


COLORS_BASE  = ["#4ca6a6", "#338a57", "#c9442b", "#ba0c63", "#8a094a"]


def render(app, df):

    layout = html.Div([
        dcc.Graph(
            id='format-donut-chart',
            config={'displayModeBar': False},
            style={'height': '100%'}
        )
    ], style={
        'backgroundColor': '#1e1b2e',
        'padding': '16px',
        'borderRadius': '12px',
        'height': '100%',
        'display': 'flex',
        'flexDirection': 'column',
        'justifyContent': 'center'
    })

    @app.callback(
        Output('format-donut-chart', 'figure'),
        [Input('author-select', 'value'),
         Input('genre-select', 'value'),
         Input('min-ratings-input', 'value'),
         Input('max-ratings-input', 'value'),
         Input('min-pages-input', 'value'),
         Input('max-pages-input', 'value')]
    )
    def update_donut(selected_author, focus_genre, min_ratings, max_ratings, min_p, max_p):
        if min_ratings is None: min_ratings = 0
        if max_ratings is None: max_ratings = float('inf')
        if min_p is None: min_p = 0
        if max_p is None: max_p = float('inf')

        filtered_df = df[
            (df['totalratings'] >= min_ratings) & (df['totalratings'] <= max_ratings) &
            (df['pages'] >= min_p) & (df['pages'] <= max_p)
        ]
        if selected_author:
            filtered_df = filtered_df[filtered_df['author'] == selected_author]

        titulo = f"Formatos — {focus_genre}" if focus_genre else "Formatos de publicação"
        if focus_genre:
            mask = filtered_df['generos_lista'].apply(lambda x: focus_genre in x)
            filtered_df = filtered_df[mask]

        if filtered_df.empty or 'bookformat' not in filtered_df.columns:
            return _empty_fig("Sem dados para os filtros selecionados")

        df_fmt = filtered_df.dropna(subset=['bookformat'])
        contagem = df_fmt['bookformat'].value_counts().reset_index()
        contagem.columns = ['Formato', 'Quantidade']

        if contagem.empty:
            return _empty_fig("Sem formatos disponíveis")

        if len(contagem) > 5:
            top5 = contagem.head(5)
            outros = pd.DataFrame([{
                'Formato': 'Outros',
                'Quantidade': contagem.iloc[5:]['Quantidade'].sum()
            }])
            contagem = pd.concat([top5, outros], ignore_index=True)

        total = contagem['Quantidade'].sum()
        labels = contagem['Formato'].tolist()
        values = contagem['Quantidade'].tolist()
        n = len(labels)

        colors_base  = COLORS_BASE[:n]

        # Texto do hover personalizado
        custom_hover = [
            f"<b>{fmt}</b><br>{qty:,} livros<br>{qty/total*100:.1f}%"
            for fmt, qty in zip(labels, values)
        ]

        fig = go.Figure(go.Pie(
            labels=labels,
            values=values,
            hole=0.70,
            marker=dict(
                colors=colors_base,
                line=dict(color='#1e1b2e', width=3)
            ),
            customdata=custom_hover,
            hovertemplate="%{customdata}<extra></extra>",
            pull=[0] * n,
            textinfo='none',
            direction='clockwise',
            sort=True,
        ))

        fig.update_traces(
            hoverlabel=dict(
                bgcolor='#2d1b4e',
                bordercolor='#e879f9',
                font=dict(color='#fdf4ff', size=13)
            ),
        )

        # anotacao central da rosquinha
        fig.add_annotation(
            text=(
                f"<span style='font-size:11px;color:#c084fc'>TOTAL</span>"
                f"<span style='font-size:6px'><br><br></span>"
                f"<b style='font-size:22px;color:#fdf4ff'>{total:,}</b>"
                f"<span style='font-size:6px'><br><br></span>"
                f"<span style='font-size:11px;color:#a1a1aa'>LIVROS</span>"
            ),
            x=0.5, y=0.5,
            showarrow=False,
            align='center',
            xanchor='center',
            yanchor='middle',
        )

        fig.update_layout(
            title=dict(
                text=titulo,
                font=dict(size=20, color="#ffffff"),
                x=0.5,
                xanchor='center',
                font_family="Poppins"
            ),
            showlegend=True,
            legend=dict(
                font=dict(size=12, color="#ffffff"),
                bgcolor='rgba(0,0,0,0)',
                bordercolor='rgba(0,0,0,0)',
                orientation='v',
                x=1.02,
                y=0.5,
                yanchor='middle',
                itemsizing='constant',
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=40, b=10, l=10, r=130),
            transition=dict(duration=500, easing='cubic-in-out'),
        )

        fig.update_traces(
            pull=[0.06 if i == 0 else 0 for i in range(n)]
        )

        return fig

    return layout


def _empty_fig(mensagem: str):
    fig = go.Figure()
    fig.add_annotation(
        text=mensagem,
        x=0.5, y=0.5,
        font=dict(size=14, color='#c084fc'),
        showarrow=False
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        margin=dict(t=20, b=20, l=20, r=20)
    )
    return fig