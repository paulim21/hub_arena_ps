"""Controller — Relatórios (classe ligada ao recurso /api/relatorios).

As rotas que apontam para esta classe ficam em `routes.py`.
"""
from flask import jsonify, request

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
