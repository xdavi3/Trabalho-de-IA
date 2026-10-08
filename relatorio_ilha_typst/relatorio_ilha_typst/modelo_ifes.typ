// Visual do IFES para o relatório: capa, sumário, cabeçalho, rodapé, títulos, blocos de código, caixas de destaque, fórmulas, tabelas e figuras provisórias. Não é preciso editar este arquivo.

// Cores derivadas do verde institucional do IFES.
#let _primaria = rgb("#006b52")
#let _cores = (
  primaria: _primaria,
  secundaria: _primaria.darken(10%),
  link: _primaria.darken(25%),
  discreta: _primaria.desaturate(60%).darken(20%),
  linha: _primaria.lighten(60%),
  fundo: _primaria.lighten(92%),
  numero-codigo: _primaria.lighten(40%),
  zebra: _primaria.lighten(96%),
  tabela-impar: _primaria.lighten(88%),
  tabela-par: _primaria.lighten(94%),
)

// Converte conteúdo em texto simples (cabeçalho e metadados do PDF).
#let _texto(it) = {
  if it == none { return "" }
  if type(it) == str { return it }
  if type(it) != content { return str(it) }
  if it.has("text") { return _texto(it.text) }
  if it.has("children") { return it.children.map(_texto).sum(default: "") }
  if it.has("body") { return _texto(it.body) }
  if it.has("child") { return _texto(it.child) }
  " "
}

// Trunca o texto em n caracteres, com reticências.
#let _truncar(texto, n) = {
  let g = texto.trim().clusters()
  if g.len() <= n { texto.trim() } else { g.slice(0, n).join().trim() + "…" }
}

#let _capa(title, subtitle, autores, cover-authors, professor, course, affiliation, date) = page(header: none, footer: none, {
  set align(center)
  image("logo_ifes.png", width: 5cm, alt: "Logotipo do Instituto Federal do Espírito Santo, Campus Serra")
  v(1fr)
  if course != none {
    text(size: 14pt, weight: "semibold", fill: _cores.secundaria, upper(course))
    v(1cm)
  }
  block(width: 90%, fill: _cores.primaria, radius: 8pt, inset: (x: 20pt, y: 15pt), {
    set par(justify: false)
    text(size: 20pt, weight: "bold", fill: white, hyphenate: false, title)
  })
  if subtitle != none {
    v(1cm)
    text(size: 18pt, weight: "bold", fill: _cores.primaria, subtitle)
  }
  v(1cm)
  line(length: 60%, stroke: 1.5pt + _cores.primaria)
  v(1fr)
  {
    set text(size: if cover-authors == none { 16pt } else { 14pt }, weight: "bold", fill: _cores.secundaria)
    if cover-authors != none { cover-authors } else { autores.join(linebreak()) }
  }
  if professor != none {
    v(1cm)
    text(size: 14pt, fill: _cores.secundaria)[Professor(a): #professor]
  }
  v(1fr)
  text(size: 13pt, fill: _cores.secundaria)[#affiliation | #date]
})

#let _rodape(padrao) = context align(center, text(size: 9pt, fill: _cores.discreta, counter(page).display(padrao, both: padrao.contains("/"))))

#let _cabecalho(title, course, autores) = {
  set text(size: 8pt, fill: _cores.discreta)
  let esquerda = if course != none { _texto(course) + " | " + _texto(title) } else { _texto(title) }
  grid(columns: (2fr, 1fr), column-gutter: 1em, align: (left, right), _truncar(esquerda, 70), autores.join(", "))
  v(-0.5em)
  line(length: 100%, stroke: 0.4pt + _cores.linha)
}

// Blocos de código com moldura, numeração de linhas, faixas alternadas e o nome da linguagem.
#let _linguagens = (python: "Python", py: "Python", sh: "Shell", bash: "Bash", typ: "Typst", typst: "Typst")

