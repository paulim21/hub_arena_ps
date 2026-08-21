"""Controller — Relatórios (classe ligada ao recurso /api/relatorios)."""
from flask import Blueprint, jsonify, request

from services.relatorio_service import (
    OcupacaoQuadrasService,
    RankingAtletasService,
    ReceitaPorArenaService,
    ReservasRecentesService,
    ResumoDashboardService,
)


class RelatorioController:

    @staticmethod
    def resumo():
        """GET /api/relatorios/resumo — contadores + receita (procedure)."""
        return jsonify(ResumoDashboardService.executar()), 200

    @staticmethod
    def reservas_recentes():
        """GET /api/relatorios/reservas-recentes?limite=6 (procedure)."""
        limite = request.args.get("limite", 6, type=int)
        return jsonify(ReservasRecentesService.executar(limite)), 200

    @staticmethod
    def receita_arenas():
        """GET /api/relatorios/receita-arenas?inicio=&fim= (procedure)."""
        try:
            return jsonify(ReceitaPorArenaService.executar(
                request.args.get("inicio"), request.args.get("fim")
            )), 200
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400

    @staticmethod
    def ocupacao_quadras():
        """GET /api/relatorios/ocupacao-quadras (procedure)."""
        return jsonify(OcupacaoQuadrasService.executar()), 200

    @staticmethod
    def ranking_atletas():
        """GET /api/relatorios/ranking-atletas?limite=10 (procedure)."""
        try:
            return jsonify(RankingAtletasService.executar(request.args.get("limite", 10))), 200
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400


relatorio_bp = Blueprint("api_relatorios", __name__)
relatorio_bp.add_url_rule("/resumo", view_func=RelatorioController.resumo, methods=["GET"], endpoint="resumo")
relatorio_bp.add_url_rule("/reservas-recentes", view_func=RelatorioController.reservas_recentes, methods=["GET"], endpoint="reservas_recentes")
relatorio_bp.add_url_rule("/receita-arenas", view_func=RelatorioController.receita_arenas, methods=["GET"], endpoint="receita_arenas")
relatorio_bp.add_url_rule("/ocupacao-quadras", view_func=RelatorioController.ocupacao_quadras, methods=["GET"], endpoint="ocupacao_quadras")
relatorio_bp.add_url_rule("/ranking-atletas", view_func=RelatorioController.ranking_atletas, methods=["GET"], endpoint="ranking_atletas")
