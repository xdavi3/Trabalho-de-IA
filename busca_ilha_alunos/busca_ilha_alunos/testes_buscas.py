"""
Testes automáticos dos algoritmos de buscas.py.

Execute com:  python3 testes_buscas.py

Cada teste é marcado como PASSOU, FALHOU ou PENDENTE (quando o algoritmo ainda levanta NotImplementedError). Os testes verificam propriedades que toda implementação correta deve ter: caminhos válidos, menor custo no UCS e no A*, busca greedy guiada pela heurística (o nó expandido é sempre o de menor h entre os abertos, e a ordem de expansão no exemplo 5x5 é a esperada), ausência de reexpansões e tratamento de destino inalcançável. As buscas são interrompidas, e o teste falha, se chamarem a função de vizinhança mais de 3 vezes o número de células da grade; como uma busca em grafo chama a vizinhança uma vez por expansão, isso indica nós expandidos mais de uma vez. Passar em todos os testes não substitui a análise pedida no trabalho.
"""

import sys
from functools import partial

import numpy as np

import ambiente
from buscas import HistoricoBusca, a_estrela, busca_greedy
from cenarios import criar_cenario, criar_exemplo

TOLERANCIA = 1e-9


class LimiteDeExpansoes(Exception):
    """Levantada quando uma busca chama a função de vizinhança muito mais vezes do que o número de células da grade."""


def com_limite(vizinhos_fn, limite):
    """Envolve vizinhos_fn com um contador de chamadas. Cada expansão chama a vizinhança uma vez, então uma busca em grafo correta não passa do número de células; o limite interrompe implementações que reexpandem nós antes que esgotem o tempo ou a memória."""
    chamadas = 0

    def vizinhos_contados(pos, alt, larg):
        nonlocal chamadas
        chamadas += 1
        if chamadas > limite:
            raise LimiteDeExpansoes(f"vizinhos_fn chamada mais de {limite} vezes; algum nó pode estar sendo expandido mais de uma vez")
        return vizinhos_fn(pos, alt, larg)

    return vizinhos_contados


def grade_com_paredes(paredes):
    """Devolve uma função de vizinhança 8-conectada que exclui as células em paredes."""
    bloqueadas = set(paredes)

    def vizinhos_fn(pos, alt, larg):
        return [p for p in ambiente.vizinhos(pos, alt, larg) if p not in bloqueadas]

    return vizinhos_fn


def caminho_valido(caminho, vizinhos_fn, altura, largura, origem, destino):
    if not caminho or caminho[0] != origem or caminho[-1] != destino:
        return False
    return all(b in vizinhos_fn(a, altura, largura) for a, b in zip(caminho, caminho[1:]))


def historico_bem_formado(historico):
    """Verifica se o histórico é um HistoricoBusca não vazio, com tuplas (nó, aberto, fechado) e snapshots (frozensets) na última entrada."""
    if not isinstance(historico, HistoricoBusca) or not historico:
        return False
    if not all(len(h) == 3 for h in historico):
        return False
    _, aberto, fechado = historico[-1]
    return isinstance(aberto, frozenset) and isinstance(fechado, frozenset) and historico[-1][0] in fechado


def custo_caminho(caminho, custo_fn):
    return sum(custo_fn(a, b) for a, b in zip(caminho, caminho[1:]))


def todos_algoritmos(vizinhos_fn, custo_fn, heuristica_fn, altura, largura, origem, destino):
    """Executa cada algoritmo e devolve {nome: (caminho, historico_passos, nós expandidos)}. O valor é None quando o algoritmo não está implementado e é a própria exceção quando a execução falha (inclusive LimiteDeExpansoes)."""
    args = (altura, largura, origem, destino)
    limite = 3 * altura * largura
    chamadas = {
        "UCS": lambda: a_estrela(com_limite(vizinhos_fn, limite), custo_fn, ambiente.heuristica_zero, *args),
        "Greedy": lambda: busca_greedy(com_limite(vizinhos_fn, limite), heuristica_fn, *args),
        "A*": lambda: a_estrela(com_limite(vizinhos_fn, limite), custo_fn, heuristica_fn, *args),
    }
    resultados = {}
    print("  executando:", end="", flush=True)  # se um algoritmo não terminar, o último nome impresso o identifica
    for nome, chamada in chamadas.items():
        print(f" {nome}", end="", flush=True)
        try:
            caminho, historico = chamada()
            total = len(historico)
        except NotImplementedError:
            resultados[nome] = None
            continue
        except Exception as erro:  # um erro de execução vira falha nos testes desse algoritmo
            resultados[nome] = erro
            continue
        resultados[nome] = (caminho, historico, total)
    print()
    return resultados


