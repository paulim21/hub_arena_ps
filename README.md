# ArenaHub

Plataforma Vertical SaaS de gestão de arenas de esportes de areia: usuários,
arenas, quadras e reservas com **anti-overbooking**, **valor calculado
automaticamente** e **relatórios via procedures no banco**.

- **Backend:** Flask (API REST) + Flask-SQLAlchemy + SQLite
- **Frontend:** HTML + CSS + JavaScript puro (sem Jinja2 / render_template),
  consumindo a API via `fetch` — com sistema de design próprio, tema claro e
  escuro e **43 ícones em traço** (nenhum emoji na interface)

## Funcionalidades Implementadas

Todas disponíveis de ponta a ponta
(**Tela → API Flask → Controller → Service → Model/Repository → Banco**):

1. **Cadastrar usuário** (tela `/usuarios` → `POST /api/usuarios`)
2. **Listar usuários com filtro por tipo** (atleta/dono/professor — procedure `sp_usuarios_por_tipo`)
3. **Buscar usuários por nome ou e-mail** (LIKE — procedure `sp_busca_usuarios`, usada pela tela `/busca`)
4. **Excluir usuário** (com bloqueio por vínculos via FK — `DELETE /api/usuarios/<id>`)
5. **Cadastrar arena** (com validação de dono do tipo 'dono' — `POST /api/arenas`)
6. **Listar arenas com dono e contagem de quadras** (JOIN — procedure `sp_arenas_com_dono`)
7. **Excluir arena** (com bloqueio por quadras vinculadas)
8. **Cadastrar quadra** (com validação da arena — `POST /api/quadras`)
9. **Listar quadras com filtro por arena** (JOIN — procedures `sp_quadras_com_arena` / `sp_quadras_por_arena`)
10. **Excluir quadra** (com bloqueio por reservas vinculadas)
11. **Criar reserva com anti-overbooking e valor automático** (procedure `sp_conflito_reserva`; valor = horas × preço/hora; vários jogadores por reserva — N:N)
12. **Listar reservas detalhadas** (JOIN triplo + jogadores — procedures `sp_reservas_detalhadas` / `sp_jogadores_da_reserva`)
13. **Confirmar reserva** (atualização de status — `PUT /api/reservas/<id>`)
14. **Cancelar reserva** (`DELETE /api/reservas/<id>`)
15. **Dashboard com resumo e atividade recente** (procedures `sp_resumo_dashboard` / `sp_reservas_recentes`)
16. **Relatório de receita por arena com período** (JOIN + GROUP BY — procedure `sp_receita_por_arena`)
17. **Relatório de ocupação das quadras** (horas e receita por quadra — procedure `sp_ocupacao_quadras`)
18. **Ranking de atletas** (jogos e horas jogadas — procedure `sp_ranking_atletas`)
19. **Busca de quadras disponíveis por período** (NOT EXISTS — procedure `sp_quadras_disponiveis`)
20. **Agenda da arena por período** (procedure `sp_agenda_arena`)
21. **Registrar consentimento LGPD** (modal bloqueante — `POST /api/consentimentos`; recusa consentimento genérico e versão desatualizada)
22. **Verificar consentimento vigente** (procedure `sp_consentimento_vigente` — libera ou bloqueia o uso do sistema)
23. **Revogar consentimento** (`POST /api/consentimentos/revogar` — tela `/termos`, Art. 8º, § 5º)
24. **Relatório de consentimentos por versão** (procedure `sp_consentimentos_por_versao` — a prova agregada do Art. 8º, § 1º)
25. **Busca global** (tela `/busca` — um termo, três procedures: `sp_busca_usuarios`, `sp_busca_arenas` e `sp_busca_quadras`; o resultado vai para a URL e pode ser compartilhado)

## Diagrama de classes

O diagrama de classes do domínio está na pasta [`docs/`](docs):

