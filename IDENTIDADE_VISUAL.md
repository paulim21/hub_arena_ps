# Identidade visual do ArenaHub

Este documento é o **porquê**. O **como** mora em
[`docs/design/PADROES.md`](docs/design/PADROES.md), e os valores em
[`frontend/css/tokens.css`](frontend/css/tokens.css). Quando este documento e o
guia discordarem, **este manda** — e então o guia é corrigido.

As tabelas de contraste abaixo são **contrato**: o
[`verificar-identidade.py`](docs/design/verificar-identidade.py) remede cada
par pela fórmula da WCAG 2.1 e recusa qualquer número que tenha se afastado da
cor.

---

## 1. De onde vem a forma

A logo é um monograma **AH** em contorno aberto, assentado sobre uma faixa de
areia. Duas coisas saem dali e viram regra:

**Traço antes de preenchimento.** O monograma não é preenchido — é desenhado.
Então cartão, botão secundário, selo e ícone também são borda de `--b` (1,5px,
o peso do traço da logo) sem fundo. **Preenchimento sólido é de UMA coisa por
tela: a ação principal.** Se duas ações disputam, as duas viram traço.

**A areia é chão, nunca letra.** Na logo, a areia sustenta o monograma; ela não
escreve. Por isso `--marca-fundo` é faixa, bloco em destaque, trilho — e é
deliberadamente fraca contra o papel (1,25:1). Texto sobre ela é `--tinta`,
nunca a própria areia.

## 2. De onde vem a cor

São **duas cores mais o fundo**:

| Papel | Claro | Escuro |
|---|---|---|
| A marca **escrevendo** — link, aba ativa, número, arco | `--marca` navy `#1B2A4A` | `#9BB8E8` |
| A marca como **chão** — faixa, destaque | `--marca-fundo` areia `#EFD6B0` | navy profundo `#00204A` |
| O papel | `--fundo` creme `#F4F1EB` | `#101419` |

No escuro a marca **clareia**: navy não escreve sobre preto. O escuro não é o
claro invertido — os dois foram medidos separadamente, e compartilham a
estrutura e os números que importam, não os valores.

**Verde e vermelho não são cores da marca.** São sinal de estado, e só aparecem
quando há estado para assinalar. Perfil não é estado; posição no ranking não é
estado. Para diferenciar **categoria**, use palavra, peso ou forma do traço.

**Não existe uma terceira cor de marca**, e não existe `--aviso`: uma quarta cor
de sinal fica perto demais do erro em matiz, e à escala de um selo pequeno as
duas lêem como a mesma cor. "Pendente" é `--marca`.

E o que não volta: **gradiente** (é uma cor que não se compromete — não tem
valor de contraste, tem intervalo), **brilho colorido**, **vidro fosco**,
**borda de 1px** e **emoji no lugar de ícone**.

---

## 3. As tabelas de contraste — o contrato

Medidas pela WCAG 2.1. Os véus translúcidos são **compostos sobre a superfície
antes de medir**, porque é essa a cor que o olho vê.

### Tema claro

| Par | Medido | O que isso garante |
|---|---|---|
| `--tinta` / `--fundo` | 15,19:1 | texto principal no papel |
| `--tinta` / `--superficie` | 17,12:1 | texto principal no cartão |
| `--tinta` / `--superficie-2` | 14,03:1 | texto no cabeçalho de tabela |
| `--tinta` / `--superficie-3` | 17,12:1 | texto no menu e no modal |
| `--tinta-fraca` / `--fundo` | 6,44:1 | legenda e apoio passam de AA |
| `--tinta-fraca` / `--superficie` | 7,27:1 | idem, no cartão |
| `--marca` / `--fundo` | 12,62:1 | link legível no papel |
| `--marca` / `--superficie` | 14,22:1 | link legível no cartão |
| `--tinta` / `--marca-fundo` | 12,16:1 | **texto sobre a faixa de areia** |
| `--linha-forte` / `--fundo` | 4,21:1 | contorno de controle (WCAG 1.4.11 pede 3:1) |
| `--linha-forte` / `--superficie` | 4,75:1 | idem, no cartão |
| `--sucesso` / `--superficie` | 6,30:1 | selo de estado positivo |
| `--erro` / `--superficie` | 6,50:1 | selo e mensagem de erro |
| `--acao-tinta` / `--acao` | 14,22:1 | texto do botão principal |
| `--acao-tinta` / `--acao-hover` | 17,12:1 | e sob o mouse |
| `--tinta` / `--marca-traco` na `--superficie-3` | 14,76:1 | texto sobre a linha em foco |
| `--tinta` / `--seletivo` | 11,09:1 | texto selecionado continua legível |
| `--linha` / `--fundo` | 1,17:1 | **proibido** para contorno — só separa |
| `--linha` / `--superficie` | 1,31:1 | idem |
| `--marca-fundo` / `--fundo` | 1,25:1 | **proibido** para texto — a areia é chão |

### Tema escuro

