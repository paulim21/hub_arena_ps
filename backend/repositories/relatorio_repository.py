"""Repository — Relatórios: agregações e combinações entre tabelas, via procedures."""
from repositories.procedure_runner import executar_procedure


class RelatorioRepository:
    @staticmethod
    def resumo_dashboard():
        return executar_procedure("sp_resumo_dashboard", unico=True)

    @staticmethod
    def receita_por_arena(inicio, fim):
        return executar_procedure(
            "sp_receita_por_arena", {"inicio": inicio, "fim": fim}
        )

    @staticmethod
    def ocupacao_quadras():
        return executar_procedure("sp_ocupacao_quadras")

    @staticmethod
    def ranking_atletas(limite=10):
        return executar_procedure("sp_ranking_atletas", {"limite": limite})
