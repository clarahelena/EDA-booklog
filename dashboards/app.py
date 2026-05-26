import pandas as pd
import numpy as np
from dash import Dash, html
from components import scatter_relacao, barras_generos

# função para converter a string do parquet em uma lista
def extrair_generos(x):
    if pd.isna(x): return []
    if isinstance(x, str):
        x = x.replace('[', '').replace(']', '').replace("'", "")
        return [g.strip() for g in x.split(',') if g.strip()]
    if isinstance(x, (list, np.ndarray)):
        return [str(g).strip() for g in x if str(g).strip()]
    return []

# carregamento dos dados do dataset
try:
    df = pd.read_parquet('../datasets/books.parquet')
except FileNotFoundError:
    df = pd.read_parquet('datasets/books.parquet')

df['generos_lista'] = df['genre'].apply(extrair_generos) 

# iniciamento do dashboard
app = Dash(__name__)

# layout Global
app.layout = html.Div(
    style={'backgroundColor': '#0f172a', 'color': '#f8fafc', 'padding': '40px', 'minHeight': '100vh', 'fontFamily': 'system-ui, sans-serif'},
    children=[
        html.H1("Booklog Dashboard Interativo", style={'textAlign': 'center', 'marginBottom': '40px', 'color': '#a3e635'}),
        
        # painel de filtros e o gráfico de dispersão
        scatter_relacao.render(app, df),
        
        # gráfico de barras
        barras_generos.render(app, df)
    ]
)

if __name__ == '__main__':
    app.run(debug=True)