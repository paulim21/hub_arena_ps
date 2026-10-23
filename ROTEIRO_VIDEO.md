# 🎬 Roteiro do Vídeo — Hub Arena (máx. 5 minutos)

## ✅ Antes de gravar (checklist)

- [ ] Servidor rodando: `venv\Scripts\activate` → `python backend/app.py`
- [ ] Navegador aberto em `http://localhost:5000` (janela limpa, sem abas extras)
- [ ] VS Code aberto na pasta do projeto, com estes arquivos já abertos em abas:
  - `backend/controllers/reserva_controller.py`
  - `backend/services/reserva_service.py`
  - `backend/models/reserva.py`
  - `backend/repositories/procedures.sql`
- [ ] Banco com poucos dados (fica mais fácil mostrar os cadastros ao vivo)
- [ ] Deixe já anotados os dados que vai digitar (nomes, e-mails, horários) para não travar
- [ ] Zoom do navegador em 100–125% e resolução de gravação 1080p

**Dica:** grave em uma tomada só, sem editar. Se errar, pause 2 segundos e refaça a frase — corta depois.

---

## 0:00 – 0:35 · Abertura + Arquitetura (VS Code)

**Mostrar:** VS Code com a árvore de pastas expandida (`backend/` e `frontend/`).

**Falar:**
> "Este é o Hub Arena, nossa plataforma de gestão de arenas de esportes de areia, feita em Flask com a arquitetura da disciplina. No backend temos as quatro camadas: **Controllers como classes**, uma por recurso…" *(clicar em `reserva_controller.py`, rolar mostrando a classe)* "…**Services com uma classe por caso de uso**…" *(clicar em `reserva_service.py`, mostrar `CriarReservaService`)* "…**Models herdando de db.Model** com o CRUD na própria model…" *(clicar em `reserva.py`, apontar `salvar`, `atualizar`, `deletar`)* "…e o **Repository**, que encapsula as consultas complexas por meio de **procedures armazenadas no banco**." *(clicar em `procedures.sql`, rolar rápido)*
>
> "O frontend é HTML e JavaScript puro consumindo a API via fetch. Vamos ver tudo funcionando."

---

## 0:35 – 1:30 · Usuários (funcionalidades 1, 2, 3 e 4)

**Mostrar:** navegador em `http://localhost:5000` → clicar em **Usuários**.

1. **Cadastrar** *(0:35)* — preencher o formulário (ex: "Ana Souza", `ana@email.com`, senha, telefone, tipo **Atleta**) e clicar em **Cadastrar usuário**.
   > "Cadastrando um usuário: a tela envia um POST em JSON para a API, o Controller chama o Service, que valida e salva pela Model. A lista atualiza sem recarregar a página."
2. **Filtrar por tipo** *(0:55)* — clicar nas pílulas **Atleta** / **Dono**.
   > "O filtro por tipo usa uma procedure no banco, chamada pelo Repository."
3. **Buscar** *(1:05)* — digitar parte de um nome ou e-mail no campo **Buscar usuário**.
   > "A busca textual por nome ou e-mail também é uma procedure, com LIKE."
4. **Excluir** *(1:15)* — excluir o usuário recém-criado? **Não ainda** — exclua um usuário sem vínculos OU tente excluir um dono com arena para mostrar o bloqueio:
   > "E se eu tentar excluir um usuário que é dono de arena, o banco bloqueia pela chave estrangeira e a API devolve uma mensagem amigável."

---

## 1:30 – 2:15 · Arenas e Quadras (funcionalidades 5 a 10)

**Mostrar:** clicar em **Arenas**.

1. **Cadastrar arena** *(1:30)* — preencher e escolher o dono no select.
   > "Toda arena exige um responsável do tipo 'dono' — essa regra de negócio fica no Service, não na Controller."
2. **Listagem com JOIN** *(1:45)* — apontar as colunas Dono e Quadras.
   > "A listagem traz o nome do dono e o total de quadras — um JOIN feito por procedure."
3. **Cadastrar quadra** *(1:55)* — ir em **Quadras**, cadastrar uma quadra na arena nova (esporte + preço/hora).
4. **Filtro por arena** *(2:05)* — clicar na pílula da arena.
   > "E aqui o filtro de quadras por arena, também via procedure."

