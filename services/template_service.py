"""
services/template_service.py
──────────────────────────────────────────────────────
Serviço responsável pelo gerenciamento de Templates de Laudo
e suas Seções.
──────────────────────────────────────────────────────
"""

import sys
import os

ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from database.db import executar_query, executar_comando
from services.cadastro_service import buscar_tipo_exame # Para validar tipo_exame_id


# ══════════════════════════════════════════════════════
# TEMPLATES DE LAUDO
# ══════════════════════════════════════════════════════

def listar_templates(apenas_ativos: bool = True, tipo_exame_id: int = None) -> list:
    """
    Retorna todos os templates de laudo cadastrados.

    Args:
        apenas_ativos: Se True, retorna só os ativos.
        tipo_exame_id: Se fornecido, filtra por tipo de exame.

    Returns:
        Lista de dicionários com os templates de laudo.
    """
    sql = """
        SELECT
            t.id,
            t.tipo_exame_id,
            te.nome AS tipo_exame_nome,
            t.nome,
            t.descricao_exame,
            t.ativo
        FROM templates t
        JOIN tipos_exame te ON t.tipo_exame_id = te.id
    """
    params = []
    conditions = []

    if apenas_ativos:
        conditions.append("t.ativo = 1")

    if tipo_exame_id is not None:
        conditions.append("t.tipo_exame_id = ?")
        params.append(tipo_exame_id)

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    sql += " ORDER BY te.nome, t.nome"

    rows = executar_query(sql, tuple(params))
    return [dict(row) for row in rows]


def buscar_template(template_id: int) -> dict | None:
    """
    Busca um template de laudo pelo ID.

    Args:
        template_id: ID do template de laudo

    Returns:
        Dicionário com os dados ou None se não encontrado
    """
    sql = """
        SELECT
            t.id,
            t.tipo_exame_id,
            te.nome AS tipo_exame_nome,
            t.nome,
            t.descricao_exame,
            t.ativo
        FROM templates t
        JOIN tipos_exame te ON t.tipo_exame_id = te.id
        WHERE t.id = ?
    """
    rows = executar_query(sql, (template_id,))

    if rows:
        return dict(rows[0])
    return None


def criar_template(
    tipo_exame_id:   int,
    nome:            str,
    descricao_exame: str = "",
) -> int:
    """
    Cria um novo template de laudo.

    Args:
        tipo_exame_id: ID do tipo de exame ao qual o template pertence
        nome:          Nome do template (ex: "Colisão", "Atropelamento")
        descricao_exame: Descrição detalhada do template

    Returns:
        ID do novo template criado

    Raises:
        ValueError: Se o tipo de exame não existir, nome vazio ou já existir
    """
    nome = nome.strip()

    if not nome:
        raise ValueError("O nome do template é obrigatório.")

    # Verifica se o tipo de exame existe
    tipo_exame = buscar_tipo_exame(tipo_exame_id)
    if not tipo_exame:
        raise ValueError("Tipo de exame não encontrado.")

    # Verifica duplicidade do nome para o mesmo tipo de exame
    existe = executar_query(
        "SELECT id FROM templates WHERE LOWER(nome) = LOWER(?) AND tipo_exame_id = ?",
        (nome, tipo_exame_id)
    )
    if existe:
        raise ValueError(
            f"Já existe um template com o nome '{nome}' "
            f"para o tipo de exame '{tipo_exame['nome']}'."
        )

    sql = """
        INSERT INTO templates (tipo_exame_id, nome, descricao_exame, ativo)
        VALUES (?, ?, ?, 1)
    """
    return executar_comando(sql, (tipo_exame_id, nome, descricao_exame.strip()))


