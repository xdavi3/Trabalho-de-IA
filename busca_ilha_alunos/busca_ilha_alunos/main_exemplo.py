"""
Exemplo 5x5, pequeno o bastante para acompanhar as buscas à mão.

Imprime o mapa do exemplo (terreno e elevação de cada célula) e, para UCS, busca greedy e A* (estes dois com a heurística euclidiana), a ordem de expansão com os valores de cada nó expandido e o caminho final.

Colunas das tabelas de expansão:
    g(n): custo do menor caminho da origem até n (calculado com o UCS).
    h(n): heurística euclidiana até o destino.
    f(n): valor usado para ordenar a fila de prioridade (g no UCS, h na greedy, g + h no A*).
"""

from buscas import a_estrela, busca_greedy
from cenarios import criar_exemplo
from ilha import NOMES_TERRENO


def imprimir_mapa(c):
    print(f"{c.nome}: origem {c.origem}, destino {c.destino}; vizinhança 8-conectada")
    print("\nTerreno (C = campo, P = pântano) e elevação de cada célula; O: marca a origem e D: o destino")
    print("      " + "".join(f"{j:>10}" for j in range(c.largura)))
    for i in range(c.altura):
        celulas = []
        for j in range(c.largura):
            marca = "O:" if (i, j) == c.origem else "D:" if (i, j) == c.destino else ""
            celulas.append(f"{marca}{NOMES_TERRENO[c.terreno[i, j]][0]} {c.elevacao[i, j]:.2f}")
        print(f"{i:>6}" + "".join(f"{x:>10}" for x in celulas))
    print()


def custos_otimos(c):
    """Custo do menor caminho da origem até cada célula alcançável, calculado com o UCS."""
    custos = {}
    for i in range(c.altura):
        for j in range(c.largura):
            caminho, _ = a_estrela(c.vizinhos, c.custo, c.heuristica("zero"), c.altura, c.largura, c.origem, (i, j), snapshots=False)
            if caminho:
                custos[(i, j)] = c.custo_caminho(caminho)
    return custos


def imprimir_busca(c, nome, executar, prioridade, g_otimo):
    print(nome)
    try:
        caminho, historico_passos = executar()
    except NotImplementedError:
        print("  (ainda não implementado)\n")
        return
    h = c.heuristica("euclidiana")
    print(f"  {'Ordem':>5}  {'Nó':<8}{'g(n)':>8}{'h(n)':>8}{'f(n)':>8}")
    for k, (no, _, _) in enumerate(historico_passos, start=1):
        g, hn = g_otimo[no], h(no, c.destino)
        f = {"g": g, "h": hn, "g+h": g + hn}[prioridade]
        g_texto = f"{g:>8.2f}" if prioridade != "h" else f"{'-':>8}"
        print(f"  {k:>5}  {str(no):<8}{g_texto}{hn:>8.2f}{f:>8.2f}")
    if caminho:
        print(f"  Caminho: {' -> '.join(str(p) for p in caminho)}")
        print(f"  Custo do caminho: {c.custo_caminho(caminho):.2f}; nós expandidos: {len(historico_passos)}\n")
    else:
        print("  Destino inalcançável\n")


if __name__ == "__main__":
    c = criar_exemplo()
    args = (c.altura, c.largura, c.origem, c.destino)
    imprimir_mapa(c)
    g_otimo = custos_otimos(c)
    imprimir_busca(c, "UCS (f = g)", lambda: a_estrela(c.vizinhos, c.custo, c.heuristica("zero"), *args), "g", g_otimo)
    imprimir_busca(c, "Greedy (f = h, euclidiana)", lambda: busca_greedy(c.vizinhos, c.heuristica("euclidiana"), *args), "h", g_otimo)
    imprimir_busca(c, "A* (f = g + h, euclidiana)", lambda: a_estrela(c.vizinhos, c.custo, c.heuristica("euclidiana"), *args), "g+h", g_otimo)
