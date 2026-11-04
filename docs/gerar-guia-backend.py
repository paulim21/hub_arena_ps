# -*- coding: utf-8 -*-
"""Gera docs/guia-backend.pdf — o guia do backend para a apresentação.

Não é dependência da aplicação: o ArenaHub roda sem isto. Para refazer o
PDF depois de mexer no backend:

    pip install reportlab
    python docs/gerar-guia-backend.py

Os números do documento (quantos Services, quantas procedures) são
CONTADOS do código, não digitados: um guia que promete 18 procedures e
entrega 16 vira ficção na primeira pergunta da banca.
"""
import os
import re
import sys

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, Frame, KeepTogether, NextPageTemplate,
                                PageBreak, PageTemplate, Paragraph, Spacer, Table,
                                TableStyle)

RAIZ = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
BACK = os.path.join(RAIZ, "backend")
SAIDA = os.path.join(RAIZ, "docs", "guia-backend.pdf")

NAVY = colors.HexColor("#1B2A4A")
AREIA = colors.HexColor("#EFD6B0")
PAPEL = colors.HexColor("#F4F1EB")
TINTA = colors.HexColor("#1F1B16")
FRACA = colors.HexColor("#5C564C")
LINHA = colors.HexColor("#D8D2C6")


# ====================================================================
#  Os números vêm do código
# ====================================================================
def ler(*caminho):
    with open(os.path.join(*caminho), encoding="utf-8") as f:
        return f.read()


def contar():
    servicos = []
    for arq in sorted(os.listdir(os.path.join(BACK, "services"))):
        if arq.endswith(".py") and arq != "__init__.py":
            servicos += re.findall(r"^class (\w+Service)", ler(BACK, "services", arq), re.M)

    controllers = []
    for arq in sorted(os.listdir(os.path.join(BACK, "controllers"))):
        if arq.endswith(".py") and arq != "__init__.py":
            fonte = ler(BACK, "controllers", arq)
            nome = re.search(r"^class (\w+)", fonte, re.M)
            if nome:
                controllers.append((nome.group(1), len(re.findall(r"@staticmethod", fonte))))

    modelos = []
    for arq in sorted(os.listdir(os.path.join(BACK, "models"))):
        if arq.endswith(".py") and arq != "__init__.py":
            fonte = ler(BACK, "models", arq)
            nome = re.search(r"^class (\w+)", fonte, re.M)
            tabela = re.search(r'__tablename__ = "(\w+)"', fonte)
            if nome and tabela:
                modelos.append((nome.group(1), tabela.group(1),
                                len(re.findall(r"db\.Column", fonte))))

    repos = []
    for arq in sorted(os.listdir(os.path.join(BACK, "repositories"))):
        if arq.endswith("_repository.py"):
            fonte = ler(BACK, "repositories", arq)
            nome = re.search(r"^class (\w+)", fonte, re.M)
            if nome:
                repos.append((nome.group(1), len(re.findall(r"@staticmethod", fonte))))

    sql = ler(BACK, "repositories", "procedures.sql")
    procedures = re.findall(r"^-- PROCEDURE: (\S+)", sql, re.M)
    rotas = len(re.findall(r"add_url_rule", ler(BACK, "routes.py")))

    return {"servicos": sorted(servicos), "controllers": controllers,
            "modelos": modelos, "repos": repos, "procedures": procedures,
            "rotas": rotas}


DADOS = contar()


# ====================================================================
#  Estilos
# ====================================================================
base = getSampleStyleSheet()
E = {
    "titulo": ParagraphStyle("titulo", parent=base["Title"], fontName="Helvetica-Bold",
                             fontSize=26, leading=30, textColor=NAVY, spaceAfter=4),
    "subtitulo": ParagraphStyle("subtitulo", parent=base["Normal"], fontSize=12,
                                leading=16, textColor=FRACA, alignment=TA_CENTER),
    "h1": ParagraphStyle("h1", parent=base["Heading1"], fontName="Helvetica-Bold",
                         fontSize=16, leading=20, textColor=NAVY,
                         spaceBefore=14, spaceAfter=7),
    "h2": ParagraphStyle("h2", parent=base["Heading2"], fontName="Helvetica-Bold",
                         fontSize=12, leading=15, textColor=TINTA,
                         spaceBefore=10, spaceAfter=4),
    "p": ParagraphStyle("p", parent=base["Normal"], fontSize=9.5, leading=14,
                        textColor=TINTA, alignment=TA_JUSTIFY, spaceAfter=6),
    "nota": ParagraphStyle("nota", parent=base["Normal"], fontSize=8.5, leading=12,
                           textColor=FRACA, spaceAfter=6),
    "cel": ParagraphStyle("cel", parent=base["Normal"], fontSize=8, leading=10.5,
                          textColor=TINTA),
    "celb": ParagraphStyle("celb", parent=base["Normal"], fontName="Helvetica-Bold",
                           fontSize=8, leading=10.5, textColor=TINTA),
    "cod": ParagraphStyle("cod", parent=base["Normal"], fontName="Courier",
                          fontSize=7.5, leading=10, textColor=NAVY),
    "cabtab": ParagraphStyle("cabtab", parent=base["Normal"], fontName="Helvetica-Bold",
                             fontSize=7.5, leading=10, textColor=colors.white),
}


