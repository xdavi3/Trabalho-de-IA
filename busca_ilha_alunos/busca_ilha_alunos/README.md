# Busca na Ilha do Tesouro

Este pacote contém um ambiente de busca em grade com relevo, os algoritmos UCS e A\* prontos, a função a implementar (busca *greedy*), scripts para executar e animar cada algoritmo, um exemplo pequeno para acompanhar as buscas à mão e testes automáticos.

## Estrutura

| Arquivo | Conteúdo |
|---|---|
| `ambiente.py` | Vizinhança 8-conectada, modelo de custo e heurísticas. |
| `ilha.py` | Gerador da Ilha do Tesouro: terrenos, obstáculos, regras de deslocamento e desenho do mapa. |
| `cenarios.py` | `criar_cenario()` (a ilha) e `criar_exemplo()` (o exemplo 5x5), que reúnem em um objeto tudo o que as buscas precisam. |
| `buscas.py` | Algoritmos de busca. `a_estrela()` está pronto (o UCS é o A\* com a heurística `zero`); `busca_greedy()` deve ser implementada. |
| `visualizacao.py` | `animar()` (GIF da busca) e `desenhar_caminhos()` (figura com um painel por caminho). |
| `main_ucs.py`, `main_greedy.py`, `main_astar.py` | Executam um algoritmo na ilha, imprimem as métricas e salvam a animação. |
| `main_comparacao.py` | Executa os três algoritmos na ilha, imprime as tabelas comparativas e salva uma figura com os caminhos. |
| `main_exemplo.py` | Executa os três algoritmos no exemplo 5x5 e imprime a ordem de expansão. |
| `testes_buscas.py` | Testes automáticos dos algoritmos. |

## Instalação

```
pip install -r requirements.txt
```

## Uso

Cada script roda sozinho, por exemplo:

```
python3 testes_buscas.py
python3 main_comparacao.py
python3 main_greedy.py
```

Os parâmetros ficam no topo do bloco `if __name__ == "__main__":` de cada script:

| Parâmetro | Scripts | Valores | Significado |
|---|---|---|---|
| `SEMENTE` | `main_ucs.py`, `main_greedy.py`, `main_astar.py`, `main_comparacao.py` | inteiro | Variação do mapa da ilha; cada grupo recebe uma semente. |
| `HEURISTICA` | `main_greedy.py`, `main_astar.py` | `"euclidiana"`, `"zero"` | Heurística usada pela busca. |
| `REPETICOES` | `main_comparacao.py` | inteiro | Número de execuções de cada algoritmo na medição de tempo (vale o menor tempo). |

Os nomes dos arquivos gerados incluem a semente (e a heurística, quando houver), por exemplo `comparacao_semente0.png` e `greedy_euclidiana_semente0.gif`. Enquanto `busca_greedy()` não for implementada, `main_greedy.py` termina com `NotImplementedError`, e `main_comparacao.py` e `main_exemplo.py` indicam a busca *greedy* como ainda não implementada.

## A Ilha do Tesouro

O mapa é uma grade de 90x90 células. O navio está ancorado na praia oeste (origem) e o tesouro está enterrado na praia leste (destino), na mesma linha. No caminho há um vulcão com cratera, um lago, um pântano, um morro, florestas, campos e praias. A semente altera detalhes do mapa (contorno da costa, colinas e manchas de floresta), mas não a posição desses elementos.

Regras de deslocamento:

- O movimento é 8-conectado: um passo ortogonal mede 1 e um passo diagonal mede √2.
- Mar e lago são intransitáveis.
- Não é possível passar entre células vizinhas cuja diferença de elevação seja maior que `LIMITE_INCLINACAO` (0,12): é um penhasco.
- Esses obstáculos são aplicados na função de vizinhança, portanto valem para todos os algoritmos.

Cada tipo de terreno tem um fator φ que multiplica o custo de entrar na célula:

| Terreno | Fator φ |
|---|---|
| Campo | 1,0 |
| Praia | 1,2 |
| Rocha vulcânica | 1,3 |
| Floresta | 1,5 |
| Pântano | 5,0 |
| Mar, lago | intransitável |

