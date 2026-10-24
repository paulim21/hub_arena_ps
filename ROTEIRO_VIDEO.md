# Roteiro do Vídeo — ArenaHub (máx. 5 minutos)

São **24 funcionalidades** em 5 minutos: 12 segundos cada, se fossem iguais.
Não são. O roteiro abaixo dá tempo cheio ao que é difícil (reserva com
anti-overbooking, consentimento comprovável) e passa rápido pelo que é CRUD.
O que não couber em demonstração aparece **citado em voz**, com a tela já
mostrando o resultado.

## Antes de gravar (checklist)

- [ ] Servidor rodando: `venv\Scripts\activate` → `python backend/app.py`
- [ ] **O navegador NÃO pode ter consentimento guardado** — senão o aviso de
      abertura não aparece. Use uma **janela anônima**, ou abra o console
      (F12) e rode:
      ```js
      localStorage.removeItem('arenahub:consentimento')
      ```
- [ ] Banco **com alguns dados** (1 dono, 2 atletas, 1 arena, 2 quadras,
      1 reserva confirmada). Assim os relatórios não aparecem vazios, e ainda
      sobra o que cadastrar ao vivo.
- [ ] VS Code aberto na pasta do projeto, com estes arquivos já em abas:
  - `backend/controllers/reserva_controller.py`
  - `backend/services/reserva_service.py`
  - `backend/models/reserva.py`
  - `backend/repositories/procedures.sql`
  - `backend/services/consentimento_service.py`
- [ ] Dados que vai digitar já anotados (nome, e-mail, **senha com 6+
      caracteres**, horários) para não travar na hora
- [ ] Zoom do navegador em 100–125%, gravação em 1080p

**Dica:** grave em uma tomada só. Se errar, pause 2 segundos e refaça a frase —
corta depois.

---

## 0:00 – 0:25 · Abertura: o sistema não abre sem consentimento (21, 22)

**Mostrar:** abrir `http://localhost:5000`. O aviso de consentimento aparece
sozinho, por cima de tudo.

1. **Apontar que a tela atrás está vazia** *(0:00)*
   > "Esta é a primeira coisa que o ArenaHub faz: pedir consentimento. E repare
   > na tela atrás — os painéis estão vazios. Não é só o visual que está
   > bloqueado: **nenhuma chamada à API acontece** antes do aceite."

2. **Clicar em "Não aceito"** *(0:10)* — aparece a explicação da consequência.
   > "Recusar é um direito, e a consequência precisa estar escrita: sem o
   > aceite, o sistema não abre." *(clicar em **Voltar**)*

3. **Marcar a caixa e aceitar** *(0:18)* — os dados aparecem atrás.
   > "Aceitei, e agora os dados carregam. Esse aceite foi **gravado no banco**
   > com a versão dos termos, data, IP e navegador — porque a LGPD exige que o
   > controlador **comprove** o consentimento, e um flag no navegador não
   > comprova nada."

---

## 0:25 – 0:55 · Arquitetura (VS Code)

**Mostrar:** VS Code com `backend/` e `frontend/` expandidos.

> "A arquitetura é a da disciplina, em camadas. **Controllers são classes**,
> uma por recurso…" *(abrir `reserva_controller.py`)* "…que só recebem a
> requisição e chamam o Service. **Um Service por caso de uso**…"
> *(abrir `reserva_service.py`, mostrar `CriarReservaService`)* "…é aqui que
> mora a regra de negócio. As **Models herdam de `db.Model`** e guardam o CRUD
> básico…" *(abrir `reserva.py`, apontar `salvar`, `atualizar`, `deletar`)*
> "…e o **Repository** encapsula as consultas complexas em **procedures
> armazenadas no banco**." *(abrir `procedures.sql`, rolar rápido)*
>
> "O frontend é HTML e JavaScript puro, consumindo a API por fetch."

---

## 0:55 – 1:40 · Usuários (1 a 4)

**Mostrar:** clicar em **Usuários**.

1. **Cadastrar** *(0:55)* — preencher e enviar.
   > "A tela manda um POST em JSON; o Controller chama o Service, que valida e
   > salva pela Model. A lista atualiza sem recarregar a página."
   >
   > *(opcional, se sobrar fôlego)* "E a senha não é guardada como foi
   > digitada: vai para o banco como resumo criptográfico."
2. **Filtrar por tipo** *(1:15)* — clicar nas pílulas **Atleta** / **Dono**.
   > "O filtro por tipo é uma procedure, chamada pelo Repository."
3. **Buscar** *(1:25)* — digitar parte de um nome no campo de busca.
   > "A busca por nome ou e-mail também é procedure, com LIKE."
4. **Excluir com vínculo** *(1:33)* — tentar excluir um **dono que tem arena**.
   > "Excluindo um dono que tem arena, o banco bloqueia pela chave
   > estrangeira, e a API devolve uma mensagem que dá para entender."

---

## 1:40 – 2:20 · Arenas e Quadras (5 a 10)

1. **Cadastrar arena** *(1:40)* — escolher o dono no menu.
   > "Toda arena exige um responsável do tipo 'dono' — essa regra está no
   > Service, não na Controller."
2. **Listagem com JOIN** *(1:55)* — apontar as colunas **Dono** e **Quadras**.
   > "Nome do dono e total de quadras vêm de um JOIN feito por procedure."