def P(txt, estilo="p"):
    return Paragraph(txt, E[estilo])


def tabela(cabecalho, linhas, larguras, destaque_col0=True):
    dados = [[Paragraph(c, E["cabtab"]) for c in cabecalho]]
    for ln in linhas:
        linha = []
        for i, c in enumerate(ln):
            if isinstance(c, Paragraph):
                linha.append(c)
            else:
                est = "celb" if (i == 0 and destaque_col0) else "cel"
                linha.append(Paragraph(str(c), E[est]))
        dados.append(linha)
    t = Table(dados, colWidths=larguras, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("GRID", (0, 0), (-1, -1), 0.4, LINHA),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PAPEL]),
    ]))
    return t


def caixa(titulo, corpo, cor=AREIA):
    """Um bloco destacado — serve de 'atenção' na apresentação."""
    interno = [P("<b>%s</b>" % titulo, "cel"), Spacer(1, 3), P(corpo, "cel")]
    t = Table([[interno]], colWidths=[170 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("LINEABOVE", (0, 0), (-1, 0), 2, cor),
        ("BOX", (0, 0), (-1, -1), 0.4, LINHA),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


# ====================================================================
#  O diagrama do caminho de uma requisição
# ====================================================================
def fluxo():
    etapas = [
        ("1. TELA", "frontend/reservas.html",
         "Monta o JSON e chama fetch('/api/reservas', POST). Não calcula valor nenhum."),
        ("2. ROTA", "backend/routes.py",
         "Mapa de URL para metodo de Controller. 34 rotas, nenhuma logica."),
        ("3. CONTROLLER", "ReservaController.criar",
         "Le o corpo JSON, chama o Service, traduz excecao em status HTTP. Sem regra."),
        ("4. SERVICE", "CriarReservaService.executar",
         "Valida, pergunta ao Repository se ha conflito, calcula horas x preco."),
        ("5. MODEL / REPOSITORY", "Reserva.salvar / ReservaRepository",
         "Model persiste; Repository executa a procedure sp_conflito_reserva."),
        ("6. BANCO", "backend/hub_arena.db",
         "SQLite com as 6 tabelas e a tabela procedures."),
    ]
    linhas = []
    for titulo, arquivo, texto in etapas:
        linhas.append([
            Paragraph("<b>%s</b><br/><font face='Courier' size='7' color='#1B2A4A'>%s</font>"
                      % (titulo, arquivo), E["cel"]),
            Paragraph(texto, E["cel"]),
        ])
    t = Table(linhas, colWidths=[58 * mm, 112 * mm])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (0, -1), PAPEL),
        ("LINEBEFORE", (0, 0), (0, -1), 3, NAVY),
        ("GRID", (0, 0), (-1, -1), 0.4, LINHA),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
    ]))
    return t