| Arquivo | O que é |
|---------|---------|
| [`docs/diagrama-classes.md`](docs/diagrama-classes.md) | Diagrama + explicação da **herança**, **composição**, **agregação** e da relação **N:N**, com a tabela de FKs correspondente no banco |
| [`docs/diagrama-classes.svg`](docs/diagrama-classes.svg) | Mesma versão em imagem (para slides e para o vídeo) |
| [`docs/guia-sistema.pdf`](docs/guia-sistema.pdf) | **Guia do sistema** (15 páginas): o caminho de uma requisição, backend camada por camada, o banco, o frontend, as 20 procedures, a tabela das 25 funcionalidades e as perguntas prováveis da banca |

Ele representa as cinco Models de [`backend/models/`](backend/models) —
`Usuario`, `Arena`, `Quadra`, `Reserva` e `ReservaJogador` — todas herdando de
`db.Model`, com `Arena ◆— Quadra` e `Reserva ◆— ReservaJogador` como
composições e as demais ligações como agregações.

## Arquitetura (padrão do material da disciplina)

```
Tela (frontend/ — HTML + JS puro, fetch nas rotas /api/...)
   │
   ▼
Controller  (backend/controllers/ — CLASSES, uma por recurso)
   │
   ▼
Service     (backend/services/ — uma CLASSE por caso de uso, método executar())
   │
   ├──▶ Model       (backend/models/ — herdam de db.Model; CRUD básico na própria Model:
   │                 salvar, atualizar, deletar, listar_todos, buscar_por_id)
   │
   └──▶ Repository  (backend/repositories/ — consultas complexas via PROCEDURES)
              │
              ▼
        SQLite (hub_arena.db — dados + tabela `procedures`)
```

### Organização das pastas

```
backend/
    controllers/            ← UsuarioController, ArenaController, QuadraController,
                              ReservaController, RelatorioController (classes)
    services/               ← um Service (classe) por caso de uso
    models/                 ← Usuario, Arena, Quadra, Reserva, ReservaJogador (db.Model)
    repositories/           ← procedures.sql + procedure_runner + repositories
    politica.py             ← a versão e as finalidades dos termos, num lugar só
    routes.py               ← mapa de rotas: URLs → métodos das Controllers
    extensions.py           ← objeto db (Flask-SQLAlchemy)
    app.py                  ← Application Factory
    database.py             ← registro das procedures no banco
frontend/
    index.html, usuarios.html, arenas.html, quadras.html, reservas.html, relatorios.html
    css/tokens.css          ← TODOS os valores da identidade (cor, texto, espaço)
    css/estilo.css          ← só componentes, nenhuma cor literal
    js/tema.js              ← tema e densidade, antes da primeira pintura
    js/base.js              ← fetch, ícones, <dialog>, menus e formatos
    js/interface.js         ← esqueleto, barra de progresso e paleta do Ctrl+K
    js/lgpd.js              ← o aviso de aceite que bloqueia o uso
    termos.html             ← a política de privacidade completa
    img/icones.svg          ← os 43 ícones em traço (a fonte do sprite)
    img/favicon.svg         ← o monograma AH
    img/logo.png            ← o logotipo (+ logo-escuro.png, para o tema escuro)
docs/
    diagrama-classes.md     ← diagrama de classes do domínio (+ .svg)
    guia-sistema.pdf        ← o guia completo, para a apresentação
    design/PADROES.md       ← os padrões de interface
    design/verificar-identidade.py  ← mede o contrato das cores
IDENTIDADE_VISUAL.md        ← o porquê das cores, com as tabelas de contraste
```

> **Sobre as procedures no SQLite:** o SQLite é um banco embarcado e não possui
> `CREATE PROCEDURE` (recurso de SGBDs cliente-servidor como MySQL). Para atender
> ao requisito, as procedures são **armazenadas no próprio banco**, na tabela
> `procedures` (nome + SQL parametrizado), registradas na subida do servidor a
> partir de [`backend/repositories/procedures.sql`](backend/repositories/procedures.sql).
> O **CALL fica encapsulado no Repository**, via
> [`procedure_runner.py`](backend/repositories/procedure_runner.py) —
> Controller e Service nunca executam SQL diretamente.

## Privacidade e LGPD

O sistema **não abre antes do aceite dos termos**: um aviso bloqueante
([`frontend/js/lgpd.js`](frontend/js/lgpd.js)) segura toda chamada à API até
que exista consentimento registrado. A página
[`/termos`](frontend/termos.html) é a única isenta — exigir aceite para *ler* a
política seria pedir consentimento no escuro.

