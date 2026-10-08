"""
Ilha do Tesouro em relevo: geração procedural do mapa, regras de deslocamento e renderização.

O mapa é uma grade quadrada de TAMANHO x TAMANHO células com duas camadas:
    elevacao: float em [0, 1], com 0 no nível do mar.
    terreno: inteiro por célula, com um dos tipos MAR, LAGO, PRAIA, CAMPO, FLORESTA, PANTANO ou ROCHA.

Elementos fixos do mapa (a semente altera apenas detalhes como o contorno da costa, colinas e manchas de floresta):
    - Navio (origem) ancorado na praia oeste e tesouro (destino) na praia leste, na mesma linha.
    - Vulcão no centro, com uma cratera cuja borda é um paredão intransitável, aberta apenas para oeste.
    - Lago ao norte do vulcão, encostado na sua borda.
    - Pântano extenso ao sul do vulcão, do paredão até a faixa de praia da costa sul.
    - Morro a sudeste, com encostas íngremes e caras de subir, transitáveis em quase toda a extensão (conforme a semente, alguns degraus isolados ultrapassam o limite de inclinação).
    - Uma faixa de mar separa a ilha da borda da grade.

Regras de deslocamento:
    - MAR e LAGO são intransitáveis.
    - Não é possível mover-se entre células vizinhas cuja diferença de elevação ultrapasse LIMITE_INCLINACAO (penhasco).
    - O custo de um movimento é custo_aresta() de ambiente.py multiplicado pelo fator φ do terreno da célula de destino (FATOR_TERRENO). Todos os fatores de terreno transitável são >= 1.
"""

from dataclasses import dataclass

import numpy as np
from scipy.ndimage import binary_fill_holes, distance_transform_edt, gaussian_filter, label

from ambiente import custo_aresta

TAMANHO = 90  # tamanho da grade para o qual o mapa foi calibrado e validado

MAR, LAGO, PRAIA, CAMPO, FLORESTA, PANTANO, ROCHA = range(7)

NOMES_TERRENO = {
    MAR: "Mar", LAGO: "Lago", PRAIA: "Praia", CAMPO: "Campo",
    FLORESTA: "Floresta", PANTANO: "Pântano", ROCHA: "Rocha vulcânica",
}

FATOR_TERRENO = {
    MAR: np.inf, LAGO: np.inf, PRAIA: 1.2, CAMPO: 1.0,
    FLORESTA: 1.5, PANTANO: 5.0, ROCHA: 1.3,
}

CORES_TERRENO = {
    MAR: (0.20, 0.45, 0.75), LAGO: (0.35, 0.65, 0.90), PRAIA: (0.91, 0.85, 0.63),
    CAMPO: (0.60, 0.78, 0.42), FLORESTA: (0.18, 0.48, 0.22), PANTANO: (0.42, 0.45, 0.25),
    ROCHA: (0.45, 0.36, 0.32),
}

LIMITE_INCLINACAO = 0.12  # diferença de elevação máxima entre células vizinhas


@dataclass
class Ilha:
    """Mapa gerado por gerar_ilha()."""

    elevacao: np.ndarray
    terreno: np.ndarray
    origem: tuple
    destino: tuple
    cratera: np.ndarray  # máscara booleana do interior da cratera
    abertura: np.ndarray  # máscara booleana da brecha oeste do paredão


def _ruido_suave(rng, tamanho, sigma):
    """Ruído gaussiano filtrado com desvio padrão unitário."""
    ruido = gaussian_filter(rng.normal(size=(tamanho, tamanho)), sigma)
    return ruido / ruido.std()


def _maior_componente(mascara):
    """Mantém apenas a maior região conexa da máscara, já com buracos preenchidos."""
    rotulos, n = label(mascara)
    if n == 0:
        return mascara
    tamanhos = np.bincount(rotulos.ravel())
    tamanhos[0] = 0
    return binary_fill_holes(rotulos == tamanhos.argmax())


