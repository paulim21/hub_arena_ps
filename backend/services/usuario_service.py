"""Services — Usuário (uma classe por caso de uso)."""
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

import validadores

from extensions import db
from models.usuario import Usuario
from repositories.usuario_repository import UsuarioRepository

TIPOS_VALIDOS = ("atleta", "dono", "professor")
TAMANHO_MINIMO_SENHA = 6


class CriarUsuarioService:
    @staticmethod
    def executar(dados):
        obrigatorios = ("nome", "email", "cpf", "senha", "telefone", "tipo_usuario")
        faltando = [c for c in obrigatorios if not dados.get(c)]
        if faltando:
            raise ValueError(f"Campos obrigatórios ausentes: {', '.join(faltando)}")

        # A forma do dado é conferida antes de qualquer coisa tocar o banco:
        # CPF com dígito verificador errado é erro de digitação, não de regra
        # de negócio, e o titular precisa saber disso na hora.
        email = validadores.normalizar_email(dados["email"])
        cpf = validadores.normalizar_cpf(dados["cpf"])
        telefone = validadores.normalizar_telefone(dados["telefone"])
        if dados["tipo_usuario"] not in TIPOS_VALIDOS:
            raise ValueError(f"tipo_usuario deve ser um de: {', '.join(TIPOS_VALIDOS)}")
        if len(dados["senha"]) < TAMANHO_MINIMO_SENHA:
            raise ValueError(
                f"A senha deve ter ao menos {TAMANHO_MINIMO_SENHA} caracteres."
            )
        try:
            # A senha NUNCA é gravada como foi digitada. O que vai para o
            # banco é um resumo criptográfico com sal: quem ler a tabela não
            # descobre a senha, e nem nós conseguimos. É o que a LGPD chama
            # de medida de segurança (Art. 46) e o que a política promete.
            return Usuario(
                nome=dados["nome"].strip(), email=email, cpf=cpf,
                senha=generate_password_hash(dados["senha"]),
                telefone=telefone, tipo_usuario=dados["tipo_usuario"],
            ).salvar()
        except IntegrityError:
            db.session.rollback()
            # São dois UNIQUE na tabela, e dizer "já existe" sem dizer qual
            # faz a pessoa conferir o campo errado.
            if Usuario.query.filter_by(email=email).first():
                raise ValueError("Já existe um usuário com este e-mail.")
            raise ValueError("Já existe um usuário com este CPF.")


class ListarUsuariosService:
    @staticmethod
    def executar(tipo=None):
        if tipo:
            # Consulta com filtro → camada Repository (procedure sp_usuarios_por_tipo)
            return UsuarioRepository.listar_por_tipo(tipo)
        return [u.to_dict() for u in Usuario.listar_todos()]


class PesquisarUsuariosService:
    @staticmethod
    def executar(termo):
        if not termo:
            raise ValueError("Informe o termo de busca (?q=).")
        # Busca textual → procedure sp_busca_usuarios (LIKE)
        return UsuarioRepository.buscar_por_termo(termo)


class BuscarUsuarioService:
    @staticmethod
    def executar(usuario_id):
        usuario = Usuario.buscar_por_id(usuario_id)
        if usuario is None:
            raise LookupError("Usuário não encontrado.")
        return usuario


class AtualizarUsuarioService:
    @staticmethod
    def executar(usuario_id, dados):
        usuario = BuscarUsuarioService.executar(usuario_id)
        usuario.nome = dados.get("nome", usuario.nome)
        if "email" in dados:
            usuario.email = validadores.normalizar_email(dados["email"])
        if "cpf" in dados:
            usuario.cpf = validadores.normalizar_cpf(dados["cpf"])
        if "telefone" in dados:
            usuario.telefone = validadores.normalizar_telefone(dados["telefone"])
        usuario.tipo_usuario = dados.get("tipo_usuario", usuario.tipo_usuario)
        if usuario.tipo_usuario not in TIPOS_VALIDOS:
            db.session.rollback()
            raise ValueError(f"tipo_usuario deve ser um de: {', '.join(TIPOS_VALIDOS)}")
        try:
            return usuario.atualizar()
        except IntegrityError:
            db.session.rollback()
            raise ValueError("Já existe outro usuário com este e-mail ou CPF.")


class DeletarUsuarioService:
    @staticmethod
    def executar(usuario_id):
        usuario = BuscarUsuarioService.executar(usuario_id)
        try:
            usuario.deletar()
        except IntegrityError:
            db.session.rollback()
            raise ValueError(
                "Este usuário tem arenas ou reservas vinculadas. Exclua-as primeiro."
            )


class ConferirSenhaService:
    """Caso de uso: a senha informada confere com a guardada?

    Existe para que o resumo criptográfico seja verificável sem nunca ser
    revertido — é assim que se confere senha sem saber qual ela é.
    """
    @staticmethod
    def executar(usuario_id, senha):
        usuario = BuscarUsuarioService.executar(usuario_id)
        if not senha:
            raise ValueError("Informe a senha.")
        return check_password_hash(usuario.senha, senha)
