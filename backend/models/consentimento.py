"""Model — Consentimento LGPD: entidade do domínio + CRUD básico.

A LGPD (Lei 13.709/2018) exige que o controlador **comprove** o
consentimento que obteve (Art. 8º, § 1º). Guardar um sinalizador no
navegador não comprova nada: o titular pode limpar, e o controlador não
teria registro. Por isso cada aceite vira uma linha aqui, com a **versão
dos termos** que estava valendo na hora.

A versão é o que permite pedir novo aceite quando a política muda: um
consentimento dado para a versão 1.0 não vale para a 2.0 (Art. 8º, § 6º).
"""
from datetime import datetime, timezone

from extensions import db


class Consentimento(db.Model):
    __tablename__ = "consentimentos"

    consentimento_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # Identificador anônimo gerado no navegador. Não é login: o sistema não
    # tem contas, e este é o fio que liga o aceite ao aparelho que o deu.
    identificador = db.Column(db.Text, nullable=False, index=True)
    versao_termos = db.Column(db.Text, nullable=False)
    finalidades = db.Column(db.Text, nullable=False)  # separadas por ';'
    aceito_em = db.Column(db.Text, nullable=False)
    revogado_em = db.Column(db.Text)                  # nulo = ainda vigente
    # Evidência do aceite, e só para isso — está declarado nos termos.
    origem_ip = db.Column(db.Text)
    agente = db.Column(db.Text)

    def to_dict(self):
        return {
            "consentimento_id": self.consentimento_id,
            "identificador": self.identificador,
            "versao_termos": self.versao_termos,
            "finalidades": [f for f in (self.finalidades or "").split(";") if f],
            "aceito_em": self.aceito_em,
            "revogado_em": self.revogado_em,
            "vigente": self.revogado_em is None,
        }

    @staticmethod
    def agora():
        return datetime.now(timezone.utc).isoformat(timespec="seconds")

    # ---------- CRUD básico (na própria Model) ----------

    def salvar(self):
        db.session.add(self)
        db.session.commit()
        return self

    def atualizar(self):
        db.session.commit()
        return self

    def deletar(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def listar_todos(cls):
        return cls.query.order_by(cls.consentimento_id.desc()).all()

    @classmethod
    def buscar_por_id(cls, consentimento_id):
        return db.session.get(cls, consentimento_id)