#let _bloco-codigo(it) = {
  let nome = if it.lang != none { _linguagens.at(lower(it.lang), default: it.lang) }
  let selo = if nome != none { box(fill: _cores.fundo, inset: (x: 0.4em, y: 0.2em), radius: 3pt, stroke: 0.4pt + _cores.linha, text(size: 7pt, fill: _cores.numero-codigo, nome)) }
  let reserva = if selo != none { measure(selo).width + 0.8em } else { 0pt }
  let celulas = it.lines.enumerate().map(((i, l)) => {
    let fundo = if calc.even(i) { _cores.zebra } else { none }
    let corpo = [#l.body#sym.zws]
    if i == 0 and selo != none { corpo = [#corpo#place(top + right, dx: reserva + 0.2em, dy: -0.1em, pdf.artifact(selo))] }
    let numero = pdf.artifact(text(size: 8pt, fill: _cores.numero-codigo, str(l.number)))
    (
      grid.cell(fill: fundo, inset: (left: 0.6em, right: 0.3em, y: 0.22em), align: right + horizon, numero),
      grid.cell(fill: fundo, inset: (left: 0.6em, right: 0.6em + if i == 0 { reserva } else { 0pt }, y: 0.22em), corpo),
    )
  }).flatten()
  block(width: 100%, breakable: true, fill: _cores.fundo, stroke: 0.5pt + _cores.linha, radius: 5pt, clip: true, inset: (y: 0.3em), {
    set align(left)
    grid(columns: (auto, 1fr), ..celulas)
  })
}

/// Layout do relatório: capa, sumário (páginas em algarismos romanos) e corpo com a numeração "página / total" recomeçando em 1.
#let report(
  title: "Título",
  subtitle: none,
  author: (),
  cover-authors: none,
  professor: none,
  course: none,
  affiliation: "IFES — Campus Serra",
  date: datetime.today().display("[day]/[month]/[year]"),
  body,
) = {
  let autores = (if type(author) == array { author } else { (author,) }).map(_texto)

  set document(title: _texto(title), author: autores)
  set page(paper: "a4", margin: 2.5cm, header: _cabecalho(title, course, autores), footer: _rodape("1 / 1"))
  set text(font: "Libertinus Serif", size: 12pt, lang: "pt", region: "BR")
  set par(justify: true, leading: 0.85em, spacing: 1em)
  set math.equation(numbering: "(1)")
  set enum(indent: 2em, body-indent: 0.8em, spacing: 0.9em)
  set list(indent: 2em, body-indent: 0.8em, spacing: 0.9em)

  set heading(numbering: "1.1.1.")
  show heading: set block(above: 1.4em, below: 0.8em, sticky: true)
  show heading: it => {
    let tamanho = 15pt * calc.pow(0.95, it.level - 1)
    if it.level == 1 {
      block(width: 100%, above: 1.6em, below: 1.2em, sticky: true, fill: _cores.primaria, radius: 6pt, inset: (x: 14pt, y: 10pt), text(size: tamanho, weight: "bold", fill: white, it))
    } else {
      set text(size: tamanho, weight: "semibold", fill: _cores.primaria)
      it
    }
  }

  show link: set text(fill: _cores.link)
  show cite: set text(fill: _cores.link)
  show table: set text(size: 11pt)
  show table.cell.where(y: 0): set text(weight: "bold")
  show raw.where(block: true): set text(size: 9pt)
  show raw.where(block: true): _bloco-codigo
  show raw.where(block: false): box.with(fill: _cores.fundo, inset: (x: 3pt), outset: (y: 3pt), radius: 2pt)

  _capa(title, subtitle, autores, cover-authors, professor, course, affiliation, date)

  {
    set page(footer: _rodape("i"))
    counter(page).update(1)
    show outline.entry.where(level: 1): set text(weight: "bold")
    outline(title: block(width: 100%, align(center, "Sumário")), indent: 1.5em, depth: 2)
    pagebreak(weak: true)
  }

  counter(page).update(1)
  body
}

// Caixa de destaque com faixa lateral colorida e título em negrito.
#let _caixa(cor, rotulo, body, title: none) = block(
  width: 100%,
  breakable: true,
  fill: cor.lighten(88%),
  stroke: (left: 4pt + cor),
  radius: (right: 5pt),
  inset: (left: 12pt, right: 10pt, y: 8pt),
)[
  #text(weight: "bold", fill: cor.darken(20%), if title == none { rotulo } else { title }) \
  #body
]

#let box-info = _caixa.with(rgb("#2980b9"), "Informação")
#let box-tip = _caixa.with(rgb("#27ae60"), "Dica")
#let box-warning = _caixa.with(rgb("#d68910"), "Atenção")
#let box-danger = _caixa.with(rgb("#c0392b"), "Cuidado")

/// Equação em destaque, em um bloco com fundo claro; a numeração e o rótulo da equação são preservados.
#let formula(body) = block(width: 100%, fill: _cores.fundo, stroke: 0.4pt + _cores.linha, radius: 5pt, inset: (x: 16pt, y: 10pt))[
  #set text(fill: _cores.primaria.darken(20%))
  #align(center, body)
]

/// Tabela com cabeçalho verde e linhas alternadas. Para numerá-la e legendá-la, envolva-a em `figure(kind: table, ...)`.
#let styled-table(headers: (), rows: (), col-widths: auto, align: left, header-size: 10pt, cell-size: 9.5pt, row-inset: (x: 8pt, y: 7pt)) = {
  let n = headers.len()
  let celulas = rows.flatten()
  assert(n > 0 and calc.rem(celulas.len(), n) == 0, message: "styled-table: cada linha deve ter uma célula por coluna do cabeçalho")
  let larguras = if col-widths == auto { (1fr,) * n } else { col-widths }
  let alinhamentos = if type(align) == array { align } else { (align,) * n }
  set par(justify: false, first-line-indent: 0em)
  table(
    columns: larguras,
    stroke: 0.5pt + _cores.linha,
    inset: row-inset,
    fill: (_, y) => if y == 0 { _cores.primaria } else if calc.odd(y) { _cores.tabela-impar } else { _cores.tabela-par },
    table.header(..headers.map(h => table.cell(align: center, text(weight: "bold", fill: white, size: header-size, h)))),
    ..celulas.enumerate().map(((i, c)) => table.cell(align: alinhamentos.at(calc.rem(i, n)), text(size: cell-size, c))),
  )
}

/// Retângulo que ocupa o lugar de uma figura ainda não gerada, com a proporção largura/altura indicada.
#let figura-provisoria(arquivo, proporcao) = layout(tamanho => block(
  width: tamanho.width,
  height: tamanho.width / proporcao,
  fill: _cores.fundo,
  stroke: (paint: _cores.linha, thickness: 1pt, dash: "dashed"),
  radius: 4pt,
  align(center + horizon, text(size: 9pt, fill: _cores.discreta)[Figura provisória \ #raw(arquivo)]),
))
