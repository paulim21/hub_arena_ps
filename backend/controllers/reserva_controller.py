"""Controller — Reserva (classe ligada ao recurso /api/reservas)."""
from flask import Blueprint, jsonify, request

from services.reserva_service import (
    AtualizarStatusReservaService,
    BuscarReservaService,
    CriarReservaService,
    DeletarReservaService,
    ListarReservasDetalhadasService,
    ListarReservasService,
)


class ReservaController:

    @staticmethod
    def listar():
        """GET /api/reservas — ?detalhes=1 traz o JOIN triplo + jogadores."""
        if request.args.get("detalhes"):
            return jsonify(ListarReservasDetalhadasService.executar()), 200
        return jsonify(ListarReservasService.executar()), 200

    @staticmethod
    def criar():
        """POST /api/reservas — anti-overbooking + valor automático."""
        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"erro": "Corpo JSON inválido ou ausente."}), 400
        try:
            return jsonify(CriarReservaService.executar(dados).to_dict()), 201
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400

    @staticmethod
    def buscar(reserva_id):
        """GET /api/reservas/<id>."""
        try:
            return jsonify(BuscarReservaService.executar(reserva_id).to_dict()), 200
        except LookupError as e:
            return jsonify({"erro": str(e)}), 404

    @staticmethod
    def atualizar(reserva_id):
        """PUT /api/reservas/<id> — muda o status (pendente/confirmada)."""
        dados = request.get_json(silent=True)
        try:
            return jsonify(AtualizarStatusReservaService.executar(reserva_id, dados).to_dict()), 200
        except LookupError as e:
            return jsonify({"erro": str(e)}), 404
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400

    @staticmethod
    def deletar(reserva_id):
        """DELETE /api/reservas/<id>."""
        try:
            DeletarReservaService.executar(reserva_id)
            return jsonify({"mensagem": "Reserva deletada com sucesso."}), 200
        except LookupError as e:
            return jsonify({"erro": str(e)}), 404


reserva_bp = Blueprint("api_reservas", __name__)
reserva_bp.add_url_rule("", view_func=ReservaController.listar, methods=["GET"], endpoint="listar")
reserva_bp.add_url_rule("", view_func=ReservaController.criar, methods=["POST"], endpoint="criar")
reserva_bp.add_url_rule("/<int:reserva_id>", view_func=ReservaController.buscar, methods=["GET"], endpoint="buscar")
reserva_bp.add_url_rule("/<int:reserva_id>", view_func=ReservaController.atualizar, methods=["PUT"], endpoint="atualizar")
reserva_bp.add_url_rule("/<int:reserva_id>", view_func=ReservaController.deletar, methods=["DELETE"], endpoint="deletar")
