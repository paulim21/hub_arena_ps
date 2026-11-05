"""Mapa de rotas da aplicação — liga cada URL ao método da Controller.

As Controllers (controllers/) são classes puras: recebem a requisição,
chamam o Service e devolvem a resposta. Aqui os Blueprints são criados
e cada rota é registrada apontando para o método correspondente.
"""
from flask import Blueprint

from controllers.usuario_controller import UsuarioController
from controllers.arena_controller import ArenaController
from controllers.quadra_controller import QuadraController
from controllers.reserva_controller import ReservaController
from controllers.relatorio_controller import RelatorioController
from controllers.consentimento_controller import ConsentimentoController
from controllers.busca_controller import BuscaController

# ---------- Usuários ----------
usuario_bp = Blueprint("api_usuarios", __name__)
usuario_bp.add_url_rule("", view_func=UsuarioController.listar, methods=["GET"], endpoint="listar")
usuario_bp.add_url_rule("", view_func=UsuarioController.criar, methods=["POST"], endpoint="criar")
usuario_bp.add_url_rule("/busca", view_func=UsuarioController.pesquisar, methods=["GET"], endpoint="pesquisar")
usuario_bp.add_url_rule("/<int:usuario_id>", view_func=UsuarioController.buscar, methods=["GET"], endpoint="buscar")
usuario_bp.add_url_rule("/<int:usuario_id>", view_func=UsuarioController.atualizar, methods=["PUT"], endpoint="atualizar")
usuario_bp.add_url_rule("/<int:usuario_id>", view_func=UsuarioController.deletar, methods=["DELETE"], endpoint="deletar")

# ---------- Arenas ----------
arena_bp = Blueprint("api_arenas", __name__)
arena_bp.add_url_rule("", view_func=ArenaController.listar, methods=["GET"], endpoint="listar")
arena_bp.add_url_rule("", view_func=ArenaController.criar, methods=["POST"], endpoint="criar")
arena_bp.add_url_rule("/<int:arena_id>/agenda", view_func=ArenaController.agenda, methods=["GET"], endpoint="agenda")
arena_bp.add_url_rule("/<int:arena_id>", view_func=ArenaController.buscar, methods=["GET"], endpoint="buscar")
arena_bp.add_url_rule("/<int:arena_id>", view_func=ArenaController.atualizar, methods=["PUT"], endpoint="atualizar")
arena_bp.add_url_rule("/<int:arena_id>", view_func=ArenaController.deletar, methods=["DELETE"], endpoint="deletar")

# ---------- Quadras ----------
quadra_bp = Blueprint("api_quadras", __name__)
quadra_bp.add_url_rule("", view_func=QuadraController.listar, methods=["GET"], endpoint="listar")
quadra_bp.add_url_rule("", view_func=QuadraController.criar, methods=["POST"], endpoint="criar")
quadra_bp.add_url_rule("/disponiveis", view_func=QuadraController.disponiveis, methods=["GET"], endpoint="disponiveis")
quadra_bp.add_url_rule("/<int:quadra_id>", view_func=QuadraController.buscar, methods=["GET"], endpoint="buscar")
quadra_bp.add_url_rule("/<int:quadra_id>", view_func=QuadraController.atualizar, methods=["PUT"], endpoint="atualizar")
quadra_bp.add_url_rule("/<int:quadra_id>", view_func=QuadraController.deletar, methods=["DELETE"], endpoint="deletar")

# ---------- Reservas ----------
reserva_bp = Blueprint("api_reservas", __name__)
reserva_bp.add_url_rule("", view_func=ReservaController.listar, methods=["GET"], endpoint="listar")
reserva_bp.add_url_rule("", view_func=ReservaController.criar, methods=["POST"], endpoint="criar")
reserva_bp.add_url_rule("/<int:reserva_id>", view_func=ReservaController.buscar, methods=["GET"], endpoint="buscar")
reserva_bp.add_url_rule("/<int:reserva_id>", view_func=ReservaController.atualizar, methods=["PUT"], endpoint="atualizar")
reserva_bp.add_url_rule("/<int:reserva_id>", view_func=ReservaController.deletar, methods=["DELETE"], endpoint="deletar")

# ---------- Relatórios ----------
relatorio_bp = Blueprint("api_relatorios", __name__)
relatorio_bp.add_url_rule("/resumo", view_func=RelatorioController.resumo, methods=["GET"], endpoint="resumo")
relatorio_bp.add_url_rule("/reservas-recentes", view_func=RelatorioController.reservas_recentes, methods=["GET"], endpoint="reservas_recentes")
relatorio_bp.add_url_rule("/receita-arenas", view_func=RelatorioController.receita_arenas, methods=["GET"], endpoint="receita_arenas")
relatorio_bp.add_url_rule("/ocupacao-quadras", view_func=RelatorioController.ocupacao_quadras, methods=["GET"], endpoint="ocupacao_quadras")
relatorio_bp.add_url_rule("/ranking-atletas", view_func=RelatorioController.ranking_atletas, methods=["GET"], endpoint="ranking_atletas")

# ---------- Busca global ----------
busca_bp = Blueprint("api_busca", __name__)
busca_bp.add_url_rule("", view_func=BuscaController.buscar, methods=["GET"], endpoint="buscar")

# ---------- Consentimento (LGPD) ----------
consentimento_bp = Blueprint("api_consentimentos", __name__)
consentimento_bp.add_url_rule("/politica", view_func=ConsentimentoController.politica, methods=["GET"], endpoint="politica")
consentimento_bp.add_url_rule("/vigente", view_func=ConsentimentoController.verificar, methods=["GET"], endpoint="verificar")
consentimento_bp.add_url_rule("/relatorio", view_func=ConsentimentoController.relatorio, methods=["GET"], endpoint="relatorio")
consentimento_bp.add_url_rule("/revogar", view_func=ConsentimentoController.revogar, methods=["POST"], endpoint="revogar")
consentimento_bp.add_url_rule("", view_func=ConsentimentoController.registrar, methods=["POST"], endpoint="registrar")

# Páginas do front-end (apenas entrega dos arquivos estáticos, sem Jinja2)
PAGINAS = {
    "/": "index.html",
    "/usuarios": "usuarios.html",
    "/arenas": "arenas.html",
    "/quadras": "quadras.html",
    "/reservas": "reservas.html",
    "/relatorios": "relatorios.html",
    "/busca": "busca.html",
    "/termos": "termos.html",
}


def registrar_rotas(app):
    """Registra os Blueprints da API e as páginas do front-end na aplicação."""
    app.register_blueprint(usuario_bp, url_prefix="/api/usuarios")
    app.register_blueprint(arena_bp, url_prefix="/api/arenas")
    app.register_blueprint(quadra_bp, url_prefix="/api/quadras")
    app.register_blueprint(reserva_bp, url_prefix="/api/reservas")
    app.register_blueprint(relatorio_bp, url_prefix="/api/relatorios")
    app.register_blueprint(consentimento_bp, url_prefix="/api/consentimentos")
    app.register_blueprint(busca_bp, url_prefix="/api/busca")

    for caminho, arquivo in PAGINAS.items():
        app.add_url_rule(
            caminho,
            endpoint=f"pagina_{arquivo}",
            view_func=(lambda arquivo=arquivo: app.send_static_file(arquivo)),
        )
