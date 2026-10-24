"""Repository — Consentimento: consultas além do CRUD, via procedures."""
from repositories.procedure_runner import executar_procedure


class ConsentimentoRepository:
    @staticmethod
    def vigente(identificador, versao):
        """O aceite ainda válido deste aparelho para a versão informada."""
        return executar_procedure(
            "sp_consentimento_vigente",
            {"identificador": identificador, "versao": versao},
            unico=True,
        )

    @staticmethod
    def resumo_por_versao():
        """RELATÓRIO: aceites, revogações e vigentes por versão dos termos."""
        return executar_procedure("sp_consentimentos_por_versao")
