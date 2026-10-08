"""
Visualização: anima a expansão de uma busca sobre o mapa e desenha figuras estáticas comparando caminhos.

Não sabe qual algoritmo gerou os dados; só espera:
    historico_passos: lista de (no_expandido, snapshot_aberto, snapshot_fechado), gerada com snapshots=True; entradas com snapshots None são ignoradas
    caminho: lista de posições (linha, coluna) da origem ao destino

As figuras são sempre salvas em arquivo (GIF ou PNG), funcionando também em máquinas sem interface gráfica.

O fundo é uma imagem RGB (altura x largura x 3), como a produzida por ilha.renderizar_mapa() e guardada em Cenario.fundo.
"""

import numpy as np
import matplotlib.animation as animation
import matplotlib.pyplot as plt

_COR_FECHADO = (0.50, 0.15, 0.75, 0.55)  # RGBA dos nós fechados
_COR_ABERTO = (1.00, 0.72, 0.01, 0.85)  # RGBA dos nós abertos


def _desenhar_fundo(ax, fundo):
    ax.imshow(fundo, origin="upper")
    ax.set_xticks([])
    ax.set_yticks([])


def _marcar_extremos(ax, origem, destino):
    ax.scatter([origem[1]], [origem[0]], c="lime", s=70, marker="o", edgecolors="black", label="Origem", zorder=6)
    ax.scatter([destino[1]], [destino[0]], c="red", s=140, marker="*", edgecolors="black", label="Destino", zorder=6)


def animar(fundo, caminho, historico_passos, origem, destino, arquivo_saida, passo=None,
           max_frames_expansao=200, max_frames_caminho=40, titulo="Busca sobre o terreno"):
    """Salva em arquivo_saida (GIF) a animação da expansão da busca seguida do traçado do caminho final.

    A fase de expansão usa as entradas do histórico que têm snapshot, no máximo cerca de max_frames_expansao quadros (ou um quadro a cada `passo` entradas com snapshot, se informado) e o traçado do caminho usa no máximo max_frames_caminho quadros, independentemente do tamanho da grade e do comprimento do caminho. Os nós fechados e abertos são pintados em uma camada semitransparente sobre o fundo.
    """
    com_snapshot = [i for i, entrada in enumerate(historico_passos) if entrada[1] is not None]
    if historico_passos and not com_snapshot:
        raise ValueError("o histórico foi gerado com snapshots=False; execute a busca com snapshots=True para animar")

    if passo is None:
        passo = max(1, -(-len(com_snapshot) // max_frames_expansao))  # divisão arredondada para cima

    fig, ax = plt.subplots(figsize=(5.5, 6.2))
    _desenhar_fundo(ax, fundo)
    ax.set_title(titulo, fontsize=9)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.94, bottom=0.10)

    altura, largura = fundo.shape[:2]
    camada = np.zeros((altura, largura, 4))
    imagem_camada = ax.imshow(camada, origin="upper", interpolation="nearest")
    linha_caminho, = ax.plot([], [], c="#e63946", linewidth=2.5, label="Caminho final")
    ax.scatter([], [], s=25, marker="s", c=[_COR_FECHADO[:3]], label="Fechado (expandido)")
    ax.scatter([], [], s=25, marker="s", c=[_COR_ABERTO[:3]], label="Aberto (fronteira)")
    _marcar_extremos(ax, origem, destino)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.01), ncol=3, fontsize=7, framealpha=0.9)

    indices_passos = com_snapshot[::passo]
    if com_snapshot and indices_passos[-1] != com_snapshot[-1]:
        indices_passos.append(com_snapshot[-1])

    if caminho:
        n_frames_caminho = min(len(caminho), max_frames_caminho)
        cortes_caminho = np.linspace(1, len(caminho), n_frames_caminho).round().astype(int)
    else:
        cortes_caminho = np.array([], dtype=int)
    frames_finais = 10  # mantêm o caminho completo visível no fim do GIF
    total_frames = len(indices_passos) + len(cortes_caminho) + frames_finais

    def pintar(celulas, cor):
        if celulas:
            linhas, colunas = zip(*celulas)
            camada[list(linhas), list(colunas)] = cor

    def atualizar(frame):
        if frame < len(indices_passos):
            _, em_aberto, fechados = historico_passos[indices_passos[frame]]
            camada[:] = 0.0
            pintar(fechados, _COR_FECHADO)
            pintar(em_aberto, _COR_ABERTO)
            imagem_camada.set_data(camada)
        else:
            k = min(frame - len(indices_passos), len(cortes_caminho) - 1)
            if k >= 0:
                trecho = caminho[:cortes_caminho[k]]
                linha_caminho.set_data([p[1] for p in trecho], [p[0] for p in trecho])
        return imagem_camada, linha_caminho

    anim = animation.FuncAnimation(fig, atualizar, frames=total_frames, interval=80, blit=False, repeat=False)
    anim.save(arquivo_saida, writer=animation.PillowWriter(fps=15), dpi=80)
    plt.close(fig)


def desenhar_caminhos(fundo, caminhos, origem, destino, arquivo_saida, titulo="Comparação de caminhos", colunas=3):
    """Salva em arquivo_saida (PNG) uma figura com um painel por caminho, todos sobre o mesmo mapa. caminhos é um dicionário {rótulo: caminho}; o rótulo é usado como título do painel e pode ter mais de uma linha. Caminhos vazios geram um painel com a indicação "sem caminho"."""
    n = max(1, len(caminhos))
    colunas = min(colunas, n)
    linhas = int(np.ceil(n / colunas))
    fig, eixos = plt.subplots(linhas, colunas, figsize=(3.6 * colunas, 4.0 * linhas), squeeze=False, layout="constrained")

    for ax, (rotulo, caminho) in zip(eixos.flat, caminhos.items()):
        _desenhar_fundo(ax, fundo)
        ax.set_title(rotulo, fontsize=9)
        if caminho:
            ax.plot([p[1] for p in caminho], [p[0] for p in caminho], color="#e63946", linewidth=1.8)
        else:
            ax.text(0.5, 0.5, "sem caminho", transform=ax.transAxes, ha="center", va="center", fontsize=10,
                    bbox={"facecolor": "white", "alpha": 0.8})
        ax.scatter([origem[1]], [origem[0]], c="lime", s=35, marker="o", edgecolors="black", zorder=6)
        ax.scatter([destino[1]], [destino[0]], c="red", s=70, marker="*", edgecolors="black", zorder=6)

    for ax in list(eixos.flat)[len(caminhos):]:
        ax.axis("off")

    fig.suptitle(titulo, fontsize=12)
    fig.savefig(arquivo_saida, dpi=110)
    plt.close(fig)
