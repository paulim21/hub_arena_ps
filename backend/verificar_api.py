"""Verifica a API de ponta a ponta, sem subir servidor.

Usa o cliente de teste do Flask: cada chamada percorre o caminho inteiro —
rota, Controller, Service, Model ou Repository e banco — como se viesse do
navegador. Roda contra um banco descartável, para nunca tocar o de verdade.

    python backend/verificar_api.py

Sai com 1 se qualquer verificação falhar, para servir em automação.
"""
import os
import sqlite3
import sys
import tempfile

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# O banco descartável precisa ser escolhido ANTES de importar a aplicação:
# é na importação que o caminho do arquivo é lido.
import database  # noqa: E402

_temporario = os.path.join(tempfile.mkdtemp(prefix="arenahub-teste-"), "teste.db")
database.NOME_BANCO = _temporario

from app import app  # noqa: E402

cli = app.test_client()
falhas = []
feitas = 0


def chamar(metodo, url, corpo=None, esperado=200, titulo=""):
    global feitas
    feitas += 1
    resp = cli.open(url, method=metodo, json=corpo)
    ok = resp.status_code == esperado
    print("  [%s] %2d. %s -> %d" % ("ok " if ok else "FALHA", feitas,
                                    titulo or (metodo + " " + url), resp.status_code))
    if not ok:
        falhas.append("%s: esperado %d, veio %d (%s)"
                      % (titulo, esperado, resp.status_code, resp.get_json()))
    return resp.get_json()


def conferir(titulo, condicao, detalhe=""):
    global feitas
    feitas += 1
    print("  [%s] %2d. %s%s" % ("ok " if condicao else "FALHA", feitas, titulo,
                                "" if condicao else "  -> " + str(detalhe)))
    if not condicao:
        falhas.append(titulo)


def cpf_valido(base):
    """Fecha os dois dígitos verificadores de uma base de nove dígitos."""
    def dv(digitos, inicio):
        soma = sum(int(d) * p for d, p in zip(digitos, range(inicio, 1, -1)))
        resto = soma % 11
        return "0" if resto < 2 else str(11 - resto)
    d1 = dv(base, 10)
    return base + d1 + dv(base + d1, 11)


def titulo(texto):
    print("\n" + texto)


# ===================================================================
titulo("TELAS E ARQUIVOS ESTATICOS")
for pagina in ("/", "/busca", "/usuarios", "/arenas", "/quadras",
               "/reservas", "/relatorios", "/termos"):
    chamar("GET", pagina, titulo="tela %s" % pagina)
for estatico in ("/css/tokens.css", "/css/estilo.css", "/js/tema.js",
                 "/js/base.js", "/js/interface.js", "/js/lgpd.js"):
    chamar("GET", estatico, titulo="estatico %s" % estatico)

titulo("USUARIOS (1 a 4)")
dono = chamar("POST", "/api/usuarios", {
    "nome": "Marcos Dono", "email": "marcos@teste.com", "cpf": cpf_valido("111444777"),
    "senha": "senha-forte", "telefone": "(31) 99999-0000", "tipo_usuario": "dono"},
    201, "cadastrar dono")
atleta = chamar("POST", "/api/usuarios", {
    "nome": "Ana Atleta", "email": "  Ana@Teste.COM ", "cpf": "123.456.789-09",
    "senha": "senha-forte", "telefone": "+55 31 98888-7777", "tipo_usuario": "atleta"},
    201, "cadastrar atleta com pontuacao e espacos")
conferir("e-mail normalizado para minusculas", atleta["email"] == "ana@teste.com",
         atleta["email"])
conferir("CPF guardado so com digitos", atleta["cpf"] == "12345678909", atleta["cpf"])
conferir("telefone guardado so com digitos", atleta["telefone"] == "31988887777",
         atleta["telefone"])

outro = chamar("POST", "/api/usuarios", {
    "nome": "Bia Atleta", "email": "bia@teste.com", "cpf": cpf_valido("529982247"),
    "senha": "senha-forte", "telefone": "31977776666", "tipo_usuario": "atleta"},
    201, "cadastrar segundo atleta")

chamar("POST", "/api/usuarios", {
    "nome": "CPF torto", "email": "x@teste.com", "cpf": "123.456.789-00",
    "senha": "senha-forte", "telefone": "31999990000", "tipo_usuario": "atleta"},
    400, "recusa CPF com digito verificador errado")
chamar("POST", "/api/usuarios", {
    "nome": "Repetido", "email": "ana@teste.com", "cpf": cpf_valido("390533447"),
    "senha": "senha-forte", "telefone": "31999990000", "tipo_usuario": "atleta"},
    400, "recusa e-mail ja cadastrado")
