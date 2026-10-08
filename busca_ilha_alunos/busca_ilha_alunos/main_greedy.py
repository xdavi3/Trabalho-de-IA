"""
Busca greedy (greedy best-first) na Ilha do Tesouro.

A fila de prioridade é ordenada só pela heurística h(n), ignorando o custo já percorrido.

Heurísticas disponíveis (cenarios.HEURISTICAS): "euclidiana" (distância em linha reta até o destino) e "zero" (h = 0).
"""

from buscas import busca_greedy
from cenarios import criar_cenario
from visualizacao import animar

if __name__ == "__main__":
    SEMENTE = 0  # semente do grupo
    HEURISTICA = "euclidiana"  # "euclidiana" ou "zero"

    cenario = criar_cenario(SEMENTE)
    caminho, historico_passos = busca_greedy(
        cenario.vizinhos, cenario.heuristica(HEURISTICA),
        cenario.altura, cenario.largura, cenario.origem, cenario.destino,
    )
    rotulo = f"Greedy (h = {HEURISTICA})"
    print(cenario.resumo(rotulo, caminho, historico_passos))

    arquivo = f"greedy_{HEURISTICA}_semente{SEMENTE}.gif"
    animar(cenario.fundo, caminho, historico_passos, cenario.origem, cenario.destino, arquivo, titulo=f"{rotulo} - {cenario.nome}")
    print(f"Animação salva em {arquivo}")
