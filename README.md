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
3. **Buscar usuários por nome ou e-mail** (LIKE — procedure `sp_busca_usuarios`)
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

## Diagrama de classes

O diagrama de classes do domínio está na pasta [`docs/`](docs):

| Arquivo | O que é |
|---------|---------|
| [`docs/diagrama-classes.md`](docs/diagrama-classes.md) | Diagrama + explicação da **herança**, **composição**, **agregação** e da relação **N:N**, com a tabela de FKs correspondente no banco |
| [`docs/diagrama-classes.svg`](docs/diagrama-classes.svg) | Mesma versão em imagem (para slides e para o vídeo) |

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
    img/icones.svg          ← os 43 ícones em traço (a fonte do sprite)
    img/favicon.svg         ← o monograma AH
    img/logo.png            ← o logotipo (+ logo-escuro.png, para o tema escuro)
docs/
    diagrama-classes.md     ← diagrama de classes do domínio (+ .svg)
IDENTIDADE_VISUAL.md        ← o porquê das cores, com as tabelas de contraste
.claude/skills/design/      ← a skill de design + o verificador da identidade
```

> **Sobre as procedures no SQLite:** o SQLite é um banco embarcado e não possui
> `CREATE PROCEDURE` (recurso de SGBDs cliente-servidor como MySQL). Para atender
> ao requisito, as procedures são **armazenadas no próprio banco**, na tabela
> `procedures` (nome + SQL parametrizado), registradas na subida do servidor a
> partir de [`backend/repositories/procedures.sql`](backend/repositories/procedures.sql).
> O **CALL fica encapsulado no Repository**, via
> [`procedure_runner.py`](backend/repositories/procedure_runner.py) —
> Controller e Service nunca executam SQL diretamente.

## Identidade visual

O front-end tem um sistema de design documentado e **verificado por máquina**:

- [`IDENTIDADE_VISUAL.md`](IDENTIDADE_VISUAL.md) — o porquê de cada decisão e as
  tabelas de contraste (WCAG 2.1), que são **contrato**.
- [`frontend/css/tokens.css`](frontend/css/tokens.css) — todos os valores. Fora
  dele não existe cor, tamanho, espaço, raio, borda ou duração literal.
- [`.claude/skills/design/SKILL.md`](.claude/skills/design/SKILL.md) — como
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
python .claude/skills/design/verificar-identidade.py
```

E, depois de mexer no sprite de ícones:

```bash
python .claude/skills/design/embutir-icones.py
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

## Telas do frontend

| Página | O que faz |
|--------|-----------|
| `/` | Visão geral: contadores animados, receita total e atividade recente |
| `/usuarios` | Tabela + cadastro + filtro por tipo + **busca por nome/e-mail** + exclusão |
| `/arenas` | Tabela com dono e nº de quadras + cadastro + exclusão |
| `/quadras` | Tabela com arena + filtro por arena + cadastro + exclusão |
| `/reservas` | Agenda com anti-overbooking, valor automático, confirmar/cancelar |
| `/relatorios` | Receita por arena, ocupação, ranking, quadras disponíveis e agenda |

## Regras de negócio

- **Arena precisa de dono**: só usuários do tipo `dono` podem ser responsáveis.
- **Quadra pertence a uma arena**: validação de FK na API e fluxo guiado no painel.
- **Anti-overbooking**: reservas com horário em conflito na mesma quadra são
  bloqueadas (procedure `sp_conflito_reserva`, encapsulada no Repository).
- **Valor automático**: `horas × preço/hora da quadra`, calculado pelo servidor.
- **Reserva com vários jogadores**: tabela N:N `reserva_jogadores`.
- **Exclusões protegidas**: FKs impedem excluir registros com vínculos, com
  mensagem amigável na tela.

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
