"""Registro das PROCEDURES no banco SQLite.

O SQLite não possui a instrução CREATE PROCEDURE (recurso de SGBDs
cliente-servidor como MySQL/PostgreSQL). Para atender ao requisito,
as procedures ficam armazenadas NA TABELA `procedures` DO PRÓPRIO BANCO
(nome + SQL parametrizado), registradas na subida do servidor a partir
de `repositories/procedures.sql`. A camada Repository as executa pelo
runner `repositories/procedure_runner.py` — o equivalente ao CALL.
"""
import os
import sqlite3

DIRETORIO = os.path.dirname(os.path.abspath(__file__))
NOME_BANCO = os.path.join(DIRETORIO, "hub_arena.db")
ARQUIVO_PROCEDURES = os.path.join(DIRETORIO, "repositories", "procedures.sql")


def registrar_procedures():
    """Lê `procedures.sql` e grava cada procedure na tabela `procedures`.

    O arquivo usa marcadores `-- PROCEDURE: nome` para separar as procedures.
    A cada subida do servidor a tabela é recarregada, garantindo que o banco
    sempre tenha a versão mais recente de cada procedure.
    """
    conexao = sqlite3.connect(NOME_BANCO)
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS procedures (
            nome TEXT PRIMARY KEY,
            sql  TEXT NOT NULL
        )
    """)
    cursor.execute("DELETE FROM procedures")

    with open(ARQUIVO_PROCEDURES, encoding="utf-8") as arquivo:
        conteudo = arquivo.read()

    def gravar(nome, corpo):
        # Linhas de comentário ficam fora do SQL armazenado no banco
        sql = "\n".join(l for l in corpo if not l.strip().startswith("--")).strip()
        cursor.execute("INSERT INTO procedures (nome, sql) VALUES (?, ?)", (nome, sql))

    nome_atual, corpo = None, []
    for linha in conteudo.splitlines():
        if linha.strip().upper().startswith("-- PROCEDURE:"):
            if nome_atual:
                gravar(nome_atual, corpo)
            nome_atual = linha.split(":", 1)[1].strip()
            corpo = []
        elif nome_atual is not None:
            corpo.append(linha)
    if nome_atual:
        gravar(nome_atual, corpo)

    conexao.commit()
    conexao.close()
