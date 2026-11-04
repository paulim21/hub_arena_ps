"""Confere o contrato da identidade visual: o que é medido e o que é proibido.

Irmão dos `verificar_*.py` do backend, mas mora na skill porque não verifica
funcionalidade: verifica **disciplina de identidade**. Cada promessa escrita no
`IDENTIDADE_VISUAL.md` que pode ser medida por máquina é medida aqui, para que
a documentação não vire ficção na primeira cor trocada.

Nove verificações, na ordem em que custam caro quando falham:

1. o contraste de cada par das tabelas do documento, remedido pela fórmula
   WCAG 2.1 e comparado com o número escrito — este é o "contrato";
2. o contraste anotado no comentário do `tokens.css`, o mesmo contrato visto
   do outro lado;
3. a distância de matiz entre sinal de estado e a cor da marca;
4. todo token de cor nasce em `:root` — nenhum tem a única definição dentro
   de um `@media` ou de um `[data-tema]`;
5. os dois blocos escuros definem exatamente o mesmo conjunto de cores;
6. nenhuma cor literal fora do `tokens.css`;
7. todo `font-size` sai da escala de sete degraus, e todo espaçamento sai da
   grade de 4px;
8. nada de gradiente, brilho colorido, vidro fosco, borda de 1px ou emoji;
9. nenhum `var(--x)` aponta para token que não existe, e nenhum estilo é
   escrito por JavaScript (a CSP bloqueia, e falha calada).

Uso:  python docs/design/verificar-identidade.py
Sai com 1 se qualquer verificação falhar.
"""
import os
import re
import sys

# O console do Windows abre em cp1252 e engasga nos acentos deste relatório.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "..", ".."))
CSS = os.path.join(RAIZ, "frontend", "css")
JS = os.path.join(RAIZ, "frontend", "js")
TOKENS = os.path.join(CSS, "tokens.css")
DOCUMENTO = os.path.join(RAIZ, "IDENTIDADE_VISUAL.md")

# Tolerância de arredondamento: o documento escreve duas casas decimais.
TOLERANCIA = 0.02

falhas = []


def titulo(texto):
    print("\n" + "=" * 68)
    print("  " + texto)
    print("=" * 68)


def conferir(nome, condicao, detalhe=""):
    if condicao:
        print(f"  ok   {nome}")
    else:
        print(f"  FALHA{' ' * 1}{nome}" + (f"  ->  {detalhe}" if detalhe else ""))
        falhas.append(nome)


def ler(caminho):
    with open(caminho, encoding="utf-8") as f:
        return f.read()


