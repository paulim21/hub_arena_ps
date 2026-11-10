"""Model — Reserva: entidade do domínio + CRUD básico do model db"""
from extensions import db
from models.reserva_jogador import ReservaJogador


class Reserva(db.Model):
    __tablename__ = "reservas"

    reserva_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quadra_id = db.Column(db.Integer, db.ForeignKey("quadras.quadra_id"), nullable=False)
    usuario_reserva_id = db.Column(db.Integer, db.ForeignKey("usuarios.usuario_id"), nullable=False)
    data_hora_inicio = db.Column(db.Text, nullable=False)  # ISO: 2026-08-21T19:00
    data_hora_fim = db.Column(db.Text, nullable=False)
    valor_total = db.Column(db.Float, nullable=False)
    status = db.Column(db.Text, nullable=False, default="pendente")  # 'pendente', 'confirmada'

    quadra = db.relationship("Quadra", backref="reservas", lazy=True)

    def to_dict(self):
        return {
            "reserva_id": self.reserva_id,
            "quadra_id": self.quadra_id,
            "usuario_reserva_id": self.usuario_reserva_id,
            "data_hora_inicio": self.data_hora_inicio,
            "data_hora_fim": self.data_hora_fim,
            "valor_total": self.valor_total,
            "status": self.status,
        }

    # ---------- CRUD básico (na própria Model) ----------

    def salvar(self, jogadores=None):
        """Insere a reserva e, se informado, os jogadores (tabela N:N)."""
        db.session.add(self)
        db.session.flush()  # garante o reserva_id antes de gravar os jogadores
        for usuario_id in (jogadores or []):
            db.session.add(ReservaJogador(reserva_id=self.reserva_id, usuario_id=usuario_id))
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
        return cls.query.order_by(cls.reserva_id).all()

    @classmethod
    def buscar_por_id(cls, reserva_id):
        return db.session.get(cls, reserva_id)
