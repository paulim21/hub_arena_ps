"""Services — Quadra (uma classe por caso de uso)."""
from datetime import datetime

from sqlalchemy.exc import IntegrityError

from extensions import db
from models.arena import Arena
from models.quadra import Quadra
from repositories.quadra_repository import QuadraRepository


class CriarQuadraService:
    @staticmethod
    def executar(dados):
        obrigatorios = ("arena_id", "nome", "tipo_esporte", "preco_hora")
        faltando = [c for c in obrigatorios if str(dados.get(c, "")) == ""]
        if faltando:
            raise ValueError(f"Campos obrigatórios ausentes: {', '.join(faltando)}")
        if Arena.buscar_por_id(dados["arena_id"]) is None:
            raise ValueError("Arena informada não existe.")
        return Quadra(
            arena_id=dados["arena_id"], nome=dados["nome"],
            tipo_esporte=dados["tipo_esporte"], preco_hora=dados["preco_hora"],
        ).salvar()


class ListarQuadrasService:
    @staticmethod
    def executar(arena_id=None, com_arena=False):
        if arena_id:
            # Filtro por arena → procedure sp_quadras_por_arena
            return QuadraRepository.listar_por_arena(arena_id)
        if com_arena:
            # Listagem enriquecida (JOIN) → procedure sp_quadras_com_arena
            return QuadraRepository.listar_com_arena()
        return [q.to_dict() for q in Quadra.listar_todos()]


class BuscarQuadraService:
    @staticmethod
    def executar(quadra_id):
        quadra = Quadra.buscar_por_id(quadra_id)
        if quadra is None:
            raise LookupError("Quadra não encontrada.")
        return quadra


class AtualizarQuadraService:
    @staticmethod
    def executar(quadra_id, dados):
        quadra = BuscarQuadraService.executar(quadra_id)
        quadra.nome = dados.get("nome", quadra.nome)
        quadra.tipo_esporte = dados.get("tipo_esporte", quadra.tipo_esporte)
        quadra.preco_hora = dados.get("preco_hora", quadra.preco_hora)
        return quadra.atualizar()


class DeletarQuadraService:
    @staticmethod
    def executar(quadra_id):
        quadra = BuscarQuadraService.executar(quadra_id)
        try:
            quadra.deletar()
        except IntegrityError:
            db.session.rollback()
            raise ValueError(
                "Esta quadra tem reservas vinculadas. Cancele as reservas primeiro."
            )


class QuadrasDisponiveisService:
    """Caso de uso: busca de quadras livres no período (procedure sp_quadras_disponiveis)."""
    @staticmethod
    def executar(inicio, fim):
        if not inicio or not fim:
            raise ValueError("Informe os parâmetros 'inicio' e 'fim'.")
        try:
            dt_inicio = datetime.fromisoformat(inicio)
            dt_fim = datetime.fromisoformat(fim)
        except ValueError:
            raise ValueError("Datas em formato inválido (use ISO, ex: 2026-08-21T19:00).")
        if dt_fim <= dt_inicio:
            raise ValueError("O horário final deve ser depois do inicial.")
        return QuadraRepository.listar_disponiveis(inicio, fim)
