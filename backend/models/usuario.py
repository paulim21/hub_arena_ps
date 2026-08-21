"""Model — Usuário: entidade do domínio + CRUD básico (herda de db.Model)."""
from extensions import db


class Usuario(db.Model):
    __tablename__ = "usuarios"

    usuario_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    senha = db.Column(db.Text, nullable=False)
    telefone = db.Column(db.Text, nullable=False)
    tipo_usuario = db.Column(db.Text, nullable=False)  # 'atleta', 'dono', 'professor'
    data_criacao = db.Column(db.Text, nullable=False, server_default=db.text("(date('now'))"))

    def to_dict(self, incluir_senha=False):
        dados = {
            "usuario_id": self.usuario_id,
            "nome": self.nome,
            "email": self.email,
            "telefone": self.telefone,
            "tipo_usuario": self.tipo_usuario,
            "data_criacao": self.data_criacao,
        }
        if incluir_senha:
            dados["senha"] = self.senha
        return dados

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
        return cls.query.order_by(cls.usuario_id).all()

    @classmethod
    def buscar_por_id(cls, usuario_id):
        return db.session.get(cls, usuario_id)
