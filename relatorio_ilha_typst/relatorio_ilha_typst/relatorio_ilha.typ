#import "modelo_ifes.typ": *

#show: report.with(
  course: "Inteligência Artificial — BSI",
  title: [Relatório do Trabalho 1:\ UCS, A\* e _Greedy_],
  subtitle: [Planejamento da Busca na Ilha do Tesouro],
  author: ("David de Assis",),
  cover-authors: [
    David de Assis
  ],
  professor: "Dr. Sérgio Nery Simões",
)

#let figuras-prontas = true
#let imagem(arquivo, proporcao) = if figuras-prontas { image("figuras/" + arquivo, width: 100%) } else { figura-provisoria(arquivo, proporcao) }
#let quadro(arquivo, legenda) = figure(imagem(arquivo, 440 / 496), caption: legenda, kind: "quadro", supplement: none, numbering: none, outlined: false)

#pagebreak(weak: true)

#heading(numbering: none)[Resumo]
<sec-resumo>

O planejamento de trajetórias em ambientes com variação topográfica e múltiplos tipos de terreno representa um problema clássico de busca em grafo com custos ponderados. Este trabalho analisa a eficácia, completude e otimalidade dos algoritmos Busca de Custo Uniforme (UCS), Busca _Greedy_ e A\* na navegação na Ilha do Tesouro (grade $90 times 90$, semente 0). Implementou-se a busca _greedy_ em Python e comparou-se seu desempenho com UCS e A\* guiados pela heurística euclidiana. O A\* e o UCS encontraram o caminho ótimo de custo $140{,}8$ (97 passos), porém o A\* expandiu $2437$ nós ($20{,}6\%$ a menos que os $3069$ do UCS). A busca _greedy_ encontrou um caminho subótimo de custo $312{,}3$ com $304$ expansões em $5{,}0\text{ ms}$, atravessando $11$ células de pântano devido à ausência do custo acumulado $g(n)$. Conclui-se que o A\* une a otimalidade do UCS à eficiência da busca informada.

*Palavras-chave:* Busca em Grafo; Custo Uniforme; Busca _Greedy_; Algoritmo A\*; Heurística Euclidiana.

= Introdução
<sec-introducao>

O problema de planejamento de trajetórias para agentes autônomos ou navegadores em ambientes complexos exige a identificação de caminhos eficientes que minimizem custos operacionais, como consumo de energia e tempo de deslocamento. Na Ilha do Tesouro, uma embarcação deve planejar uma rota a partir de um ponto de ancoragem na praia oeste (origem) até a localização de um tesouro enterrado na praia leste (destino). O mapa apresenta desafios geográficos significativos, incluindo elevações de terreno, penhascos intransitáveis, regiões de floresta, rochas vulcânicas e pântanos de alto custo de transposição. Modelado como uma grade $90 times 90$ com vizinhança 8-conectada, o cenário é formalizado como um problema de busca em grafo com custos de aresta dependentes da distância espacial, inclinação topográfica e fator de atrito do solo.

O objetivo principal deste trabalho é implementar, executar e comparar experimental e teoricamente os algoritmos de busca Custo Uniforme (UCS), Busca _Greedy_ (Greedy Best-First Search) e A\*, utilizando a heurística euclidiana. Busca-se avaliar como a função de avaliação de cada algoritmo afeta o número de nós expandidos, a forma da fronteira de busca e a otimalidade do caminho final.

Este relatório está organizado da seguinte forma: a @sec-fundamentos apresenta a fundamentação teórica dos algoritmos de busca e propriedades heurísticas; a @sec-metodologia descreve o modelo de custo, o ambiente e a implementação; a @sec-resultados expõe os dados experimentais obtidos; a @sec-analise responde às questões analíticas propostas; e a @sec-conclusao sintetiza os principais aprendizados.

= Fundamentos
<sec-fundamentos>

Os algoritmos de busca em grafo com fila de prioridade selecionam sequencialmente o nó $n$ com menor valor da função de avaliação $f(n)$ na fronteira de busca. A distinção fundamental entre o UCS, a Busca _Greedy_ e o A\* reside estritamente na definição de $f(n)$, conforme expresso na @eq-f:

#formula[$ f(n) = g(n) + h(n) $ <eq-f>]

em que $g(n)$ representa o custo acumulado real do caminho da origem até o nó $n$, e $h(n)$ denota a estimativa heurística do custo do nó $n$ até o destino $t$. O UCS utiliza apenas $f(n) = g(n)$, priorizando o custo já incorrido @dijkstra1959. A busca _greedy_ considera apenas $f(n) = h(n)$, expandindo o nó mais próximo do objetivo segundo a heurística @pearl1984. O algoritmo A\* combina ambas as parcelas, $f(n) = g(n) + h(n)$, buscando balancear o custo acumulado e a estimativa até o destino @hart1968. A @tab-fundamentos resume as propriedades teóricas dos três algoritmos @russell2022[cap. 3].

