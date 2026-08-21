"""Repository — Reserva: consultas além do CRUD, via procedures."""
from repositories.procedure_runner import executar_procedure


class ReservaRepository:
    @staticmethod
    def existe_conflito(quadra_id, inicio, fim):
        conflitos = executar_procedure(
            "sp_conflito_reserva",
            {"quadra_id": quadra_id, "inicio": inicio, "fim": fim},
        )
        return len(conflitos) > 0

    @staticmethod
    def listar_detalhadas():
        return executar_procedure("sp_reservas_detalhadas")

    @staticmethod
    def listar_recentes(limite=6):
        return executar_procedure("sp_reservas_recentes", {"limite": limite})

    @staticmethod
    def jogadores_da_reserva(reserva_id):
        return executar_procedure("sp_jogadores_da_reserva", {"reserva_id": reserva_id})
