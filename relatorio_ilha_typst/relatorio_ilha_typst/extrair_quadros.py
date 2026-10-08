"""
Prepara a pasta figuras/ do relatório a partir da pasta do pacote da Ilha do Tesouro, depois de executados main_comparacao.py e as três animações da Parte B com a semente do grupo.

Execute a partir desta pasta, informando a pasta do pacote e a semente do grupo:
    python3 extrair_quadros.py CAMINHO_DO_PACOTE SEMENTE

O script copia a figura de main_comparacao.py e salva, de cada animação, um quadro intermediário e o quadro final, com os nomes que relatorio_ilha.typ espera. O quadro intermediário fica na fração FRACAO_INTERMEDIARIA da animação; ajuste a fração de cada animação para mostrar um momento relevante da busca.
"""

import shutil
import sys
from pathlib import Path

from PIL import Image

FIGURA = "comparacao_semente{semente}.png"  # figura de main_comparacao.py, salva como figuras/comparacao.png
ANIMACOES = {  # GIF gerado pelos scripts main_*.py: prefixo dos quadros no relatório
    "ucs_semente{semente}.gif": "quadro_ucs",
    "greedy_euclidiana_semente{semente}.gif": "quadro_greedy",
    "astar_euclidiana_semente{semente}.gif": "quadro_astar",
}
FRACAO_INTERMEDIARIA = {  # posição do quadro intermediário, entre 0 (início) e 1 (fim da animação)
    "quadro_ucs": 1 / 3,
    "quadro_greedy": 1 / 3,
    "quadro_astar": 1 / 3,
}


def salvar_quadro(gif, indice, destino):
    gif.seek(indice)
    gif.convert("RGB").save(destino)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("uso: python3 extrair_quadros.py CAMINHO_DO_PACOTE SEMENTE")
    origem = Path(sys.argv[1])
    semente = int(sys.argv[2])
    destino = Path(__file__).resolve().parent / "figuras"
    destino.mkdir(exist_ok=True)
    figura = FIGURA.format(semente=semente)
    animacoes = {nome.format(semente=semente): prefixo for nome, prefixo in ANIMACOES.items()}
    faltando = [nome for nome in (figura, *animacoes) if not (origem / nome).exists()]
    if faltando:
        raise SystemExit("arquivos não encontrados em " + str(origem) + ": " + ", ".join(faltando))
    shutil.copy(origem / figura, destino / "comparacao.png")
    print(f"copiada: {figura} -> figuras/comparacao.png")
    for nome, prefixo in animacoes.items():
        with Image.open(origem / nome) as gif:
            intermediario = min(gif.n_frames - 1, int(FRACAO_INTERMEDIARIA[prefixo] * gif.n_frames))
            salvar_quadro(gif, intermediario, destino / f"{prefixo}_intermediario.png")
            salvar_quadro(gif, gif.n_frames - 1, destino / f"{prefixo}_final.png")
            print(f"quadros de {nome}: {intermediario + 1} e {gif.n_frames} de {gif.n_frames}")
