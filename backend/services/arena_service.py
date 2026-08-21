"""Services — Arena (uma classe por caso de uso)."""
from datetime import datetime

from sqlalchemy.exc import IntegrityError

from extensions import db
from models.arena import Arena
from models.usuario import Usuario
from repositories.arena_repository import ArenaRepository


def _validar_dia_vencimento(valor):
    try:
        dia = int(valor)
    except (TypeError, ValueError):
        dia = 0
    if not 1 <= dia <= 28:
        raise ValueError("dia_vencimento deve ser um número entre 1 e 28.")
    return dia


class CriarArenaService:
    @staticmethod
    def executar(dados):
        obrigatorios = ("nome", "endereco", "cidade", "dono_id", "taxa_saas")
        faltando = [c for c in obrigatorios if str(dados.get(c, "")) == ""]
        if faltando:
            raise ValueError(f"Campos obrigatórios ausentes: {', '.join(faltando)}")

        # Regra de negócio: o responsável precisa existir e ser do tipo 'dono'
        dono = Usuario.buscar_por_id(dados["dono_id"])
        if dono is None or dono.tipo_usuario != "dono":
            raise ValueError("dono_id inválido: usuário não existe ou não é do tipo 'dono'.")

        return Arena(
            nome=dados["nome"], cnpj=dados.get("cnpj"), endereco=dados["endereco"],
            cidade=dados["cidade"], dono_id=dados["dono_id"], taxa_saas=dados["taxa_saas"],
            dia_vencimento=_validar_dia_vencimento(dados.get("dia_vencimento", 5)),
        ).salvar()


class ListarArenasService:
    @staticmethod
    def executar(cidade=None):
        if cidade:
            # Filtro por cidade → procedure sp_arenas_por_cidade
            return ArenaRepository.listar_por_cidade(cidade)
        return [a.to_dict() for a in Arena.listar_todos()]


class ListarArenasComDonoService:
    """Listagem enriquecida do painel: JOIN com dono + contagem de quadras."""
    @staticmethod
    def executar():
        return ArenaRepository.listar_com_dono()


class BuscarArenaService:
    @staticmethod
    def executar(arena_id):
        arena = Arena.buscar_por_id(arena_id)
        if arena is None:
            raise LookupError("Arena não encontrada.")
        return arena


class AtualizarArenaService:
    @staticmethod
    def executar(arena_id, dados):
        arena = BuscarArenaService.executar(arena_id)
        arena.nome = dados.get("nome", arena.nome)
        arena.cnpj = dados.get("cnpj", arena.cnpj)
        arena.endereco = dados.get("endereco", arena.endereco)
        arena.cidade = dados.get("cidade", arena.cidade)
        arena.taxa_saas = dados.get("taxa_saas", arena.taxa_saas)
        if "dia_vencimento" in dados:
            arena.dia_vencimento = _validar_dia_vencimento(dados["dia_vencimento"])
        return arena.atualizar()


class DeletarArenaService:
    @staticmethod
    def executar(arena_id):
        arena = BuscarArenaService.executar(arena_id)
        try:
            arena.deletar()
        except IntegrityError:
            db.session.rollback()
            raise ValueError(
                "Esta arena ainda tem quadras cadastradas. Exclua as quadras primeiro."
            )


class AgendaArenaService:
    """Caso de uso: agenda da arena no período (procedure sp_agenda_arena)."""
    @staticmethod
    def executar(arena_id, inicio=None, fim=None):
        BuscarArenaService.executar(arena_id)
        for rotulo, valor in (("inicio", inicio), ("fim", fim)):
            if valor:
                try:
                    datetime.fromisoformat(valor)
                except ValueError:
                    raise ValueError(f"Parâmetro '{rotulo}' em formato inválido (use ISO, ex: 2026-08-21T19:00).")
        # Sem período informado, a agenda cobre tudo (texto ISO ordena cronologicamente)
        return ArenaRepository.agenda(arena_id, inicio or "0000", fim or "9999")
