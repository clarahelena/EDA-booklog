import pandas as pd
from dash import html
from components import vg_callbacks

def render(app, df: pd.DataFrame):
    df_valido = df[(df['pages'] > 0) & (df['rating'] > 0)].copy()
 
    # registra os callbacks dos KPIs
    vg_callbacks.registrar(app, df, df_valido, [], 0, 0, 0)

    layout = html.Div(id='vg-kpi-row', style={'display': 'flex', 'gap': '16px', 'flexWrap': 'wrap', 'marginBottom': '24px'})
    
    return layout