chamar("POST", "/api/usuarios", {
    "nome": "Senha curta", "email": "curta@teste.com", "cpf": cpf_valido("222333444"),
    "senha": "123", "telefone": "31999990000", "tipo_usuario": "atleta"},
    400, "recusa senha curta")

chamar("GET", "/api/usuarios?tipo=atleta", titulo="filtrar por tipo (procedure)")
chamar("GET", "/api/usuarios/busca?q=ana", titulo="buscar por nome (procedure LIKE)")

titulo("ARENAS E QUADRAS (5 a 10)")
chamar("POST", "/api/arenas", {
    "nome": "Arena do atleta", "endereco": "R", "cidade": "C",
    "dono_id": atleta["usuario_id"], "taxa_saas": 10}, 400,
    "recusa dono que nao e do tipo dono")
arena = chamar("POST", "/api/arenas", {
    "nome": "Arena Beira-Mar", "cnpj": "11.222.333/0001-81", "endereco": "Av Atlantica, 100",
    "cidade": "Salvador", "dono_id": dono["usuario_id"], "taxa_saas": 199.9,
    "dia_vencimento": 10}, 201, "cadastrar arena")
conferir("CNPJ guardado so com digitos", arena["cnpj"] == "11222333000181", arena["cnpj"])
chamar("POST", "/api/arenas", {
    "nome": "CNPJ torto", "cnpj": "11.222.333/0001-00", "endereco": "R", "cidade": "C",
    "dono_id": dono["usuario_id"], "taxa_saas": 10}, 400,
    "recusa CNPJ com digito verificador errado")

quadra = chamar("POST", "/api/quadras", {
    "arena_id": arena["arena_id"], "nome": "Quadra Central",
    "tipo_esporte": "Beach Tennis", "preco_hora": 90}, 201, "cadastrar quadra")
chamar("POST", "/api/quadras", {
    "arena_id": arena["arena_id"], "nome": "Quadra Mar",
    "tipo_esporte": "Futevolei", "preco_hora": 60}, 201, "cadastrar segunda quadra")
detalhadas = chamar("GET", "/api/quadras?detalhes=1", titulo="quadras com arena (JOIN)")
conferir("o JOIN trouxe o nome da arena", bool(detalhadas) and "nome_arena" in detalhadas[0])

titulo("RESERVAS (11 a 14) — o coracao do sistema")
reserva = chamar("POST", "/api/reservas", {
    "quadra_id": quadra["quadra_id"],
    "jogadores": [atleta["usuario_id"], outro["usuario_id"]],
    "data_hora_inicio": "2026-12-05T19:00", "data_hora_fim": "2026-12-05T20:30"},
    201, "criar reserva com dois jogadores")
conferir("valor calculado pelo servidor (1,5h x R$ 90)",
         reserva["valor_total"] == 135.0, reserva["valor_total"])
chamar("POST", "/api/reservas", {
    "quadra_id": quadra["quadra_id"], "jogadores": [atleta["usuario_id"]],
    "data_hora_inicio": "2026-12-05T20:00", "data_hora_fim": "2026-12-05T21:00"},
    400, "ANTI-OVERBOOKING barra horario em conflito")
chamar("POST", "/api/reservas", {
    "quadra_id": quadra["quadra_id"], "jogadores": [atleta["usuario_id"]],
    "data_hora_inicio": "2026-12-06T21:00", "data_hora_fim": "2026-12-06T20:00"},
    400, "recusa fim antes do inicio")
chamar("POST", "/api/reservas", {
    "quadra_id": quadra["quadra_id"], "jogadores": [],
    "data_hora_inicio": "2026-12-07T19:00", "data_hora_fim": "2026-12-07T20:00"},
    400, "exige ao menos um jogador")

confirmada = chamar("PUT", "/api/reservas/%d" % reserva["reserva_id"],
                    {"status": "confirmada"}, titulo="confirmar reserva")
conferir("status virou confirmada", confirmada["status"] == "confirmada")

titulo("RELATORIOS E BUSCAS (15 a 20)")
resumo = chamar("GET", "/api/relatorios/resumo", titulo="resumo do painel")
conferir("o resumo tem receita", resumo["receita_total"] > 0, resumo)
chamar("GET", "/api/relatorios/receita-arenas", titulo="receita por arena")
chamar("GET", "/api/relatorios/ocupacao-quadras", titulo="ocupacao das quadras")
chamar("GET", "/api/relatorios/ranking-atletas?limite=10", titulo="ranking de atletas")
ocupado = chamar("GET", "/api/quadras/disponiveis"
                        "?inicio=2026-12-05T19:30&fim=2026-12-05T20:00",
                 titulo="quadras livres num horario OCUPADO")
