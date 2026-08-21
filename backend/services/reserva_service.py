"""Services — Reserva (uma classe por caso de uso).

Concentra as regras de negócio: anti-overbooking (via procedure na camada
Repository) e valor total calculado pelo servidor (horas × preço/hora).
"""
from datetime import datetime

from models.quadra import Quadra
from models.reserva import Reserva
from models.usuario import Usuario
from repositories.reserva_repository import ReservaRepository

STATUS_VALIDOS = ("pendente", "confirmada")


class CriarReservaService:
    @staticmethod
    def executar(dados):
        quadra_id = dados.get("quadra_id")
        inicio = dados.get("data_hora_inicio")
        fim = dados.get("data_hora_fim")

        # Aceita 'jogadores' (lista) ou o campo clássico 'usuario_reserva_id'
        jogadores = dados.get("jogadores") or []
        if not jogadores and dados.get("usuario_reserva_id"):
            jogadores = [dados["usuario_reserva_id"]]
        jogadores = list(dict.fromkeys(jogadores))  # remove repetidos preservando a ordem

        if not quadra_id or not inicio or not fim:
            raise ValueError("Campos obrigatórios: quadra_id, data_hora_inicio, data_hora_fim.")
        if not jogadores:
            raise ValueError("Selecione ao menos um jogador.")

        quadra = Quadra.buscar_por_id(quadra_id)
        if quadra is None:
            raise ValueError("Quadra informada não existe.")
        for usuario_id in jogadores:
            if Usuario.buscar_por_id(usuario_id) is None:
                raise ValueError(f"Jogador {usuario_id} não existe.")

        try:
            dt_inicio = datetime.fromisoformat(inicio)
            dt_fim = datetime.fromisoformat(fim)
        except (TypeError, ValueError):
            raise ValueError("Datas em formato inválido (use ISO, ex: 2026-08-21T19:00).")
        if dt_fim <= dt_inicio:
            raise ValueError("O horário final deve ser depois do inicial.")

        # Anti-overbooking → procedure sp_conflito_reserva (Repository)
        if ReservaRepository.existe_conflito(quadra_id, inicio, fim):
            raise ValueError("Horário indisponível: já existe reserva nesse período.")

        horas = (dt_fim - dt_inicio).total_seconds() / 3600
        valor_total = round(horas * float(quadra.preco_hora), 2)

        return Reserva(
            quadra_id=quadra_id, usuario_reserva_id=jogadores[0],
            data_hora_inicio=inicio, data_hora_fim=fim,
            valor_total=valor_total,
        ).salvar(jogadores=jogadores)


class ListarReservasService:
    @staticmethod
    def executar():
        return [r.to_dict() for r in Reserva.listar_todos()]


class ListarReservasDetalhadasService:
    """Agenda completa do painel: JOIN triplo + nomes dos jogadores (procedures)."""
    @staticmethod
    def executar():
        reservas = ReservaRepository.listar_detalhadas()
        for reserva in reservas:
            nomes = [j["nome"] for j in ReservaRepository.jogadores_da_reserva(reserva["reserva_id"])]
            reserva["nomes_jogadores"] = nomes
            reserva["nome_usuario"] = ", ".join(nomes) if nomes else "—"
        return reservas


class BuscarReservaService:
    @staticmethod
    def executar(reserva_id):
        reserva = Reserva.buscar_por_id(reserva_id)
        if reserva is None:
            raise LookupError("Reserva não encontrada.")
        return reserva


class AtualizarStatusReservaService:
    @staticmethod
    def executar(reserva_id, dados):
        if not dados or dados.get("status") not in STATUS_VALIDOS:
            raise ValueError(f"Informe status: {' ou '.join(repr(s) for s in STATUS_VALIDOS)}.")
        reserva = BuscarReservaService.executar(reserva_id)
        reserva.status = dados["status"]
        return reserva.atualizar()


class DeletarReservaService:
    @staticmethod
    def executar(reserva_id):
        reserva = BuscarReservaService.executar(reserva_id)
        reserva.deletar()