class Relatorio:
    def __init__(self):
        self.contagem = {"PASSOU": 0, "FALHOU": 0, "PENDENTE": 0}

    def verificar(self, descricao, resultados, nomes, condicao):
        """Avalia condicao(resultados) se todos os algoritmos em nomes estiverem implementados e tiverem executado sem erro."""
        erros = [resultados[n] for n in nomes if isinstance(resultados[n], Exception)]
        if any(resultados[n] is None for n in nomes):
            estado = "PENDENTE"
        elif erros:
            estado = "FALHOU"
            descricao += f" [erro na execução: {type(erros[0]).__name__}: {erros[0]}]"
        else:
            try:
                estado = "PASSOU" if condicao(resultados) else "FALHOU"
            except Exception as erro:  # um erro na implementação conta como falha do teste
                estado = "FALHOU"
                descricao += f" [{type(erro).__name__}: {erro}]"
        self.contagem[estado] += 1
        print(f"  [{estado:^8}] {descricao}")


def testar_historico(rel):
    print("HistoricoBusca")
    hist = HistoricoBusca(snapshots=True, max_snapshots=10)
    fechados = set()
    for i in range(1000):
        fechados.add(i)
        hist.registrar(i, {i + 1}, fechados)
    com_snapshot = [i for i, h in enumerate(hist) if h[1] is not None]
    r = {"HistoricoBusca": True}
    rel.verificar("registra todas as expansões", r, list(r), lambda r: [h[0] for h in hist] == list(range(1000)))
    rel.verificar("limita o número de snapshots guardados", r, list(r), lambda r: len(com_snapshot) <= 2 * 10 + 1)
    rel.verificar("mantém o snapshot da última expansão", r, list(r), lambda r: com_snapshot[-1] == 999 and hist[-1][2] == frozenset(range(1000)))
    rel.verificar("snapshots refletem o estado no momento da expansão", r, list(r), lambda r: all(hist[i][2] == frozenset(range(i + 1)) for i in com_snapshot))


def testar_grade_aberta(rel):
    print("Grade 9x9 sem obstáculos, terreno plano")
    alt = larg = 9
    elev = np.zeros((alt, larg))
    viz = ambiente.vizinhos
    custo = partial(ambiente.custo_aresta, elev)
    o, d = (0, 0), (6, 8)
    r = todos_algoritmos(viz, custo, ambiente.heuristica_euclidiana, alt, larg, o, d)
    for nome in r:
        rel.verificar(f"{nome}: caminho válido", r, [nome], lambda r, n=nome: caminho_valido(r[n][0], viz, alt, larg, o, d))
    rel.verificar("Greedy: segue a heurística (em grade aberta, expande no máximo 2 x (passos + 1) nós)", r, ["Greedy"], lambda r: r["Greedy"][2] <= 2 * len(r["Greedy"][0]))
    custo_otimo = 6 * np.sqrt(2) + 2
    rel.verificar("UCS: custo ótimo (6*sqrt(2) + 2)", r, ["UCS"], lambda r: abs(custo_caminho(r["UCS"][0], custo) - custo_otimo) < TOLERANCIA)
    rel.verificar("A*: custo ótimo (6*sqrt(2) + 2)", r, ["A*"], lambda r: abs(custo_caminho(r["A*"][0], custo) - custo_otimo) < TOLERANCIA)


def menor_h_a_cada_expansao(historico, destino, heuristica_fn):
    """Verifica, em cada entrada do histórico com snapshot, se o nó expandido tem h menor ou igual ao de todos os nós abertos (ainda não fechados) naquele momento."""
    for no, aberto, fechado in historico:
        if aberto is None:
            continue
        restantes = [heuristica_fn(n, destino) for n in aberto if n not in fechado]
        if restantes and heuristica_fn(no, destino) > min(restantes) + TOLERANCIA:
            return False
    return True


