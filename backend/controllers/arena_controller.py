"""Controller — Arena (classe ligada ao recurso /api/arenas).

As rotas que apontam para esta classe ficam em `routes.py`.
"""
from flask import jsonify, request

from services.arena_service import (
    AgendaArenaService,
    AtualizarArenaService,
    BuscarArenaService,
    CriarArenaService,
    DeletarArenaService,
    ListarArenasComDonoService,
    ListarArenasService,
)


class ArenaController:

    @staticmethod
    def listar():
        """GET /api/arenas — ?detalhes=1 (JOIN dono) ou ?cidade= (procedures)."""
        if request.args.get("detalhes"):
            return jsonify(ListarArenasComDonoService.executar()), 200
        return jsonify(ListarArenasService.executar(request.args.get("cidade"))), 200

    @staticmethod
    def criar():
        """POST /api/arenas — cadastra validando o dono."""
        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"erro": "Corpo JSON inválido ou ausente."}), 400
        try:
            return jsonify(CriarArenaService.executar(dados).to_dict()), 201
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400

    @staticmethod
    def agenda(arena_id):
        """GET /api/arenas/<id>/agenda?inicio=&fim= (procedure sp_agenda_arena)."""
        try:
            return jsonify(AgendaArenaService.executar(
                arena_id, request.args.get("inicio"), request.args.get("fim")
            )), 200
        except LookupError as e:
            return jsonify({"erro": str(e)}), 404
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400

    @staticmethod
    def buscar(arena_id):
        """GET /api/arenas/<id>."""
        try:
            return jsonify(BuscarArenaService.executar(arena_id).to_dict()), 200
        except LookupError as e:
            return jsonify({"erro": str(e)}), 404

    @staticmethod
    def atualizar(arena_id):
        """PUT /api/arenas/<id>."""
        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"erro": "Corpo JSON ausente."}), 400
        try:
            return jsonify(AtualizarArenaService.executar(arena_id, dados).to_dict()), 200
        except LookupError as e:
            return jsonify({"erro": str(e)}), 404
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400

    @staticmethod
    def deletar(arena_id):
        """DELETE /api/arenas/<id>."""
        try:
            DeletarArenaService.executar(arena_id)
            return jsonify({"mensagem": "Arena deletada com sucesso."}), 200
        except LookupError as e:
            return jsonify({"erro": str(e)}), 404
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400
