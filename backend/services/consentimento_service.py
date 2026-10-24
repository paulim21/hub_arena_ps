"""Services — Consentimento LGPD (uma classe por caso de uso)."""
import politica
from models.consentimento import Consentimento
from repositories.consentimento_repository import ConsentimentoRepository

TAMANHO_MINIMO_ID = 8
TAMANHO_MAXIMO_ID = 64


def _validar_identificador(identificador):
    identificador = (identificador or "").strip()
    if not TAMANHO_MINIMO_ID <= len(identificador) <= TAMANHO_MAXIMO_ID:
        raise ValueError("Identificador de consentimento inválido.")
    if not identificador.replace("-", "").isalnum():
        raise ValueError("Identificador de consentimento inválido.")
    return identificador


class ConsultarPoliticaService:
    """Caso de uso: qual política está valendo agora."""
    @staticmethod
    def executar():
        return politica.resumo()


class RegistrarConsentimentoService:
    """Caso de uso: o titular aceitou os termos.

    Recusa consentimento parcial: as finalidades declaradas obrigatórias
    sustentam o próprio funcionamento do sistema, e aceitar "metade" dele
    deixaria o titular achando que escolheu algo que não existe.
    """
    @staticmethod
    def executar(dados, origem_ip=None, agente=None):
        dados = dados or {}
        identificador = _validar_identificador(dados.get("identificador"))

        versao = (dados.get("versao_termos") or "").strip()
        if versao != politica.VERSAO:
            raise ValueError(
                f"Versão dos termos desatualizada: a vigente é {politica.VERSAO}."
            )

        aceitas = dados.get("finalidades") or []
        if not isinstance(aceitas, list):
            raise ValueError("Campo 'finalidades' deve ser uma lista.")
        faltando = [f["nome"] for f in politica.FINALIDADES
                    if f["obrigatoria"] and f["chave"] not in aceitas]
        if faltando:
            raise ValueError(
                "Para usar o sistema é preciso aceitar: " + ", ".join(faltando) + "."
            )

        # Um aceite novo substitui o anterior do mesmo aparelho: o histórico
        # fica, mas só um consentimento é o vigente.
        RevogarConsentimentoService.executar(
            {"identificador": identificador}, silencioso=True
        )

        return Consentimento(
            identificador=identificador,
            versao_termos=versao,
            finalidades=";".join(aceitas),
            aceito_em=Consentimento.agora(),
            origem_ip=origem_ip,
            agente=(agente or "")[:300],
        ).salvar()


class VerificarConsentimentoService:
    """Caso de uso: este aparelho já aceitou a versão vigente?"""
    @staticmethod
    def executar(identificador):
        try:
            identificador = _validar_identificador(identificador)
        except ValueError:
            # Identificador malformado não é erro do titular: é a primeira
            # visita, ou um valor que o navegador perdeu. Trata como "não".
            return {"vigente": False, "versao": politica.VERSAO}

        registro = ConsentimentoRepository.vigente(identificador, politica.VERSAO)
        if not registro:
            return {"vigente": False, "versao": politica.VERSAO}
        return {
            "vigente": True,
            "versao": politica.VERSAO,
            "aceito_em": registro["aceito_em"],
            "finalidades": [f for f in (registro["finalidades"] or "").split(";") if f],
        }


class RevogarConsentimentoService:
    """Caso de uso: o titular revoga o consentimento (Art. 8º, § 5º).

    A revogação é sempre possível e gratuita. O registro NÃO é apagado —
    ele é marcado como revogado, porque o controlador precisa continuar
    podendo provar o que houve, inclusive a própria revogação.
    """
    @staticmethod
    def executar(dados, silencioso=False):
        dados = dados or {}
        identificador = _validar_identificador(dados.get("identificador"))

        registros = Consentimento.query.filter_by(
            identificador=identificador, revogado_em=None
        ).all()
        if not registros and not silencioso:
            raise LookupError("Nenhum consentimento vigente para este identificador.")

        agora = Consentimento.agora()
        for registro in registros:
            registro.revogado_em = agora
        if registros:
            registros[0].atualizar()
        return {"revogados": len(registros), "revogado_em": agora if registros else None}


class RelatorioConsentimentosService:
    """Caso de uso: quantos aceites por versão — a prova agregada."""
    @staticmethod
    def executar():
        return ConsentimentoRepository.resumo_por_versao()
