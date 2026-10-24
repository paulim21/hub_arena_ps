"""A política de privacidade como DADO, não como texto solto na tela.

A versão mora aqui, num lugar só. O front-end não a repete: ele pergunta
ao servidor qual é a versão vigente (`GET /api/consentimentos/politica`) e
pede novo aceite quando ela muda. Política versionada em dois lugares
sempre acaba divergindo, e aí o sistema passa a aceitar consentimento de
uma versão que ninguém leu.

Mexeu no texto de `frontend/termos.html` de um jeito que muda o que é
coletado, para que serve ou com quem é compartilhado? Suba a VERSAO. Todo
mundo será convidado a aceitar de novo, que é o que a LGPD pede quando a
finalidade muda (Art. 8º, § 6º).
"""

VERSAO = "1.0"
ATUALIZADO_EM = "2026-10-23"

# As finalidades ficam separadas porque consentimento é POR FINALIDADE:
# juntar tudo em "aceito os termos" é o que a LGPD chama de consentimento
# genérico, e ele é nulo (Art. 8º, § 4º).
FINALIDADES = [
    {
        "chave": "operacao",
        "nome": "Operar a plataforma",
        "detalhe": "Criar seu cadastro, agendar reservas, calcular o valor "
                   "das partidas e manter o histórico da arena.",
        "base_legal": "Execução de contrato (Art. 7º, V)",
        "obrigatoria": True,
    },
    {
        "chave": "comprovacao",
        "nome": "Comprovar este consentimento",
        "detalhe": "Guardar a data, a versão dos termos, o endereço IP e o "
                   "navegador usados no aceite — apenas como prova de que "
                   "ele existiu.",
        "base_legal": "Cumprimento de obrigação legal (Art. 7º, II)",
        "obrigatoria": True,
    },
]


def resumo():
    """O que o front-end precisa saber para montar o aviso de aceite."""
    return {
        "versao": VERSAO,
        "atualizado_em": ATUALIZADO_EM,
        "finalidades": FINALIDADES,
        "chaves": [f["chave"] for f in FINALIDADES],
    }