# ====================================================================
#  Conteúdo
# ====================================================================
def construir():
    h = []

    # ---------------- capa ----------------
    h.append(Spacer(1, 45 * mm))
    h.append(P("ArenaHub", "titulo"))
    h.append(P("Guia do backend", "subtitulo"))
    h.append(Spacer(1, 4 * mm))
    h.append(P("O que cada camada faz, por que ela existe<br/>"
               "e por onde passa cada uma das 24 funcionalidades.", "subtitulo"))
    h.append(Spacer(1, 14 * mm))

    numeros = [
        ("%d" % len(DADOS["modelos"]), "Models"),
        ("%d" % len(DADOS["controllers"]), "Controllers"),
        ("%d" % len(DADOS["servicos"]), "Services"),
        ("%d" % len(DADOS["repos"]), "Repositories"),
        ("%d" % len(DADOS["procedures"]), "Procedures"),
        ("%d" % DADOS["rotas"], "Rotas"),
    ]
    cels = [[Paragraph("<font size='17' color='#1B2A4A'><b>%s</b></font><br/>"
                       "<font size='7.5' color='#5C564C'>%s</font>" % (n, r),
                       ParagraphStyle("c", parent=E["cel"], alignment=TA_CENTER))
             for n, r in numeros]]
    t = Table(cels, colWidths=[28 * mm] * 6)
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LINEABOVE", (0, 0), (-1, 0), 2, AREIA),
        ("LINEBELOW", (0, -1), (-1, -1), 2, AREIA),
    ]))
    h.append(t)
    h.append(Spacer(1, 10 * mm))
    h.append(P("Flask + Flask-SQLAlchemy + SQLite &#183; "
               "github.com/paulim21/hub_arena_ps", "subtitulo"))

    # ---------------- 1. o caminho ----------------
    h.append(PageBreak())
    h.append(P("1. O caminho de uma requisicao", "h1"))
    h.append(P("Toda funcionalidade do sistema faz o mesmo percurso. O exemplo abaixo e o de "
               "criar uma reserva, que e o mais completo: ele passa por todas as camadas e "
               "ainda consulta uma procedure no meio do caminho."))
    h.append(Spacer(1, 3 * mm))
    h.append(fluxo())
    h.append(Spacer(1, 5 * mm))
    h.append(caixa(
        "A pergunta que a banca faz: por que tantas camadas?",
        "Porque cada uma responde por uma coisa so, e isso aparece quando algo muda. "
        "Trocar SQLite por MySQL mexe no Repository e nao toca no Service. Mudar a regra de "
        "cobranca mexe no Service e nao toca na Controller. Trocar a tela nao mexe em nada do "
        "backend, porque a tela so fala com a API. Em um arquivo unico, qualquer uma dessas "
        "mudancas obriga a reler tudo."))
    h.append(Spacer(1, 4 * mm))
    h.append(caixa(
        "O valor da reserva e calculado no SERVIDOR, nunca na tela",
        "O frontend manda quadra, inicio, fim e jogadores. Quem multiplica horas pelo preco "
        "da quadra e o CriarReservaService. Se o valor viesse da tela, bastaria abrir o "
        "console do navegador e mandar 'valor_total: 0'.", NAVY))

    # ---------------- 2. mapa de arquivos ----------------
    h.append(PageBreak())
    h.append(P("2. Mapa do backend, arquivo por arquivo", "h1"))
    arquivos = [
        ("app.py", "Application Factory: cria a aplicacao, liga o SQLAlchemy, ativa as "
                   "chaves estrangeiras do SQLite, cria as tabelas e registra as rotas."),
        ("routes.py", "Mapa de URL -> metodo de Controller. Os Blueprints vivem aqui, e "
                      "nenhuma logica mora neste arquivo."),
        ("extensions.py", "O objeto db, criado sem vinculo com a app para que Models e "
                          "Repositories possam importar sem import circular."),
        ("database.py", "Registra as procedures no banco e aplica as migracoes de coluna "
                        "(create_all nao altera tabela que ja existe)."),
        ("politica.py", "A versao e as finalidades dos termos de uso, num lugar so."),
        ("validadores.py", "A forma de CPF, CNPJ, telefone e e-mail: digito verificador, "
                           "DDD e normalizacao."),
        ("models/", "6 classes que herdam de db.Model. Cada uma e uma tabela, e carrega o "
                    "CRUD basico."),
        ("controllers/", "6 classes, uma por recurso. Recebem HTTP e devolvem HTTP."),
        ("services/", "%d classes, uma por caso de uso. Toda a regra de negocio."
                      % len(DADOS["servicos"])),
        ("repositories/", "6 classes para consultas complexas, mais o runner que executa "
                          "as procedures e o arquivo procedures.sql."),
    ]
    h.append(tabela(["Arquivo ou pasta", "Do que responde"],
                    [[Paragraph("<font face='Courier' size='8'><b>%s</b></font>" % a, E["cel"]), b]
                     for a, b in arquivos],
                    [38 * mm, 132 * mm]))

    # ---------------- 3. models ----------------
    h.append(PageBreak())
    h.append(P("3. Models: as entidades do dominio", "h1"))
    h.append(P("Herdam de <font face='Courier'>db.Model</font>, e e essa heranca que mapeia "
               "cada classe a uma tabela. O CRUD basico fica na propria Model, como pede a "
               "arquitetura da disciplina: <font face='Courier'>salvar()</font>, "
               "<font face='Courier'>atualizar()</font>, <font face='Courier'>deletar()</font>, "
               "<font face='Courier'>listar_todos()</font> e "
               "<font face='Courier'>buscar_por_id()</font>."))
    descr = {
        "Usuario": "Atleta, dono ou professor. E-mail e CPF sao UNIQUE; a senha e guardada "
                   "como resumo scrypt, nunca em texto.",
        "Arena": "Pertence a um dono (FK para usuarios) e agrega quadras.",
        "Quadra": "Pertence a uma arena. O preco por hora daqui e a base do valor da reserva.",
        "Reserva": "Quadra, periodo, valor e status. salvar() e redefinida para gravar a "
                   "reserva e os jogadores na mesma transacao.",
        "ReservaJogador": "Classe associativa que resolve o N:N entre Reserva e Usuario. "
                          "Chave primaria composta, e ON DELETE CASCADE.",
        "Consentimento": "O aceite dos termos, com versao, data, IP e navegador. Nao tem FK "
                         "para Usuario de proposito (ver secao 8).",
    }
    h.append(tabela(["Model", "Tabela", "Colunas", "O que representa"],
                    [[n, Paragraph("<font face='Courier' size='7.5'>%s</font>" % t, E["cel"]),
                      str(c), descr.get(n, "")]
                     for n, t, c in DADOS["modelos"]],
                    [28 * mm, 30 * mm, 15 * mm, 97 * mm]))
    h.append(Spacer(1, 4 * mm))
    h.append(caixa(
        "Relacionamentos, na linguagem do diagrama de classes",
        "<b>Composicao</b> (a parte nao existe sem o todo): Arena para Quadra, e Reserva para "
        "ReservaJogador. <b>Agregacao</b> (a parte existe por si so): Usuario para Arena, "
        "Quadra para Reserva, Usuario para Reserva e Usuario para ReservaJogador. "
        "O diagrama completo esta em docs/diagrama-classes.svg."))

    # ---------------- 4. controllers ----------------
    h.append(PageBreak())
    h.append(P("4. Controllers: a fronteira com o HTTP", "h1"))
    h.append(P("Sao classes, uma por recurso. Fazem tres coisas e nada mais: leem o que veio "
               "na requisicao, chamam o Service correspondente e traduzem o resultado (ou a "
               "excecao) em resposta HTTP com o status certo."))
    h.append(tabela(["Controller", "Metodos", "Recurso"],
                    [[n, str(m), Paragraph("<font face='Courier' size='7.5'>/api/%s</font>"
                                           % n.replace("Controller", "").lower()
                                           .replace("relatorio", "relatorios")
                                           .replace("consentimento", "consentimentos")
                                           + ("s" if n.replace("Controller", "").lower()
                                              not in ("relatorio", "consentimento") else ""),
                                           E["cel"])]
                     for n, m in DADOS["controllers"]],
                    [40 * mm, 25 * mm, 105 * mm]))
    h.append(Spacer(1, 4 * mm))
    h.append(P("A traducao de excecao em status e a convencao do projeto:", "h2"))
    h.append(tabela(["Excecao no Service", "Status HTTP", "Quando acontece"],
                    [["ValueError", "400", "Dado invalido ou regra de negocio violada "
                                           "(CPF errado, horario em conflito)"],
                     ["LookupError", "404", "O registro pedido nao existe"],
                     ["IntegrityError", "400", "O banco recusou (UNIQUE ou chave estrangeira), "
                                               "e o Service traduz em mensagem legivel"]],
                    [40 * mm, 25 * mm, 105 * mm]))
    h.append(Spacer(1, 4 * mm))
    h.append(caixa(
        "O que NAO pode aparecer numa Controller",
        "Calculo, validacao de regra, SQL e chamada de procedure. Se a banca abrir um arquivo "
        "de controller e encontrar um 'if' decidindo preco, a separacao de camadas caiu.", NAVY))

    # ---------------- 5. services ----------------
    h.append(PageBreak())
    h.append(P("5. Services: um por caso de uso", "h1"))
    h.append(P("Cada classe responde por <b>uma acao</b> do sistema e expoe um unico metodo "
               "<font face='Courier'>executar()</font>. E aqui que mora toda a regra de "
               "negocio, e e por isso que sao %d classes e nao seis."
               % len(DADOS["servicos"])))
    cols, por_col = [], (len(DADOS["servicos"]) + 2) // 3
    for i in range(3):
        pedaco = DADOS["servicos"][i * por_col:(i + 1) * por_col]
        cols.append(Paragraph("<br/>".join(pedaco), E["cod"]))
    t = Table([cols], colWidths=[56 * mm] * 3)
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("BACKGROUND", (0, 0), (-1, -1), PAPEL),
                           ("BOX", (0, 0), (-1, -1), 0.4, LINHA),
                           ("TOPPADDING", (0, 0), (-1, -1), 7),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                           ("LEFTPADDING", (0, 0), (-1, -1), 7)]))
    h.append(t)
    h.append(Spacer(1, 5 * mm))
    h.append(P("Os tres Services que vale abrir na apresentacao", "h2"))
    h.append(tabela(["Service", "Por que ele e interessante"],
                    [["CriarReservaService",
                      "Concentra as duas regras mais citadas do projeto: pergunta ao Repository "
                      "se ha conflito de horario (anti-overbooking) e calcula o valor como "
                      "horas x preco da quadra. Tambem aceita varios jogadores, gravando o N:N."],
                     ["CriarUsuarioService",
                      "Valida a forma dos dados antes de tocar o banco (CPF com digito "
                      "verificador, e-mail normalizado, telefone com DDD) e transforma a senha "
                      "em resumo scrypt. Quando o UNIQUE estoura, diz QUAL campo colidiu."],
                     ["RegistrarConsentimentoService",
                      "Recusa consentimento parcial e versao desatualizada dos termos, e revoga "
                      "o aceite anterior do mesmo aparelho antes de gravar o novo."]],
                    [42 * mm, 128 * mm]))

    # ---------------- 6. repository e procedures ----------------
    h.append(PageBreak())
    h.append(P("6. Repository e as procedures", "h1"))
    h.append(P("O Repository nao repete CRUD simples: isso ja esta na Model. Ele existe para "
               "<b>consulta complexa</b> — JOIN, GROUP BY, NOT EXISTS, ranking, relatorio — e "
               "e o unico lugar do sistema que executa SQL."))
    h.append(Spacer(1, 2 * mm))
    h.append(caixa(
        "Como existem procedures em SQLite",
        "O SQLite e um banco embarcado e nao tem CREATE PROCEDURE, que e recurso de SGBD "
        "cliente-servidor. Para atender ao requisito, cada procedure e <b>armazenada na propria "
        "tabela procedures do banco</b> (nome + SQL parametrizado), registrada na subida do "
        "servidor a partir de repositories/procedures.sql. Quem faz o papel do CALL e o "
        "procedure_runner.py, dentro do Repository. Controller e Service nunca executam SQL."))
    h.append(Spacer(1, 4 * mm))
    h.append(P("As %d procedures" % len(DADOS["procedures"]), "h2"))
    uso = {
        "sp_usuarios_por_tipo": "Filtro de usuarios por perfil",
        "sp_busca_usuarios": "Busca textual por nome ou e-mail (LIKE)",
        "sp_arenas_por_cidade": "Filtro de arenas por cidade",
        "sp_arenas_com_dono": "JOIN com o dono + contagem de quadras",
        "sp_quadras_com_arena": "JOIN quadra/arena",
        "sp_quadras_por_arena": "Quadras de uma arena",
        "sp_conflito_reserva": "ANTI-OVERBOOKING: reservas que colidem no periodo",
        "sp_reservas_detalhadas": "JOIN triplo reserva/quadra/arena",
        "sp_reservas_recentes": "Ultimas reservas do painel",
        "sp_jogadores_da_reserva": "Nomes dos jogadores (JOIN no N:N)",
        "sp_resumo_dashboard": "Contadores e receita total",
        "sp_receita_por_arena": "RELATORIO: JOIN + GROUP BY + ticket medio",
        "sp_ocupacao_quadras": "RELATORIO: horas reservadas e receita por quadra",
        "sp_ranking_atletas": "RELATORIO: ranking por jogos e horas",
        "sp_quadras_disponiveis": "BUSCA: quadras livres no periodo (NOT EXISTS)",
        "sp_agenda_arena": "Agenda da arena no periodo",
        "sp_consentimento_vigente": "LGPD: o aceite ainda valido deste aparelho",
        "sp_consentimentos_por_versao": "LGPD: aceites, vigentes e revogados por versao",
    }
    h.append(tabela(["Procedure", "Para que serve"],
                    [[Paragraph("<font face='Courier' size='7.5'>%s</font>" % p, E["cel"]),
                      uso.get(p, "")] for p in DADOS["procedures"]],
                    [52 * mm, 118 * mm]))

    # ---------------- 7. as 24 funcionalidades ----------------
    h.append(PageBreak())
    h.append(P("7. As 24 funcionalidades, de ponta a ponta", "h1"))
    h.append(P("Cada linha e um caminho completo: tela, rota, Controller, Service e, quando "
               "ha consulta complexa, a procedure que o Repository executa."))
    func = [
        ("1", "Cadastrar usuario", "POST /api/usuarios", "CriarUsuarioService", "-"),
        ("2", "Listar/filtrar por tipo", "GET /api/usuarios?tipo=", "ListarUsuariosService",
         "sp_usuarios_por_tipo"),
        ("3", "Buscar por nome ou e-mail", "GET /api/usuarios/busca", "PesquisarUsuariosService",
         "sp_busca_usuarios"),
        ("4", "Excluir usuario", "DELETE /api/usuarios/<id>", "DeletarUsuarioService", "-"),
        ("5", "Cadastrar arena", "POST /api/arenas", "CriarArenaService", "-"),
        ("6", "Listar arenas com dono", "GET /api/arenas?detalhes=1", "ListarArenasComDonoService",
         "sp_arenas_com_dono"),
        ("7", "Excluir arena", "DELETE /api/arenas/<id>", "DeletarArenaService", "-"),
        ("8", "Cadastrar quadra", "POST /api/quadras", "CriarQuadraService", "-"),
        ("9", "Listar/filtrar quadras", "GET /api/quadras", "ListarQuadrasService",
         "sp_quadras_com_arena"),
        ("10", "Excluir quadra", "DELETE /api/quadras/<id>", "DeletarQuadraService", "-"),
        ("11", "Criar reserva", "POST /api/reservas", "CriarReservaService",
         "sp_conflito_reserva"),
        ("12", "Listar reservas detalhadas", "GET /api/reservas?detalhes=1",
         "ListarReservasDetalhadasService", "sp_reservas_detalhadas"),
        ("13", "Confirmar reserva", "PUT /api/reservas/<id>", "AtualizarStatusReservaService", "-"),
        ("14", "Cancelar reserva", "DELETE /api/reservas/<id>", "DeletarReservaService", "-"),
        ("15", "Painel com resumo", "GET /api/relatorios/resumo", "ResumoDashboardService",
         "sp_resumo_dashboard"),
        ("16", "Receita por arena", "GET /api/relatorios/receita-arenas", "ReceitaPorArenaService",
         "sp_receita_por_arena"),
        ("17", "Ocupacao das quadras", "GET /api/relatorios/ocupacao-quadras",
         "OcupacaoQuadrasService", "sp_ocupacao_quadras"),
        ("18", "Ranking de atletas", "GET /api/relatorios/ranking-atletas", "RankingAtletasService",
         "sp_ranking_atletas"),
        ("19", "Quadras disponiveis", "GET /api/quadras/disponiveis", "QuadrasDisponiveisService",
         "sp_quadras_disponiveis"),
        ("20", "Agenda da arena", "GET /api/arenas/<id>/agenda", "AgendaArenaService",
         "sp_agenda_arena"),
        ("21", "Registrar consentimento", "POST /api/consentimentos",
         "RegistrarConsentimentoService", "-"),
        ("22", "Verificar consentimento", "GET /api/consentimentos/vigente",
         "VerificarConsentimentoService", "sp_consentimento_vigente"),
        ("23", "Revogar consentimento", "POST /api/consentimentos/revogar",
         "RevogarConsentimentoService", "-"),
        ("24", "Relatorio de consentimentos", "GET /api/consentimentos/relatorio",
         "RelatorioConsentimentosService", "sp_consentimentos_por_versao"),
    ]
    h.append(tabela(["#", "Funcionalidade", "Rota", "Service", "Procedure"],
                    [[n, f,
                      Paragraph("<font face='Courier' size='6.5'>%s</font>" % r, E["cel"]),
                      Paragraph("<font face='Courier' size='6.5'>%s</font>" % s, E["cel"]),
                      Paragraph("<font face='Courier' size='6.5'>%s</font>" % p, E["cel"])]
                     for n, f, r, s, p in func],
                    [8 * mm, 38 * mm, 42 * mm, 46 * mm, 36 * mm]))

    # ---------------- 8. LGPD ----------------
    h.append(PageBreak())
    h.append(P("8. O consentimento LGPD no backend", "h1"))
    h.append(P("O sistema nao abre antes do aceite: o frontend segura toda chamada a API ate "
               "existir consentimento. Mas a parte que importa para a defesa esta no backend."))
    h.append(tabela(["O que a lei pede", "Onde isso esta no codigo"],
                    [["Comprovar o consentimento obtido (Art. 8, par. 1)",
                      "Cada aceite e uma linha na tabela consentimentos, com versao dos termos, "
                      "data, IP e navegador. Um sinalizador no navegador nao comprova nada."],
                     ["Consentimento por finalidade; o generico e nulo (Art. 8, par. 4)",
                      "politica.py declara as finalidades separadas, e o "
                      "RegistrarConsentimentoService recusa aceite parcial."],
                     ["Novo aceite quando a finalidade muda (Art. 8, par. 6)",
                      "O campo versao_termos. O Service recusa aceite de versao que nao e a "
                      "vigente; subir a VERSAO faz todo mundo aceitar de novo."],
                     ["Revogacao livre e gratuita (Art. 8, par. 5)",
                      "RevogarConsentimentoService preenche revogado_em. O registro NAO e "
                      "apagado: ele e a prova, inclusive da revogacao."],
                     ["Medidas de seguranca (Art. 46)",
                      "A senha vai ao banco como resumo scrypt com sal. Nem a equipe consegue "
                      "ler a senha de um usuario."],
                     ["Minimizacao (Art. 6, III)",
                      "Consentimento guarda um identificador ALEATORIO do navegador, e nao o "
                      "usuario_id. Por isso a Model nao tem chave estrangeira para Usuario."]],
                    [52 * mm, 118 * mm]))

    # ---------------- 9. validacao e seguranca ----------------
    h.append(PageBreak())
    h.append(P("9. Validacao e seguranca", "h1"))
    h.append(P("O arquivo <font face='Courier'>validadores.py</font> conhece a forma dos dados "
               "que tem forma. Ele fica fora dos Services de proposito: nao e caso de uso, e a "
               "forma do dado, e ela e a mesma para quem cadastra e para quem atualiza."))
    h.append(tabela(["Dado", "O que e conferido", "Como vai ao banco"],
                    [["CPF", "11 digitos, digitos verificadores calculados, e recusa de "
                             "sequencias repetidas como 111.111.111-11", "12345678909"],
                     ["CNPJ", "14 digitos e digitos verificadores (opcional na arena)",
                      "11222333000181"],
                     ["Telefone", "DDD valido e 8 ou 9 digitos; celular de 9 precisa comecar "
                                  "com 9; o 55 do pais e descartado", "31999990000"],
                     ["E-mail", "formato, e normalizacao para minusculas (senao Ana@x.com e "
                                "ana@x.com viram duas contas)", "ana@email.com"],
                     ["Senha", "minimo de 6 caracteres", "resumo scrypt com sal"]],
                    [22 * mm, 100 * mm, 48 * mm]))
    h.append(Spacer(1, 4 * mm))
    h.append(caixa(
        "A pontuacao e apresentacao, e apresentacao nao se persiste",
        "O banco guarda 12345678909, nunca 123.456.789-09. Gravar formatado obriga todo filtro, "
        "toda busca e todo indice a adivinhar qual das grafias veio. A mascara aparece ao "
        "digitar, no frontend, e a formatacao para leitura acontece na tela."))
    h.append(Spacer(1, 4 * mm))
    h.append(P("Integridade no banco", "h2"))
    h.append(P("O SQLite so respeita chave estrangeira se o PRAGMA for ligado <b>em cada "
               "conexao</b>, e e isso que o app.py faz. E por causa disso que excluir um dono "
               "com arena, uma arena com quadras ou uma quadra com reservas e recusado — e o "
               "Service traduz esse erro do banco em uma frase que a pessoa entende."))

    # ---------------- 10. rodar e demonstrar ----------------
    h.append(PageBreak())
    h.append(P("10. Como rodar e o que mostrar", "h1"))
    h.append(P("Subir o projeto", "h2"))
    h.append(Paragraph(
        "python -m venv venv<br/>"
        "venv\\Scripts\\activate<br/>"
        "pip install -r requirements.txt<br/>"
        "python backend/app.py", E["cod"]))
    h.append(Spacer(1, 2 * mm))
    h.append(P("O banco <font face='Courier'>backend/hub_arena.db</font> e criado sozinho na "
               "primeira execucao, com as tabelas e as procedures registradas. Painel em "
               "localhost:5000; a API responde em /api/... e pode ser aberta direto no "
               "navegador ou no Postman."))
    h.append(Spacer(1, 3 * mm))
    h.append(P("A sequencia que mostra o backend inteiro em quatro minutos", "h2"))
    h.append(tabela(["Passo", "O que dizer enquanto mostra"],
                    [["Aceitar os termos",
                      "O aviso aparece antes de tudo e os paineis atras estao vazios: nenhuma "
                      "chamada a API acontece sem consentimento, e o aceite vai para o banco."],
                     ["Cadastrar um usuario",
                      "Digitar o CPF devagar para a mascara aparecer, e citar que o servidor "
                      "confere os digitos verificadores e guarda so os numeros."],
                     ["Criar uma reserva",
                      "Apontar o valor na tabela: ele veio do servidor. Em seguida tentar o "
                      "mesmo horario na mesma quadra e mostrar o bloqueio."],
                     ["Abrir os relatorios",
                      "Receita por arena (JOIN + GROUP BY), ocupacao, ranking e quadras "
                      "disponiveis (NOT EXISTS). Todos sao procedure chamada pelo Repository."],
                     ["Abrir o codigo",
                      "reserva_controller.py (so recebe e devolve), reserva_service.py (a regra), "
                      "reserva.py (o CRUD na Model) e procedures.sql (o SQL)."]],
                    [34 * mm, 136 * mm]))

    # ---------------- 11. perguntas ----------------
    h.append(PageBreak())
    h.append(P("11. Perguntas provaveis, e o que responder", "h1"))
    perguntas = [
        ("Por que o Repository nao tem os metodos de CRUD?",
         "Porque o CRUD simples ja esta na Model, como a arquitetura da disciplina pede. "
         "Criar um Repository so para repetir save e delete seria uma camada sem trabalho. "
         "O Repository existe para o que a Model nao faz: JOIN, GROUP BY, NOT EXISTS e as "
         "procedures."),
        ("Isso e procedure de verdade? SQLite nao tem CREATE PROCEDURE.",
         "Nao tem mesmo, e por isso o projeto guarda cada procedure na tabela procedures do "
         "proprio banco, com o SQL parametrizado, e as executa pelo procedure_runner. O que o "
         "requisito pede — SQL fora do codigo, encapsulado no Repository, chamado por nome — "
         "esta cumprido. Controller e Service nunca executam SQL."),
        ("Por que %d Services? Nao daria para ter um por recurso?"
         % len(DADOS["servicos"]),
         "Daria, mas ai cada classe teria varias responsabilidades. O criterio adotado e um "
         "Service por CASO DE USO, entao cadastrar usuario e listar usuarios sao classes "
         "diferentes, com um metodo executar() cada."),
        ("Onde esta a regra de negocio?",
         "Sempre no Service. A Controller so traduz HTTP, a Model so persiste e o Repository "
         "so consulta. O anti-overbooking e o calculo do valor estao no CriarReservaService."),
        ("Como o sistema impede duas reservas no mesmo horario?",
         "O Service chama ReservaRepository.existe_conflito, que executa a procedure "
         "sp_conflito_reserva: ela procura reserva na mesma quadra cujo inicio seja menor que o "
         "fim pedido e cujo fim seja maior que o inicio pedido. Se achar, o Service levanta "
         "ValueError e a Controller devolve 400."),
        ("E se o usuario mandar o valor da reserva pela API?",
         "E ignorado. O CriarReservaService nem le esse campo: ele calcula horas vezes o preco "
         "da quadra que esta no banco."),
    ]
    for q, r in perguntas:
        h.append(KeepTogether([P("<b>%s</b>" % q, "h2"), P(r)]))

    return h


