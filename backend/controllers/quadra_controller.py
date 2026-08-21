"""Controller — Quadra (classe ligada ao recurso /api/quadras).

As rotas que apontam para esta classe ficam em `routes.py`.
"""
from flask import jsonify, request

from services.quadra_service import (
    AtualizarQuadraService,
    BuscarQuadraService,
    CriarQuadraService,
    DeletarQuadraService,
    ListarQuadrasService,
    QuadrasDisponiveisService,
)


class QuadraController:

    @staticmethod
    def listar():
        """GET /api/quadras — ?arena_id= ou ?detalhes=1 com JOIN (procedures)."""
        return jsonify(ListarQuadrasService.executar(
            arena_id=request.args.get("arena_id"),
            com_arena=bool(request.args.get("detalhes")),
        )), 200

    @staticmethod
    def criar():
        """POST /api/quadras — cadastra validando a arena."""
        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"erro": "Corpo JSON inválido ou ausente."}), 400
        try:
            return jsonify(CriarQuadraService.executar(dados).to_dict()), 201
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400

    @staticmethod
    def disponiveis():
        """GET /api/quadras/disponiveis?inicio=&fim= (procedure NOT EXISTS)."""
        try:
            return jsonify(QuadrasDisponiveisService.executar(
                request.args.get("inicio"), request.args.get("fim")
            )), 200
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400

    @staticmethod
    def buscar(quadra_id):
        """GET /api/quadras/<id>."""
        try:
            return jsonify(BuscarQuadraService.executar(quadra_id).to_dict()), 200
        except LookupError as e:
            return jsonify({"erro": str(e)}), 404

    @staticmethod
    def atualizar(quadra_id):
        """PUT /api/quadras/<id>."""
        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"erro": "Corpo JSON ausente."}), 400
        try:
            return jsonify(AtualizarQuadraService.executar(quadra_id, dados).to_dict()), 200
        except LookupError as e:
            return jsonify({"erro": str(e)}), 404
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400

    @staticmethod
    def deletar(quadra_id):
        """DELETE /api/quadras/<id>."""
        try:
            DeletarQuadraService.executar(quadra_id)
            return jsonify({"mensagem": "Quadra deletada com sucesso."}), 200
        except LookupError as e:
            return jsonify({"erro": str(e)}), 404
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400
