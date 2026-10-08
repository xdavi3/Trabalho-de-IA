#import "modelo_ifes.typ": *

#show: report.with(
  course: "Inteligência Artificial — BSI",
  title: [Relatório do Trabalho 1:\ UCS, A\* e _Greedy_],
  subtitle: [Planejamento da Busca na Ilha do Tesouro],
  // Nomes curtos: aparecem no cabeçalho das páginas e nos metadados do PDF. Em dupla, deixem apenas dois nomes.
  author: ("Aluno(a) 1", "Aluno(a) 2", "Aluno(a) 3"),
  // Nomes completos: aparecem apenas na capa. Em dupla, deixem apenas duas linhas.
  cover-authors: [
    Nome Completo do(a) Aluno(a) 1 — Matrícula \
    Nome Completo do(a) Aluno(a) 2 — Matrícula \
    Nome Completo do(a) Aluno(a) 3 — Matrícula
  ],
  professor: "Dr. Sérgio Nery Simões",
)

// Com false, cada figura aparece como um retângulo provisório. Troque para true depois de gerar a pasta figuras/ com extrair_quadros.py (veja o README.md).
#let figuras-prontas = false
#let imagem(arquivo, proporcao) = if figuras-prontas { image("figuras/" + arquivo, width: 100%) } else { figura-provisoria(arquivo, proporcao) }

// Quadro de uma animação, com uma legenda curta abaixo da imagem.
#let quadro(arquivo, legenda) = figure(imagem(arquivo, 440 / 496), caption: legenda, kind: "quadro", supplement: none, numbering: none, outlined: false)

#heading(numbering: none, outlined: false)[Como usar este modelo]

Este arquivo é um *esqueleto*, não um relatório pronto. Ele traz a estrutura exigida no enunciado, o que cada seção precisa conter e os erros mais comuns. Três tipos de caixa aparecem ao longo do documento:

#box-tip(title: "Instrução")[
  O que vocês devem escrever na seção: o conteúdo, não a forma.
]

#box-warning(title: "Armadilhas comuns")[
  Erros frequentes na seção.
]

#box-info(title: "Dica de Typst")[
  Como fazer algo no Typst: citar, numerar equações, montar tabelas e incluir figuras. O básico: `*negrito*`, `_itálico_`, listas com linhas começando por `-` (marcadores) ou `+` (numeradas), comentários com `//` e asterisco literal com `\*`, como em `A\*`. O `README.md` explica como compilar, gerar as figuras e citar.
]

#box-danger(title: "Antes de entregar")[
  Apaguem esta seção e todas as caixas de instrução, armadilhas e dicas. O relatório tem no máximo 12 páginas, contadas da página 1 (a do Resumo) até a página anterior às Referências: capa, sumário e referências não entram na contagem. Confiram também que `figuras-prontas` está como `true` e que nenhuma figura provisória restou no PDF.
]

#pagebreak(weak: true)

#heading(numbering: none)[Resumo]
<sec-resumo>

#box-tip(title: "Instrução")[
  No máximo 150 palavras, em um único parágrafo, sem citações. Contexto (uma frase), objetivo (uma frase), o que foi feito (uma ou duas frases), principais resultados, com pelo menos dois números (duas frases), e conclusão (uma frase). Escrevam por último, depois que o restante do relatório estiver pronto.
]

#box-warning(title: "Armadilhas comuns")[
  Resumo genérico, sem nenhum número; ultrapassar 150 palavras; resumo escrito no início do trabalho e nunca atualizado.
]

*Palavras-chave:* palavra 1; palavra 2; palavra 3; palavra 4.

= Introdução
<sec-introducao>

#box-tip(title: "Instrução")[
  Três blocos, nesta ordem: (1) o problema: encontrar o caminho do navio até o tesouro em uma ilha com relevo e tipos de terreno diferentes, e por que isso é um problema de busca em grafo com custos; (2) o objetivo do trabalho, em uma frase verificável; (3) um parágrafo curto com a organização do restante do relatório.
]

#box-warning(title: "Armadilhas comuns")[
  Reproduzir o enunciado em vez de apresentar o problema com as próprias palavras; objetivo vago demais para ser retomado na conclusão.
]

= Fundamentos
<sec-fundamentos>

#box-tip(title: "Instrução")[
  Apresentem os três algoritmos como variações da mesma busca com fila de prioridade, que diferem apenas no critério de ordenação da fila: $g(n)$ na busca de custo uniforme, $h(n)$ na busca _greedy_ e $f(n) = g(n) + h(n)$ no A\* (@eq-f). Citem a fonte original ou o livro-texto de cada algoritmo. Definam formalmente heurística admissível e heurística consistente, pois essas definições são usadas na análise. Completem a @tab-fundamentos, exigida no enunciado, e comentem-na no texto.
]

#formula[$ f(n) = g(n) + h(n) $ <eq-f>]

