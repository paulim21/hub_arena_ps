"""Embute o sprite de ícones em cada HTML do frontend.

O `<use href="arquivo.svg#id">` externo não funciona no Chrome, então a
cópia que o navegador usa precisa estar na própria página. A FONTE
continua sendo um arquivo só — `frontend/img/icones.svg` —, e este
script copia dali para dentro de cada HTML, entre os marcadores:

    <!-- sprite:inicio -->  ...  <!-- sprite:fim -->

Rode depois de mexer no sprite:

    python .claude/skills/design/embutir-icones.py

Sai com 1 se algum HTML não tiver os marcadores.
"""
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", "..", ".."))
FRONT = os.path.join(RAIZ, "frontend")
FONTE = os.path.join(FRONT, "img", "icones.svg")

INICIO = "<!-- sprite:inicio -->"
FIM = "<!-- sprite:fim -->"


def ler(caminho):
    with open(caminho, encoding="utf-8") as f:
        return f.read()


bruto = ler(FONTE)

# Só os <symbol>: o comentário de cabeçalho do arquivo-fonte explica a
# regra de desenho para quem edita, e não precisa viajar para o HTML.
simbolos = re.findall(r"<symbol\b.*?</symbol>", bruto, re.S)
if not simbolos:
    print("FALHA: nenhum <symbol> encontrado em frontend/img/icones.svg")
    sys.exit(1)

sprite = ('<svg class="sprite" aria-hidden="true" xmlns="http://www.w3.org/2000/svg">'
          + "".join(simbolos) + "</svg>")

print(f"{len(simbolos)} ícones lidos de frontend/img/icones.svg\n")

falhou = False
for arquivo in sorted(os.listdir(FRONT)):
    if not arquivo.endswith(".html"):
        continue
    caminho = os.path.join(FRONT, arquivo)
    fonte = ler(caminho)
    if INICIO not in fonte or FIM not in fonte:
        print(f"  FALHA {arquivo}: faltam os marcadores do sprite")
        falhou = True
        continue
    novo = re.sub(re.escape(INICIO) + r".*?" + re.escape(FIM),
                  INICIO + sprite + FIM, fonte, flags=re.S)
    if novo != fonte:
        with open(caminho, "w", encoding="utf-8") as f:
            f.write(novo)
        print(f"  ok   {arquivo} (sprite atualizado)")
    else:
        print(f"  ok   {arquivo} (já estava em dia)")

sys.exit(1 if falhou else 0)
