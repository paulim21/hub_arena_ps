"""Model — Arena: entidade do domínio + CRUD básico (herda de db.Model)."""
from extensions import db


class Arena(db.Model):
    __tablename__ = "arenas"

    arena_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.Text, nullable=False)
    cnpj = db.Column(db.Text)
    endereco = db.Column(db.Text, nullable=False)
    cidade = db.Column(db.Text, nullable=False)
    dono_id = db.Column(db.Integer, db.ForeignKey("usuarios.usuario_id"), nullable=False)
    taxa_saas = db.Column(db.Float, nullable=False)
    dia_vencimento = db.Column(db.Integer, nullable=False, default=5)

    dono = db.relationship("Usuario", backref="arenas", lazy=True)

    def to_dict(self):
        return {
            "arena_id": self.arena_id,
            "nome": self.nome,
            "cnpj": self.cnpj,
            "endereco": self.endereco,
            "cidade": self.cidade,
            "dono_id": self.dono_id,
            "taxa_saas": self.taxa_saas,
            "dia_vencimento": self.dia_vencimento,
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
        return cls.query.order_by(cls.arena_id).all()

    @classmethod
    def buscar_por_id(cls, arena_id):
        return db.session.get(cls, arena_id)
