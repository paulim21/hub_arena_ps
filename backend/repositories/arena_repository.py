"""Repository — Arena: consultas além do CRUD, via procedures."""
from repositories.procedure_runner import executar_procedure


class ArenaRepository:
    @staticmethod
    def listar_por_cidade(cidade):
        return executar_procedure("sp_arenas_por_cidade", {"cidade": cidade})

    @staticmethod
    def listar_com_dono():
        return executar_procedure("sp_arenas_com_dono")

    @staticmethod
    def agenda(arena_id, inicio, fim):
        return executar_procedure(
            "sp_agenda_arena", {"arena_id": arena_id, "inicio": inicio, "fim": fim}
        )
