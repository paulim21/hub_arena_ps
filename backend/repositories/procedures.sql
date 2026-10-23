-- ============================================================
-- PROCEDURES DO ARENAHUB
--
-- O SQLite não possui CREATE PROCEDURE (é um banco embarcado).
-- Por isso, cada procedure abaixo é armazenada NA TABELA `procedures`
-- DO PRÓPRIO BANCO e executada pelo runner da camada Repository
-- (repositories/procedure_runner.py), que faz o papel do CALL.
-- Parâmetros usam a sintaxe :nome (placeholders nomeados).
-- ============================================================


-- PROCEDURE: sp_usuarios_por_tipo
-- Filtro por tipo de usuário (WHERE + ORDER BY). Parâmetros: :tipo
SELECT usuario_id, nome, email, telefone, tipo_usuario, data_criacao
FROM usuarios
WHERE tipo_usuario = :tipo
ORDER BY nome;

-- PROCEDURE: sp_busca_usuarios
-- Busca textual por nome ou e-mail (LIKE + ORDER BY). Parâmetros: :termo
SELECT usuario_id, nome, email, telefone, tipo_usuario, data_criacao
FROM usuarios
WHERE nome  LIKE '%' || :termo || '%'
   OR email LIKE '%' || :termo || '%'
ORDER BY nome;

-- PROCEDURE: sp_arenas_por_cidade
-- Filtro de arenas por cidade (LIKE + ORDER BY). Parâmetros: :cidade
SELECT *
FROM arenas
WHERE cidade LIKE '%' || :cidade || '%'
ORDER BY nome;

-- PROCEDURE: sp_arenas_com_dono
-- Arenas com o nome do dono (JOIN) e total de quadras (subconsulta). Sem parâmetros.
SELECT a.*, u.nome AS nome_dono,
       (SELECT COUNT(*) FROM quadras q WHERE q.arena_id = a.arena_id) AS total_quadras
FROM arenas a
JOIN usuarios u ON u.usuario_id = a.dono_id
ORDER BY a.nome;

-- PROCEDURE: sp_quadras_com_arena
-- Quadras com dados da arena (JOIN + ORDER BY). Sem parâmetros.
SELECT q.*, a.nome AS nome_arena, a.cidade
FROM quadras q
JOIN arenas a ON a.arena_id = q.arena_id
ORDER BY a.nome, q.nome;

-- PROCEDURE: sp_quadras_por_arena
-- Quadras de uma arena específica (JOIN + WHERE). Parâmetros: :arena_id
SELECT q.*, a.nome AS nome_arena, a.cidade
FROM quadras q
JOIN arenas a ON a.arena_id = q.arena_id
WHERE q.arena_id = :arena_id
ORDER BY q.nome;

-- PROCEDURE: sp_conflito_reserva
-- Regra anti-overbooking: reservas que colidem com o período informado.
-- Parâmetros: :quadra_id, :inicio, :fim
SELECT reserva_id
FROM reservas
WHERE quadra_id = :quadra_id
  AND data_hora_inicio < :fim
  AND data_hora_fim > :inicio;

-- PROCEDURE: sp_reservas_detalhadas
-- Agenda completa com quadra e arena (JOIN triplo + ORDER BY). Sem parâmetros.
SELECT r.*, q.nome AS nome_quadra, q.tipo_esporte,
       a.nome AS nome_arena
FROM reservas r
JOIN quadras q ON q.quadra_id = r.quadra_id
JOIN arenas  a ON a.arena_id  = q.arena_id
ORDER BY r.data_hora_inicio DESC;

-- PROCEDURE: sp_reservas_recentes
-- Últimas reservas para o dashboard (JOIN triplo + LIMIT). Parâmetros: :limite
SELECT r.reserva_id, r.data_hora_inicio, r.valor_total, r.status,
       q.nome AS nome_quadra, q.tipo_esporte,
       a.nome AS nome_arena,
       (SELECT GROUP_CONCAT(u.nome, ', ')
        FROM reserva_jogadores rj
        JOIN usuarios u ON u.usuario_id = rj.usuario_id
        WHERE rj.reserva_id = r.reserva_id) AS nome_usuario
FROM reservas r
JOIN quadras q ON q.quadra_id = r.quadra_id
JOIN arenas  a ON a.arena_id  = q.arena_id
ORDER BY r.reserva_id DESC
LIMIT :limite;

-- PROCEDURE: sp_jogadores_da_reserva
-- Nomes dos jogadores de uma reserva (JOIN N:N). Parâmetros: :reserva_id
SELECT u.usuario_id, u.nome
FROM reserva_jogadores rj
JOIN usuarios u ON u.usuario_id = rj.usuario_id
WHERE rj.reserva_id = :reserva_id
ORDER BY u.nome;