def testar_obstaculo_u(rel):
    print("Grade 9x9 com obstáculo em U aberto na direção da origem, terreno plano")
    alt = larg = 9
    paredes = [(i, 5) for i in range(2, 7)] + [(2, j) for j in range(3, 5)] + [(6, j) for j in range(3, 5)]
    viz = grade_com_paredes(paredes)
    custo = partial(ambiente.custo_aresta, np.zeros((alt, larg)))
    o, d = (4, 1), (4, 8)
    r = todos_algoritmos(viz, custo, ambiente.heuristica_euclidiana, alt, larg, o, d)
    rel.verificar("Greedy: caminho válido", r, ["Greedy"], lambda r: caminho_valido(r["Greedy"][0], viz, alt, larg, o, d))
    rel.verificar("Greedy: cada nó expandido tem o menor h entre os abertos naquele momento", r, ["Greedy"], lambda r: menor_h_a_cada_expansao(r["Greedy"][1], d, ambiente.heuristica_euclidiana))
    rel.verificar("Greedy: nenhum nó expandido duas vezes", r, ["Greedy"], lambda r: len({h[0] for h in r["Greedy"][1]}) == len(r["Greedy"][1]))


def testar_exemplo(rel):
    c = criar_exemplo()
    print(f"{c.nome} (ver main_exemplo.py)")
    r = todos_algoritmos(c.vizinhos, c.custo, c.heuristica("euclidiana"), c.altura, c.largura, c.origem, c.destino)
    ordem_esperada = [(3, 0), (2, 1), (2, 2), (2, 3), (2, 4)]
    rel.verificar("Greedy: caminho válido", r, ["Greedy"], lambda r: c.caminho_valido(r["Greedy"][0]))
    rel.verificar(f"Greedy: ordem de expansão {ordem_esperada}", r, ["Greedy"], lambda r: [h[0] for h in r["Greedy"][1]] == ordem_esperada)


def testar_casos_limite(rel):
    print("Casos-limite")
    alt = larg = 7
    elev = np.zeros((alt, larg))
    custo = partial(ambiente.custo_aresta, elev)
    viz = grade_com_paredes([(i, 3) for i in range(alt)])
    r = todos_algoritmos(viz, custo, ambiente.heuristica_euclidiana, alt, larg, (3, 0), (3, 6))
    for nome in r:
        rel.verificar(f"{nome}: destino inalcançável devolve caminho vazio", r, [nome], lambda r, n=nome: r[n][0] == [])

    r = todos_algoritmos(ambiente.vizinhos, custo, ambiente.heuristica_euclidiana, alt, larg, (2, 2), (2, 2))
    for nome in r:
        rel.verificar(f"{nome}: origem igual ao destino devolve [origem]", r, [nome], lambda r, n=nome: r[n][0] == [(2, 2)])


def testar_ilha(rel):
    c = criar_cenario(0)
    print(f"{c.nome}")
    r = todos_algoritmos(c.vizinhos, c.custo, c.heuristica("euclidiana"), c.altura, c.largura, c.origem, c.destino)
    for nome in r:
        rel.verificar(f"{nome}: caminho válido (sem atravessar água ou penhascos)", r, [nome], lambda r, n=nome: c.caminho_valido(r[n][0]))
    for nome in r:
        rel.verificar(f"{nome}: nenhum nó expandido duas vezes", r, [nome], lambda r, n=nome: len({h[0] for h in r[n][1]}) == len(r[n][1]))
    rel.verificar("A* (euclidiana): mesmo custo do UCS", r, ["UCS", "A*"], lambda r: abs(c.custo_caminho(r["A*"][0]) - c.custo_caminho(r["UCS"][0])) < TOLERANCIA)
    rel.verificar("A* (euclidiana): expande menos nós que o UCS", r, ["UCS", "A*"], lambda r: r["A*"][2] < r["UCS"][2])
    rel.verificar("UCS: custo menor ou igual ao de todos os outros caminhos", r, list(r), lambda r: all(c.custo_caminho(r["UCS"][0]) <= c.custo_caminho(v[0]) + TOLERANCIA for v in r.values()))
    rel.verificar("Histórico no formato HistoricoBusca, com snapshot na última expansão", r, list(r), lambda r: all(historico_bem_formado(v[1]) for v in r.values()))


if __name__ == "__main__":
    relatorio = Relatorio()
    testar_historico(relatorio)
    testar_grade_aberta(relatorio)
    testar_obstaculo_u(relatorio)
    testar_exemplo(relatorio)
    testar_casos_limite(relatorio)
    testar_ilha(relatorio)
    cont = relatorio.contagem
    print(f"\nResumo: {cont['PASSOU']} passaram, {cont['FALHOU']} falharam, {cont['PENDENTE']} pendentes")
    sys.exit(1 if cont["FALHOU"] else 0)