def gerar_ilha(semente=0, tamanho=TAMANHO):
    """Gera a Ilha do Tesouro. A mesma (semente, tamanho) produz sempre o mesmo mapa.

    As posições e dimensões dos elementos são proporcionais ao tamanho, mas o limite de inclinação e a escala de elevação são absolutos por célula: em grades maiores as encostas ficam mais suaves e o paredão do vulcão pode deixar de ser intransitável. Por isso o mapa foi calibrado e validado (com verificar_armadilhas.py) apenas para tamanho=TAMANHO.
    """
    rng = np.random.default_rng(semente)
    t = tamanho
    Y, X = np.mgrid[0:t, 0:t].astype(float)

    # contorno da costa: elipse deformada por ruído de baixa frequência, com uma faixa de mar de 2 células junto à borda da grade
    raio = np.sqrt(((Y - 0.5 * t) / (0.42 * t)) ** 2 + ((X - 0.5 * t) / (0.44 * t)) ** 2)
    raio += 0.05 * _ruido_suave(rng, t, 0.10 * t)
    moldura = np.zeros((t, t), dtype=bool)
    moldura[2:-2, 2:-2] = True
    terra = _maior_componente((raio < 1.0) & moldura)
    dist_mar = distance_transform_edt(terra)

    # relevo de fundo: sobe suavemente a partir da costa, com colinas aleatórias
    elev = 0.18 * (1.0 - np.exp(-dist_mar / (0.10 * t)))
    elev += 0.025 * _ruido_suave(rng, t, 0.05 * t)

    # vulcão: anel alto e estreito (paredão) com brecha voltada para oeste e cratera rasa no interior
    cy, cx, r_cratera = 0.46 * t, 0.52 * t, 0.12 * t
    dist_vulcao = np.hypot(Y - cy, X - cx)
    angulo = np.arctan2(Y - cy, X - cx)
    desvio_oeste = np.pi - np.abs(angulo)  # 0 exatamente a oeste do centro
    brecha = np.clip((0.55 - desvio_oeste) / 0.12, 0.0, 1.0)
    anel = np.exp(-(((dist_vulcao - r_cratera) / (0.025 * t)) ** 2))
    elev += 0.85 * anel * (1.0 - brecha)
    elev += 0.10 * np.exp(-(((dist_vulcao - r_cratera) / (0.09 * t)) ** 2)) * (dist_vulcao > r_cratera)
    cratera = dist_vulcao < r_cratera - 0.035 * t
    elev[cratera] = np.minimum(elev[cratera], 0.12)
    abertura = (brecha > 0) & (dist_vulcao >= r_cratera - 0.035 * t) & (dist_vulcao <= r_cratera + 0.075 * t)

    # morro a sudeste: encostas íngremes, em geral abaixo do limite de inclinação
    morro = 0.55 * np.exp(-(((Y - 0.70 * t) ** 2 + (X - 0.78 * t) ** 2) / (2 * (0.075 * t) ** 2)))
    elev += morro

    elev = np.clip(elev, 0.0, 1.0) * terra

    terreno = np.full((t, t), CAMPO)
    floresta = _ruido_suave(rng, t, 0.05 * t) > 0.35
    terreno[floresta] = FLORESTA
    terreno[(anel > 0.25) | cratera | (morro > 0.30)] = ROCHA

    # pântano: região extensa ao sul do vulcão, do paredão até a costa sul (a faixa de praia é definida depois e prevalece)
    forma = ((Y - 0.80 * t) / (0.34 * t)) ** 4 + ((X - cx) / (0.22 * t)) ** 4
    pantano = forma + 0.15 * _ruido_suave(rng, t, 0.04 * t) < 1.0
    pantano &= Y > cy + 0.08 * t
    terreno[pantano & (terreno != ROCHA)] = PANTANO

    # lago ao norte, encostado no vulcão
    lago = (((Y - 0.22 * t) / (0.13 * t)) ** 2 + ((X - 0.50 * t) / (0.22 * t)) ** 2) < 1.0
    lago &= dist_vulcao > r_cratera + 0.03 * t
    lago &= dist_mar > 0.08 * t
    terreno[lago] = LAGO
    elev[lago] = 0.10

    terreno[dist_mar <= 0.04 * t] = PRAIA
    terreno[~terra] = MAR
    elev[~terra] = 0.0

    linha = int(round(0.5 * t))
    colunas_terra = np.flatnonzero(terra[linha])
    origem = (linha, int(colunas_terra.min()) + 1)
    destino = (linha, int(colunas_terra.max()) - 1)

    return Ilha(elevacao=elev, terreno=terreno, origem=origem, destino=destino, cratera=cratera, abertura=abertura)


def fabricar_vizinhos(elevacao, terreno, limite_inclinacao=LIMITE_INCLINACAO):
    """Devolve uma função vizinhos(pos, altura, largura) com a mesma assinatura de ambiente.vizinhos, mas que exclui células de água e movimentos entre células cuja diferença de elevação ultrapassa limite_inclinacao."""
    transitavel = np.isfinite(np.vectorize(FATOR_TERRENO.get)(terreno))
    deslocamentos = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def vizinhos_ilha(pos, altura, largura):
        x, y = pos
        resultado = []
        for dx, dy in deslocamentos:
            nx, ny = x + dx, y + dy
            if not (0 <= nx < altura and 0 <= ny < largura):
                continue
            if not transitavel[nx, ny]:
                continue
            if abs(elevacao[nx, ny] - elevacao[x, y]) > limite_inclinacao:
                continue
            resultado.append((nx, ny))
        return resultado

    return vizinhos_ilha


def fabricar_custo(elevacao, terreno):
    """Devolve uma função custo(a, b) = c(a, b): custo_aresta() de ambiente.py multiplicado pelo fator φ(b) do terreno da célula de destino."""

    def custo_ilha(a, b):
        return custo_aresta(elevacao, a, b) * FATOR_TERRENO[terreno[b]]

    return custo_ilha


def renderizar_mapa(elevacao, terreno):
    """Imagem RGB (altura x largura x 3, valores em [0, 1]) com as cores dos terrenos e sombreamento do relevo."""
    rgb = np.zeros(terreno.shape + (3,))
    for tipo, cor in CORES_TERRENO.items():
        rgb[terreno == tipo] = cor

    agua = (terreno == MAR) | (terreno == LAGO)
    gy, gx = np.gradient(elevacao)
    sombra = np.clip(1.0 + 3.0 * (gx + gy), 0.6, 1.3)  # luz vindo do noroeste: encostas voltadas para ele ficam mais claras
    altitude = 0.85 + 0.45 * elevacao  # regiões mais altas ficam mais claras
    fator = np.where(agua, 1.0, sombra * altitude)
    return np.clip(rgb * fator[..., None], 0.0, 1.0)
