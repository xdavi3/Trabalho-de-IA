"""
Cenários de busca: reúne em um único objeto tudo o que os algoritmos e a visualização precisam (dimensões, origem, destino, vizinhança, custo, heurísticas e imagem de fundo).

Cenários disponíveis:
    criar_cenario(semente): Ilha do Tesouro de ilha.py, com TAMANHO x TAMANHO células; cada grupo usa a sua semente.
    criar_exemplo(): grade 5x5 com um pântano e um pequeno morro, pequena o bastante para acompanhar as buscas à mão.
"""

from dataclasses import dataclass
from typing import Callable, Optional

import numpy as np

import ambiente
import ilha

HEURISTICAS = ("zero", "euclidiana")


@dataclass
class Cenario:
    """Ambiente pronto para ser passado aos algoritmos de buscas.py."""

    nome: str
    elevacao: np.ndarray
    terreno: np.ndarray
    origem: tuple
    destino: tuple
    vizinhos: Callable  # vizinhos(pos, altura, largura) -> lista de posições
    custo: Callable  # custo(a, b) -> float, para a e b vizinhos
    fundo: np.ndarray  # imagem RGB usada como fundo nas figuras
    cratera: Optional[np.ndarray] = None  # máscara do interior da cratera (somente na ilha)
    abertura: Optional[np.ndarray] = None  # máscara da brecha oeste do paredão (somente na ilha)

    @property
    def altura(self):
        return self.elevacao.shape[0]

    @property
    def largura(self):
        return self.elevacao.shape[1]

    def heuristica(self, nome):
        """Devolve a função h(a, destino) pedida. Nomes válidos: os de HEURISTICAS."""
        if nome == "zero":
            return ambiente.heuristica_zero
        if nome == "euclidiana":
            return ambiente.heuristica_euclidiana
        raise ValueError(f"heurística desconhecida: {nome!r}; use uma de {HEURISTICAS}")

    def custo_caminho(self, caminho):
        """Custo total de um caminho segundo o modelo de custo do cenário."""
        return float(sum(self.custo(a, b) for a, b in zip(caminho, caminho[1:])))

    def decompor_custo(self, caminho):
        """Decompõe o custo do caminho em três parcelas que somam o total.

        Para cada movimento de a para b, com c(a, b) = L * (1 + 60 * s + 10 * d) * φ(b):
            comprimento: L
            elevacao: L * (60 * s + 10 * d)
            terreno: L * (1 + 60 * s + 10 * d) * (φ(b) - 1)
        Devolve um dicionário com a soma de cada parcela ao longo do caminho e o total.
        """
        partes = {"comprimento": 0.0, "elevacao": 0.0, "terreno": 0.0}
        for a, b in zip(caminho, caminho[1:]):
            comprimento = ambiente.distancia(a, b)
            sem_terreno = ambiente.custo_aresta(self.elevacao, a, b)
            partes["comprimento"] += comprimento
            partes["elevacao"] += sem_terreno - comprimento
            partes["terreno"] += sem_terreno * (ilha.FATOR_TERRENO[self.terreno[b]] - 1.0)
        partes["total"] = partes["comprimento"] + partes["elevacao"] + partes["terreno"]
        return partes

    def caminho_valido(self, caminho):
        """Indica se o caminho começa na origem, termina no destino e só usa movimentos permitidos pela vizinhança."""
        if not caminho or caminho[0] != self.origem or caminho[-1] != self.destino:
            return False
        return all(b in self.vizinhos(a, self.altura, self.largura) for a, b in zip(caminho, caminho[1:]))

    def contar_terreno(self, caminho, tipo):
        """Número de células do caminho (exceto a origem) com o tipo de terreno indicado."""
        return int(sum(self.terreno[p] == tipo for p in caminho[1:]))

    def contar_cratera(self, historico_passos):
        """Número de células do interior da cratera expandidas pela busca; 0 se o cenário não tem cratera."""
        if self.cratera is None:
            return 0
        return int(sum(bool(self.cratera[entrada[0]]) for entrada in historico_passos))

    def resumo(self, algoritmo, caminho, historico_passos):
        """Texto com as métricas de um resultado de busca neste cenário."""
        linhas = [f"Cenário: {self.nome} ({self.altura}x{self.largura})", f"Algoritmo: {algoritmo}"]
        if not caminho:
            linhas.append("Destino inalcançável: nenhum caminho encontrado")
        else:
            linhas.append(f"Passos do caminho: {len(caminho) - 1}")
            linhas.append(f"Custo do caminho: {self.custo_caminho(caminho):.1f}")
            linhas.append(f"Células de pântano no caminho: {self.contar_terreno(caminho, ilha.PANTANO)}")
        if self.cratera is not None:
            linhas.append(f"Células da cratera expandidas: {self.contar_cratera(historico_passos)}")
        linhas.append(f"Nós expandidos: {len(historico_passos)}")
        return "\n".join(linhas)


def criar_cenario(semente=0):
    """Cria o cenário da Ilha do Tesouro com a semente indicada (ilha.TAMANHO x ilha.TAMANHO células)."""
    mapa = ilha.gerar_ilha(semente)
    return Cenario(
        nome=f"Ilha do Tesouro (semente {semente})",
        elevacao=mapa.elevacao,
        terreno=mapa.terreno,
        origem=mapa.origem,
        destino=mapa.destino,
        vizinhos=ilha.fabricar_vizinhos(mapa.elevacao, mapa.terreno),
        custo=ilha.fabricar_custo(mapa.elevacao, mapa.terreno),
        fundo=ilha.renderizar_mapa(mapa.elevacao, mapa.terreno),
        cratera=mapa.cratera,
        abertura=mapa.abertura,
    )


def criar_exemplo():
    """Cria o exemplo 5x5: grade de campo com uma célula de pântano em (2, 2) e um pequeno morro a sudeste, com origem em (3, 0) e destino em (2, 4). Usa as mesmas regras de vizinhança e custo da ilha."""
    elevacao = np.zeros((5, 5))
    for pos, valor in {(2, 3): 0.05, (3, 2): 0.05, (3, 3): 0.10, (3, 4): 0.05, (4, 3): 0.05}.items():
        elevacao[pos] = valor
    terreno = np.full((5, 5), ilha.CAMPO)
    terreno[2, 2] = ilha.PANTANO
    return Cenario(
        nome="Exemplo 5x5",
        elevacao=elevacao,
        terreno=terreno,
        origem=(3, 0),
        destino=(2, 4),
        vizinhos=ilha.fabricar_vizinhos(elevacao, terreno),
        custo=ilha.fabricar_custo(elevacao, terreno),
        fundo=ilha.renderizar_mapa(elevacao, terreno),
    )
