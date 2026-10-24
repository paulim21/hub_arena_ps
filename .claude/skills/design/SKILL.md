---
name: design
description: A identidade visual do ArenaHub como regra de trabalho — tokens, componentes que já existem, e as armadilhas que já custaram correção. Use SEMPRE que a tarefa tocar em aparência ou interface: mexer em frontend/css/*.css, em frontend/*.html, no HTML gerado por frontend/js/*.js, nos ícones de frontend/img/, escolher ou trocar cor, tamanho de texto, espaçamento, borda, raio, sombra ou animação, criar tela, bloco, botão, campo, selo, tabela, lista, modal, aba, menu suspenso ou estado vazio, ajustar tema claro/escuro, foco, contraste, acessibilidade, responsivo/celular, carregamento, esqueleto, aviso flutuante ou spinner. Também quando a pergunta for "que cor uso aqui", "por que isso está assim" ou "isso está no padrão".
---

# A identidade do ArenaHub como regra de trabalho

O **porquê** de cada decisão mora no [`IDENTIDADE_VISUAL.md`](../../../IDENTIDADE_VISUAL.md)
(raiz do projeto). Este arquivo é o **como**: o que fazer, o que não fazer, e o
que já deu errado. Quando os dois discordarem, o documento manda — e então
conserte este.

**A ordem de trabalho é sempre a mesma:**

1. Procurar o componente que já existe (§ 4). Quase nada precisa ser inventado.
2. Usar token, nunca valor literal (§ 2).
3. Conferir as armadilhas (§ 5) antes de declarar pronto.
4. Rodar o verificador (§ 8). Ele mede 177 promessas em menos de um segundo.

---

## 1. As três leis

**A forma vem da logo: traço antes de preenchimento.** O monograma "AH" é
contorno aberto. Então cartão, botão secundário, selo e ícone também são borda
de 1,5px sem fundo. **Preenchimento sólido é de UMA coisa por tela: a ação
principal.** Se duas ações disputam, as duas viram traço.

**A cor é navy sobre papel creme, com a areia como chão**, e são duas cores
mais o fundo — as mesmas da logo: o monograma em navy assentado na faixa de
areia. No escuro a marca **clareia**, porque navy não escreve sobre preto.
Verde e vermelho não são cores da marca — são sinal de estado, e só aparecem
quando há estado para assinalar.

**O número de contraste é contrato.** Trocou uma cor? Remeça pela fórmula da
WCAG 2.1 e reescreva o número nos **dois** lugares: na tabela do
`IDENTIDADE_VISUAL.md` e no comentário do `tokens.css`. O verificador recusa a
divergência.

Mais duas, que não são de cor mas moram na mesma lógica: **um arco por tela** e
**uma sobreposição por tela**, as duas sempre com função.

---

## 2. Os tokens — a lista inteira

Nenhuma cor, tamanho, espaço, raio, borda ou duração fora desta lista, em
nenhum arquivo. Tudo nasce em `:root`, no `frontend/css/tokens.css`.

### Cor

| Token | Claro | Escuro | Para quê |
|---|---|---|---|
| `--fundo` | `#F4F1EB` | `#101419` | o papel da página — o creme da logo |
| `--superficie` | `#FFFFFF` | `#191E26` | cartão, tabela, painel flutuante |
| `--tinta` | `#1F1B16` | `#EDE7DD` | texto principal |
| `--tinta-fraca` | `#5C564C` | `#A8A294` | explicação, legenda, rótulo, apoio |
| `--superficie-2` | `#EDE8DF` | `#141920` | **recua**: cabeçalho de tabela, rodapé de cartão, trilho |
| `--superficie-3` | `#FFFFFF` | `#1F262F` | **avança**: menu, popover, modal. No claro é o próprio branco, e quem separa é a elevação |
| `--linha` | `#E6E0D4` | `#262D37` | **só separa** — divisória, borda de cartão |
| `--linha-forte` | `#7A7265` | `#7E8794` | **delimita** — tudo que o dedo toca |
| `--marca` | `#1B2A4A` navy | `#9BB8E8` | a marca **escrevendo**: link, aba ativa, arco, assinatura |
| `--marca-fundo` | `#EFD6B0` areia | `#00204A` | a marca como **chão**: faixa, item escolhido, chip. Nunca texto |
| `--marca-traco` | `rgba(27,42,74,.08)` | `rgba(155,184,232,.08)` | a marca como **véu**: linha sob o cursor, trilho, item em foco |
| `--seletivo` | `rgba(27,42,74,.22)` | `rgba(155,184,232,.26)` | fundo do texto selecionado; a cor do texto é forçada a `--tinta` |
| `--foco` | `#1B2A4A` | `#9BB8E8` | o anel de foco, por dentro |
| `--foco-halo` | `#FFFFFF` | `#101419` | o anel de foco, por fora — **nunca use um sem o outro** |
| `--sucesso` | `#3F6B1F` | `#9CC46B` | estado positivo, e só |
| `--erro` | `#A8371F` | `#E08A72` | estado negativo, e só |
| `--acao` | `#1B2A4A` | `#9BB8E8` | o preenchimento do botão principal |
| `--acao-tinta` | `#FFFFFF` | `#101419` | o texto por cima dele |
| `--acao-hover` | `#101B33` | `#D6E2F5` | no escuro **clareia**, não escurece |
| `--veu` | `rgba(31,41,51,.46)` | `rgba(5,9,12,.66)` | véu do modal |
| `--elev-0…4` | — | — | nada / cartão / cartão sob o cursor / menu / modal |

**Não existe um `--aviso`.** Uma quarta cor de sinal foi medida e recusada: o
âmbar fica perto demais do erro em matiz, e à escala de um selo os dois lêem
como a mesma cor. "Pendente" é `--marca`.

**A areia é chão, não traço fino.** `--marca-fundo` é fraca contra o papel de
propósito (1,25:1 no claro, 1,15:1 no escuro). Isso serve para área grande —
faixa, chip, item escolhido — e **não** para uma barra de 3px: a assinatura do
`.bloco-numero` nasceu em `--marca-fundo` e sumia no escuro, navy sobre navy.
Faixa fina é `--marca`.

### Texto — sete degraus, e nenhum a mais

`--t-rotulo` 12px · `--t-apoio` 14px · `--t-corpo` 16px · `--t-titulo` 20px ·
`--t-destaque` 22→26px · `--t-pagina` 26→34px · `--t-numero` 34→46px

Os quatro primeiros são **fixos** (rótulo de 12px não encolhe, e campo abaixo de
16px faz o iPhone dar zoom sozinho ao focar). Os três grandes são **fluidos**,
em `clamp()` — e é por isso que **não existe mais remendo de tamanho no
`@media` de celular**: se você estiver prestes a escrever um, o token já
resolveu.

Hierarquia é **peso** (700 contra 300), não cor. A família é `--fonte`
(a do sistema): fonte externa é bloqueada pela CSP.

### Espaço — grade de 4px

`--e-1` 4 · `--e-2` 8 · `--e-3` 12 · `--e-4` 16 · `--e-5` 24 · `--e-6` 32 ·
`--e-7` 48 · `--e-8` 64

### Raio, borda e movimento

`--r-campo` 8px · `--r-botao` 10px · `--r-cartao` 14px · `--r-modal` 20px ·
`--r-selo` 999px · `--r-interno` (raio concêntrico, para o que encosta na borda
interna de um cartão) · `--b` **1,5px** (nunca 1px: é o peso do traço da logo) ·
`--b-grosso` 3px

**Movimento.** Duração e curva são tokens separados, porque são decisões
separadas: `--d-instante` 80 · `--d-rapido` 160 · `--d-medio` 240 ·
`--d-calmo` 360 · `--d-dado` 720ms, contra `--c-padrao`, `--c-entra`, `--c-sai`,
`--c-enfase` e as molas `--c-mola` / `--c-mola-forte`. `--d-saida` é um
multiplicador (.72), não uma duração.

Nada de **interface** passa de 400ms. Só animação de **dado** chega aos 720ms,
porque ali o movimento é a informação. Os quatro nomes antigos (`--mov-cor`,
`--mov-abre`, `--mov-fecha`, `--mov-modal`) continuam, montados a partir
destes.

**Densidade** é dimensão de primeira classe: `--densidade` (1, ou .75 em
`[data-densidade="compacto"]`), `--altura-controle`, `--altura-linha-tabela`,
`--pad-celula`.

---

## 3. As regras de cor, na ordem em que são violadas

1. **`--marca` escreve, `--marca-fundo` é chão.** Nunca texto em
   `--marca-fundo` (1,15:1 no claro: some), nunca faixa em `--marca`.
2. **Texto sobre a faixa da marca é `--tinta`.** Nos dois temas.
3. **`--linha` separa, `--linha-forte` delimita.** Se o dedo toca, é
   `--linha-forte` — a WCAG 1.4.11 pede 3:1 para contorno de controle, e
   `--linha` está a 1,17:1. Este é o erro mais fácil e o mais caro: a tela
   continua bonita e fica impossível de usar.
4. **Uma coisa sólida por tela.**
5. **Verde e vermelho só com estado**, e longe do navy em matiz. Para
   diferenciar **categoria**, use palavra, peso ou forma do traço — nunca cor.
   Perfil não é estado. Posição no ranking não é estado. "Bloqueada" não é erro
   nem sucesso: é ausência, e se diz com traço **tracejado** em `--tinta-fraca`.

E o que não volta nunca: **gradiente** (é uma cor que não se compromete: não
tem valor de contraste, tem intervalo), **brilho colorido**, **vidro fosco**,
**emoji** no lugar de ícone, e **uma terceira cor de marca** — ela é o começo
do fim da identidade.

---

## 4. O que já existe — procure aqui antes de criar

### Estrutura e blocos
`.area` (grade da página) · `.bloco` (cartão padrão) · `.bloco-principal`
(traço na cor da marca + um degrau de elevação; o olho pousa aqui) ·
`.bloco-numero` + `.numero-assinatura` (o número grande que monta na borda de
cima — **um por tela**) · `.destaque` (`.valor` + `.apoio`) · `.tira-numeros`
(números secundários, menores de propósito) · `.titulo-pagina`

### Controle
`button` (**nasce em traço**) · `button.principal` (o sólido, **um por tela**) ·
`button.perigo` · `button.sucesso` · `.botao-menor` ·
`a.botao-link` · `.botao-texto` (botão que é só texto clicável) ·
`.botao-tema` · `.abas` com `aria-selected` · `.filtros`

### Formulário
`form.painel` (duas colunas, uma no celular) · `.form-linha`
(`auto-fit minmax(176px, 1fr)`) · `label` (é **grid**, atenção à § 5) ·
`input`/`select`/`textarea` com os cinco estados · `.dd` (menu suspenso que
substitui o `<select>` nativo) · `.multi-sel` + `.ms-chip` · `.dtp` (seletor de
data e hora) · `.caixa-aceite`

### Dado
`.painel-lista` / `.painel-vidro` + `table` · `.tabela-responsiva` (vira lista
no celular, com `data-rotulo` em cada `td`) · `.lista` + `.item`
(`.titulo`, `.lado`, `.preco`, `.acoes-item`) · `.selo` com
`.confirmada` / `.recusada` / `.cancelada` / `.pendente` / `.bloqueada` ·
`.id-pill` · `.arco-meta`

### Aviso e vazio
`.aviso` · `.erro-form` · `.erro-topo` · `.aviso-sucesso` · `.vazio` /
`.vazio-util` (com `<strong>`) · `.modal` (`<dialog>`, véu no `::backdrop`) ·
`.aviso-flutuante`

### Espera e resposta — a camada de acabamento (`frontend/js/interface.js`)
- `HubUI.esqueleto(forma, quantas)` e `HubUI.esperando(id, forma, quantas)` —
  o **desenho** do que está chegando, no lugar exato. A tela nunca fica em
  branco esperando o servidor, e nada pula quando o dado chega, porque o
  esqueleto tem a mesma estrutura da coisa real. As formas são `tabela`
  (o padrão), `cartoes`, `lista` e `texto`. O `aria-busy` se desliga sozinho
  quando o conteúdo entra — quem escreve `lista.innerHTML = tabela` não ia
  lembrar de desmarcar, e o leitor de tela ficaria anunciando a região como
  ocupada para sempre.
- A **barra de progresso do topo** acende sozinha em toda chamada à API, com
  120ms de atraso para resposta rápida não virar lampejo. Ela conta as
  chamadas em voo, porque a página dispara várias em paralelo e a barra tem
  que esperar a última. O estado vai em `data-estado`, nunca em style.
- `HubUI.abrirBusca()` — a paleta do **Ctrl+K**, montada **a cada abertura** a
  partir do próprio menu da página: ela nunca oferece um lugar que a página
  não oferece. Leva também o que a página **faz** (tema, densidade), em
  grupos, com o trecho casado realçado — e a busca ignora acento, então
  "relatorios" acha "Relatórios". Toda ação dali **aciona um botão que já
  existe no cabeçalho**: a paleta é caminho de teclado, nunca uma porta que só
  ela abre. É por isso que o item de tema se renomeia sozinho depois do
  clique — ele relê o `aria-label` do botão.

  **Não tem grupo "Recentes", e não deve ganhar um.** Ele existiu: com 6
  destinos e 2 ações, repetia no topo itens visíveis logo abaixo — "Reservas"
  duas vezes — e ainda empurrava o resto para fora da tela. Recência só se
  paga quando a lista não cabe. Se um dia a paleta passar de umas 15 linhas,
  aí vale reabrir a conversa.
- `HubUI.toast(mensagem, tipo)` — o que deu certo some em 4s; **o que deu
  errado só some no clique**, porque erro que desaparece sozinho é erro que
  ninguém leu.
- `HubUI.carregando(botao, ligado)` — desabilita o botão e marca `aria-busy`
  enquanto a chamada corre.
- `HubUI.erroTopo(mensagem)` — o erro que fica no topo da página até ser
  resolvido; `''` limpa.

De `frontend/js/base.js`: `api`, `esc`, `moeda`, `dataHora`, `telefone`,
`cnpj`, `ico`, `arco`, `erroTopo`, `toast`, `carregando`, `confirmar`,
`informar`, `melhorar`, `animarNumeros`.
**Não existe `alert()` neste projeto** — use `HubUI.informar`/`confirmar`,
que são `<dialog>` com véu no `::backdrop`.

De `frontend/js/tema.js`: `HubTema.atual`, `alternar`, `densidadeAtual`,
`alternarDensidade`.

De `frontend/js/interface.js`: `esqueleto`, `esperando`, `abrirBusca`. Ele
carrega **depois** do `base.js` e **antes** do script da página, porque
envolve o `HubUI.api` para acender a barra.

**Ainda NÃO existe** — e o documento não promete o que não foi construído:
o `painel.css`. Se for construído, entra aqui **e** no
`IDENTIDADE_VISUAL.md`.

### Ícones — 43, em traço, nunca emoji
`.ico` (20px), `.ico-grande` (32px), `.ico-marca` (28px). Via
`HubUI.ico('i-nome')`. A **fonte** é `frontend/img/icones.svg`; a cópia que o
navegador usa é a embutida em cada HTML, porque `<use href="arquivo.svg#id">`
externo não funciona no Chrome. Mexeu no sprite? Rode
`python .claude/skills/design/embutir-icones.py`, que copia a fonte para
dentro dos seis HTML, entre `<!-- sprite:inicio -->` e `<!-- sprite:fim -->`.

`i-futevolei` `i-beach-tennis` `i-volei` `i-frescobol` `i-esporte` `i-arena`
`i-quadra` `i-local` `i-agenda` `i-agenda-mais` `i-agenda-ok` `i-relogio`
`i-dinheiro` `i-grafico` `i-trofeu` `i-busca` `i-busca-vazia` `i-ok`
`i-ok-circulo` `i-x` `i-x-circulo` `i-alerta` `i-proibido` `i-usuario`
`i-usuario-mais` `i-escudo` `i-formatura` `i-atleta` `i-oculto` `i-mais`
`i-lixeira` `i-seta` `i-sair` `i-registro` `i-entrada` `i-saida` `i-barrado`
`i-faisca` `i-sol` `i-lua` `i-arejado` `i-denso` `i-monograma`

Falta um ícone? Desenhe no mesmo peso (`viewBox 24`, `stroke-width 1.8`,
`fill: none`, `linecap`/`linejoin` redondos) — nunca emoji, nunca ícone cheio.

---

## 5. As armadilhas — cada uma já custou correção

### O botão nasce em traço (a dívida foi paga)
`button` é contorno, transparente, com `justify-self: start`. **Quem é a ação
principal declara `.principal`** e recebe o sólido. Se duas ações disputam a
tela, as duas ficam em traço — é o que acontece em relatórios (cinco painéis de
mesmo peso) e na aba de marcar horário (marcar e fechar são pedidos igualmente
legítimos).

Era o contrário, e o avesso mordeu três vezes: item da busca do Ctrl+K, item da
paleta de destinos e palpite de e-mail no cadastro — sempre um botão nascendo
cheio e esticado onde cabia uma linha de lista.

**Não recrie o que a inversão apagou.** `.secundario` não existe mais: ela
dizia "eu não sou a principal", e isso virou o padrão. Se você se pegar
escrevendo `background: transparent`, `width: auto` ou `min-height: 0` num
botão, pare — a base já faz isso, e o que você quer provavelmente é
`.botao-texto`.

### Botão esticado tem duas causas, e elas dão a mesma medida
Um seletor largo vencendo a cascata (`.cartao-entrada button { width: 100% }`) e
um filho de grade esticando produzem exatamente o mesmo `width` computado.
**`width: auto` não distingue** — ele diz "não force largura", e a grade força
depois. A medida que separa é **`justify-self`/`align-self`**, não `width`.

E o `label` deste sistema é `display: grid`, então **todo botão dentro de um
rótulo cai no segundo caso**. Esta armadilha consumiu duas correções em
sequência: a primeira, na cascata, estava certa e não resolveu.

### A ordem no arquivo importa
A `.botao-texto` mora **antes** dos componentes, de propósito: ela **desfaz**, e
quem vem depois **refina**. Invertida a ordem, o `font: inherit` dela passa por
cima do tamanho que cada componente escolheu — foi o que aconteceu quando ela
nasceu junto do `button`, lá embaixo, e as abas perderam o próprio desenho.

### A caixa alta é do texto, não do `<label>`
O `<label>` **não** é mais caixa alta. Quem grita é o texto do rótulo, e ele
pede `.rotulo`:

```html
<label><span class="rotulo">E-mail</span><input name="email" type="email"></label>
```

Era o contrário, e custou cinco remendos: um `<label>` contém o rótulo, o campo
e às vezes uma frase de ajuda, e tudo que não fosse o primeiro precisava se
desfazer da caixa alta herdada.

Dois detalhes que não se adivinham:

- **O espaçador `.invisivel` leva `.rotulo` junto**
  (`<span class="invisivel rotulo">buscar</span>`). Ele reserva a linha do
  rótulo para o botão alinhar com os campos vizinhos, e precisa das mesmas
  métricas de 12px/300/.08em — sem elas cresce para 16px e o botão desce.
- **Não existe `.label-texto`.** Esse nome existiu, sem regra nenhuma no CSS, e
  por isso "Quem vai jogar" era o único rótulo do sistema em minúsculas. É
  `.rotulo`, como todos os outros.

### `display: inline` não funciona em `<button>`
O navegador blocifica controle de formulário de qualquer jeito, e a propriedade
é ignorada **em silêncio**: a regra parece não ter sido aplicada, mas foi.

### `.sessao-nav button` vence regra de classe dentro de `@media`
Esconder um botão do cabeçalho exige o seletor completo, não só a classe.

### A CSP bloqueia estilo escrito por JavaScript
`style-src 'self'` → **`element.style` não funciona**. Por isso: largura de
esqueleto é classe, estado é classe, altura de barra vem de `data-nivel`, e
valor por instância (o arco da meta) vai em **atributo de apresentação** do SVG,
que a transição do CSS consegue animar. Também bloqueia fonte externa, CDN e
framework — os três falham calados.

### Nunca `outline: none` sem substituto, e o anel é de DUAS cores
O foco visível é `outline: 3px solid var(--foco)` com `outline-offset: 2px`
**mais** `box-shadow: 0 0 0 2px var(--foco-halo)`, que preenche o vão do offset.

O halo não é enfeite: o anel da cor da marca sobre o botão principal — feito da
mesma cor — dá **1,00:1**, e o foco sumia justamente no controle mais
importante da tela. Onde um some, o outro aparece. **Usar `--foco` sozinho
reintroduz o defeito.**

O anel tem desfoque zero de propósito: sombra colorida **com** desfoque é
brilho, e brilho saiu da identidade.

### Celular: 44px de área de toque
Abaixo de 720px, `button`, `.botao-menor`, `a.botao-link`, `.dd-gatilho`,
`.ms-gatilho`, `input` e `select` vão a `min-height: 44px`. Tabela usa
`.tabela-responsiva`; `form.painel` vira uma coluna.

### `tema.js` no `<head>` **sem `defer`**
Ele escreve no `<html>` tudo que precisa existir **antes da primeira pintura**:
o tema e a densidade. O nome é histórico. Com `defer`, a tela pisca branca
antes de escurecer e a tabela nasce larga e encolhe na cara de quem já está
lendo. Qualquer escolha nova que mude o layout entra aqui, não no `base.js`.

### `overflow-x: hidden` quebra `position: sticky`
`hidden` faz do elemento um **contêiner de rolagem**, e contêiner de rolagem
mata o `sticky` lá dentro. O cabeçalho deste projeto declarava `sticky` havia
tempo e nunca tinha grudado: rolando a política de privacidade, ele ficava em
-1000px. A guarda contra estouro horizontal agora é `overflow-x: clip`, que
corta igual sem criar contêiner. Se você precisar esconder estouro em volta de
algo grudento, é `clip`.

### Densidade: dois modos, e eles TROCAM valores da grade
`--altura-controle` (40/32px) e `--pad-celula-y|x` (12/8px, 16/12px) mudam em
`:root[data-densidade="compacto"]`. Densidade **não** é multiplicador: `.75`
sobre a grade de 4px produz 9px e 30px, medidas que não existem aqui. O
verificador confere os dois modos.

Quem escreve o atributo é o `tema.js`, antes da primeira pintura. No celular a
densidade não existe — lá o mínimo é a área de toque de 44px —, e o botão some
por `.sessao-nav .botao-densidade`, com o seletor completo pelo motivo da
armadilha logo acima.

### `prefers-reduced-motion: reduce`
Quem pediu menos movimento recebe menos movimento — e o arco girando **some**
em vez de congelar, porque um disco parado comunica menos que nenhum disco.

---

## 6. Os três blocos de tema, nesta ordem, e nada fora deles

1. `:root` com o tema claro **completo** — todo token nasce aqui.
2. `@media (prefers-color-scheme: dark)` protegido por
   `:root:not([data-tema="claro"])` — o aparelho decide, mas o botão vence.
3. `:root[data-tema="escuro"]` — o botão vence também no sentido contrário.

Os dois blocos escuros são gêmeos: mesmo conjunto, mesmos valores. O par
repetido é o preço de o botão vencer nos dois sentidos, e o verificador confere
que eles não se separaram. `color-scheme` em cada bloco.

Um tema **nunca** é o outro invertido: os dois foram medidos separadamente.
Eles compartilham a estrutura e os números que importam, não os valores.

---

## 7. Onde cada coisa mora

| Arquivo | O que tem |
|---|---|
| `IDENTIDADE_VISUAL.md` | o porquê de cada decisão, e as tabelas de contraste |
| `frontend/css/tokens.css` | todos os valores, com o contraste no comentário |
| `frontend/css/estilo.css` | só componentes — **nenhuma cor literal** |
| `frontend/js/tema.js` | tema e densidade, no `<head>` sem `defer` |
| `frontend/js/base.js` | `api`, `<dialog>`, formatos, `ico`, `arco`, `melhorar` |
| `frontend/js/interface.js` | esqueleto, barra de progresso e a paleta do Ctrl+K |
| `frontend/img/icones.svg` | os 43 ícones em traço (a fonte) |
| `frontend/img/logo.png` · `logo-escuro.png` | o logotipo da marca, uma versão por tema — o navy do "Arena" sumiria no fundo escuro |
| `frontend/img/favicon.svg` | o monograma. É o **único** arquivo com cor literal fora do `tokens.css`, porque é servido solto, fora do CSS |
| `.claude/skills/design/embutir-icones.py` | copia o sprite para dentro dos HTML |
| `.claude/skills/design/verificar-identidade.py` | mede o contrato |

---

## 8. Antes de dizer que está pronto

```bash
python .claude/skills/design/verificar-identidade.py
```

224 verificações, e todas passam hoje: o contraste de cada par das tabelas, remedido — inclusive os
véus translúcidos, **compostos sobre cada superfície antes de medir**, que é a
cor que o olho vê; o contraste
anotado em cada comentário do `tokens.css`; os três pares que são **proibidos**
para texto e contorno; o mínimo de 3:1 em tudo que o dedo toca e de 4,5:1 em
todo texto; a distância de matiz entre sinal e marca; a estrutura dos três
blocos de tema; cor literal fora do `tokens.css`; a escala de sete degraus e a
grade de 4px; gradiente, brilho, vidro, borda de 1px e emoji; `var(--x)`
apontando para token que não existe; estilo escrito por JavaScript; e o sprite
de ícones — a contagem que o documento promete, e todo `HubUI.ico('i-nome')`
que pede ícone existente.

Ele tem teste negativo: trocar `--tinta` sem remedir derruba seis verificações
de uma vez, nas tabelas **e** nos comentários. Se mexer em cor e tudo passar,
desconfie do verificador antes de confiar na cor.

E a olho, o que a máquina não mede:

- [ ] **Uma** coisa sólida na tela?
- [ ] **Um** arco, e com função?
- [ ] **Uma** sobreposição?
- [ ] Todo contorno de controle é `--linha-forte`, não `--linha`?
- [ ] Verde e vermelho só onde há estado?
- [ ] Os dois temas, olhados de verdade — e o claro por último, que é onde a
      cor-chão costuma sumir?
- [ ] Teclado: `Tab` acende foco visível em tudo? `Esc` fecha modal e menu?
- [ ] 720px de largura: nada escapa, nada corta, 44px de toque?
- [ ] A tela mostra o formato do que vem, em vez de ficar em branco?
- [ ] Erro na tela espera o clique?