---

## 2:15 – 3:30 · Reservas — o coração do sistema (funcionalidades 11 a 14)

**Mostrar:** clicar em **Reservas**.

1. **Criar reserva** *(2:15)* — escolher a quadra, selecionar **2 jogadores** no multi-select, escolher início e fim (ex: 1h30 de duração), **Reservar horário**.
   > "Na reserva, o servidor calcula o valor automaticamente: uma hora e meia vezes o preço da quadra. E a reserva aceita vários jogadores — uma relação N-para-N."
   >
   > *(apontar o valor na tabela)* "R$ tanto, calculado pelo backend — o frontend não manda valor nenhum."
2. **Anti-overbooking** *(2:50)* — tentar criar OUTRA reserva na mesma quadra em horário sobreposto.
   > "Agora tento reservar a mesma quadra num horário em conflito… e o sistema bloqueia: 'Horário indisponível'. Essa checagem é a procedure de conflito, chamada pelo Repository dentro do Service."
3. **Confirmar** *(3:10)* — clicar em **Confirmar** na reserva pendente (selo muda para confirmada).
   > "Confirmando a reserva — um PUT que atualiza o status."
4. **Cancelar** *(3:20)* — clicar em **Cancelar** em alguma reserva e confirmar no modal.

---

## 3:30 – 4:40 · Relatórios (funcionalidades 15 a 20)

**Mostrar:** clicar em **Relatórios**.

1. **Receita por arena** *(3:30)* — clicar em **Gerar relatório** (sem período, ou com período preenchido).
   > "Receita por arena: JOIN com GROUP BY, agregando reservas e ticket médio — tudo procedure."
2. **Ocupação + Ranking** *(3:50)* — rolar até as tabelas que já carregaram.
   > "Ocupação das quadras com horas reservadas e receita, e o ranking de atletas por jogos e horas jogadas."
3. **Quadras disponíveis** *(4:05)* — buscar primeiro um horário **ocupado** (resultado vazio), depois um horário **livre**.
   > "Busca de disponibilidade: no horário que acabei de reservar, nenhuma quadra livre. Num horário vago, ela aparece. É um NOT EXISTS no banco."
4. **Agenda da arena** *(4:25)* — escolher a arena e clicar em **Ver agenda**.
   > "E a agenda completa da arena no período."

---

## 4:40 – 5:00 · Encerramento

**Mostrar:** README no GitHub (ou no VS Code), rolando pela seção **Funcionalidades Implementadas**.

**Falar:**
> "Todas as funcionalidades estão enumeradas no README — são 20, todas de ponta a ponta: tela, API, Controller, Service, Model ou Repository e banco. O código completo está no repositório. Obrigado!"

---

## 🎯 Mapa rápido: funcionalidade → momento do vídeo

| # | Funcionalidade | Momento |
|---|----------------|---------|
| 1 | Cadastrar usuário | 0:35 |
| 2 | Listar/filtrar usuários por tipo | 0:55 |
| 3 | Buscar usuários (LIKE) | 1:05 |
| 4 | Excluir usuário (com bloqueio FK) | 1:15 |
| 5 | Cadastrar arena (validação de dono) | 1:30 |
| 6 | Listar arenas com dono + nº quadras | 1:45 |
| 7 | Excluir arena | (citar na fala de FKs) |
| 8 | Cadastrar quadra | 1:55 |
| 9 | Listar quadras por arena | 2:05 |
| 10 | Excluir quadra | (opcional, se sobrar tempo) |
| 11 | Criar reserva (valor automático + anti-overbooking + N jogadores) | 2:15–3:05 |
| 12 | Listar reservas detalhadas | 2:45 |
| 13 | Confirmar reserva | 3:10 |
| 14 | Cancelar reserva | 3:20 |
| 15 | Dashboard (mostrar de passagem ao abrir o site) | 0:35 |
| 16 | Receita por arena | 3:30 |
| 17 | Ocupação das quadras | 3:50 |
| 18 | Ranking de atletas | 3:55 |
| 19 | Quadras disponíveis por período | 4:05 |
| 20 | Agenda da arena | 4:25 |
