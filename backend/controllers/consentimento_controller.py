"""Controller — Consentimento LGPD (classe ligada ao recurso /api/consentimentos).

Recebe a requisição, interpreta os dados, chama o Service e devolve a
resposta. O IP e o navegador são lidos da requisição, e passados ao
Service: ler `request` dentro do Service amarraria a regra de negócio ao
Flask.
"""
from flask import jsonify, request

from services.consentimento_service import (
    ConsultarPoliticaService,
    RegistrarConsentimentoService,
    RelatorioConsentimentosService,
    RevogarConsentimentoService,
    VerificarConsentimentoService,
)


class ConsentimentoController:

    @staticmethod
    def politica():
        """GET /api/consentimentos/politica — versão e finalidades vigentes."""
        return jsonify(ConsultarPoliticaService.executar()), 200

    @staticmethod
    def registrar():
        """POST /api/consentimentos — grava o aceite com a versão dos termos."""
        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"erro": "Corpo JSON inválido ou ausente."}), 400
        try:
            registro = RegistrarConsentimentoService.executar(
                dados,
                origem_ip=request.headers.get("X-Forwarded-For", request.remote_addr),
                agente=request.headers.get("User-Agent"),
            )
            return jsonify(registro.to_dict()), 201
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400

    @staticmethod
    def verificar():
        """GET /api/consentimentos/vigente?identificador= — já aceitou?"""
        return jsonify(VerificarConsentimentoService.executar(
            request.args.get("identificador")
        )), 200

    @staticmethod
    def revogar():
        """POST /api/consentimentos/revogar — o titular retira o consentimento."""
        dados = request.get_json(silent=True)
        try:
            return jsonify(RevogarConsentimentoService.executar(dados)), 200
        except LookupError as e:
            return jsonify({"erro": str(e)}), 404
        except ValueError as e:
            return jsonify({"erro": str(e)}), 400

    @staticmethod
    def relatorio():
        """GET /api/consentimentos/relatorio — aceites por versão (procedure)."""
        return jsonify(RelatorioConsentimentosService.executar()), 200
