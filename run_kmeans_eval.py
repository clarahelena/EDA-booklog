import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')
from sklearn.preprocessing import MultiLabelBinarizer, MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

df = pd.read_parquet('Machine Learning/data/processed/books_clean.parquet')
df = df.dropna(subset=['genre_list', 'rating', 'pages', 'totalratings']).copy()

mlb = MultiLabelBinarizer()
genre_matrix = mlb.fit_transform(df['genre_list'])

cols_numericas = ['rating', 'pages', 'totalratings']
scaler = MinMaxScaler()
numeric_matrix = scaler.fit_transform(df[cols_numericas])

X_cluster = np.hstack((genre_matrix, numeric_matrix))

K_range = range(2, 9)
sample_size = min(10000, X_cluster.shape[0])
np.random.seed(42)
sample_indices = np.random.choice(X_cluster.shape[0], sample_size, replace=False)
X_sample = X_cluster[sample_indices]

for k in K_range:
    kmeans = KMeans(n_clusters=k, init='k-means++', random_state=42, n_init=10)
    kmeans.fit(X_cluster)
    score = silhouette_score(X_sample, kmeans.labels_[sample_indices])
    print(f"K={k} -> Inercia: {kmeans.inertia_:.0f} | Silhouette Score: {score:.4f}")