#figure(
  kind: table,
  supplement: [Tabela],
  styled-table(
    headers: ("Algoritmo", "Ordenação da fila", "Completo?", "Ótimo?", "Complexidade de tempo", "Complexidade de espaço"),
    rows: (
      ([UCS], [...], [...], [...], [...], [...]),
      ([_Greedy_], [...], [...], [...], [...], [...]),
      ([A\*], [...], [...], [...], [...], [...]),
    ),
    col-widths: (0.9fr, 1.1fr, 1.4fr, 1.4fr, 1.2fr, 1.2fr),
    align: (left, center, left, left, center, center),
  ),
  caption: [Comparação dos três algoritmos de busca.],
) <tab-fundamentos>

#box-info(title: "Dica de Typst")[
  Para citar, escrevam `@` seguido da chave da obra no arquivo `referencias.bib`: `@hart1968` produz @hart1968. Várias obras de uma vez: `@dijkstra1959 @russell2022`. Para indicar o capítulo, usem colchetes logo depois da chave: `@russell2022[cap. 3]`. A lista de referências no fim do relatório é montada automaticamente, no padrão ABNT, apenas com as obras citadas. Para citar uma obra que não está no arquivo, acrescentem a entrada BibTeX dela em `referencias.bib`.
]

#box-warning(title: "Armadilhas comuns")[
  Definições sem nenhuma citação; confundir admissibilidade com consistência; dizer que um algoritmo é ótimo sem indicar sob quais condições; descrever em detalhe algoritmos que o trabalho não usa.
]

= Metodologia
<sec-metodologia>

== Ambiente e modelo de custo
<sec-ambiente>

#box-tip(title: "Instrução")[
  Descrevam o mapa (grade, semente do grupo, posições do navio e do tesouro e os elementos da ilha), as regras de deslocamento (vizinhança, água e limite de inclinação), os tipos de terreno com o fator $phi$ (@tab-terrenos), o modelo de custo e a heurística euclidiana, com as equações numeradas. A descrição deve permitir que alguém reproduza os experimentos sem ler o enunciado.
]

#box-info(title: "Dica de Typst")[
  Uma equação numerada é escrita entre cifrões com espaços nas pontas e recebe um rótulo logo depois, como a @eq-f: `$ f(n) = g(n) + h(n) $ <eq-f>`. Depois, `@eq-f` produz a referência numerada no texto. Para destacá-la em uma caixa, como no esqueleto, envolvam-na em `#formula[...]`.
]

#figure(
  kind: table,
  supplement: [Tabela],
  styled-table(
    headers: ("Terreno", [Fator $phi$], "Onde aparece no mapa"),
    rows: (
      ([Campo], [...], [...]),
      ([Praia], [...], [...]),
      ([Rocha vulcânica], [...], [...]),
      ([Floresta], [...], [...]),
      ([Pântano], [...], [...]),
      ([Mar e lago], [...], [...]),
    ),
    col-widths: (1fr, 0.7fr, 3fr),
    align: (left, center, left),
  ),
  caption: [Tipos de terreno do mapa.],
) <tab-terrenos>

== Implementação
<sec-implementacao>

#box-tip(title: "Instrução")[
  Expliquem como `busca_greedy()` foi implementada a partir de `a_estrela()`: como a prioridade da fila é calculada, como os empates são desempatados, quando o predecessor de um nó é definido e o que acontece com um nó já descoberto ou já fechado. Incluam apenas o trecho central do código (de 5 a 15 linhas), comentado, e informem o resultado de `testes_buscas.py`. Se usaram o exemplo de $5 times 5$ (`main_exemplo.py`) para conferir a implementação, digam como.
]

```python
# Trecho central de busca_greedy() (de 5 a 15 linhas, comentado).
```

#box-warning(title: "Armadilhas comuns")[
  Colar a função inteira no texto; trecho de código diferente do que foi usado nos experimentos; não informar o resultado dos testes.
]

== Experimentos
<sec-experimentos>

#box-tip(title: "Instrução")[
  Descrevam o que foi executado e onde: a semente do grupo, os algoritmos e a heurística de cada um, as métricas registradas e como cada uma é calculada (passos, custo, nós expandidos, tempo, células de pântano no caminho, células da cratera expandidas e as três parcelas da decomposição do custo) e o ambiente de execução (computador, sistema operacional e versão do Python).
]

#box-warning(title: "Armadilhas comuns")[
  Não informar a semente; usar uma métrica sem defini-la; não dizer como o tempo foi medido.
]

= Resultados
<sec-resultados>

#box-tip(title: "Instrução")[
  Apresentem os resultados da Parte B sem interpretá-los: a interpretação fica na @sec-analise. Toda tabela e toda figura precisa ser citada no texto (por exemplo, "a @tab-comparacao mostra..."), com uma frase que diga o que ela contém.
]

#box-info(title: "Dica de Typst")[
  As tabelas abaixo têm as mesmas colunas das duas tabelas impressas por `main_comparacao.py`. Copiem os valores impressos pelo script e troquem o ponto decimal por vírgula. As figuras aparecem como retângulos provisórios até que `figuras-prontas` seja trocado para `true` no início deste arquivo.
]

== Comparação dos algoritmos
<sec-res-comparacao>

