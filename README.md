# EDA Booklog

Análise Exploratória de Dados (EDA) do catálogo de livros que fundamenta o sistema de recomendação do aplicativo **Booklog**. O projeto investiga padrões de qualidade, popularidade, consistência autoral e tendências da indústria editorial a partir de um dataset com ~6.800 títulos extraído do Kaggle.

Desenvolvido como projeto da disciplina **PISI3 — UFRPE**.

---

## Estrutura dos Notebooks

| Notebook | Tema | Pergunta central |
|---|---|---|
| `notebook_00` | Pré-processamento | Limpeza e exportação do dataset tratado |
| `notebook_01` | Visão geral do acervo | Quais são os gêneros, autores, anos e avaliações mais representativos? |
| `notebook_02` | Qualidade vs. popularidade | O que faz um livro ser verdadeiramente bom? |
| `notebook_03` | Formato e diversificação | A indústria está encurtando os livros e diversificando gêneros? |
| `notebook_04` | Consistência autoral | Recomendar um autor é suficiente, ou é preciso recomendar a obra certa? |

### Detalhamento

**Notebook 00 — Limpeza dos Dados**
Carrega o dataset bruto (`data.csv`, 6.810 registros), remove linhas com valores ausentes nas colunas obrigatórias (título, autor, categoria, descrição, ano, nota, páginas e contagem de avaliações) e exporta o dataset limpo (`books.csv`, 6.411 registros).

**Notebook 01 — Análise Geral do Acervo**
Panorama do catálogo: top 10 gêneros e autores por volume, distribuição de anos de publicação, dispersão de engajamento (curva de avaliações), distribuição de notas médias e perfil de extensão das obras.

**Notebook 02 — Qualidade vs. Popularidade**
Investiga o *Paradoxo da Popularidade* (notas perfeitas se concentram em obras de nicho enquanto bestsellers convergem para médias moderadas), identifica autores de elite por consistência de nota (mín. 5 obras) e mapeia a evolução histórica das avaliações por década.

**Notebook 03 — Formato e Diversificação**
Analisa a distribuição de páginas por década via boxplot e aplica o **Teste T de Welch** para verificar se livros modernos (pós-1990) são estatisticamente menores. Conclusão: a hipótese nula não é rejeitada — o formato médio permanece estável em ~300 páginas. Complementa com análise de crescimento dos top 10 gêneros ao longo das décadas em escala logarítmica.

**Notebook 04 — Consistência Autoral**
Usa o **desvio padrão das notas** como métrica central para 544 autores com 3+ obras. Classifica autores em consistentes (desvio < 0.1), moderados (0.1–0.3) e irregulares (> 0.3). Identifica os 15 mais consistentes (ex: Richard Feynman, desvio 0.010) e os 15 mais irregulares (ex: Arthur Conan Doyle, desvio 0.458). Testa se volume de produção determina consistência — correlação de Pearson de 0.149 indica que não.

---

## Dataset

| Arquivo | Descrição |
|---|---|
| `datasets/data.csv` | Dataset bruto extraído do Kaggle (6.810 registros) |
| `datasets/books.csv` | Dataset limpo gerado pelo `notebook_00` (6.411 registros) |

**Colunas principais:** `isbn13`, `title`, `authors`, `categories`, `published_year`, `average_rating`, `num_pages`, `ratings_count`, `description`.

---

## Tecnologias

- Python 3
- pandas · numpy
- matplotlib · seaborn
- plotly
- scipy

---

## Como executar

```bash
# 1. Instale as dependências
pip install -r requirements.txt

# 2. Execute os notebooks em ordem
jupyter notebook
```

> Execute o `notebook_00` primeiro — ele gera o `datasets/books.csv` consumido por todos os demais.