# ====================================================================
#  Montagem
# ====================================================================
def rodape(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(FRACA)
    if doc.page > 1:
        canvas.drawString(20 * mm, 12 * mm, "ArenaHub - Guia do backend")
        canvas.drawRightString(190 * mm, 12 * mm, "%d" % doc.page)
        canvas.setStrokeColor(LINHA)
        canvas.setLineWidth(0.4)
        canvas.line(20 * mm, 15 * mm, 190 * mm, 15 * mm)
    canvas.restoreState()


def gerar():
    doc = BaseDocTemplate(SAIDA, pagesize=A4,
                          leftMargin=20 * mm, rightMargin=20 * mm,
                          topMargin=18 * mm, bottomMargin=20 * mm,
                          title="ArenaHub - Guia do backend",
                          author="ArenaHub")
    quadro = Frame(doc.leftMargin, doc.bottomMargin,
                   doc.width, doc.height, id="corpo")
    doc.addPageTemplates([PageTemplate(id="padrao", frames=[quadro], onPage=rodape)])
    doc.build(construir())
    print("PDF gerado: %s (%.0f KB)" % (SAIDA, os.path.getsize(SAIDA) / 1024))
    print("  %d Models, %d Controllers, %d Services, %d Repositories, "
          "%d procedures, %d rotas" % (
              len(DADOS["modelos"]), len(DADOS["controllers"]), len(DADOS["servicos"]),
              len(DADOS["repos"]), len(DADOS["procedures"]), DADOS["rotas"]))


if __name__ == "__main__":
    try:
        gerar()
    except ImportError:
        print("Falta o reportlab:  pip install reportlab")
        sys.exit(1)
