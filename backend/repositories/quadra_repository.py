"""Repository — Quadra: consultas além do CRUD, via procedures."""
from repositories.procedure_runner import executar_procedure


class QuadraRepository:
    @staticmethod
    def listar_com_arena():
        return executar_procedure("sp_quadras_com_arena")

    @staticmethod
    def buscar_por_termo(termo):
        """Busca textual por nome da quadra, esporte ou nome da arena."""
        return executar_procedure("sp_busca_quadras", {"termo": termo})

    @staticmethod
    def listar_por_arena(arena_id):
        return executar_procedure("sp_quadras_por_arena", {"arena_id": arena_id})

    @staticmethod
    def listar_disponiveis(inicio, fim):
        return executar_procedure(
            "sp_quadras_disponiveis", {"inicio": inicio, "fim": fim}
        )
