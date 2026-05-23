import numpy as np


def precision_at_k(
    modelo,
    X,
    df,
    test_idx,
    train_idx=None
):
    """
    Calcula Precision@K baseado em gêneros compartilhados.
    """

    acertos = 0
    total = 0

    for idx in test_idx:

        # Vetor do item de teste
        vec = X[idx].reshape(1, -1)

        # Buscar vizinhos
        _, indices = modelo.kneighbors(vec)

        recomendados = indices[0][1:]

        # Mapear índices locais -> globais
        if train_idx is not None:
            recomendados = train_idx[recomendados]

        # Gêneros do item alvo
        g_alvo = set(df.iloc[idx]['genre_list'])

        # Comparar gêneros
        for r in recomendados:

            g_rec = set(df.iloc[r]['genre_list'])

            if g_alvo & g_rec:
                acertos += 1

        total += len(recomendados)

    return acertos / total if total else 0


def catalog_coverage(
    modelo,
    X,
    n_queries=100,
    train_idx=None
):
    """
    Mede a porcentagem do catálogo
    que aparece nas recomendações.
    """

    recomendados_total = set()

    indices_teste = np.random.choice(
        len(X),
        size=min(n_queries, len(X)),
        replace=False
    )

    for idx in indices_teste:

        vec = X[idx].reshape(1, -1)

        _, indices = modelo.kneighbors(vec)

        recomendados = indices[0][1:]

        # Mapear índices locais -> globais
        if train_idx is not None:
            recomendados = train_idx[recomendados]

        recomendados_total.update(recomendados)

    cobertura = len(recomendados_total) / len(X)

    return cobertura