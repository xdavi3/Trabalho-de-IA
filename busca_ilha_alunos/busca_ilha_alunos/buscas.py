"""
Algoritmos de busca: busca greedy e A* (que também cobre o UCS, usando heurística nula).

a_estrela() está pronta. busca_greedy() é uma adaptação de a_estrela() e deve ser implementada seguindo os requisitos descritos em seu docstring.

Os algoritmos recebem o ambiente de fora (funções de vizinhança, custo e heurística) e devolvem resultados no mesmo formato:

    caminho: lista de posições da origem ao destino; lista vazia se o destino for inalcançável.
    historico_passos: um HistoricoBusca (subclasse de list) com uma tupla (no_expandido, snapshot_aberto, snapshot_fechado) por expansão, na ordem em que ocorreram. len(historico_passos) é o número de nós expandidos. Para economizar memória, os snapshots são guardados apenas em algumas entradas uniformemente espaçadas e na última (nas demais valem None), o que basta para a animação feita pelo módulo de visualização.

Com snapshots=False, todas as entradas do histórico são (no_expandido, None, None). Isso evita o custo de copiar os conjuntos aberto/fechado, o que é útil para medir tempo de execução, mas impede a animação.

Os nós são expandidos (e o teste de objetivo é feito) quando saem da fronteira. As buscas são em grafo: um nó já fechado não é expandido novamente. A fronteira é sempre uma fila de prioridade, e o que distingue os algoritmos é o critério de ordenação: por g (UCS), por h (greedy) ou por g + h (A*).
"""

import heapq


class HistoricoBusca(list):
    """Histórico de expansões de uma busca: uma lista de tuplas (no_expandido, snapshot_aberto, snapshot_fechado), uma por expansão, na ordem em que ocorreram.

    Copiar os conjuntos aberto e fechado a cada expansão custaria memória proporcional ao quadrado do número de expansões, o que esgota a memória em grades grandes. Por isso os snapshots (frozensets) são mantidos apenas em entradas uniformemente espaçadas, no máximo cerca de 2 * max_snapshots, e sempre na última entrada; nas demais, snapshot_aberto e snapshot_fechado valem None. O nó expandido é sempre registrado, então len(historico) é o número de expansões. Com snapshots=False nenhum snapshot é guardado.
    """

    def __init__(self, snapshots=True, max_snapshots=200):
        super().__init__()
        self.snapshots = snapshots
        self.max_snapshots = max_snapshots
        self.intervalo = 1  # snapshots são mantidos nas entradas de índice múltiplo do intervalo
        self._com_snapshot = 0  # entradas no múltiplo do intervalo que têm snapshot

    def registrar(self, no, em_aberto, fechados):
        """Registra a expansão de no, com cópias dos conjuntos aberto e fechado no momento da expansão."""
        if not self.snapshots:
            self.append((no, None, None))
            return

        # a entrada anterior só manteve snapshot por ser a última; se não está no espaçamento, perde-o agora
        if self and (len(self) - 1) % self.intervalo != 0:
            self[-1] = (self[-1][0], None, None)

        self.append((no, frozenset(em_aberto), frozenset(fechados)))
        if (len(self) - 1) % self.intervalo == 0:
            self._com_snapshot += 1

        if self._com_snapshot > 2 * self.max_snapshots:
            self.intervalo *= 2
            self._com_snapshot = 0
            ultimo = len(self) - 1
            for i in range(len(self)):
                if i % self.intervalo == 0:
                    self._com_snapshot += 1
                elif i != ultimo and self[i][1] is not None:
                    self[i] = (self[i][0], None, None)


def _reconstruir_caminho(veio_de, destino):
    """Reconstrói o caminho seguindo os predecessores a partir do destino. Devolve lista vazia se o destino nunca foi alcançado."""
    if destino not in veio_de:
        return []
    caminho = []
    no = destino
    while no is not None:
        caminho.append(no)
        no = veio_de[no]
    caminho.reverse()
    return caminho


def busca_greedy(vizinhos_fn, heuristica_fn, altura, largura, origem, destino, snapshots=True):
    """Busca greedy pela melhor escolha (greedy best-first): expande sempre o nó com menor h(n), ignorando o custo já acumulado.

    A IMPLEMENTAR, adaptando a_estrela(). Requisitos:
        - Usar uma fila de prioridade (heapq) ordenada por h(n), desempatando pela ordem de inserção.
        - Não expandir duas vezes o mesmo nó; o predecessor de cada nó é definido na primeira vez em que ele é descoberto.
        - Criar o histórico com HistoricoBusca(snapshots), registrar cada expansão com historico_passos.registrar(no, em_aberto, fechados) e devolver (caminho, historico_passos), com caminho vazio se o destino for inalcançável.
    """
    raise NotImplementedError("busca_greedy() ainda não foi implementada")


def a_estrela(vizinhos_fn, custo_fn, heuristica_fn, altura, largura, origem, destino, snapshots=True):
    """Busca A*: expande o nó com menor f(n) = g(n) + h(n), onde g é o custo acumulado e h a estimativa até o destino.

    Com heuristica_fn nula, equivale à busca de custo uniforme (UCS/Dijkstra). Esta implementação não reabre nós já fechados: quando um nó sai da fronteira e é expandido, o seu custo acumulado e o seu predecessor não mudam mais. Empates de f(n) são desempatados pela ordem de inserção na fila.
    """
    contador = 0
    fronteira = [(heuristica_fn(origem, destino), contador, origem)]
    veio_de = {origem: None}
    custo_ate_aqui = {origem: 0.0}
    em_aberto = {origem}
    fechados = set()
    historico_passos = HistoricoBusca(snapshots)

    while fronteira:
        _, _, atual = heapq.heappop(fronteira)
        if atual in fechados:
            continue  # entrada obsoleta na fila (o nó já foi expandido por um caminho melhor)

        em_aberto.discard(atual)
        fechados.add(atual)
        historico_passos.registrar(atual, em_aberto, fechados)

        if atual == destino:
            break

        for prox in vizinhos_fn(atual, altura, largura):
            if prox in fechados:
                continue
            novo_custo = custo_ate_aqui[atual] + custo_fn(atual, prox)
            if prox not in custo_ate_aqui or novo_custo < custo_ate_aqui[prox]:
                custo_ate_aqui[prox] = novo_custo
                veio_de[prox] = atual
                contador += 1
                heapq.heappush(fronteira, (novo_custo + heuristica_fn(prox, destino), contador, prox))
                em_aberto.add(prox)

    return _reconstruir_caminho(veio_de, destino), historico_passos