conferir("a quadra reservada nao aparece como livre",
         quadra["quadra_id"] not in [q["quadra_id"] for q in ocupado])
livre = chamar("GET", "/api/quadras/disponiveis"
                      "?inicio=2027-01-10T19:00&fim=2027-01-10T20:00",
               titulo="quadras livres num horario VAGO")
conferir("a quadra aparece quando o horario esta livre",
         quadra["quadra_id"] in [q["quadra_id"] for q in livre])
chamar("GET", "/api/arenas/%d/agenda?inicio=2026-12-01T00:00&fim=2026-12-31T23:59"
       % arena["arena_id"], titulo="agenda da arena no periodo")

titulo("CONSENTIMENTO LGPD (21 a 24)")
APARELHO = "aparelho-de-teste-0001"
politica = chamar("GET", "/api/consentimentos/politica", titulo="politica vigente")
antes = chamar("GET", "/api/consentimentos/vigente?identificador=" + APARELHO,
               titulo="verificar antes de aceitar")
conferir("nao ha consentimento no comeco", antes["vigente"] is False)
chamar("POST", "/api/consentimentos", {
    "identificador": APARELHO, "versao_termos": politica["versao"],
    "finalidades": ["operacao"]}, 400, "recusa consentimento parcial")
chamar("POST", "/api/consentimentos", {
    "identificador": APARELHO, "versao_termos": "0.1",
    "finalidades": politica["chaves"]}, 400, "recusa versao desatualizada")
chamar("POST", "/api/consentimentos", {
    "identificador": APARELHO, "versao_termos": politica["versao"],
    "finalidades": politica["chaves"]}, 201, "registrar consentimento")
depois = chamar("GET", "/api/consentimentos/vigente?identificador=" + APARELHO,
                titulo="verificar depois de aceitar")
conferir("o consentimento passou a valer", depois["vigente"] is True)
chamar("POST", "/api/consentimentos/revogar", {"identificador": APARELHO},
       titulo="revogar consentimento")
revogado = chamar("GET", "/api/consentimentos/vigente?identificador=" + APARELHO,
                  titulo="deixou de valer depois da revogacao")
conferir("a revogacao surtiu efeito", revogado["vigente"] is False)
relatorio = chamar("GET", "/api/consentimentos/relatorio", titulo="relatorio por versao")
conferir("o registro foi preservado apos a revogacao",
         bool(relatorio) and relatorio[0]["revogados"] >= 1, relatorio)

titulo("BUSCA GLOBAL (25)")
chamar("GET", "/api/busca?q=", esperado=400, titulo="exige um termo")
chamar("GET", "/api/busca?q=a", esperado=400, titulo="exige ao menos dois caracteres")
busca = chamar("GET", "/api/busca?q=beira", titulo="busca por nome de arena")
conferir("achou a arena e as quadras dela",
         len(busca["arenas"]) == 1 and len(busca["quadras"]) == 2, busca["total"])
porcidade = chamar("GET", "/api/busca?q=salvador", titulo="busca pela cidade")
conferir("a cidade encontra a arena", len(porcidade["arenas"]) == 1)
poresporte = chamar("GET", "/api/busca?q=beach", titulo="busca pelo esporte")
conferir("o esporte encontra a quadra", len(poresporte["quadras"]) == 1)
porcpf = chamar("GET", "/api/busca?q=" + atleta["cpf"][:6],
                titulo="o CPF NAO encontra ninguem (privacidade)")
conferir("o CPF nao vaza pela busca", porcpf["total"] == 0, porcpf)

titulo("INTEGRIDADE E SEGURANCA")
chamar("DELETE", "/api/usuarios/%d" % dono["usuario_id"], esperado=400,
       titulo="bloqueia excluir dono com arena")
chamar("DELETE", "/api/arenas/%d" % arena["arena_id"], esperado=400,
       titulo="bloqueia excluir arena com quadras")
chamar("DELETE", "/api/quadras/%d" % quadra["quadra_id"], esperado=400,
       titulo="bloqueia excluir quadra com reservas")

conexao = sqlite3.connect(database.NOME_BANCO)
senhas = [linha[0] for linha in conexao.execute("SELECT senha FROM usuarios")]
conexao.close()
conferir("nenhuma senha foi guardada em texto puro",
         not any("senha-forte" in s for s in senhas))

# ===================================================================
print("\n" + "=" * 62)
if falhas:
    print("RESULTADO: %d FALHA(S) em %d verificacoes\n" % (len(falhas), feitas))
    for f in falhas:
        print("  - " + f)
    sys.exit(1)
print("RESULTADO: todas as %d verificacoes passaram." % feitas)
