"""Services — Relatórios (uma classe por caso de uso).

Todos os acessos complexos ficam na camada Repository (procedures).
"""
from datetime import datetime

from repositories.relatorio_repository import RelatorioRepository
from repositories.reserva_repository import ReservaRepository


def _validar_iso(rotulo, valor):
    try:
        datetime.fromisoformat(valor)
    except (TypeError, ValueError):
        raise ValueError(f"Parâmetro '{rotulo}' em formato inválido (use ISO, ex: 2026-08-21T19:00).")
    return valor


class ResumoDashboardService:
    @staticmethod
    def executar():
        return RelatorioRepository.resumo_dashboard()


class ReservasRecentesService:
    @staticmethod
    def executar(limite=6):
        return ReservaRepository.listar_recentes(limite)


class ReceitaPorArenaService:
    @staticmethod
    def executar(inicio=None, fim=None):
        inicio = _validar_iso("inicio", inicio) if inicio else "0000-01-01T00:00"
        fim = _validar_iso("fim", fim) if fim else "9999-12-31T23:59"
        return RelatorioRepository.receita_por_arena(inicio, fim)


class OcupacaoQuadrasService:
    @staticmethod
    def executar():
        return RelatorioRepository.ocupacao_quadras()


class RankingAtletasService:
    @staticmethod
    def executar(limite=10):
        try:
            limite = int(limite)
        except (TypeError, ValueError):
            raise ValueError("Parâmetro 'limite' deve ser um número inteiro.")
        if limite < 1:
            raise ValueError("Parâmetro 'limite' deve ser maior que zero.")
        return RelatorioRepository.ranking_atletas(limite)
