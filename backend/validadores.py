"""Validação e normalização dos dados que têm forma — CPF, CNPJ, telefone
e e-mail.

Mora fora dos Services porque não é caso de uso: é a forma do dado, e ela
é a mesma para quem cadastra, para quem atualiza e para quem um dia for
importar uma planilha.

Duas decisões que valem para os quatro:

**O que é guardado é o dado, não a pontuação.** CPF vai ao banco como
`12345678909`, nunca `123.456.789-09`. A máscara é apresentação, e
apresentação não se persiste: gravar formatado obriga todo filtro, toda
busca e todo índice a adivinhar qual das grafias veio. A formatação para
leitura acontece na tela (`HubUI.cpf`, `HubUI.cnpj`, `HubUI.telefone`).

**Dígito verificador é regra, não enfeite.** Um CPF com 11 dígitos
aleatórios passa em qualquer validação de tamanho e falha na primeira
conferência de verdade. Aqui ele é conferido.
"""
import re

APENAS_DIGITOS = re.compile(r"\D")

# Não é a RFC 5322 inteira — essa ninguém valida com regex. É o que
# reprova o erro real de digitação (espaço, vírgula, domínio sem ponto)
# sem reprovar endereço legítimo.
FORMATO_EMAIL = re.compile(r"^[^@\s,;]+@[^@\s,;.]+(\.[^@\s,;.]+)+$")


def so_digitos(valor):
    return APENAS_DIGITOS.sub("", str(valor or ""))


def _digito(digitos, pesos):
    soma = sum(int(d) * p for d, p in zip(digitos, pesos))
    resto = soma % 11
    return "0" if resto < 2 else str(11 - resto)


def normalizar_cpf(valor, obrigatorio=True):
    """Devolve o CPF com 11 dígitos, ou levanta ValueError."""
    cpf = so_digitos(valor)
    if not cpf:
        if obrigatorio:
            raise ValueError("Informe o CPF.")
        return None
    if len(cpf) != 11:
        raise ValueError("O CPF deve ter 11 dígitos.")
    # 111.111.111-11 e companhia passam na conta dos dígitos verificadores,
    # e por isso precisam de uma recusa própria.
    if cpf == cpf[0] * 11:
        raise ValueError("CPF inválido.")
    se_dv1 = _digito(cpf[:9], range(10, 1, -1))
    se_dv2 = _digito(cpf[:10], range(11, 1, -1))
    if cpf[9:] != se_dv1 + se_dv2:
        raise ValueError("CPF inválido: os dígitos verificadores não conferem.")
    return cpf


def normalizar_cnpj(valor, obrigatorio=False):
    """Devolve o CNPJ com 14 dígitos, ou levanta ValueError. Opcional."""
    cnpj = so_digitos(valor)
    if not cnpj:
        if obrigatorio:
            raise ValueError("Informe o CNPJ.")
        return None
    if len(cnpj) != 14:
        raise ValueError("O CNPJ deve ter 14 dígitos.")
    if cnpj == cnpj[0] * 14:
        raise ValueError("CNPJ inválido.")
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6] + pesos1
    if cnpj[12:] != _digito(cnpj[:12], pesos1) + _digito(cnpj[:13], pesos2):
        raise ValueError("CNPJ inválido: os dígitos verificadores não conferem.")
    return cnpj


def normalizar_telefone(valor, obrigatorio=True):
    """Devolve o telefone com 10 ou 11 dígitos (com DDD), sem pontuação."""
    fone = so_digitos(valor)
    if not fone:
        if obrigatorio:
            raise ValueError("Informe o telefone.")
        return None
    # 55 na frente é código do país, não DDD: quem cola de uma agenda traz.
    if len(fone) in (12, 13) and fone.startswith("55"):
        fone = fone[2:]
    if len(fone) not in (10, 11):
        raise ValueError("O telefone deve ter DDD e 8 ou 9 dígitos.")
    if fone[:2] < "11":
        raise ValueError("DDD inválido.")
    if len(fone) == 11 and fone[2] != "9":
        raise ValueError("Celular com 9 dígitos deve começar com 9 após o DDD.")
    return fone


def normalizar_email(valor, obrigatorio=True):
    """Devolve o e-mail sem espaços e em minúsculas.

    A caixa é normalizada porque o domínio é insensível a ela, e porque o
    cadastro tem UNIQUE no e-mail: sem isso, `Ana@x.com` e `ana@x.com`
    viram duas contas da mesma pessoa.
    """
    email = str(valor or "").strip().lower()
    if not email:
        if obrigatorio:
            raise ValueError("Informe o e-mail.")
        return None
    if len(email) > 254 or not FORMATO_EMAIL.match(email):
        raise ValueError("E-mail inválido.")
    return email


# ---------- formatação, para quando o servidor precisa escrever ----------

def formatar_cpf(cpf):
    cpf = so_digitos(cpf)
    if len(cpf) != 11:
        return cpf
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"


def formatar_cnpj(cnpj):
    cnpj = so_digitos(cnpj)
    if len(cnpj) != 14:
        return cnpj
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"


def formatar_telefone(fone):
    fone = so_digitos(fone)
    if len(fone) == 11:
        return f"({fone[:2]}) {fone[2:7]}-{fone[7:]}"
    if len(fone) == 10:
        return f"({fone[:2]}) {fone[2:6]}-{fone[6:]}"
    return fone