## Modelo de custo

O custo de mover da célula `a` para a célula vizinha `b` é

```
c(a, b) = L(a, b) · (1 + 60·s + 10·d) · φ(b)
```

em que `L(a, b)` é a distância entre as células (1 no passo ortogonal e √2 no diagonal), `s = max(0, e(b) − e(a))` é a subida, `d = max(0, e(a) − e(b))` é a descida, `e(n)` é a elevação da célula `n`, normalizada em [0, 1], e `φ(b)` é o fator do terreno da célula de destino. Subir é mais caro que descer, e andar no plano custa apenas a distância percorrida multiplicada pelo fator do terreno. No código, os coeficientes 60 e 10 são `FATOR_SUBIDA` e `FATOR_DESCIDA` (em `ambiente.py`).

`main_comparacao.py` decompõe o custo de cada caminho em três parcelas que somam o total: comprimento, a soma de `L(a, b)`; elevação, a soma de `L(a, b) · (60·s + 10·d)`; e terreno, a soma de `L(a, b) · (1 + 60·s + 10·d) · (φ(b) − 1)`.

## Heurísticas

| Nome | Definição |
|---|---|
| `zero` | h(n) = 0 (com ela, o A\* se torna o UCS). |
| `euclidiana` | Distância em linha reta da célula até o destino, medida em células. |

## Exemplo 5x5

`criar_exemplo()` cria uma grade de 5x5 células de campo com um pântano em (2, 2) e um pequeno morro a sudeste, com origem em (3, 0) e destino em (2, 4), usando as mesmas regras de vizinhança e custo da ilha. `main_exemplo.py` imprime o mapa do exemplo e, para cada algoritmo, a ordem de expansão com g(n), h(n) e f(n) de cada nó e o caminho final. O exemplo serve para conferir à mão o funcionamento das buscas; os testes verificam a ordem de expansão da busca *greedy* nele.

Os vizinhos de uma célula são gerados na ordem norte, sul, oeste, leste, noroeste, nordeste, sudoeste e sudeste, e as buscas desempatam nós com a mesma prioridade pela ordem de inserção na fila.

## Formato dos resultados

Todas as buscas devolvem `(caminho, historico_passos)`:

- `caminho` é a lista de posições `(linha, coluna)` da origem ao destino, ou uma lista vazia se o destino for inalcançável.
- `historico_passos` é um `HistoricoBusca` (uma lista) com uma tupla `(no_expandido, snapshot_aberto, snapshot_fechado)` por expansão. `len(historico_passos)` é o número de nós expandidos. Para economizar memória, os snapshots dos conjuntos aberto e fechado são guardados apenas em algumas entradas uniformemente espaçadas e sempre na última; nas demais valem `None`. Esse histórico alimenta a animação.
- Com `snapshots=False`, nenhum snapshot é guardado. É assim que `main_comparacao.py` mede o tempo de execução.

## O que implementar

Em `buscas.py`, implemente `busca_greedy()`, que ainda levanta `NotImplementedError`, seguindo os requisitos descritos no seu docstring. Ela é uma adaptação de `a_estrela()` em que a fila de prioridade passa a ser ordenada só por h(n).

Depois de implementar, execute `python3 testes_buscas.py`. Cada teste aparece como PASSOU, FALHOU ou PENDENTE (algoritmo ainda não implementado). Antes de cada bloco de testes, a linha `executando: ...` lista os algoritmos à medida que são executados. Se uma busca chamar a função de vizinhança mais de 3 vezes o número de células da grade, ela é interrompida e os testes correspondentes falham com a mensagem `LimiteDeExpansoes`. Passar em todos os testes indica que a implementação tem as propriedades esperadas, mas não substitui a análise pedida no trabalho.

## Observações

- Sem animação, cada busca na ilha leva menos de 0,1 s. Nas medições de referência (um núcleo de um processador Intel Xeon de 2,1 GHz), cada animação levou de 15 a 23 segundos para ser gerada e usou até cerca de 380 MB de memória; o tempo varia conforme o computador.
- O mapa da ilha foi calibrado e validado para o tamanho 90x90; outros tamanhos não são suportados.
