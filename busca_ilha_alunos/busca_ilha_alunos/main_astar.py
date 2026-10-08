"""
A* na Ilha do Tesouro.

A fila de prioridade é ordenada por f(n) = g(n) + h(n), combinando o custo já percorrido com a estimativa da heurística até o destino.

Heurísticas disponíveis (cenarios.HEURISTICAS): "euclidiana" (distância em linha reta até o destino) e "zero" (h = 0).
"""

from buscas import a_estrela
from cenarios import criar_cenario
from visualizacao import animar

if __name__ == "__main__":
    SEMENTE = 0  # semente do grupo
    HEURISTICA = "euclidiana"  # "euclidiana" ou "zero"

    cenario = criar_cenario(SEMENTE)
    caminho, historico_passos = a_estrela(
        cenario.vizinhos, cenario.custo, cenario.heuristica(HEURISTICA),
        cenario.altura, cenario.largura, cenario.origem, cenario.destino,
    )
    rotulo = f"A* (h = {HEURISTICA})"
    print(cenario.resumo(rotulo, caminho, historico_passos))

    arquivo = f"astar_{HEURISTICA}_semente{SEMENTE}.gif"
    animar(cenario.fundo, caminho, historico_passos, cenario.origem, cenario.destino, arquivo, titulo=f"{rotulo} - {cenario.nome}")
    print(f"Animação salva em {arquivo}")