3. **Cadastrar quadra** *(2:02)* — em **Quadras**, criar uma na arena nova.
4. **Filtro por arena** *(2:12)* — clicar na pílula da arena.
   > "Filtro de quadras por arena, também por procedure. E excluir arena ou
   > quadra com vínculo é bloqueado do mesmo jeito que o usuário."

---

## 2:20 – 3:25 · Reservas — o coração do sistema (11 a 14)

1. **Criar reserva** *(2:20)* — escolher a quadra, **2 jogadores** no
   multi-select, início e fim com 1h30 de duração.
   > "A reserva aceita vários jogadores — é uma relação N-para-N. E o valor
   > **o servidor calcula**: uma hora e meia vezes o preço da quadra."
   >
   > *(apontar o valor na tabela)* "Este valor veio do backend. O frontend não
   > manda valor nenhum — se mandasse, dava para forjar o preço."
2. **Anti-overbooking** *(2:55)* — tentar outra reserva na **mesma quadra em
   horário sobreposto**.
   > "Agora o mesmo horário, na mesma quadra… e o sistema bloqueia. A checagem
   > de conflito é uma procedure, chamada pelo Repository dentro do Service."
3. **Confirmar** *(3:12)* — o selo muda para **Confirmada**.
4. **Cancelar** *(3:19)* — confirmar no modal.

---

## 3:25 – 4:20 · Relatórios (15 a 20)

**Mostrar:** clicar em **Relatórios**.

1. **Receita por arena** *(3:25)* — **Gerar relatório**.
   > "Receita por arena: JOIN com GROUP BY, agregando reservas e ticket médio."
2. **Ocupação e ranking** *(3:45)* — rolar até as tabelas já carregadas.
   > "Ocupação por quadra, com horas e receita — o arco mostra cada quadra
   > contra a mais ocupada. E o ranking de atletas por jogos e horas."
3. **Quadras disponíveis** *(4:00)* — buscar um horário **ocupado** (vazio) e
   depois um **livre**.
   > "No horário que acabei de reservar, nenhuma quadra livre; num horário
   > vago, ela aparece. É um NOT EXISTS no banco."
4. **Agenda da arena** *(4:12)* — escolher a arena e **Ver agenda**.

> O **dashboard** (funcionalidade 15) já apareceu na abertura — basta citar:
> "os contadores e a receita da tela inicial também vêm de procedure."

---

## 4:20 – 4:45 · A prova do consentimento (23 e 24)

1. **Relatório de consentimentos** *(4:20)* — ainda em **Relatórios**, rolar
   até o último painel.
   > "E este é o lado que quase ninguém mostra: **aceites por versão dos
   > termos**, quantos estão vigentes e quantos foram revogados. É a prova
   > agregada que o Art. 8º exige."
2. **Termos e revogação** *(4:32)* — clicar em **Termos e privacidade** no
   rodapé, rolar rápido pela política e parar no item 9.
   > "A política inteira está aqui — o que é coletado, para quê, com que base
   > legal e por quanto tempo. E a revogação é um botão: ela não apaga o
   > registro, marca como revogado, porque o registro é a prova — inclusive da
   > própria revogação."

---

## 4:45 – 5:00 · Encerramento

**Mostrar:** README, na seção **Funcionalidades Implementadas**.

> "São 24 funcionalidades, todas de ponta a ponta: tela, API, Controller,
> Service, Model ou Repository e banco. O diagrama de classes está em `docs/`,
> e o código completo no repositório. Obrigado!"

---

## Mapa rápido: funcionalidade → momento do vídeo

| # | Funcionalidade | Momento |
|---|----------------|---------|
| 1 | Cadastrar usuário | 0:55 |
| 2 | Listar/filtrar usuários por tipo | 1:15 |
| 3 | Buscar usuários (LIKE) | 1:25 |
| 4 | Excluir usuário (com bloqueio FK) | 1:33 |
| 5 | Cadastrar arena (validação de dono) | 1:40 |
| 6 | Listar arenas com dono + nº quadras | 1:55 |
| 7 | Excluir arena | (citado em 2:12) |
| 8 | Cadastrar quadra | 2:02 |
| 9 | Listar quadras por arena | 2:12 |
| 10 | Excluir quadra | (citado em 2:12) |
| 11 | Criar reserva (valor automático + anti-overbooking + N jogadores) | 2:20–3:10 |
| 12 | Listar reservas detalhadas | 2:50 |
| 13 | Confirmar reserva | 3:12 |
| 14 | Cancelar reserva | 3:19 |
| 15 | Dashboard | 0:18 (abertura) + citado em 4:12 |
| 16 | Receita por arena | 3:25 |
| 17 | Ocupação das quadras | 3:45 |
| 18 | Ranking de atletas | 3:52 |
| 19 | Quadras disponíveis por período | 4:00 |
| 20 | Agenda da arena | 4:12 |
| 21 | Registrar consentimento LGPD | 0:18 |
| 22 | Verificar consentimento (bloqueio do sistema) | 0:00 |
| 23 | Revogar consentimento | 4:32 |
| 24 | Relatório de consentimentos por versão | 4:20 |

---

## Se o tempo apertar

Corte **nesta ordem**, que é a do menos custoso para a nota:

1. O "Não aceito" da abertura (0:10) — o bloqueio já se vê na tela vazia.
2. A busca de usuários (1:25) — o filtro por tipo já mostra procedure.
3. A agenda da arena (4:12) — é parecida com a listagem de reservas.

E **não corte**, porque são o que diferencia o trabalho: o valor calculado no
servidor, o anti-overbooking, o relatório de consentimentos e a revogação.
