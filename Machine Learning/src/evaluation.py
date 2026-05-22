import numpy as np


def precision_at_k(modelo, X, df, test_idx, k=10):

    acertos = 0
    total = 0

    for idx in test_idx:

        vec = X[idx].reshape(1, -1)

        _, indices = modelo.kneighbors(
            vec,
            n_neighbors=k + 1
        )

        recomendados = indices[0][1:]

        g_alvo = set(df.iloc[idx]['genre_list'])

        for r in recomendados:

            if g_alvo & set(df.iloc[r]['genre_list']):
                acertos += 1

        total += k

    return acertos / total if total else 0


def catalog_coverage(modelo, X, n_queries=100, k=10):

    recomendados_total = set()

    indices_teste = np.random.choice(
        len(X),
        size=min(n_queries, len(X)),
        replace=False
    )

    for idx in indices_teste:

        vec = X[idx].reshape(1, -1)

        _, indices = modelo.kneighbors(
            vec,
            n_neighbors=k + 1
        )

        recomendados = indices[0][1:]

        recomendados_total.update(recomendados)

    cobertura = len(recomendados_total) / len(X)

    return cobertura