O que foi levado a sério, e por quê:

- **O consentimento é comprovável** (Art. 8º, § 1º). Cada aceite vira uma linha
  na tabela `consentimentos`, com a versão dos termos, data, IP e navegador.
  Um sinalizador no `localStorage` não comprova nada.
- **É pedido por finalidade** (Art. 8º, § 4º), não num bloco só: consentimento
  genérico é nulo.
- **A versão governa**: se a política mudar, a versão sobe e o aceite é pedido
  de novo (Art. 8º, § 6º). A versão vive num lugar só,
  [`backend/politica.py`](backend/politica.py), e o front-end a consulta.
- **Revogar é possível, gratuito e não apaga o registro** (Art. 8º, § 5º): a
  linha é marcada como revogada, porque ela é a prova — inclusive da revogação.
- **Recusar é possível**, e a consequência está escrita na tela.
- **Senhas não são guardadas**: vai para o banco um resumo criptográfico com
  sal (scrypt), medida de segurança do Art. 46.
- **Sem cookies, sem rastreamento**: o navegador guarda só um identificador
  aleatório do consentimento e as preferências de aparência.

> **Atenção:** o texto dos termos é um modelo para trabalho acadêmico, com
> marcadores onde faltam os dados reais do controlador e do encarregado. Antes
> de qualquer uso real, precisa de revisão jurídica.

## Identidade visual

O front-end tem um sistema de design documentado e **verificado por máquina**:

- [`IDENTIDADE_VISUAL.md`](IDENTIDADE_VISUAL.md) — o porquê de cada decisão e as
  tabelas de contraste (WCAG 2.1), que são **contrato**.
- [`frontend/css/tokens.css`](frontend/css/tokens.css) — todos os valores. Fora
  dele não existe cor, tamanho, espaço, raio, borda ou duração literal.
- [`docs/design/PADROES.md`](docs/design/PADROES.md) — como
  trabalhar nele: o que já existe, o que não fazer, e as armadilhas conhecidas.

A marca vem da logo: **navy escreve, a areia é chão**, sobre papel creme. Tema
claro e escuro medidos separadamente, densidade confortável/compacta, foco
visível de duas cores e 44px de área de toque no celular.

A tela nunca fica em branco esperando o servidor: cada painel mostra um
**esqueleto** com a estrutura do que vem, e uma barra de progresso acende no
topo depois de 120ms. **Ctrl+K** abre uma paleta de navegação montada a partir
do próprio menu da página.

**Nenhum emoji na interface.** Emoji muda de forma entre aparelhos, não aceita
o peso do traço da marca e não herda cor — no lugar dele vão os 43 ícones de
[`frontend/img/icones.svg`](frontend/img/icones.svg), em `viewBox 24` e
`stroke-width 1.8`.

Para conferir que nada saiu do contrato (224 verificações):

```bash
python docs/design/verificar-identidade.py
```

E, depois de mexer no sprite de ícones:

```bash
python docs/design/embutir-icones.py
```

## Rotas da API

