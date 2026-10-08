"""
Comparação dos algoritmos na Ilha do Tesouro.

Executa UCS, busca greedy e A* (estes dois com a heurística euclidiana) e imprime duas tabelas:
    1. Passos, custo, nós expandidos, tempo, células de pântano no caminho e células do interior da cratera expandidas.
    2. Decomposição do custo de cada caminho em comprimento, elevação e terreno (ver Cenario.decompor_custo).
Salva também uma figura com um painel por algoritmo mostrando o caminho encontrado. Algoritmos ainda não implementados em buscas.py são indicados na tabela e omitidos da figura.

As buscas são executadas com snapshots=False, para que o tempo medido reflita o algoritmo e não a cópia dos conjuntos usada na animação. Cada algoritmo é executado REPETICOES vezes e o menor tempo é reportado.
"""

import time

from buscas import a_estrela, busca_greedy
from cenarios import criar_cenario
from ilha import PANTANO
from visualizacao import desenhar_caminhos


def executar(funcao, repeticoes):
    """Executa funcao() repeticoes vezes e devolve (resultado, menor tempo em segundos)."""
    melhor = float("inf")
    resultado = None
    for _ in range(repeticoes):
        inicio = time.perf_counter()
        resultado = funcao()
        melhor = min(melhor, time.perf_counter() - inicio)
    return resultado, melhor


if __name__ == "__main__":
    SEMENTE = 0  # semente do grupo
    REPETICOES = 3

    c = criar_cenario(SEMENTE)
    args = (c.altura, c.largura, c.origem, c.destino)
    experimentos = [
        ("UCS", lambda: a_estrela(c.vizinhos, c.custo, c.heuristica("zero"), *args, snapshots=False)),
        ("Greedy (euclidiana)", lambda: busca_greedy(c.vizinhos, c.heuristica("euclidiana"), *args, snapshots=False)),
        ("A* (euclidiana)", lambda: a_estrela(c.vizinhos, c.custo, c.heuristica("euclidiana"), *args, snapshots=False)),
    ]

    print(f"Cenário: {c.nome} ({c.altura}x{c.largura}), origem {c.origem}, destino {c.destino}\n")
    cabecalho = f"{'Algoritmo':<22}{'Passos':>8}{'Custo':>9}{'Expandidos':>12}{'Tempo (ms)':>12}{'Pântano':>9}{'Cratera':>9}"
    print(cabecalho)
    print("-" * len(cabecalho))

    caminhos = {}
    decomposicoes = []
    for nome, funcao in experimentos:
        try:
            (caminho, historico_passos), tempo = executar(funcao, REPETICOES)
        except NotImplementedError:
            print(f"{nome:<22}  (ainda não implementado)")
            continue

        expandidos = len(historico_passos)
        cratera = c.contar_cratera(historico_passos)
        if not caminho:
            print(f"{nome:<22}{'-':>8}{'-':>9}{expandidos:>12}{1000 * tempo:>12.1f}{'-':>9}{cratera:>9}  (destino inalcançável)")
            continue

        custo = c.custo_caminho(caminho)
        print(f"{nome:<22}{len(caminho) - 1:>8}{custo:>9.1f}{expandidos:>12}{1000 * tempo:>12.1f}{c.contar_terreno(caminho, PANTANO):>9}{cratera:>9}")
        caminhos[f"{nome}\n{len(caminho) - 1} passos | custo {custo:.1f} | {expandidos} exp."] = caminho
        decomposicoes.append((nome, c.decompor_custo(caminho)))

    print("\nPântano: células de pântano no caminho. Cratera: células do interior da cratera expandidas.")

    if decomposicoes:
        print("\nDecomposição do custo do caminho")
        cabecalho = f"{'Algoritmo':<22}{'Comprimento':>13}{'Elevação':>10}{'Terreno':>10}{'Total':>9}"
        print(cabecalho)
        print("-" * len(cabecalho))
        for nome, partes in decomposicoes:
            print(f"{nome:<22}{partes['comprimento']:>13.1f}{partes['elevacao']:>10.1f}{partes['terreno']:>10.1f}{partes['total']:>9.1f}")

    arquivo = f"comparacao_semente{SEMENTE}.png"
    desenhar_caminhos(c.fundo, caminhos, c.origem, c.destino, arquivo, titulo=c.nome)
    print(f"\nFigura salva em {arquivo}")