| Par | Medido | O que isso garante |
|---|---|---|
| `--tinta` / `--fundo` | 15,03:1 | texto principal no papel |
| `--tinta` / `--superficie` | 13,61:1 | texto principal no cartão |
| `--tinta` / `--superficie-2` | 14,35:1 | texto no cabeçalho de tabela |
| `--tinta` / `--superficie-3` | 12,40:1 | texto no menu e no modal |
| `--tinta-fraca` / `--fundo` | 7,27:1 | legenda e apoio passam de AA |
| `--tinta-fraca` / `--superficie` | 6,58:1 | idem, no cartão |
| `--marca` / `--fundo` | 9,17:1 | link legível no papel |
| `--marca` / `--superficie` | 8,30:1 | link legível no cartão |
| `--tinta` / `--marca-fundo` | 13,08:1 | **texto sobre a faixa da marca** |
| `--linha-forte` / `--fundo` | 5,09:1 | contorno de controle |
| `--linha-forte` / `--superficie` | 4,61:1 | idem, no cartão |
| `--sucesso` / `--superficie` | 8,38:1 | selo de estado positivo |
| `--erro` / `--superficie` | 6,41:1 | selo e mensagem de erro |
| `--acao-tinta` / `--acao` | 9,17:1 | texto do botão principal |
| `--acao-tinta` / `--acao-hover` | 14,13:1 | e sob o mouse |
| `--tinta` / `--marca-traco` na `--superficie-3` | 10,54:1 | texto sobre a linha em foco |
| `--tinta` / `--seletivo` | 7,75:1 | texto selecionado continua legível |
| `--linha` / `--fundo` | 1,33:1 | **proibido** para contorno — só separa |
| `--linha` / `--superficie` | 1,21:1 | idem |
| `--marca-fundo` / `--fundo` | 1,15:1 | **proibido** para texto |

### Distância de matiz

Contraste diz se **dá para ler**; matiz diz se **dá para distinguir**. Um selo
pequeno, de traço fino, perde a diferença de cor antes de perder a legibilidade
— por isso o sinal de estado precisa ficar longe da marca em matiz. O mínimo
aqui é **60°**.

| Tema | Par | Distância |
|---|---|---|
| claro | `--sucesso` (95°) contra `--marca` (221°) | 126° |
| claro | `--erro` (11°) contra `--marca` (221°) | 150° |
| escuro | `--sucesso` (87°) contra `--marca` (217°) | 130° |
| escuro | `--erro` (13°) contra `--marca` (217°) | 156° |

---

## 4. As três leis, em uma linha cada

1. **`--marca` escreve, `--marca-fundo` é chão.** Nunca o contrário.
2. **`--linha` separa, `--linha-forte` delimita.** Se o dedo toca, é
   `--linha-forte`. Este é o erro mais fácil e o mais caro: a tela continua
   bonita e fica impossível de usar.
3. **O número de contraste é contrato.** Trocou uma cor? Remeça e reescreva o
   número nos **dois** lugares — na tabela acima e no comentário do
   `tokens.css`.

E mais duas, que não são de cor: **um arco por tela** e **uma sobreposição por
tela**, as duas sempre com função.

---

## 5. Texto, espaço e movimento

**Sete degraus de texto, e nenhum a mais.** `--t-rotulo` 12px · `--t-apoio` 14px
· `--t-corpo` 16px · `--t-titulo` 20px · `--t-destaque` · `--t-pagina` ·
`--t-numero`. Os quatro primeiros são fixos — rótulo de 12px não encolhe, e
campo abaixo de 16px faz o iPhone dar zoom sozinho ao focar. Os três grandes são
fluidos, em `clamp()`, e é por isso que não existe remendo de tamanho no
`@media` de celular.

Hierarquia é **peso**, não cor. A família é a do sistema: fonte externa é uma
dependência de rede que a identidade não precisa.

**Espaço: grade de 4px**, de `--e-1` (4px) a `--e-8` (64px).

**Espera.** A tela mostra o **formato** do que está chegando — um esqueleto
com a mesma estrutura da tabela real — em vez de ficar em branco. E a barra de
progresso do topo só acende depois de 120ms: resposta rápida não vira
lampejo.

**Movimento:** nada de interface passa de 400ms. Só animação de **dado** chega
aos 720ms, porque ali o movimento é a informação. Quem pede
`prefers-reduced-motion: reduce` recebe menos movimento — e o arco girando
**some**, em vez de congelar, porque um disco parado comunica menos que nenhum
disco.

**Densidade** é dimensão de primeira classe, com dois modos que **trocam**
valores da grade (`--altura-controle` 40/32px, `--pad-celula` 12/8px e 16/12px)
em vez de multiplicá-los: `.75` sobre a grade de 4px produziria 9px e 30px,
medidas que não existem aqui. No celular a densidade não existe — lá o mínimo é
a área de toque de 44px.

---

## 6. Ícones

São **os 43 ícones em traço** de [`frontend/img/icones.svg`](frontend/img/icones.svg),
desenhados no mesmo peso do monograma: `viewBox 24`, `stroke-width 1.8`,
`fill: none`, pontas e junções redondas. A cor vem de `currentColor`.

Nenhum emoji na interface. Emoji é desenhado pela fonte do sistema: muda de
forma entre aparelhos, não aceita o peso do traço da marca, não herda cor e não
tem como ser medido. O verificador varre todo `.html` e `.js` do `frontend/` e
recusa qualquer um.

Falta um ícone? Desenhe no mesmo peso — nunca emoji, nunca ícone cheio.

---

## 7. Antes de dizer que está pronto

```bash
python docs/design/verificar-identidade.py
```

Ele mede o contraste de cada par das tabelas acima, o contraste anotado em cada
comentário do `tokens.css`, os pares proibidos, o mínimo de 3:1 em tudo que o
dedo toca e de 4,5:1 em todo texto, a distância de matiz, a estrutura dos três
blocos de tema, cor literal fora do `tokens.css`, a escala de sete degraus, a
grade de 4px, gradiente, brilho, vidro, borda de 1px, emoji, `var(--x)` órfão,
estilo escrito por JavaScript e a contagem de ícones.

E a olho, o que a máquina não mede: **uma** coisa sólida na tela? **um** arco, e
com função? Todo contorno de controle é `--linha-forte`? Verde e vermelho só
onde há estado? Os dois temas, olhados de verdade — e o claro por último, que é
onde a cor-chão costuma sumir?