# ===================================================================
#  A fórmula: luminância relativa e contraste da WCAG 2.1
# ===================================================================
def canal(valor):
    c = valor / 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def luminancia(hexa):
    r, g, b = (int(hexa[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * canal(r) + 0.7152 * canal(g) + 0.0722 * canal(b)


def contraste(a, b):
    la, lb = luminancia(a), luminancia(b)
    claro, escuro = max(la, lb), min(la, lb)
    return (claro + 0.05) / (escuro + 0.05)


def matiz(hexa):
    r, g, b = (int(hexa[i:i + 2], 16) / 255 for i in (1, 3, 5))
    alto, baixo = max(r, g, b), min(r, g, b)
    if alto == baixo:
        return 0.0
    d = alto - baixo
    if alto == r:
        h = ((g - b) / d) % 6
    elif alto == g:
        h = (b - r) / d + 2
    else:
        h = (r - g) / d + 4
    return h * 60


def numero(texto):
    """"13,97:1" e "13.97" viram 13.97."""
    return float(texto.replace(",", ".").replace(":1", "").strip())


# ===================================================================
#  Ler os tokens: tema claro (:root) e os dois blocos escuros
# ===================================================================
fonte_tokens = ler(TOKENS)

# Os três blocos que interessam, recortados por contagem de chaves — regex não
# fecha chave aninhada, e o bloco escuro do @media mora dentro de outro.
#   :root { … }   @media … { :root:not(…) { … } }   :root[data-tema="escuro"] { … }
def bloco(selector):
    i = fonte_tokens.find(selector + " {")
    if i < 0:
        return ""
    i = fonte_tokens.index("{", i)
    nivel, fim = 0, i
    for pos in range(i, len(fonte_tokens)):
        if fonte_tokens[pos] == "{":
            nivel += 1
        elif fonte_tokens[pos] == "}":
            nivel -= 1
            if nivel == 0:
                fim = pos
                break
    return fonte_tokens[i + 1:fim]


corpo_claro = bloco(":root")
corpo_media = bloco(':root:not([data-tema="claro"])')
corpo_botao = bloco(':root[data-tema="escuro"]')


def tokens_de(corpo):
    # O comentário sai ANTES de procurar declaração: o comentário de
    # --marca-fundo cita "--tinta: 12,16:1" em prosa, e sem isto essa citação
    # é lida como se fosse a declaração de --tinta. Custou a primeira execução
    # deste arquivo, com sintoma de "a cor não é #RRGGBB".
    limpo = re.sub(r"/\*.*?\*/", "", corpo, flags=re.S)
    return dict(re.findall(r"--([a-z0-9-]+):\s*([^;]+);", limpo))


claro = tokens_de(corpo_claro)
media = tokens_de(corpo_media)
botao = tokens_de(corpo_botao)

escuro = dict(claro)
escuro.update(media)


def cor(tema, nome):
    valor = (tema.get(nome) or "").split("/*")[0].strip()
    return valor if re.fullmatch(r"#[0-9A-Fa-f]{6}", valor) else None


def translucido(valor):
    """rgba(15, 110, 120, .08) -> (15.0, 110.0, 120.0, 0.08)"""
    m = re.fullmatch(r"rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)"
                     r"(?:[,/\s]+([\d.]*\.?\d+))?\s*\)", valor)
    if not m:
        return None
    a = float(m.group(4)) if m.group(4) else 1.0
    return (float(m.group(1)), float(m.group(2)), float(m.group(3)), a)


def compor(frente, fundo_hex):
    """Compõe um véu translúcido sobre uma superfície sólida.

    É a composição que o olho vê, e é ela que precisa ser medida: a cor de
    origem de um véu de 8% não diz nada sobre o contraste do que fica por
    cima dele."""
    r, g, b, a = frente
    f = [int(fundo_hex[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02X%02X%02X" % tuple(
        round(c * a + f[i] * (1 - a)) for i, c in enumerate((r, g, b)))


def cor_efetiva(tema, nome, sobre="superficie"):
    """A cor sólida que o olho enxerga: o próprio hex, ou o véu já composto."""
    solida = cor(tema, nome)
    if solida:
        return solida
    veu = translucido((tema.get(nome) or "").split("/*")[0].strip())
    if not veu:
        return None
    base = cor(tema, sobre)
    return compor(veu, base) if base else None


# ===================================================================
#  1. As tabelas do documento são o contrato
# ===================================================================
titulo("1. CONTRASTE DAS TABELAS DO IDENTIDADE_VISUAL.MD")

documento = ler(DOCUMENTO)
secao = documento.split("### Tema claro")
if len(secao) < 2:
    conferir("As tabelas de contraste existem no documento", False,
             "não achei '### Tema claro'")
else:
    bruto_claro, resto = secao[1].split("### Tema escuro")
    bruto_escuro = resto.split("### Distância de matiz")[0]

    # O sufixo opcional "na `--superficie-3`" diz sobre qual superfície o véu
    # da marca foi composto antes de medir. Sem ele, a composição é sobre a
    # --superficie, que é onde o véu mora na maioria das vezes.
    linha_par = re.compile(
        r"\|\s*`--([a-z0-9-]+)`\s*/\s*`--([a-z0-9-]+)`"
        r"(?:\s*na\s*`--([a-z0-9-]+)`)?\s*\|\s*\*{0,2}([\d,\.]+):1")

    for rotulo, bruto, tema in (("claro", bruto_claro, claro),
                                ("escuro", bruto_escuro, escuro)):
        pares = linha_par.findall(bruto)
        conferir(f"A tabela do tema {rotulo} tem pares para medir", len(pares) >= 10,
                 f"{len(pares)} pares")
        for frente, fundo, sobre, escrito in pares:
            base = sobre or "superficie"
            onde = f" na --{sobre}" if sobre else ""
            a, b = cor_efetiva(tema, frente, base), cor_efetiva(tema, fundo, base)
            if not a or not b:
                conferir(f"[{rotulo}] --{frente} / --{fundo}: cor legível",
                         False, "não é #RRGGBB nem rgba() componível")
                continue
            medido = contraste(a, b)
            conferir(f"[{rotulo}] --{frente} / --{fundo}{onde} = {escrito}:1",
                     abs(medido - numero(escrito)) <= TOLERANCIA,
                     f"medido {medido:.2f}:1 ({a} sobre {b})")

# ===================================================================
#  2. O mesmo contrato, visto do comentário do tokens.css
# ===================================================================
titulo("2. CONTRASTE ANOTADO NO COMENTÁRIO DO TOKENS.CSS")

# "--tinta: #1F2933; /* texto principal — 13,97:1 no fundo, 14,76:1 na superfície */"
ONDE = {"no fundo": "fundo", "na superfície": "superficie",
        "na superfície-2": "superficie-2", "na superfície-3": "superficie-3",
        "sobre o petróleo claro": "acao", "sobre o petróleo": "acao",
        "sobre a --acao": "acao"}

for rotulo, corpo, tema in (("claro", corpo_claro, claro),
                            ("escuro", corpo_media, escuro)):
    anotados = 0
    # Cada declaração com o seu rastro de comentário, até a próxima declaração:
    # o comentário de --marca continua na linha seguinte, e conta.
    for m in re.finditer(r"--([a-z0-9-]+):\s*(#[0-9A-Fa-f]{6});(.*?)(?=\n\s*--|\Z)",
                         corpo, re.S):
        nome, valor, rastro = m.group(1), m.group(2), m.group(3)
        # A ordem das alternativas é o que faz "na superfície-2" não ser lido
        # como "na superfície": a alternância do Python casa a PRIMEIRA que
        # servir, então a mais longa vem antes. Trocar a ordem aqui faz oito
        # anotações corretas falharem calado, medindo contra a superfície errada.
        for escrito, onde in re.findall(r"([\d,]+):1\s+(no fundo|na superfície-2|"
                                        r"na superfície-3|na superfície|"
                                        r"sobre o petróleo claro|sobre o petróleo|"
                                        r"sobre a --acao)",
                                        rastro):
            alvo = cor(tema, ONDE[onde])
            if not alvo:
                continue
            medido = contraste(valor, alvo)
            anotados += 1
            conferir(f"[{rotulo}] comentário de --{nome}: {escrito}:1 {onde}",
                     abs(medido - numero(escrito)) <= TOLERANCIA,
                     f"medido {medido:.2f}:1")
    conferir(f"O tema {rotulo} tem contraste anotado no comentário", anotados >= 6,
             f"{anotados} anotações")

# A faixa da marca é o par que o comentário descreve em prosa.
for rotulo, tema, esperado in (("claro", claro, 12.16), ("escuro", escuro, 13.08)):
    a, b = cor(tema, "tinta"), cor(tema, "marca-fundo")
    if a and b:
        medido = contraste(a, b)
        conferir(f"[{rotulo}] texto sobre a faixa da marca = {esperado}:1",
                 abs(medido - esperado) <= TOLERANCIA, f"medido {medido:.2f}:1")

# ===================================================================
#  3. Os três pares que são PROIBIDOS para texto e contorno
# ===================================================================
titulo("3. OS PARES PROIBIDOS CONTINUAM PROIBIDOS")

proibidos = [("claro", claro, "linha", "fundo"),
             ("claro", claro, "marca-fundo", "fundo"),
             ("escuro", escuro, "linha", "superficie")]
for rotulo, tema, frente, fundo in proibidos:
    a, b = cor(tema, frente), cor(tema, fundo)
    medido = contraste(a, b)
    conferir(f"[{rotulo}] --{frente} / --{fundo} fica abaixo de 3:1 (só separa)",
             medido < 3.0, f"medido {medido:.2f}:1 — se subiu, o papel mudou")

titulo("4. O QUE O DEDO TOCA PASSA DE 3:1, E TODO TEXTO PASSA DE 4,5:1")

for rotulo, tema in (("claro", claro), ("escuro", escuro)):
    for fundo in ("fundo", "superficie"):
        a, b = cor(tema, "linha-forte"), cor(tema, fundo)
        medido = contraste(a, b)
        conferir(f"[{rotulo}] --linha-forte / --{fundo} >= 3:1 (WCAG 1.4.11)",
                 medido >= 3.0, f"medido {medido:.2f}:1")
    for tinta in ("tinta", "tinta-fraca", "marca", "sucesso", "erro"):
        a = cor(tema, tinta)
        b = cor(tema, "superficie")
        medido = contraste(a, b)
        conferir(f"[{rotulo}] --{tinta} / --superficie >= 4,5:1 (WCAG AA)",
                 medido >= 4.5, f"medido {medido:.2f}:1")
    a, b = cor(tema, "acao-tinta"), cor(tema, "acao")
    conferir(f"[{rotulo}] texto do botão principal >= 4,5:1",
             contraste(a, b) >= 4.5, f"medido {contraste(a, b):.2f}:1")
    a, b = cor(tema, "acao-tinta"), cor(tema, "acao-hover")
    conferir(f"[{rotulo}] texto do botão principal sob o mouse >= 4,5:1",
             contraste(a, b) >= 4.5, f"medido {contraste(a, b):.2f}:1")

# ===================================================================
#  5. Distância de matiz: contraste diz se dá para ler, matiz se dá
#     para distinguir
# ===================================================================
titulo("5. DISTÂNCIA DE MATIZ ENTRE SINAL DE ESTADO E A COR DA MARCA")

MINIMO_MATIZ = 60.0  # abaixo disso, em selo pequeno de traço fino, lê como a mesma cor

for rotulo, tema in (("claro", claro), ("escuro", escuro)):
    h_marca = matiz(cor(tema, "marca"))
    for sinal in ("sucesso", "erro"):
        h = matiz(cor(tema, sinal))
        distancia = abs(h - h_marca)
        distancia = min(distancia, 360 - distancia)
        conferir(f"[{rotulo}] --{sinal} fica a mais de {MINIMO_MATIZ:.0f}° do petróleo",
                 distancia >= MINIMO_MATIZ,
                 f"{distancia:.0f}° (marca {h_marca:.0f}°, sinal {h:.0f}°)")

# ===================================================================
#  6. Todo token nasce em :root; os dois blocos escuros são gêmeos
# ===================================================================
titulo("6. ESTRUTURA DOS TRÊS BLOCOS DE TOKENS")

conferir("O :root existe e traz o tema claro completo", len(claro) >= 25,
         f"{len(claro)} tokens")

so_no_escuro = sorted(set(media) - set(claro))
conferir("Nenhum token nasce dentro do @media escuro", not so_no_escuro,
         ", ".join("--" + t for t in so_no_escuro))

so_no_botao = sorted(set(botao) - set(claro))
conferir("Nenhum token nasce dentro do [data-tema=\"escuro\"]", not so_no_botao,
         ", ".join("--" + t for t in so_no_botao))

diferenca = sorted(set(media) ^ set(botao))
conferir("Os dois blocos escuros redefinem o mesmo conjunto", not diferenca,
         ", ".join("--" + t for t in diferenca))

divergentes = [t for t in set(media) & set(botao)
               if media[t].split("/*")[0].strip() != botao[t].split("/*")[0].strip()]
conferir("Os dois blocos escuros têm os mesmos valores", not divergentes,
         ", ".join("--" + t for t in sorted(divergentes)))

for rotulo, corpo in (("claro", corpo_claro), ("@media escuro", corpo_media),
                      ("botão escuro", corpo_botao)):
    conferir(f"O bloco {rotulo} declara color-scheme", "color-scheme:" in corpo)

# ===================================================================
#  7. Nenhuma cor literal fora do tokens.css
# ===================================================================
titulo("7. COR LITERAL SÓ NO TOKENS.CSS")

outros_css = [f for f in sorted(os.listdir(CSS)) if f.endswith(".css")
              and f != "tokens.css"]
for arquivo in outros_css:
    fonte = ler(os.path.join(CSS, arquivo))
    # Comentário não é estilo: o nome de uma cor pode aparecer em prosa.
    sem_comentario = re.sub(r"/\*.*?\*/", "", fonte, flags=re.S)
    literais = re.findall(r"#[0-9A-Fa-f]{3,8}\b|\brgba?\([^)]*\)|\bhsla?\([^)]*\)",
                          sem_comentario)
    conferir(f"{arquivo} não tem cor literal", not literais,
             ", ".join(sorted(set(literais))[:6]))

for arquivo in sorted(os.listdir(JS)):
    if not arquivo.endswith(".js"):
        continue
    fonte = ler(os.path.join(JS, arquivo))
    sem_comentario = re.sub(r"/\*.*?\*/", "", fonte, flags=re.S)
    literais = re.findall(r"#[0-9A-Fa-f]{6}\b|\brgba?\(\s*\d", sem_comentario)
    conferir(f"js/{arquivo} não tem cor literal", not literais,
             ", ".join(sorted(set(literais))[:6]))

# ===================================================================
#  8. A escala fechada: sete degraus de texto, grade de 4px
# ===================================================================
titulo("8. ESCALA DE TEXTO E GRADE DE ESPAÇAMENTO")

# Os tokens de densidade entram aqui como espacamento legitimo PORQUE a
# verificacao logo abaixo confere que eles proprios saem da grade, nos
# dois modos. Liberar o nome sem conferir o valor seria abrir um buraco.
UNIDADE = (r"var\(--e-[1-9]\)|var\(--pad-celula-[xy]\)|calc\([^;]*\)|"
           r"max\([^;]*\)|min\([^;]*\)|clamp\([^;]*\)|env\([^;]*\)|0")
ESPACO_OK = re.compile(
    r"^\s*(0|auto|inherit|initial|unset|revert|"
    r"(" + UNIDADE + r")(\s+(" + UNIDADE + r"|auto))*)\s*$")

for arquivo in outros_css:
    fonte = ler(os.path.join(CSS, arquivo))
    sem_comentario = re.sub(r"/\*.*?\*/", "", fonte, flags=re.S)

    fora_da_escala = [v for v in re.findall(r"font-size:\s*([^;}]+)", sem_comentario)
                      if not re.fullmatch(r"\s*var\(--t-[a-z]+\)\s*", v)
                      and "inherit" not in v]
    conferir(f"{arquivo}: todo font-size sai da escala de sete degraus",
             not fora_da_escala, ", ".join(sorted(set(fora_da_escala))[:5]))

    fora_da_grade = [f"{p}: {v.strip()}" for p, v in
                     re.findall(r"\b(padding|margin|gap|row-gap|column-gap|"
                                r"padding-top|padding-right|padding-bottom|padding-left|"
                                r"padding-block|padding-inline|margin-top|margin-right|"
                                r"margin-bottom|margin-left|margin-block|margin-inline)"
                                r":\s*([^;}]+)", sem_comentario)
                     if not ESPACO_OK.match(v)]
    conferir(f"{arquivo}: todo espaçamento sai da grade de 4px",
             not fora_da_grade, "; ".join(sorted(set(fora_da_grade))[:5]))

# A densidade troca valores da grade em vez de multiplica-los: e isso que
# permite que ela exista sem inventar medida. Conferido nos DOIS modos —
# um compacto que saia da grade estraga a grade inteira de quem o escolher.
for rotulo_d, seletor in (("confortável", ":root"),
                          ("compacto", ':root[data-densidade="compacto"]')):
    corpo_d = bloco(seletor)
    densidade = dict(re.findall(r"--([a-z0-9-]+):\s*([^;]+);",
                                re.sub(r"/\*.*?\*/", "", corpo_d, flags=re.S)))
    for nome in ("pad-celula-y", "pad-celula-x"):
        valor = (densidade.get(nome) or "").strip()
        conferir(f"[{rotulo_d}] --{nome} sai da grade de 4px",
                 bool(re.fullmatch(r"var\(--e-[1-9]\)", valor)), f"vale {valor!r}")
    altura = (densidade.get("altura-controle") or "").strip()
    casa = re.fullmatch(r"(\d+)px", altura)
    conferir(f"[{rotulo_d}] --altura-controle é múltiplo de 4px",
             bool(casa) and int(casa.group(1)) % 4 == 0, f"vale {altura!r}")

    conferir(f"{arquivo}: a borda é --b (1,5px), nunca 1px",
             not re.search(r"border(-[a-z]+)?:\s*(1px|[^;}]*\s1px\s)", sem_comentario),
             "achei border de 1px")

# ===================================================================
#  9. O que saiu da identidade não volta
# ===================================================================
titulo("9. GRADIENTE, BRILHO, VIDRO E EMOJI NÃO VOLTAM")

PROIBIDO_CSS = {
    "gradiente": r"linear-gradient|radial-gradient|conic-gradient",
    "vidro fosco": r"backdrop-filter|filter:\s*blur",
}

# Brilho é sombra COM DESFOQUE na cor da marca. O anel de foco também é um
# box-shadow em --marca, e não é brilho: ele tem deslocamento e desfoque zero
# (`0 0 0 3px`), ou seja, é contorno. A diferença está na forma, e é essa a
# medida — não a cor.
ANEL = re.compile(r"box-shadow:\s*0\s+0\s+0\s+[\d.]+px")
COLORIDA = re.compile(r"box-shadow:[^;}]*(?:var\(--marca|var\(--acao|"
                      r"#[0-9A-Fa-f]{3,8}|color-mix)")

for arquivo in sorted(os.listdir(CSS)):
    if not arquivo.endswith(".css"):
        continue
    fonte = ler(os.path.join(CSS, arquivo))
    sem_comentario = re.sub(r"/\*.*?\*/", "", fonte, flags=re.S)
    for nome, padrao in PROIBIDO_CSS.items():
        achados = re.findall(padrao, sem_comentario)
        conferir(f"{arquivo} não tem {nome}", not achados, f"{len(achados)} ocorrência(s)")

    brilhos = [d for d in re.findall(r"box-shadow:[^;}]+", sem_comentario)
               if COLORIDA.match(d) and not ANEL.match(d)]
    conferir(f"{arquivo}: sombra na cor da marca só como anel, nunca brilho",
             not brilhos, "; ".join(brilhos[:3]))

# Emoji na INTERFACE. Comentário de código não pinta pixel, então sai antes da
# busca: o que a regra proíbe é o ícone desenhado por fonte do sistema no lugar
# do SVG em traço, não a anotação que um humano deixou para outro.
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿⬀-⯿️]")
FRONT = os.path.join(RAIZ, "frontend")
for pasta, _subs, arquivos in os.walk(FRONT):
    for arquivo in sorted(arquivos):
        if not arquivo.endswith((".html", ".js")):
            continue
        caminho = os.path.join(pasta, arquivo)
        relativo = os.path.relpath(caminho, RAIZ).replace("\\", "/")
        fonte = ler(caminho)
        if arquivo.endswith(".js"):
            fonte = re.sub(r"/\*.*?\*/|//[^\n]*", "", fonte, flags=re.S)
        else:
            fonte = re.sub(r"<!--.*?-->", "", fonte, flags=re.S)
        achados = EMOJI.findall(fonte)
        conferir(f"{relativo} usa ícone em traço, nunca emoji", not achados,
                 "".join(sorted(set(achados))[:8]))

# ===================================================================
#  10. Token inexistente, e estilo escrito por JavaScript (a CSP bloqueia)
# ===================================================================
titulo("10. TOKEN QUE NÃO EXISTE E ESTILO ESCRITO POR JAVASCRIPT")

definidos = set(claro) | set(media) | set(botao)
for arquivo in outros_css:
    fonte = ler(os.path.join(CSS, arquivo))
    usados = set(re.findall(r"var\(--([a-z0-9-]+)", fonte))
    orfaos = sorted(usados - definidos)
    conferir(f"{arquivo}: todo var(--x) aponta para token existente", not orfaos,
             ", ".join("--" + t for t in orfaos))

for arquivo in sorted(os.listdir(JS)):
    if not arquivo.endswith(".js"):
        continue
    fonte = ler(os.path.join(JS, arquivo))
    sem_comentario = re.sub(r"/\*.*?\*/|//[^\n]*", "", fonte, flags=re.S)
    escritas = re.findall(r"\.style\.[a-zA-Z]+\s*=|\.style\s*=|"
                          r"setAttribute\(\s*['\"]style['\"]", sem_comentario)
    conferir(f"js/{arquivo} não escreve estilo (a CSP bloqueia em silêncio)",
             not escritas, f"{len(escritas)} escrita(s)")

# ===================================================================
#  11. A contagem de ícones não envelhece
# ===================================================================
titulo("11. O SPRITE DE ÍCONES E O NÚMERO ESCRITO NO DOCUMENTO")

icones = set(re.findall(r'id="(i-[a-z0-9-]+)"',
                        ler(os.path.join(RAIZ, "frontend", "img", "icones.svg"))))
escrito = re.search(r"os (\d+) ícones em traço", documento)
conferir("O documento diz quantos ícones existem", bool(escrito))
if escrito:
    conferir(f"O sprite tem os {escrito.group(1)} ícones que o documento promete",
             len(icones) == int(escrito.group(1)),
             f"o sprite tem {len(icones)}")

conferir("Todo ícone do sprite segue o prefixo i-", len(icones) == len(
    re.findall(r'id="', ler(os.path.join(RAIZ, "frontend", "img", "icones.svg")))))

# Ícone pedido por HubUI.ico('i-nome') precisa existir no sprite.
for pasta, _subs, arquivos in os.walk(FRONT):
    for arquivo in sorted(arquivos):
        if not arquivo.endswith(".js"):
            continue
        caminho = os.path.join(pasta, arquivo)
        fonte = re.sub(r"/\*.*?\*/|//[^\n]*", "", ler(caminho), flags=re.S)
        pedidos = set(re.findall(r"""ico\(\s*['"](i-[a-z0-9-]+)['"]""", fonte))
        faltando = sorted(pedidos - icones)
        conferir(f"js/{arquivo}: todo ícone pedido existe no sprite", not faltando,
                 ", ".join(faltando))

# ===================================================================
titulo("A IDENTIDADE VISUAL ESTÁ ÍNTEGRA" if not falhas
       else f"{len(falhas)} VERIFICAÇÃO(ÕES) DE IDENTIDADE FALHARAM")
if falhas:
    for nome in falhas:
        print(f"  - {nome}")
    print("\n  Trocou uma cor? Remeça o contraste e reescreva o número nos DOIS"
          "\n  lugares: na tabela do IDENTIDADE_VISUAL.md e no comentário do"
          "\n  tokens.css. O número é contrato, não enfeite.")
sys.exit(1 if falhas else 0)
