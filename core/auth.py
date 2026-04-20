"""
core/auth.py
──────────────────────────────────────────────────────
Gerencia autenticação, senhas e sessão do usuário.
Login simplificado por username (prefixo do e-mail).
──────────────────────────────────────────────────────
"""

import bcrypt
import streamlit as st
from database.db import executar_query, executar_comando


# ──────────────────────────────────────────────────────
# FUNÇÕES DE SENHA
# ──────────────────────────────────────────────────────

def gerar_hash_senha(senha: str) -> str:
    """
    Transforma a senha em um hash criptografado.
    A senha original NUNCA é guardada no banco.

    Args:
        senha: senha em texto puro digitada pelo usuário

    Returns:
        String com o hash criptografado
    """
    senha_bytes = senha.encode("utf-8")
    hash_bytes  = bcrypt.hashpw(senha_bytes, bcrypt.gensalt())
    return hash_bytes.decode("utf-8")


def verificar_senha(senha: str, hash_salvo: str) -> bool:
    """
    Verifica se a senha digitada corresponde ao hash salvo.

    Args:
        senha:      senha em texto puro digitada pelo usuário
        hash_salvo: hash armazenado no banco de dados

    Returns:
        True se a senha está correta
        False se a senha está errada
    """
    senha_bytes = senha.encode("utf-8")
    hash_bytes  = hash_salvo.encode("utf-8")
    return bcrypt.checkpw(senha_bytes, hash_bytes)


# ──────────────────────────────────────────────────────
# FUNÇÕES DE USERNAME
# ──────────────────────────────────────────────────────

def extrair_username(email: str) -> str:
    """
    Extrai o nome de usuário a partir do e-mail.
    Pega tudo que vem antes do '@'.

    Args:
        email: endereço de e-mail completo

    Returns:
        Nome de usuário em minúsculo

    Exemplo:
        nome.sobrenome@policiacientifica.pr.gov.br
        → nome.sobrenome
    """
    return email.strip().lower().split("@")[0].strip()


# ──────────────────────────────────────────────────────
# FUNÇÕES DE USUÁRIO
# ──────────────────────────────────────────────────────

def usuario_existe() -> bool:
    """
    Verifica se já existe algum usuário cadastrado.
    Usado para decidir se mostra tela de cadastro
    inicial ou tela de login.

    Returns:
        True se já existe usuário cadastrado
        False se o sistema ainda não foi configurado
    """
    rows = executar_query("SELECT COUNT(*) as total FROM usuarios")
    return rows[0]["total"] > 0


def criar_usuario(
    nome:       str,
    cargo:      str,
    matricula:  str,
    lotacao:    str,
    email:      str,
    senha:      str
) -> int:
    """
    Cria o usuário do sistema (perito).
    Extrai automaticamente o username do e-mail.
    Deve ser chamado apenas uma vez na configuração inicial.

    Args:
        nome:      nome completo do perito
        cargo:     cargo (ex: 'Perito Oficial Criminal')
        matricula: matrícula funcional (opcional)
        lotacao:   unidade de trabalho
        email:     e-mail institucional
        senha:     senha escolhida pelo usuário

    Returns:
        ID do usuário criado
    """
    hash_senha = gerar_hash_senha(senha)

    # Extrai username automaticamente do e-mail
    username = extrair_username(email.strip())

    return executar_comando("""
        INSERT INTO usuarios
            (nome, cargo, matricula, username,
             lotacao, email, senha_hash)
        VALUES
            (?, ?, ?, ?, ?, ?, ?)
    """, (
        nome,
        cargo,
        matricula if matricula else None,
        username,
        lotacao,
        email.strip().lower(),
        hash_senha
    ))


def buscar_usuario_por_username(username: str) -> dict | None:
    """
    Busca um usuário pelo nome de usuário (prefixo do e-mail).
    Usado no login do sistema.

    Args:
        username: nome de usuário (ex: nome.sobrenome)

    Returns:
        Dicionário com os dados do usuário ou None
    """
    rows = executar_query(
        "SELECT * FROM usuarios WHERE LOWER(username) = LOWER(?)",
        (username,)
    )
    if rows:
        return dict(rows[0])
    return None


def buscar_usuario_por_email(email: str) -> dict | None:
    """
    Busca um usuário pelo e-mail completo.
    Mantido para uso futuro (recuperação de senha, backup).

    Args:
        email: e-mail completo do perito

    Returns:
        Dicionário com os dados do usuário ou None
    """
    rows = executar_query(
        "SELECT * FROM usuarios WHERE LOWER(email) = LOWER(?)",
        (email,)
    )
    if rows:
        return dict(rows[0])
    return None


def buscar_usuario_por_id(usuario_id: int) -> dict | None:
    """
    Busca um usuário pelo ID.

    Args:
        usuario_id: ID do usuário no banco

    Returns:
        Dicionário com os dados do usuário ou None
    """
    rows = executar_query(
        "SELECT * FROM usuarios WHERE id = ?",
        (usuario_id,)
    )
    if rows:
        return dict(rows[0])
    return None


