"""Model — Quadra: entidade do domínio + CRUD básico (herda de db.Model)."""
from extensions import db


class Quadra(db.Model):
    __tablename__ = "quadras"

    quadra_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    arena_id = db.Column(db.Integer, db.ForeignKey("arenas.arena_id"), nullable=False)
    nome = db.Column(db.Text, nullable=False)
    tipo_esporte = db.Column(db.Text, nullable=False)
    preco_hora = db.Column(db.Float, nullable=False)

    arena = db.relationship("Arena", backref="quadras", lazy=True)

    def to_dict(self):
        return {
            "quadra_id": self.quadra_id,
            "arena_id": self.arena_id,
            "nome": self.nome,
            "tipo_esporte": self.tipo_esporte,
            "preco_hora": self.preco_hora,
        }

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
        return cls.query.order_by(cls.quadra_id).all()

    @classmethod
    def buscar_por_id(cls, quadra_id):
        return db.session.get(cls, quadra_id)
