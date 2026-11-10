"""Controller de Busca (classe ligada ao recurso /api/busca).

Recebe a requisição, chama o Service e devolve a resposta. As rotas que
apontam para esta classe ficam em `routes.py`.
"""
from flask import jsonify, request

from services.busca_service import BuscaGlobalService


class BuscaController:

    @staticmethod
    def buscar():
        """GET /api/busca?q= — procura em usuários, arenas e quadras."""
        try:
            return jsonify(BuscaGlobalService.executar(request.args.get("q"))), 200
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400