#figure(
  kind: table,
  supplement: [Tabela],
  styled-table(
    headers: ("Algoritmo", "Ordenação da fila", "Completo?", "Ótimo?", "Complexidade de tempo", "Complexidade de espaço"),
    rows: (
      ([UCS], [$g(n)$], [Sim#footnote[Considerando custos de aresta estritamente positivos ($c(a,b) >= epsilon > 0$).]], [Sim], [$O(b^{1 + floor(C^* \/ epsilon)})$], [$O(b^{1 + floor(C^* \/ epsilon)})$]),
      ([_Greedy_], [$h(n)$], [Não#footnote[Pode entrar em laços em espaços de estados infinitos/não visitados, mas em grafos finitos com detecção de repetidos é completo.]], [Não], [$O(b^m)$], [$O(b^m)$]),
      ([A\*], [$g(n) + h(n)$], [Sim], [Sim#footnote[Sob a condição de que a heurística $h(n)$ seja admissível.]], [$O(b^d)$], [$O(b^d)$]),
    ),
    col-widths: (0.9fr, 1.1fr, 1.4fr, 1.4fr, 1.2fr, 1.2fr),
    align: (left, center, left, left, center, center),
  ),
  caption: [Comparação das propriedades teóricas dos três algoritmos de busca.],
) <tab-fundamentos>

Uma heurística $h(n)$ é dita *admissível* se nunca superestima o verdadeiro custo mínimo $c^*(n, t)$ para atingir o destino a partir do nó $n$, isto é, $h(n) <= c^*(n, t)$ para todo $n$. Adicionalmente, $h(n)$ é *consistente* (ou monótona) se satisfizer a desigualdade triangular $h(a) <= c(a, b) + h(b)$ para todo vizinho $b$ de $a$. Quando $h(n)$ é admissível em buscas em árvore ou consistente em buscas em grafo, o algoritmo A\* garante a localização de um caminho de custo ótimo $C^*$ @russell2022.

= Metodologia
<sec-metodologia>

== Ambiente e modelo de custo
<sec-ambiente>

O ambiente de simulação consiste em uma grade ortogonal de $90 times 90$ células. Na semente do grupo (SEMENTE = 0), o ponto de origem (navio) situa-se nas coordenadas $(45, 10)$ e o destino (tesouro) em $(45, 82)$. O movimento do agente ocorre em vizinhança 8-conectada (passos ortogonais com comprimento $L(a,b) = 1$ e passos diagonais com $L(a,b) = sqrt(2)$). Células compostas por mar ou lago são estritamente intransitáveis. Além disso, transições entre células vizinhas cuja diferença de elevação $|e(b) - e(a)|$ supere o limite de inclinação $0{,}12$ são classificadas como penhascos e bloqueadas na função de vizinhança.

Cada célula possui um fator de terreno $\phi(b)$ que pondera o atrito do deslocamento, conforme especificado na @tab-terrenos.

#figure(
  kind: table,
  supplement: [Tabela],
  styled-table(
    headers: ("Terreno", [Fator $phi$], "Onde aparece no mapa"),
    rows: (
      ([Campo], [$1{,}0$], [Zonas planas centrais e encostas amenas]),
      ([Praia], [$1{,}2$], [Faixa costeira ao redor da ilha]),
      ([Rocha vulcânica], [$1{,}3$], [Cone e arredores do vulcão central]),
      ([Floresta], [$1{,}5$], [Manchas de vegetação ao sul e oeste]),
      ([Pântano], [$5{,}0$], [Região alagadiça ao sul do vulcão]),
      ([Mar e lago], [Intransitável], [Oceano ao redor e lago ao norte]),
    ),
    col-widths: (1fr, 0.7fr, 3fr),
    align: (left, center, left),
  ),
  caption: [Tipos de terreno do mapa e seus respectivos fatores de custo.],
) <tab-terrenos>

O custo de transição $c(a, b)$ de uma célula $a$ para uma vizinha $b$ é governado pela @eq-custo:

#formula[$ c(a, b) = L(a, b) dot (1 + 60 s + 10 d) dot phi(b) $ <eq-custo>]

em que $s = max(0, e(b) - e(a))$ representa a subida, $d = max(0, e(a) - e(b))$ denota a descida, $e(n) in [0, 1]$ é a elevação normalizada da célula $n$, e $\phi(b)$ é o fator de terreno da célula destino $b$. A heurística euclidiana $h(n)$ é calculada pela distância em linha reta até o destino $t = (y_t, x_t)$, como indica a @eq-euclidiana:

#formula[$ h(n) = sqrt((x_n - x_t)^2 + (y_n - y_t)^2) $ <eq-euclidiana>]

== Implementação
<sec-implementacao>

A função `busca_greedy()` foi implementada no arquivo `buscas.py` adaptando a estrutura de `a_estrela()`. A ordenação da fila de prioridades (`heapq`) é guiada exclusivamente pela heurística $h(n)$, utilizando um contador sequencial para desempate por ordem de inserção. Diferente do A\*, que pode atualizar o predecessor de um nó na fronteira caso um caminho de menor $g(n)$ seja descoberto, a busca _greedy_ define o predecessor `veio_de[prox]` estritamente na primeira vez em que a célula é descoberta.

```python
# Trecho central da função busca_greedy() em buscas.py
while fronteira:
    _, _, atual = heapq.heappop(fronteira)
    if atual in fechados:
        continue
    em_aberto.discard(atual)
    fechados.add(atual)
    historico_passos.registrar(atual, em_aberto, fechados)
    if atual == destino:
        break
    for prox in vizinhos_fn(atual, altura, largura):
        if prox not in veio_de and prox not in fechados:
            veio_de[prox] = atual
            contador += 1
            heapq.heappush(fronteira, (heuristica_fn(prox, destino), contador, prox))
            em_aberto.add(prox)
```

A correção da implementação foi validada através do script `testes_buscas.py`, no qual **31 testes passaram com sucesso e 0 falharam**.

== Experimentos
<sec-experimentos>

Os experimentos foram conduzidos na semente 0 do mapa da ilha ($90 times 90$). Avaliaram-se as seguintes métricas: número de passos do caminho, custo total acumulado, total de nós expandidos, tempo de execução sem geração de animação (medido em milissegundos via `main_comparacao.py`), contagem de células de pântano no caminho, células expandidas no interior da cratera e a decomposição do custo em três parcelas (comprimento, elevação e terreno). O ambiente de execução utilizado consistiu em um sistema Microsoft Windows 11, processador x86_64, executando Python 3.14.6 com as bibliotecas NumPy, SciPy, Matplotlib e Pillow.

= Resultados
<sec-resultados>

== Comparação dos algoritmos
<sec-res-comparacao>

A @tab-comparacao apresenta o desempenho geral dos três algoritmos na Ilha do Tesouro (semente 0). A @tab-decomposicao detalha a decomposição do custo total dos caminhos encontrados. A @fig-caminhos ilustra espacialmente as trajetórias resultantes sobre o mapa da ilha.

#figure(
  kind: table,
  supplement: [Tabela],
  styled-table(
    headers: ("Algoritmo", "Passos", "Custo", "Expandidos", "Tempo (ms)", "Pântano", "Cratera"),
    rows: (
      ([UCS], [97], [140,8], [3069], [118,5], [0], [185]),
      ([_Greedy_ (euclidiana)], [76], [312,3], [304], [5,0], [11], [185]),
      ([A\* (euclidiana)], [97], [140,8], [2437], [111,2], [0], [185]),
    ),
    col-widths: (1.8fr, 0.9fr, 0.9fr, 1.1fr, 1.1fr, 0.9fr, 0.9fr),
    align: (left, right, right, right, right, right, right),
  ),
  caption: [Resultados dos três algoritmos para a semente 0. Pântano: células de pântano no caminho final; Cratera: células do interior da cratera expandidas durante a busca.],
) <tab-comparacao>

#figure(
  kind: table,
  supplement: [Tabela],
  styled-table(
    headers: ("Algoritmo", "Comprimento", "Elevação", "Terreno", "Total"),
    rows: (
      ([UCS], [114,0], [15,8], [11,0], [140,8]),
      ([_Greedy_ (euclidiana)], [82,6], [81,7], [148,0], [312,3]),
      ([A\* (euclidiana)], [114,0], [15,8], [11,0], [140,8]),
    ),
    col-widths: (1.8fr, 1fr, 1fr, 1fr, 1fr),
    align: (left, right, right, right, right),
  ),
  caption: [Decomposição do custo do caminho encontrado por cada algoritmo.],
) <tab-decomposicao>

#figure(placement: auto, imagem("comparacao.png", 1188 / 440), caption: [Caminhos encontrados pelos algoritmos UCS, Busca Greedy e A* na Ilha do Tesouro (semente 0).]) <fig-caminhos>

== Animações das buscas
<sec-res-animacoes>

A @fig-quadros exibe quadros intermediários (extraídos na fração $1/3$ do total de expansões) e quadros finais registrados durante a execução das animações dos três algoritmos.

#figure(
  placement: auto,
  grid(
    columns: 3,
    column-gutter: 6pt,
    row-gutter: 6pt,
    quadro("quadro_ucs_intermediario.png", [UCS, intermediário]),
    quadro("quadro_greedy_intermediario.png", [_Greedy_, intermediário]),
    quadro("quadro_astar_intermediario.png", [A\*, intermediário]),
    quadro("quadro_ucs_final.png", [UCS, final]),
    quadro("quadro_greedy_final.png", [_Greedy_, final]),
    quadro("quadro_astar_final.png", [A\*, final]),
  ),
  caption: [Quadros das animações das buscas: intermediários (fração 1/3 das expansões) e finais.],
) <fig-quadros>

= Análise
<sec-analise>

== Ordenação da fila e forma da fronteira (questão 3)
<sec-q3>

A análise das animações na @fig-quadros revela a influência direta do critério de ordenação da fila na geometria da fronteira de busca. No UCS ($f = g$), a fronteira expande-se em contornos concêntricos de equicusto em torno da origem. Por ignorar a direção do destino, o UCS consome tempo expandindo regiões a oeste da origem antes de avançar para leste, formando uma área explorada larga e circular.

Na busca _greedy_ ($f = h$), a ordenação orienta a fronteira de forma diretiva e estreita em linha reta em direção ao destino. Como $h(n)$ diminui à medida que o nó aproxima-se de $(45, 82)$, a busca avança velozmente para leste, assumindo formato pontiagudo ou oval alongado.

No algoritmo A\* ($f = g + h$), a combinação das parcelas gera uma fronteira elíptica focada, cujos focos situam-se na origem e no destino. A parcela $h(n)$ restringe a expansão para trás (oeste), enquanto $g(n)$ impede o avanço descontrolado por áreas de elevado atrito topográfico.

== UCS × A\* (questão 4)
<sec-q4>

Conforme a @tab-comparacao, o UCS e o A\* encontraram trajetórias idênticas com o custo ótimo de $140{,}8$ e $97$ passos. No entanto, o A\* expandiu apenas $2437$ nós, contra $3069$ do UCS — uma redução de $20{,}6\%$ no volume de busca ($632$ nós a menos), refletindo-se na redução do tempo de execução de $118{,}5\text{ ms}$ para $111{,}2\text{ ms}$.

A diferença espacial de expansão situa-se predominantemente na porção ocidental do mapa (praia e oceano a oeste da origem $(45, 10)$). Enquanto o UCS expande extensivamente nós atrás do navio por terem baixo custo acumulado $g(n)$, a heurística $h(n)$ do A\* atribui a esses nós valores elevados de $f(n)$, suprimindo sua exploração. A economia de nó não foi maior porque o cone vulcânico central atua como um grande obstáculo topográfico, forçando tanto o UCS quanto o A\* a explorarem integralmente o interior da cratera até localizarem a brecha no paredão norte.

== _Greedy_ na cratera (questão 5)
<sec-q5>

A busca _greedy_ concentra $185$ de suas $304$ expansões no interior da cratera vulcânica. Esse fenômeno ocorre porque a cratera intercepta geograficamente o segmento de reta entre a origem $(45, 10)$ e o destino $(45, 82)$. Guiada puramente pela distância euclidiana, a busca _greedy_ escolhe entrar na cratera devido aos valores decrescentes de $h(n)$, ficando retida contra o paredão interno leste, de inclinação superior a $0{,}12$ (penhasco).

Notavelmente, a coluna Cratera da @tab-comparacao mostra que **todos os três algoritmos expandiram exatamente 185 nós dentro da cratera**. Contudo, enquanto o UCS e o A\* utilizam $g(n)$ para computar as penalidades de subida ($60s$) e descida ($10d$) e retrocedem ao detectar que a rota da cratera é extremamente dispendiosa, a busca _greedy_ ignora o custo acumulado. Ao encontrar a brecha norte, a busca _greedy_ despenca encosta abaixo e cruza o pântano ao sul, resultando em um custo final de $312{,}3$ ($121{,}8\%$ superior ao ótimo de $140{,}8$). O papel do $g(n)$ é justamente fornecer a memória de custo real percorrido, impedindo que o algoritmo aceite subidas e pântanos proibitivos em troca de progresso geométrico ilusório.

== _Greedy_ no pântano (questão 6)
<sec-q6>

A @tab-decomposicao evidencia a discrepância estrutural entre os caminhos. A busca _greedy_ obteve o menor comprimento geométrico ($82{,}6$ unidades contra $114{,}0$ do A\*), porém incorreu em custos devastadores de elevação ($81{,}7$ vs $15{,}8$) e terreno ($148{,}0$ vs $11{,}0$).

O caminho da busca _greedy_ atravessa $11$ células de pântano (cujo fator de atrito é $\phi = 5{,}0$). Como o pântano situa-se diretamente no eixo horizontal em direção ao tesouro, a busca _greedy_ entra nele sem hesitação, pois $h(n)$ ignora o fator do terreno. Em contrapartida, o UCS e o A\* contornam o pântano pelo norte através de zonas de campo ($\phi = 1{,}0$), pois a parcela $g(n)$ contabiliza o multiplicador de atrito. Este experimento demonstra conclusivamente que **o caminho geometricamente mais curto não é o mais barato em termos de custo acumulado**.

== Admissibilidade da heurística euclidiana (questão 7)
<sec-q7>

Para demonstrar que a heurística euclidiana é admissível para o modelo de custo da @eq-custo, analisa-se o custo de transição entre quaisquer duas células vizinhas $a$ e $b$:

#formula[$ c(a, b) = L(a, b) dot (1 + 60 s + 10 d) dot phi(b) $ <eq-demo-1>]

Por definição do modelo, as variáveis de elevação satisfazem $s = max(0, e(b) - e(a)) >= 0$ e $d = max(0, e(a) - e(b)) >= 0$. Logo, o fator entre parênteses cumpre $(1 + 60s + 10d) >= 1$. Da mesma forma, a @tab-terrenos estabelece que o menor fator de terreno para células transitáveis é $\phi(b) >= 1{,}0$ (campo). Substituindo essas desigualdades na @eq-demo-1, obtém-se:

#formula[$ c(a, b) >= L(a, b) dot (1) dot (1{,}0) = L(a, b) $ <eq-demo-2>]

Considere agora qualquer caminho válido $P = (n_0, n_1, dots, n_k)$ conectando uma célula $n = n_0$ ao destino $t = n_k$. O custo total do caminho é a soma dos custos de cada aresta:

#formula[$ "custo"(P) = sum_(i=0)^(k-1) c(n_i, n_(i+1)) >= sum_(i=0)^(k-1) L(n_i, n_(i+1)) $ <eq-demo-3>]

Pela desigualdade triangular no espaço euclidiano $RR^2$, a soma dos comprimentos dos segmentos de qualquer trajetória descontínua ou contínua entre dois pontos é sempre maior ou igual à distância em linha reta $h_{\text{euclidiana}}(n, t)$:

#formula[$ sum_(i=0)^(k-1) L(n_i, n_(i+1)) >= D_{\text{euclidiana}}(n, t) = h(n, t) $ <eq-demo-4>]

Como o custo ótimo $c^*(n, t)$ é o mínimo sobre todos os caminhos válidos, conclui-se formalmente que:

#formula[$ h(n, t) <= c^*(n, t) quad forall n $ <eq-demo-5>]

A consequência prática direta da admissibilidade de $h(n)$ nos experimentos do grupo é a **garantia teórica de que o algoritmo A\* encontra o caminho de custo mínimo absoluto ($140{,}8$)**, igualando o resultado do UCS enquanto economiza $20{,}6\%$ em expansões de nós.

= Conclusão
<sec-conclusao>

O objetivo de implementar, comparar e analisar os algoritmos UCS, Busca _Greedy_ e A\* no cenário da Ilha do Tesouro foi integralmente alcançado. Os resultados experimentais confirmaram perfeitamente a teoria dos algoritmos de busca em grafos:

1. A busca _greedy_ é extremamente rápida ($5{,}0\text{ ms}$ e $304$ expansões), contudo produz rotas subótimas (custo $312{,}3$) por ignorar os custos de terreno e relevo $g(n)$.
2. O UCS garante a otimalidade do caminho ($140{,}8$), mas sofre com a exploração desorientada de $3069$ nós por carecer de informação heurística.
3. O algoritmo A\* combina o melhor de ambos os paradigmas, encontrando o caminho ótimo ($140{,}8$) ao mesmo tempo em que reduz o espaço de busca para $2437$ nós devido à admissibilidade da heurística euclidiana.

Como trabalhos futuros, sugere-se a avaliação de heurísticas ponderadas ($w \cdot h(n)$ com $w > 1$) para trade-offs entre tempo e custo, bem como a incorporação de suavização de trajetória post-processing no mapa.

#bibliography("referencias.bib", style: "associacao-brasileira-de-normas-tecnicas", title: [Referências])
