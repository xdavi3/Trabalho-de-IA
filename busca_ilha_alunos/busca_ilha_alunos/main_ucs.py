"""
UCS (busca de custo uniforme) na Ilha do Tesouro.

O UCS é executado como A* com heurística nula: a_estrela() já é genérica o suficiente para isso, sem precisar de um algoritmo separado. A fila de prioridade é ordenada só pelo custo acumulado g(n).
"""

from buscas import a_estrela
from cenarios import criar_cenario
from visualizacao import animar

if __name__ == "__main__":
    SEMENTE = 0  # semente do grupo

    cenario = criar_cenario(SEMENTE)
    caminho, historico_passos = a_estrela(
        cenario.vizinhos, cenario.custo, cenario.heuristica("zero"),
        cenario.altura, cenario.largura, cenario.origem, cenario.destino,
    )
    print(cenario.resumo("UCS", caminho, historico_passos))

    arquivo = f"ucs_semente{SEMENTE}.gif"
    animar(cenario.fundo, caminho, historico_passos, cenario.origem, cenario.destino, arquivo, titulo=f"UCS - {cenario.nome}")
    print(f"Animação salva em {arquivo}")
