"""
Ambiente: vizinhança da grade, modelo de custo de deslocamento e heurísticas. Não sabe nada sobre algoritmos de busca.

Convenções:
    - Posições são tuplas (linha, coluna).
    - A elevação é um array 2D normalizado em [0, 1]; e(n) é a elevação da célula n.
    - A grade é 8-conectada: cada célula tem até 8 vizinhas (ortogonais e diagonais).

Modelo de custo (assimétrico), para células vizinhas a e b:

    c(a, b) = L(a, b) * (1 + 60 * s + 10 * d) * φ(b)

em que L(a, b) é a distância entre as células (1 no passo ortogonal e sqrt(2) no diagonal), s = max(0, e(b) - e(a)) é a subida, d = max(0, e(a) - e(b)) é a descida e φ(b) é o fator do terreno da célula de destino. Os coeficientes 60 e 10 são FATOR_SUBIDA e FATOR_DESCIDA. Este módulo calcula o custo sem o fator de terreno, L(a, b) * (1 + 60 * s + 10 * d); ilha.fabricar_custo() multiplica o resultado por φ(b).
"""

import numpy as np

FATOR_SUBIDA = 60.0  # penalidade por unidade de elevação ganha
FATOR_DESCIDA = 10.0  # penalidade por unidade de elevação perdida


def vizinhos(pos, altura, largura):
    """Vizinhança 8-conectada (inclui diagonais), respeitando os limites da grade, na ordem: norte, sul, oeste, leste, noroeste, nordeste, sudoeste, sudeste."""
    x, y = pos
    candidatos = [
        (x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1),
        (x - 1, y - 1), (x - 1, y + 1), (x + 1, y - 1), (x + 1, y + 1),
    ]
    return [(nx, ny) for nx, ny in candidatos if 0 <= nx < altura and 0 <= ny < largura]


def distancia(a, b):
    """Distância L(a, b) entre duas células (1 no passo ortogonal e sqrt(2) no diagonal)."""
    return float(np.hypot(a[0] - b[0], a[1] - b[1]))


def custo_aresta(elevacao, a, b):
    """Custo de mover da célula a para a célula vizinha b, sem o fator de terreno: L(a, b) * (1 + FATOR_SUBIDA * s + FATOR_DESCIDA * d)."""
    variacao = elevacao[b] - elevacao[a]
    s = max(0.0, variacao)
    d = max(0.0, -variacao)
    return float(distancia(a, b) * (1.0 + FATOR_SUBIDA * s + FATOR_DESCIDA * d))


def heuristica_zero(a, destino):
    """Heurística nula, h(n) = 0. Com ela, a_estrela() se torna a busca de custo uniforme (UCS)."""
    return 0.0


def heuristica_euclidiana(a, destino):
    """Distância euclidiana (em linha reta) entre a célula e o destino, medida em células."""
    return distancia(a, destino)