def atualizar_template(
    template_id:     int,
    tipo_exame_id:   int,
    nome:            str,
    descricao_exame: str = "",
) -> None:
    """
    Atualiza os dados de um template de laudo existente.

    Args:
        template_id:     ID do template a atualizar
        tipo_exame_id:   Novo ID do tipo de exame
        nome:            Novo nome do template
        descricao_exame: Nova descrição detalhada

    Raises:
        ValueError: Se o template não existir, tipo de exame não existir,
                    nome vazio ou já em uso
    """
    nome = nome.strip()

    if not nome:
        raise ValueError("O nome do template é obrigatório.")

    # Verifica se o template existe
    template = buscar_template(template_id)
    if not template:
        raise ValueError("Template de laudo não encontrado.")

    # Verifica se o tipo de exame existe
    tipo_exame = buscar_tipo_exame(tipo_exame_id)
    if not tipo_exame:
        raise ValueError("Tipo de exame não encontrado.")

    # Verifica duplicidade do nome (ignora o próprio registro)
    existe = executar_query(
        """
        SELECT id FROM templates
        WHERE LOWER(nome) = LOWER(?) AND tipo_exame_id = ? AND id != ?
        """,
        (nome, tipo_exame_id, template_id)
    )
    if existe:
        raise ValueError(
            f"Já existe um template com o nome '{nome}' "
            f"para o tipo de exame '{tipo_exame['nome']}'."
        )

    sql = """
        UPDATE templates
        SET tipo_exame_id = ?, nome = ?, descricao_exame = ?
        WHERE id = ?
    """
    executar_comando(sql, (tipo_exame_id, nome, descricao_exame.strip(), template_id))


def alternar_status_template(template_id: int) -> bool:
    """
    Ativa ou desativa um template de laudo.

    Args:
        template_id: ID do template de laudo

    Returns:
        True se ficou ativo, False se ficou inativo

    Raises:
        ValueError: Se o template não existir
    """
    template = buscar_template(template_id)
    if not template:
        raise ValueError("Template de laudo não encontrado.")

    novo_status = 0 if template["ativo"] else 1

    executar_comando(
        "UPDATE templates SET ativo = ? WHERE id = ?",
        (novo_status, template_id)
    )

    return bool(novo_status)


def excluir_template(template_id: int) -> None:
    """
    Exclui um template de laudo pelo ID.

    Só permite excluir se não houver laudos vinculados.

    Args:
        template_id: ID do template de laudo

    Raises:
        ValueError: Se não existir ou tiver laudos vinculados
    """
    template = buscar_template(template_id)
    if not template:
        raise ValueError("Template de laudo não encontrado.")

    # Verifica se há laudos vinculados
    em_uso = executar_query(
        "SELECT id FROM laudos WHERE template_id = ? LIMIT 1",
        (template_id,)
    )
    if em_uso:
        raise ValueError(
            f"Não é possível excluir o template '{template['nome']}' "
            f"pois existem laudos vinculados a ele. Desative-o ao invés de excluir."
        )

    executar_comando(
        "DELETE FROM templates WHERE id = ?",
        (template_id,)
    )


# ══════════════════════════════════════════════════════
# SEÇÕES DE TEMPLATE
# ══════════════════════════════════════════════════════

def listar_secoes_template(template_id: int) -> list:
    """
    Lista as seções de um template específico, ordenadas.

    Args:
        template_id: ID do template

    Returns:
        Lista de dicionários com as seções.
    """
    sql = """
        SELECT id, template_id, titulo, conteudo_base, ordem, obrigatoria, permite_fotos
        FROM secoes_template
        WHERE template_id = ?
        ORDER BY ordem
    """
    rows = executar_query(sql, (template_id,))
    return [dict(row) for row in rows]


def buscar_secao_template(secao_id: int) -> dict | None:
    """
    Busca uma seção de template pelo ID.

    Args:
        secao_id: ID da seção

    Returns:
        Dicionário com os dados ou None se não encontrada
    """
    sql = """
        SELECT id, template_id, titulo, conteudo_base, ordem, obrigatoria, permite_fotos
        FROM secoes_template
        WHERE id = ?
    """
    rows = executar_query(sql, (secao_id,))
    if rows:
        return dict(rows[0])
    return None


