"""Services — Usuário (uma classe por caso de uso)."""
from sqlalchemy.exc import IntegrityError

from extensions import db
from models.usuario import Usuario
from repositories.usuario_repository import UsuarioRepository

TIPOS_VALIDOS = ("atleta", "dono", "professor")


class CriarUsuarioService:
    @staticmethod
    def executar(dados):
        obrigatorios = ("nome", "email", "senha", "telefone", "tipo_usuario")
        faltando = [c for c in obrigatorios if not dados.get(c)]
        if faltando:
            raise ValueError(f"Campos obrigatórios ausentes: {', '.join(faltando)}")
        if dados["tipo_usuario"] not in TIPOS_VALIDOS:
            raise ValueError(f"tipo_usuario deve ser um de: {', '.join(TIPOS_VALIDOS)}")
        try:
            return Usuario(
                nome=dados["nome"], email=dados["email"], senha=dados["senha"],
                telefone=dados["telefone"], tipo_usuario=dados["tipo_usuario"],
            ).salvar()
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Já existe um usuário com este e-mail.")


class ListarUsuariosService:
    @staticmethod
    def executar(tipo=None):
        if tipo:
            # Consulta com filtro → camada Repository (procedure sp_usuarios_por_tipo)
            return UsuarioRepository.listar_por_tipo(tipo)
        return [u.to_dict() for u in Usuario.listar_todos()]


class PesquisarUsuariosService:
    @staticmethod
    def executar(termo):
        if not termo:
            raise ValueError("Informe o termo de busca (?q=).")
        # Busca textual → procedure sp_busca_usuarios (LIKE)
        return UsuarioRepository.buscar_por_termo(termo)


class BuscarUsuarioService:
    @staticmethod
    def executar(usuario_id):
        usuario = Usuario.buscar_por_id(usuario_id)
        if usuario is None:
            raise LookupError("Usuário não encontrado.")
        return usuario


class AtualizarUsuarioService:
    @staticmethod
    def executar(usuario_id, dados):
        usuario = BuscarUsuarioService.executar(usuario_id)
        usuario.nome = dados.get("nome", usuario.nome)
        usuario.email = dados.get("email", usuario.email)
        usuario.telefone = dados.get("telefone", usuario.telefone)
        usuario.tipo_usuario = dados.get("tipo_usuario", usuario.tipo_usuario)
        if usuario.tipo_usuario not in TIPOS_VALIDOS:
            db.session.rollback()
            raise ValueError(f"tipo_usuario deve ser um de: {', '.join(TIPOS_VALIDOS)}")
        try:
            return usuario.atualizar()
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Já existe um usuário com este e-mail.")


class DeletarUsuarioService:
    @staticmethod
    def executar(usuario_id):
        usuario = BuscarUsuarioService.executar(usuario_id)
        try:
            usuario.deletar()
        except IntegrityError:
            db.session.rollback()
            raise ValueError(
                "Este usuário tem arenas ou reservas vinculadas. Exclua-as primeiro."
            )
