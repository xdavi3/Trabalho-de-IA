# Modelo de relatório — busca na Ilha do Tesouro

Modelo do relatório do trabalho, em Typst. O arquivo `relatorio_ilha.typ` é um esqueleto com a estrutura exigida no enunciado: cada seção traz caixas com o que deve ser escrito, os erros mais comuns e dicas de Typst.

| Arquivo | Conteúdo |
|---|---|
| `relatorio_ilha.typ` | O relatório a preencher. É o único arquivo que vocês editam. |
| `referencias.bib` | As referências bibliográficas, em formato BibTeX. |
| `extrair_quadros.py` | Prepara a pasta `figuras/` a partir dos resultados do pacote da Ilha do Tesouro. |
| `modelo_ifes.typ` e `logo_ifes.png` | O visual do IFES. Não alterem estes arquivos. |

## Como compilar

Usem o Typst 0.15.1 de uma destas formas: no navegador, em typst.app, enviando todos os arquivos desta pasta para um projeto vazio; no VS Code, com a extensão Tinymist (comando "Typst Preview"); ou na linha de comando, com o executável baixado de github.com/typst/typst/releases. Na linha de comando, a partir desta pasta, `typst watch relatorio_ilha.typ` gera `relatorio_ilha.pdf` e o atualiza a cada vez que o arquivo é salvo.

## Passo a passo

1. **Capa.** No início de `relatorio_ilha.typ`, preencham `author` (nomes curtos, usados no cabeçalho) e `cover-authors` (nomes completos e matrículas, usados na capa). Em dupla, deixem apenas dois nomes em cada um.
2. **Figuras.** Com a semente do grupo, executem `main_comparacao.py`, `main_ucs.py`, `main_greedy.py` e `main_astar.py` (os dois últimos com a heurística `euclidiana`). Depois, a partir desta pasta, executem `python3 extrair_quadros.py ../busca_ilha_alunos 7`, trocando o caminho pela pasta do pacote da Ilha do Tesouro e `7` pela semente do grupo. O script cria a pasta `figuras/` com a figura dos caminhos e, de cada animação, um quadro intermediário (a um terço da animação, ajustável em `FRACAO_INTERMEDIARIA`, no início do script) e o quadro final. Em seguida, troquem `#let figuras-prontas = false` por `true` no início de `relatorio_ilha.typ`; enquanto for `false`, cada figura aparece como um retângulo provisório.
3. **Tabelas.** Troquem cada `[...]` das tabelas de resultados pelo valor impresso por `main_comparacao.py`, com vírgula no lugar do ponto decimal. As tabelas de fundamentos e de terrenos são preenchidas pelo grupo.
4. **Texto.** Escrevam cada seção seguindo as caixas e apaguem as caixas à medida que avançarem.

## Citações

Para citar, escrevam `@` seguido da chave da obra: `@hart1968` produz "(Hart; Nilsson; Raphael, 1968)" e `@russell2022[cap. 3]` produz "(Russell; Norvig, 2022, cap. 3)". A lista de referências, no padrão ABNT, é montada automaticamente apenas com as obras citadas. As chaves disponíveis são `russell2022` (livro-texto, 4. ed. brasileira), `dijkstra1959` (artigo original do algoritmo de caminho mínimo), `hart1968` (artigo original do A\*) e `pearl1984` (livro de referência sobre busca heurística). Para citar outra obra, acrescentem a entrada BibTeX dela em `referencias.bib`; toda referência precisa corresponder a uma obra real, que vocês consultaram.

## Antes de entregar

- A seção "Como usar este modelo" e todas as caixas de instrução, armadilhas e dicas foram apagadas.
- `figuras-prontas` está como `true`, e nenhuma figura provisória restou no PDF.
- Nenhuma tabela ainda tem `[...]`, e toda figura e toda tabela é citada no texto.
- O resumo tem no máximo 150 palavras, e o relatório, no máximo 12 páginas, sem contar capa, sumário e referências: a numeração recomeça em 1 depois do sumário, e a página das Referências deve ter número no máximo 13.
- O relatório compila sem erros com o Typst 0.15.1.

Entreguem o PDF e esta pasta (com a pasta `figuras/`), junto com o restante da entrega descrita no enunciado.
