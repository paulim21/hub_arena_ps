"""Repository — Usuário: consultas além do CRUD, via procedures."""
from repositories.procedure_runner import executar_procedure


class UsuarioRepository:
    @staticmethod
    def listar_por_tipo(tipo):
        return executar_procedure("sp_usuarios_por_tipo", {"tipo": tipo})

    @staticmethod
    def buscar_por_termo(termo):
        return executar_procedure("sp_busca_usuarios", {"termo": termo})
