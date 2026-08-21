"""Model — ReservaJogador: tabela N:N entre reservas e usuários (jogadores)."""
from extensions import db


class ReservaJogador(db.Model):
    __tablename__ = "reserva_jogadores"

    reserva_id = db.Column(
        db.Integer,
        db.ForeignKey("reservas.reserva_id", ondelete="CASCADE"),
        primary_key=True,
    )
    usuario_id = db.Column(
        db.Integer,
        db.ForeignKey("usuarios.usuario_id"),
        primary_key=True,
    )

    def to_dict(self):
        return {"reserva_id": self.reserva_id, "usuario_id": self.usuario_id}
