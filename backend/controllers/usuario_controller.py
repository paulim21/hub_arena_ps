"""Controller — Usuário (classe ligada ao recurso /api/usuarios).

Recebe a requisição HTTP, interpreta os dados, chama o Service
correspondente e devolve a resposta da API.
As rotas que madam essa classe estaem rotes.
"""
from flask import jsonify, request

from services.usuario_service import (
    AtualizarUsuarioService,
    BuscarUsuarioService,
    CriarUsuarioService,
    DeletarUsuarioService,
    ListarUsuariosService,
    PesquisarUsuariosService,
)


class UsuarioController:

    @staticmethod
    def listar():
        """GET /api/usuarios — filtro opcional ?tipo=atleta (procedure)."""
        return jsonify(ListarUsuariosService.executar(request.args.get("tipo"))), 200

    @staticmethod
    def criar():
        """POST /api/usuarios — cadastra a partir do corpo JSON."""
        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"erro": "Corpo JSON inválido ou ausente."}), 400
        try:
            return jsonify(CriarUsuarioService.executar(dados).to_dict()), 201
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400

    @staticmethod
    def pesquisar():
        """GET /api/usuarios/busca?q= — busca textual por nome/e-mail (LIKE)."""
        try:
            return jsonify(PesquisarUsuariosService.executar(request.args.get("q"))), 200
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400

    @staticmethod
    def buscar(usuario_id):
        """GET /api/usuarios/<id>."""
        try:
            return jsonify(BuscarUsuarioService.executar(usuario_id).to_dict()), 200
        except LookupError as e:
            return jsonify({"erro": str(e)}), 404

    @staticmethod
    def atualizar(usuario_id):
        """PUT /api/usuarios/<id>."""
        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"erro": "Corpo JSON ausente."}), 400
        try:
            return jsonify(AtualizarUsuarioService.executar(usuario_id, dados).to_dict()), 200
        except LookupError as e:
            return jsonify({"erro": str(e)}), 404
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400

    @staticmethod
    def deletar(usuario_id):
        """DELETE /api/usuarios/<id>."""
        try:
            DeletarUsuarioService.executar(usuario_id)
            return jsonify({"mensagem": "Usuário deletado com sucesso."}), 200
        except LookupError as e:
            return jsonify({"erro": str(e)}), 404
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400