def criar_secao_template(
    template_id:   int,
    titulo:        str,
    conteudo_base: str = "",
    ordem:         int = 0,
    obrigatoria:   bool = False,
    permite_fotos: bool = False,
) -> int:
    """
    Cria uma nova seção para um template.

    Args:
        template_id:   ID do template pai
        titulo:        Título da seção
        conteudo_base: Conteúdo padrão da seção
        ordem:         Ordem de exibição
        obrigatoria:   Se a seção é obrigatória
        permite_fotos: Se a seção permite anexar fotos

    Returns:
        ID da nova seção criada

    Raises:
        ValueError: Se o template não existir, título vazio ou já existir
    """
    titulo = titulo.strip()

    if not titulo:
        raise ValueError("O título da seção é obrigatório.")

    # Verifica se o template existe
    template = buscar_template(template_id)
    if not template:
        raise ValueError("Template de laudo não encontrado.")

    # Verifica duplicidade do título para o mesmo template
    existe = executar_query(
        "SELECT id FROM secoes_template WHERE LOWER(titulo) = LOWER(?) AND template_id = ?",
        (titulo, template_id)
    )
    if existe:
        raise ValueError(
            f"Já existe uma seção com o título '{titulo}' "
            f"para o template '{template['nome']}'."
        )

    sql = """
        INSERT INTO secoes_template (template_id, titulo, conteudo_base, ordem, obrigatoria, permite_fotos)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    return executar_comando(
        sql,
        (template_id, titulo, conteudo_base, ordem, int(obrigatoria), int(permite_fotos))
    )


def atualizar_secao_template(
    secao_id:      int,
    titulo:        str,
    conteudo_base: str = "",
    ordem:         int = 0,
    obrigatoria:   bool = False,
    permite_fotos: bool = False,
) -> None:
    """
    Atualiza os dados de uma seção de template existente.

    Args:
        secao_id:      ID da seção a atualizar
        titulo:        Novo título
        conteudo_base: Novo conteúdo padrão
        ordem:         Nova ordem de exibição
        obrigatoria:   Novo status de obrigatoriedade
        permite_fotos: Novo status de permissão de fotos

    Raises:
        ValueError: Se a seção não existir, título vazio ou já em uso
    """
    titulo = titulo.strip()

    if not titulo:
        raise ValueError("O título da seção é obrigatório.")

    # Verifica se a seção existe
    secao = buscar_secao_template(secao_id)
    if not secao:
        raise ValueError("Seção de template não encontrada.")

    # Verifica duplicidade do título (ignora o próprio registro)
    existe = executar_query(
        """
        SELECT id FROM secoes_template
        WHERE LOWER(titulo) = LOWER(?) AND template_id = ? AND id != ?
        """,
        (titulo, secao["template_id"], secao_id)
    )
    if existe:
        raise ValueError(
            f"Já existe uma seção com o título '{titulo}' "
            f"para este template."
        )

    sql = """
        UPDATE secoes_template
        SET titulo = ?, conteudo_base = ?, ordem = ?, obrigatoria = ?, permite_fotos = ?
        WHERE id = ?
    """
    executar_comando(
        sql,
        (titulo, conteudo_base, ordem, int(obrigatoria), int(permite_fotos), secao_id)
    )


def excluir_secao_template(secao_id: int) -> None:
    """
    Exclui uma seção de template pelo ID.

    Args:
        secao_id: ID da seção a excluir

    Raises:
        ValueError: Se a seção não existir
    """
    secao = buscar_secao_template(secao_id)
    if not secao:
        raise ValueError("Seção de template não encontrada.")

    # TODO: Adicionar verificação se a seção está em uso em algum laudo ativo
    # Por enquanto, a restrição ON DELETE CASCADE no models.py já cuida disso
    # se o template pai for excluído.

    executar_comando(
        "DELETE FROM secoes_template WHERE id = ?",
        (secao_id,)
    )