-- PROCEDURE: sp_resumo_dashboard
-- Contadores gerais + receita total (subconsultas agregadas). Sem parâmetros.
SELECT (SELECT COUNT(*) FROM usuarios)                       AS total_usuarios,
       (SELECT COUNT(*) FROM arenas)                         AS total_arenas,
       (SELECT COUNT(*) FROM quadras)                        AS total_quadras,
       (SELECT COUNT(*) FROM reservas)                       AS total_reservas,
       (SELECT COALESCE(SUM(valor_total), 0) FROM reservas)  AS receita_total;

-- PROCEDURE: sp_receita_por_arena
-- RELATÓRIO: receita agregada por arena no período (JOIN + GROUP BY + ORDER BY).
-- Parâmetros: :inicio, :fim
SELECT a.arena_id, a.nome AS nome_arena, a.cidade,
       COUNT(r.reserva_id)                 AS total_reservas,
       COALESCE(SUM(r.valor_total), 0)     AS receita,
       COALESCE(AVG(r.valor_total), 0)     AS ticket_medio
FROM arenas a
LEFT JOIN quadras  q ON q.arena_id  = a.arena_id
LEFT JOIN reservas r ON r.quadra_id = q.quadra_id
                    AND r.data_hora_inicio >= :inicio
                    AND r.data_hora_inicio <= :fim
GROUP BY a.arena_id, a.nome, a.cidade
ORDER BY receita DESC;

-- PROCEDURE: sp_ocupacao_quadras
-- RELATÓRIO: ocupação por quadra — reservas, horas e receita (JOIN + GROUP BY).
-- Sem parâmetros.
SELECT q.quadra_id, q.nome AS nome_quadra, q.tipo_esporte, q.preco_hora,
       a.nome AS nome_arena,
       COUNT(r.reserva_id) AS total_reservas,
       COALESCE(ROUND(SUM(
           (julianday(r.data_hora_fim) - julianday(r.data_hora_inicio)) * 24
       ), 1), 0)           AS horas_reservadas,
       COALESCE(SUM(r.valor_total), 0) AS receita
FROM quadras q
JOIN arenas a ON a.arena_id = q.arena_id
LEFT JOIN reservas r ON r.quadra_id = q.quadra_id
GROUP BY q.quadra_id, q.nome, q.tipo_esporte, q.preco_hora, a.nome
ORDER BY horas_reservadas DESC, receita DESC;

-- PROCEDURE: sp_ranking_atletas
-- RELATÓRIO: ranking de atletas por jogos e horas em quadra
-- (JOIN N:N + GROUP BY + ORDER BY). Parâmetros: :limite
SELECT u.usuario_id, u.nome, u.tipo_usuario,
       COUNT(rj.reserva_id) AS total_jogos,
       COALESCE(ROUND(SUM(
           (julianday(r.data_hora_fim) - julianday(r.data_hora_inicio)) * 24
       ), 1), 0)            AS horas_jogadas
FROM usuarios u
JOIN reserva_jogadores rj ON rj.usuario_id = u.usuario_id
JOIN reservas r           ON r.reserva_id  = rj.reserva_id
GROUP BY u.usuario_id, u.nome, u.tipo_usuario
ORDER BY total_jogos DESC, horas_jogadas DESC
LIMIT :limite;

-- PROCEDURE: sp_quadras_disponiveis
-- BUSCA: quadras livres no período informado (JOIN + NOT EXISTS anti-overbooking).
-- Parâmetros: :inicio, :fim
SELECT q.quadra_id, q.nome AS nome_quadra, q.tipo_esporte, q.preco_hora,
       a.arena_id, a.nome AS nome_arena, a.cidade
FROM quadras q
JOIN arenas a ON a.arena_id = q.arena_id
WHERE NOT EXISTS (
    SELECT 1 FROM reservas r
    WHERE r.quadra_id = q.quadra_id
      AND r.data_hora_inicio < :fim
      AND r.data_hora_fim > :inicio
)
ORDER BY a.cidade, a.nome, q.nome;

-- PROCEDURE: sp_agenda_arena
-- RELATÓRIO: agenda de uma arena no período (JOIN + WHERE + ORDER BY).
-- Parâmetros: :arena_id, :inicio, :fim
SELECT r.reserva_id, r.data_hora_inicio, r.data_hora_fim, r.valor_total, r.status,
       q.nome AS nome_quadra, q.tipo_esporte,
       (SELECT GROUP_CONCAT(u.nome, ', ')
        FROM reserva_jogadores rj
        JOIN usuarios u ON u.usuario_id = rj.usuario_id
        WHERE rj.reserva_id = r.reserva_id) AS jogadores
FROM reservas r
JOIN quadras q ON q.quadra_id = r.quadra_id
WHERE q.arena_id = :arena_id
  AND r.data_hora_inicio >= :inicio
  AND r.data_hora_inicio <= :fim
ORDER BY r.data_hora_inicio;
