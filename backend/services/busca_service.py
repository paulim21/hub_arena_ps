"""Service — Busca global (um caso de uso: procurar em todo o sistema).

A busca de cada recurso já existia espalhada: usuário tinha a dela, arena
e quadra ganharam a sua. O que este Service acrescenta não é SQL, é
coordenação — ele faz as três perguntas de uma vez e devolve uma resposta
só, para que a tela não precise saber que são três procedures.

Por que o CPF não entra na busca: a política de privacidade promete que o
CPF não aparece em lugar público do sistema. Uma caixa de busca que
devolve gente por CPF é exatamente esse lugar.
"""
from repositories.arena_repository import ArenaRepository
from repositories.quadra_repository import QuadraRepository
from repositories.usuario_repository import UsuarioRepository

TERMO_MINIMO = 2


class BuscaGlobalService:
    @staticmethod
    def executar(termo):
        termo = (termo or "").strip()
        if not termo:
            raise ValueError("Informe o que procurar (?q=).")
        if len(termo) < TERMO_MINIMO:
            # Uma letra casa com quase tudo: a resposta seria o banco
            # inteiro, e quem procurou não aprenderia nada com ela.
            raise ValueError(
                f"Digite ao menos {TERMO_MINIMO} caracteres para buscar."
            )

        usuarios = UsuarioRepository.buscar_por_termo(termo)
        arenas = ArenaRepository.buscar_por_termo(termo)
        quadras = QuadraRepository.buscar_por_termo(termo)

        return {
            "termo": termo,
            "usuarios": usuarios,
            "arenas": arenas,
            "quadras": quadras,
            "total": len(usuarios) + len(arenas) + len(quadras),
        }