def atualizar_usuario(
    usuario_id:         int,
    nome:               str,
    cargo:              str,
    matricula:          str,
    lotacao:            str,
    email:              str,
    pasta_exportacao:   str,
    alerta_prazo:       bool,
    dias_alerta:        int
) -> None:
    """
    Atualiza os dados do perfil do usuário.
    Recalcula o username caso o e-mail seja alterado.

    Args:
        usuario_id:       ID do usuário
        nome:             novo nome
        cargo:            novo cargo
        matricula:        nova matrícula (opcional)
        lotacao:          nova lotação
        email:            novo e-mail
        pasta_exportacao: pasta padrão para salvar laudos
        alerta_prazo:     ativar/desativar alertas de prazo
        dias_alerta:      quantos dias antes do vencimento alertar
    """
    # Recalcula o username baseado no novo e-mail
    username = extrair_username(email)

    executar_comando("""
        UPDATE usuarios SET
            nome             = ?,
            cargo            = ?,
            matricula        = ?,
            username         = ?,
            lotacao          = ?,
            email            = ?,
            pasta_exportacao = ?,
            alerta_prazo     = ?,
            dias_alerta      = ?,
            atualizado_em    = datetime('now','localtime')
        WHERE id = ?
    """, (
        nome,
        cargo,
        matricula if matricula else None,
        username,
        lotacao,
        email.strip().lower(),
        pasta_exportacao,
        int(alerta_prazo),
        dias_alerta,
        usuario_id
    ))


def alterar_senha(usuario_id: int, nova_senha: str) -> None:
    """
    Altera a senha do usuário.

    Args:
        usuario_id:  ID do usuário
        nova_senha:  nova senha em texto puro
    """
    novo_hash = gerar_hash_senha(nova_senha)
    executar_comando("""
        UPDATE usuarios SET
            senha_hash    = ?,
            atualizado_em = datetime('now','localtime')
        WHERE id = ?
    """, (novo_hash, usuario_id))


# ──────────────────────────────────────────────────────
# FUNÇÕES DE SESSÃO (Streamlit)
# ──────────────────────────────────────────────────────

def fazer_login(username: str, senha: str) -> bool:
    """
    Realiza o login do usuário por username e senha.
    O username é o prefixo do e-mail institucional.
    Se correto, salva os dados na sessão do Streamlit.

    Args:
        username: nome de usuário (ex: nome.sobrenome)
        senha:    senha digitada

    Returns:
        True se login bem-sucedido
        False se usuário ou senha incorretos
    """
    usuario = buscar_usuario_por_username(username)

    if usuario and verificar_senha(senha, usuario["senha_hash"]):

        # Salva dados na sessão do Streamlit
        st.session_state["autenticado"]   = True
        st.session_state["usuario_id"]    = usuario["id"]
        st.session_state["usuario_nome"]  = usuario["nome"]
        st.session_state["usuario_cargo"] = usuario["cargo"]

        # Registra o login no histórico
        _registrar_login(usuario["id"])
        return True

    return False


def fazer_logout() -> None:
    """
    Encerra a sessão do usuário.
    Limpa todos os dados salvos na sessão do Streamlit.
    """
    import streamlit as st

    usuario_id = st.session_state.get("usuario_id")

    if usuario_id:
        _registrar_logout(usuario_id)

    # Limpa toda a sessão EXCETO dados do Streamlit
    session_keys = list(st.session_state.keys())
    for chave in session_keys:
        if chave not in ['_streamlit_version', 'theme', 'scriptrunner']:
            try:
                del st.session_state[chave]
            except:
                pass

    st.cache_data.clear()


def esta_autenticado() -> bool:
    """
    Verifica se há um usuário logado na sessão atual.

    Returns:
        True se há usuário autenticado
        False se não há sessão ativa
    """
    return st.session_state.get("autenticado", False)


def obter_usuario_logado() -> dict | None:
    """
    Retorna os dados completos do usuário logado.

    Returns:
        Dicionário com dados do usuário ou None
    """
    usuario_id = st.session_state.get("usuario_id")
    if usuario_id:
        return buscar_usuario_por_id(usuario_id)
    return None


def exigir_autenticacao() -> None:
    """
    Bloqueia o acesso à página se não houver usuário logado.
    Deve ser chamado no início de cada página protegida.
    """
    if not esta_autenticado():
        st.warning(
            "⚠️ Você precisa estar logado para "
            "acessar esta página."
        )
        st.stop()


# ──────────────────────────────────────────────────────
# VERIFICAÇÃO DE SENHA PARA OPERAÇÕES CRÍTICAS
# ──────────────────────────────────────────────────────

def confirmar_senha_critica(senha_digitada: str) -> bool:
    """
    Confirma a senha do usuário logado para operações
    críticas como exclusão ou arquivamento.

    Args:
        senha_digitada: senha digitada para confirmar

    Returns:
        True se a senha está correta
        False se a senha está errada
    """
    usuario = obter_usuario_logado()
    if usuario:
        return verificar_senha(
            senha_digitada,
            usuario["senha_hash"]
        )
    return False


# ──────────────────────────────────────────────────────
# FUNÇÕES INTERNAS DE AUDITORIA
# ──────────────────────────────────────────────────────

def _registrar_login(usuario_id: int) -> None:
    """Registra o evento de login no histórico."""
    executar_comando("""
        INSERT INTO historico
            (usuario_id, tabela, registro_id,
             operacao, descricao)
        VALUES
            (?, 'usuarios', ?, 'LOGIN',
             'Login realizado com sucesso')
    """, (usuario_id, usuario_id))


def _registrar_logout(usuario_id: int) -> None:
    """Registra o evento de logout no histórico."""
    executar_comando("""
        INSERT INTO historico
            (usuario_id, tabela, registro_id,
             operacao, descricao)
        VALUES
            (?, 'usuarios', ?, 'LOGOUT',
             'Logout realizado')
    """, (usuario_id, usuario_id))