| Método | Rota | Descrição |
|--------|------|-----------|
| GET/POST | `/api/usuarios` | Lista (filtro `?tipo=`) / cria |
| GET | `/api/usuarios/busca?q=` | Busca por nome ou e-mail (LIKE) |
| GET/PUT/DELETE | `/api/usuarios/<id>` | Busca / atualiza / remove |
| GET/POST | `/api/arenas` | Lista (`?detalhes=1` = JOIN dono, `?cidade=`) / cria |
| GET | `/api/arenas/<id>/agenda` | Agenda da arena no período |
| GET/PUT/DELETE | `/api/arenas/<id>` | Busca / atualiza / remove |
| GET/POST | `/api/quadras` | Lista (`?detalhes=1`, `?arena_id=`) / cria |
| GET | `/api/quadras/disponiveis` | Quadras livres no período |
| GET/PUT/DELETE | `/api/quadras/<id>` | Busca / atualiza / remove |
| GET/POST | `/api/reservas` | Lista (`?detalhes=1` = JOIN triplo) / cria (anti-overbooking) |
| GET/PUT/DELETE | `/api/reservas/<id>` | Busca / muda status / remove |
| GET | `/api/relatorios/resumo` | Contadores + receita total |
| GET | `/api/relatorios/reservas-recentes` | Últimas reservas (dashboard) |
| GET | `/api/relatorios/receita-arenas` | Receita por arena no período |
| GET | `/api/relatorios/ocupacao-quadras` | Ocupação por quadra |
| GET | `/api/relatorios/ranking-atletas` | Ranking de atletas |
| GET | `/api/consentimentos/politica` | Versão e finalidades vigentes dos termos |
| GET | `/api/consentimentos/vigente?identificador=` | Este navegador já aceitou? |
| POST | `/api/consentimentos` | Registra o aceite (com versão, IP e navegador) |
| POST | `/api/consentimentos/revogar` | Revoga o consentimento |
| GET | `/api/consentimentos/relatorio` | Aceites, vigentes e revogados por versão |
| GET | `/api/busca?q=` | Busca global em usuários, arenas e quadras |

## Telas do frontend

| Página | O que faz |
|--------|-----------|
| `/` | Visão geral: contadores animados, receita total e atividade recente |
| `/busca` | **Busca global**: um termo procurado em usuários, arenas e quadras ao mesmo tempo |
| `/usuarios` | Tabela + cadastro + filtro por tipo + exclusão |
| `/arenas` | Tabela com dono e nº de quadras + cadastro + exclusão |
| `/quadras` | Tabela com arena + filtro por arena + cadastro + exclusão |
| `/reservas` | Agenda com anti-overbooking, valor automático, confirmar/cancelar |
| `/relatorios` | Receita por arena, ocupação, ranking, quadras disponíveis, agenda e consentimentos LGPD |
| `/termos` | Política de privacidade completa, com revogação do consentimento |

## Regras de negócio

- **Arena precisa de dono**: só usuários do tipo `dono` podem ser responsáveis.
- **Quadra pertence a uma arena**: validação de FK na API e fluxo guiado no painel.
- **Anti-overbooking**: reservas com horário em conflito na mesma quadra são
  bloqueadas (procedure `sp_conflito_reserva`, encapsulada no Repository).
- **Valor automático**: `horas × preço/hora da quadra`, calculado pelo servidor.
- **Reserva com vários jogadores**: tabela N:N `reserva_jogadores`.
- **Exclusões protegidas**: FKs impedem excluir registros com vínculos, com
  mensagem amigável na tela.
- **CPF, CNPJ, telefone e e-mail têm forma conferida** em
  [`backend/validadores.py`](backend/validadores.py): os **dígitos
  verificadores** de CPF e CNPJ são calculados, o telefone exige DDD e o
  e-mail é normalizado para minúsculas (senão `Ana@x.com` e `ana@x.com` viram
  duas contas da mesma pessoa). O banco guarda **só os dígitos**; a máscara
  `000.000.000-00` é aplicada ao digitar, pelo `data-mascara` do campo, e a
  formatação para leitura acontece na tela.

## Conferindo que tudo funciona

Duas verificações, as duas sem subir servidor e sem tocar o banco de verdade:

```bash
python backend/verificar_api.py
```

Percorre a API de ponta a ponta num banco descartável — 77 verificações, das
regras de negócio (anti-overbooking, valor calculado no servidor) às de
privacidade (o CPF não aparece na busca, a senha não fica em texto puro).

```bash
python docs/design/verificar-identidade.py
```

Mede o contrato visual: 224 verificações de contraste, escala, grade,
cor literal fora do `tokens.css`, emoji e a contagem de ícones.

## Como rodar

```bash
python -m venv venv
venv\Scripts\activate     # Windows  (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
python backend/app.py
```

- Painel web: http://localhost:5000
- API JSON: http://localhost:5000/api/usuarios (teste com Postman/curl)

O arquivo `backend/hub_arena.db` é criado automaticamente na primeira execução,
já com as tabelas (via `db.create_all()`) e as procedures registradas.
Para usar outra porta, defina a variável de ambiente `PORT`.