#figure(
  kind: table,
  supplement: [Tabela],
  styled-table(
    headers: ("Algoritmo", "Passos", "Custo", "Expandidos", "Tempo (ms)", "Pântano", "Cratera"),
    rows: (
      ([UCS], [...], [...], [...], [...], [...], [...]),
      ([_Greedy_ (euclidiana)], [...], [...], [...], [...], [...], [...]),
      ([A\* (euclidiana)], [...], [...], [...], [...], [...], [...]),
    ),
    col-widths: (1.8fr, 0.9fr, 0.9fr, 1.1fr, 1.1fr, 0.9fr, 0.9fr),
    align: (left, right, right, right, right, right, right),
  ),
  caption: [Resultados dos três algoritmos com a semente do grupo. Pântano: células de pântano no caminho; Cratera: células do interior da cratera expandidas.],
) <tab-comparacao>

#figure(
  kind: table,
  supplement: [Tabela],
  styled-table(
    headers: ("Algoritmo", "Comprimento", "Elevação", "Terreno", "Total"),
    rows: (
      ([UCS], [...], [...], [...], [...]),
      ([_Greedy_ (euclidiana)], [...], [...], [...], [...]),
      ([A\* (euclidiana)], [...], [...], [...], [...]),
    ),
    col-widths: (1.8fr, 1fr, 1fr, 1fr, 1fr),
    align: (left, right, right, right, right),
  ),
  caption: [Decomposição do custo do caminho encontrado por cada algoritmo.],
) <tab-decomposicao>

#figure(placement: auto, imagem("comparacao.png", 1188 / 440), caption: [Caminhos encontrados pelos três algoritmos.]) <fig-caminhos>

== Animações das buscas
<sec-res-animacoes>

#box-tip(title: "Instrução")[
  Para cada animação pedida na Parte B, um quadro intermediário e o quadro final. Escolham um quadro intermediário que mostre algo relevante sobre a busca e digam no texto em que momento da busca ele foi tirado.
]

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
  caption: [Quadros das animações das três buscas.],
) <fig-quadros>

#box-warning(title: "Armadilhas comuns")[
  Figuras ou tabelas que não são citadas no texto; tabelas incompletas; quadros escolhidos sem critério; interpretar os resultados nesta seção em vez de na análise.
]

= Análise
<sec-analise>

#box-tip(title: "Instrução")[
  Uma subseção para cada questão da Parte C, na ordem do enunciado. Toda resposta deve se apoiar nos números e nas figuras da @sec-resultados, citando-os.
]

== Ordenação da fila e forma da fronteira (questão 3)
<sec-q3>

#box-tip(title: "Instrução")[
  Comparem as animações dos três algoritmos (@fig-quadros) e expliquem como o critério de ordenação da fila determina a forma da fronteira ao longo da busca e a ordem em que as regiões do mapa são expandidas.
]

== UCS × A\* (questão 4)
<sec-q4>

#box-tip(title: "Instrução")[
  Comparem o UCS e o A\* quanto ao custo do caminho e ao número de nós expandidos. Expliquem por que o A\* expande menos nós, em que regiões do mapa está a diferença (comparando os quadros das duas animações) e por que a economia não é maior.
]

== _Greedy_ na cratera (questão 5)
<sec-q5>

#box-tip(title: "Instrução")[
  Digam em que região do mapa a busca _greedy_ concentra as suas expansões e por que a heurística a levou até lá. Usem a coluna Cratera da @tab-comparacao para comparar com o UCS e o A\*. Com base na função de avaliação de cada algoritmo, expliquem por que o A\* chega ao caminho de menor custo e a busca _greedy_ não, e qual é o papel de $g(n)$.
]

== _Greedy_ no pântano (questão 6)
<sec-q6>

#box-tip(title: "Instrução")[
  Comparem os caminhos da busca _greedy_ e do A\* quanto aos terrenos atravessados e à decomposição do custo (@tab-decomposicao). Expliquem por que a busca _greedy_ atravessa o pântano, enquanto o UCS e o A\* o contornam, e respondam se o caminho mais curto é o mais barato.
]

== Admissibilidade da heurística euclidiana (questão 7)
<sec-q7>

#box-tip(title: "Instrução")[
  Demonstrem que a heurística euclidiana é admissível para o modelo de custo da @sec-ambiente, para o caso geral, com as hipóteses usadas explícitas e as equações numeradas. Em seguida, digam que consequência essa propriedade tem para o caminho encontrado pelo A\* nos experimentos do grupo.
]

#box-warning(title: "Armadilhas comuns")[
  Respostas genéricas, que não citam os resultados do grupo; demonstrar para um exemplo numérico em vez do caso geral; afirmar um comportamento que os dados não mostram; deixar de responder uma das perguntas de uma questão.
]

= Conclusão
<sec-conclusao>

#box-tip(title: "Instrução")[
  Retomem o objetivo da introdução e digam se foi atingido, com base nos resultados. Destaquem os dois ou três aprendizados principais sobre os três algoritmos e terminem com uma ou duas sugestões concretas de continuação.
]

#box-warning(title: "Armadilhas comuns")[
  Introduzir na conclusão informação que não foi discutida antes; repetir o resumo.
]

#bibliography("referencias.bib", style: "associacao-brasileira-de-normas-tecnicas", title: [Referências])
