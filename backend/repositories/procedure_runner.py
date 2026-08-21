"""Runner de procedures — o "CALL" da camada Repository.

As procedures ficam gravadas na tabela `procedures` do banco
(registradas na subida do servidor a partir de `procedures.sql`).
Este módulo busca o SQL pelo nome e o executa com os parâmetros
nomeados (:nome) via SQLAlchemy, devolvendo dicts prontos para o Service.
Controller e Service nunca executam SQL diretamente.
"""
from sqlalchemy import text

from extensions import db


def executar_procedure(nome, parametros=None, unico=False):
    """Executa a procedure `nome` com os `parametros` informados.

    - unico=False → lista de dicts (fetchall)
    - unico=True  → um dict ou None (fetchone)
    """
    procedure = db.session.execute(
        text("SELECT sql FROM procedures WHERE nome = :nome"), {"nome": nome}
    ).first()
    if procedure is None:
        raise LookupError(f"Procedure '{nome}' não está registrada no banco.")

    resultado = db.session.execute(text(procedure[0]), parametros or {})
    if unico:
        linha = resultado.mappings().first()
        return dict(linha) if linha is not None else None
    return [dict(linha) for linha in resultado.mappings().all()]
