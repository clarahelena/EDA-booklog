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
    Para cada item de teste, verifica quantos dos K recomendados
    compartilham pelo menos um gênero com o item consultado.
    """

    acertos = 0
    total = 0

    for idx in test_idx:

        vec = X[idx].reshape(1, -1)

        _, indices = modelo.kneighbors(vec)

        recomendados = indices[0][1:]

        if train_idx is not None:
            recomendados = train_idx[recomendados]

        g_alvo = set(df.iloc[idx]['genre_list'])

        for r in recomendados:
            g_rec = set(df.iloc[r]['genre_list'])
            if g_alvo & g_rec:
                acertos += 1

        total += len(recomendados)

    return acertos / total if total else 0


def recall_at_k(
    modelo,
    X,
    df,
    test_idx,
    train_idx=None
):
    """
    Calcula Recall@K baseado em gêneros compartilhados.
    Para cada item de teste, verifica quantos dos itens relevantes
    do conjunto de treino aparecem nos K recomendados.
    Relevante = compartilha pelo menos um gênero com o item consultado.
    O recall é limitado a K (cap) para evitar valores próximos de zero
    quando o catálogo tem muitos itens relevantes.
    """

    recalls = []

    indices_busca = train_idx if train_idx is not None else range(len(X))

    for idx in test_idx:

        vec = X[idx].reshape(1, -1)

        _, indices = modelo.kneighbors(vec)

        recomendados = indices[0][1:]

        if train_idx is not None:
            recomendados = train_idx[recomendados]

        g_alvo = set(df.iloc[idx]['genre_list'])

        # Contar quantos itens relevantes existem no conjunto de busca
        total_relevantes = sum(
            1 for i in indices_busca
            if i != idx and g_alvo & set(df.iloc[i]['genre_list'])
        )

        if total_relevantes == 0:
            continue

        acertos = sum(
            1 for r in recomendados
            if g_alvo & set(df.iloc[r]['genre_list'])
        )

        # Cap em K: não faz sentido recall > 1 quando há mais relevantes que K
        recalls.append(acertos / min(total_relevantes, len(recomendados)))

    return sum(recalls) / len(recalls) if recalls else 0


def f1_at_k(precision, recall):
    """
    Calcula F1@K a partir de Precision@K e Recall@K já computados.
    F1 = 2 * (P * R) / (P + R)
    Retorna 0 se ambos forem zero (evita divisão por zero).
    """

    if precision + recall == 0:
        return 0.0

    return 2 * (precision * recall) / (precision + recall)


def catalog_coverage(
    modelo,
    X,
    n_queries=100,
    train_idx=None
):
    """
    Mede a porcentagem do catálogo que aparece nas recomendações.
    Quanto maior, mais diverso é o sistema — evita recomendar
    sempre os mesmos livros populares.
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

        if train_idx is not None:
            recomendados = train_idx[recomendados]

        recomendados_total.update(recomendados)

    cobertura = len(recomendados_total) / len(X)

    return cobertura