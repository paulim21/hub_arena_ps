"""
HUB ARENA — API REST + Front-end estático
Flask + SQLAlchemy + SQLite (sem Jinja2 / render_template)

Arquitetura em camadas (padrão do material da disciplina):

    Tela (frontend/ — HTML + JS puro, fetch nas rotas /api/...)
       │
       ▼
    Controller (classes em controllers/)  →  recebe as requisições HTTP
    Service (uma classe por caso de uso)  →  regras de negócio e validações
    Model (herda de db.Model)             →  entidades do domínio + CRUD básico
    Repository                            →  consultas complexas via PROCEDURES
       │
       ▼
    SQLite (hub_arena.db — dados + tabela `procedures`)
"""
import os

from flask import Flask
from sqlalchemy import event

from database import NOME_BANCO, registrar_procedures
from extensions import db

DIRETORIO = os.path.dirname(os.path.abspath(__file__))
PASTA_FRONTEND = os.path.abspath(os.path.join(DIRETORIO, "..", "frontend"))


def create_app():
    """Application Factory: cria e configura a aplicação Flask."""
    app = Flask(__name__, static_folder=PASTA_FRONTEND, static_url_path="")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + NOME_BANCO
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # Models (registro no SQLAlchemy)
    from models.usuario import Usuario
    from models.arena import Arena
    from models.quadra import Quadra
    from models.reserva import Reserva
    from models.reserva_jogador import ReservaJogador

    with app.app_context():
        # SQLite exige o PRAGMA em cada conexão para as FKs valerem
        @event.listens_for(db.engine, "connect")
        def ligar_chaves_estrangeiras(conexao_dbapi, _registro):
            conexao_dbapi.execute("PRAGMA foreign_keys = ON")

        db.create_all()  # cria as tabelas das Models caso não existam

    # Registra as procedures na tabela `procedures` do banco
    registrar_procedures()

    # Controllers (classes) expostos por Blueprints
    from controllers.usuario_controller import usuario_bp
    from controllers.arena_controller import arena_bp
    from controllers.quadra_controller import quadra_bp
    from controllers.reserva_controller import reserva_bp
    from controllers.relatorio_controller import relatorio_bp

    app.register_blueprint(usuario_bp, url_prefix="/api/usuarios")
    app.register_blueprint(arena_bp, url_prefix="/api/arenas")
    app.register_blueprint(quadra_bp, url_prefix="/api/quadras")
    app.register_blueprint(reserva_bp, url_prefix="/api/reservas")
    app.register_blueprint(relatorio_bp, url_prefix="/api/relatorios")

    # ===== Páginas do front-end (apenas entrega dos arquivos estáticos) =====
    PAGINAS = {
        "/": "index.html",
        "/usuarios": "usuarios.html",
        "/arenas": "arenas.html",
        "/quadras": "quadras.html",
        "/reservas": "reservas.html",
        "/relatorios": "relatorios.html",
    }
    for caminho, arquivo in PAGINAS.items():
        app.add_url_rule(
            caminho,
            endpoint=f"pagina_{arquivo}",
            view_func=(lambda arquivo=arquivo: app.send_static_file(arquivo)),
        )

    return app


app = create_app()

# ===== Método run: inicia o servidor de desenvolvimento =====
if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))
