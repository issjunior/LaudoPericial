"""
pages/templates.py
──────────────────────────────────────────────────────
Página de gerenciamento de Templates de Laudo e suas Seções.
Permite criar, editar, ativar/desativar e excluir templates.
Permite criar, editar e excluir seções dentro de cada template.
──────────────────────────────────────────────────────
"""

import sys
import os
import streamlit as st
import base64

# Garante que a raiz do projeto está no sys.path
# Funciona localmente E no Streamlit Cloud
ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from database.db import executar_query
from components.menu import renderizar_menu
from services.cadastro_service import listar_tipos_exame
from services.template_service import (
    listar_templates,
    buscar_template,
    criar_template,
    atualizar_template,
    alternar_status_template,
    excluir_template,
    listar_secoes_template,
    buscar_secao_template,
    criar_secao_template,
    atualizar_secao_template,
    excluir_secao_template,
)
from services.gerador_pdf_playwright import gerar_pdf_template_preview

try:
    from streamlit_jodit import st_jodit
except ImportError:
    st_jodit = None

PLACEHOLDERS = """
**Placeholders disponíveis (copie e cole no texto):**

*Dados Gerais da REP:*
| Placeholder | Descrição |
|-------------|-----------|
| `{{numero_rep}}` | Número da REP |
| `{{data_solicitacao}}` | Data da solicitação (DD/MM/AAAA) |
| `{{tipo_exame}}` | Nome do tipo de exame |
| `{{nome_envolvido}}` | Nome do envolvido/vítima |
| `{{observacoes}}` | Observações adicionais da REP |

*Dados do Solicitante:*
| Placeholder | Descrição |
|-------------|-----------|
| `{{solicitante}}` | Nome do órgão solicitante |
| `{{solicitante_orgao}}` | Órgão do solicitante |
| `{{nome_autoridade}}` | Nome da autoridade solicitante |

*Detalhes da Solicitação:*
| Placeholder | Descrição |
|-------------|-----------|
| `{{tipo_solicitacao}}` | Tipo de documento (BO, Ofício, etc) |
| `{{numero_documento}}` | Número do documento |
| `{{data_documento}}` | Data do documento (DD/MM/AAAA) |

*Dados do Local (se aplicável):*
| Placeholder | Descrição |
|-------------|-----------|
| `{{local_fato}}` | Descrição do local do fato |
| `{{horario_acionamento}}` | Horário de acionamento |
| `{{horario_chegada}}` | Horário de chegada ao local |
| `{{horario_saida}}` | Horário de saída do local |
| `{{latitude}}` | Latitude do local |
| `{{longitude}}` | Longitude do local |

*Dados do Template:*
| Placeholder | Descrição |
|-------------|-----------|
| `{{template_nome}}` | Nome do template de laudo vinculado |
| `{{template_descricao}}` | Descrição do template de laudo vinculado |

*Dados do Perito:*
| Placeholder | Descrição |
|-------------|-----------|
| `{{perito_nome}}` | Nome do perito responsável |
| `{{perito_matricula}}` | Matrícula do perito |
| `{{perito_cargo}}` | Cargo do perito |
| `{{perito_lotacao}}` | Lotação do perito |
"""

# ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Templates de Laudo — LaudoPericial",
    page_icon="📄",
    layout="wide",
)

# Renderiza o menu lateral (já exige autenticação)
renderizar_menu()

# ──────────────────────────────────────────────────────
# FUNÇÕES AUXILIARES DE ESTADO
# ──────────────────────────────────────────────────────

def inicializar_estado():
    """
    Inicializa as variáveis de controle de estado da página.
    Controla qual formulário está aberto no momento.
    """
    if "temp_modo" not in st.session_state:
        # Modos possíveis: None | "criar_template" | "editar_template" | "gerenciar_secoes"
        st.session_state["temp_modo"]        = None
    if "temp_id_editando" not in st.session_state:
        # ID do template sendo editado ou com seções gerenciadas
        st.session_state["temp_id_editando"] = None
    if "secao_modo" not in st.session_state:
        # Modos possíveis: None | "criar_secao" | "editar_secao"
        st.session_state["secao_modo"]       = None
    if "secao_id_editando" not in st.session_state:
        # ID da seção sendo editada
        st.session_state["secao_id_editando"] = None


def abrir_criar_template():
    """Abre o formulário de criação de template."""
    st.session_state["temp_modo"]        = "criar_template"
    st.session_state["temp_id_editando"] = None
    st.session_state["secao_modo"]       = None
    st.session_state["secao_id_editando"] = None


def abrir_editar_template(template_id: int):
    """Abre o formulário de edição para o template informado."""
    st.session_state["temp_modo"]        = "editar_template"
    st.session_state["temp_id_editando"] = template_id
    st.session_state["secao_modo"]       = None
    st.session_state["secao_id_editando"] = None


def abrir_gerenciar_secoes(template_id: int):
    """Abre a visualização para gerenciar seções de um template."""
    st.session_state["temp_modo"]        = "gerenciar_secoes"
    st.session_state["temp_id_editando"] = template_id
    st.session_state["secao_modo"]       = None
    st.session_state["secao_id_editando"] = None


def abrir_criar_secao():
    """Abre o formulário de criação de seção."""
    st.session_state["secao_modo"]        = "criar_secao"
    st.session_state["secao_id_editando"] = None


def abrir_editar_secao(secao_id: int):
    """Abre o formulário de edição para a seção informada."""
    st.session_state["secao_modo"]        = "editar_secao"
    st.session_state["secao_id_editando"] = secao_id


def fechar_formularios():
    """Fecha todos os formulários abertos e volta para a listagem."""
    st.session_state["temp_modo"]        = None
    st.session_state["temp_id_editando"] = None
    st.session_state["secao_modo"]       = None
    st.session_state["secao_id_editando"] = None


# ──────────────────────────────────────────────────────
# FORMULÁRIOS DE TEMPLATE
# ──────────────────────────────────────────────────────

def formulario_criar_template():
    """
    Formulário para criação de novo template de laudo.
    """
    st.markdown("### ➕ Novo Template de Laudo")

    tipos_exame = listar_tipos_exame(apenas_ativos=True)
    # Mapeia para {nome: id} para o selectbox
    opcoes_tipos_exame = {te["nome"]: te["id"] for te in tipos_exame}
    nomes_tipos_exame = list(opcoes_tipos_exame.keys())

    with st.form("form_criar_template"):
        col1, col2 = st.columns([2, 1])

        with col1:
            nome = st.text_input(
                "Nome do Template *",
                placeholder="Ex: Colisão, Atropelamento, Incêndio Residencial"
            )
            # Selectbox para o tipo de exame
            tipo_exame_selecionado = st.selectbox(
                "Tipo de Exame *",
                options=["Selecione um Tipo de Exame"] + nomes_tipos_exame,
                index=0,
                help="O template será associado a este tipo de exame."
            )
            descricao_exame = st.text_area(
                "Descrição Detalhada do Template (Opcional)",
                placeholder="Descreva o propósito e escopo deste template.",
                height=100,
            )

        with col2:
            st.markdown(" ")
            st.info(
                "**Criação de Template**\n\n"
                "Defina um nome para o template e associe-o a um tipo de exame. "
                "A descrição é opcional."
            )

        st.markdown("---")
        col_salvar, col_cancelar, _ = st.columns([1, 1, 3])

        with col_salvar:
            submitted = st.form_submit_button(
                "💾 Salvar",
                use_container_width=True,
                type="primary"
            )
        with col_cancelar:
            cancelar = st.form_submit_button(
                "Cancelar",
                use_container_width=True,
            )

        if cancelar:
            fechar_formularios()
            st.rerun()

        if submitted:
            if tipo_exame_selecionado == "Selecione um Tipo de Exame":
                st.error("❌ Por favor, selecione um Tipo de Exame.")
            else:
                tipo_exame_id = opcoes_tipos_exame[tipo_exame_selecionado]
                try:
                    criar_template(
                        tipo_exame_id   = tipo_exame_id,
                        nome            = nome,
                        descricao_exame = descricao_exame,
                    )
                    st.success(f"✅ Template **{nome}** criado com sucesso!")
                    fechar_formularios()
                    st.rerun()

                except ValueError as e:
                    st.error(f"❌ {e}")
                except Exception as e:
                    st.error(f"❌ Erro inesperado: {e}")


def formulario_editar_template(template_id: int):
    """
    Formulário para edição de um template de laudo existente.

    Args:
        template_id: ID do template a editar
    """
    template = buscar_template(template_id)

    if not template:
        st.error("❌ Template de laudo não encontrado.")
        fechar_formularios()
        return

    st.markdown(f"### ✏️ Editando Template: {template['nome']}")

    tipos_exame = listar_tipos_exame(apenas_ativos=True)
    opcoes_tipos_exame = {te["nome"]: te["id"] for te in tipos_exame}
    nomes_tipos_exame = list(opcoes_tipos_exame.keys())

    # Encontra o índice do tipo de exame atual do template
    try:
        indice_tipo_exame_atual = nomes_tipos_exame.index(template["tipo_exame_nome"])
    except ValueError:
        indice_tipo_exame_atual = 0 # Caso o tipo de exame não seja encontrado (ex: inativo)

    with st.form("form_editar_template"):
        col1, col2 = st.columns([2, 1])

        with col1:
            nome = st.text_input(
                "Nome do Template *",
                value=template["nome"]
            )
            tipo_exame_selecionado = st.selectbox(
                "Tipo de Exame *",
                options=nomes_tipos_exame,
                index=indice_tipo_exame_atual,
                help="O template será associado a este tipo de exame."
            )
            descricao_exame = st.text_area(
                "Descrição Detalhada do Template (Opcional)",
                value=template["descricao_exame"] or "",
                height=100,
            )

        with col2:
            st.markdown(" ")
            st.info(
                "**Edição de Template**\n\n"
                "Altere os dados do template. "
                "A associação com o tipo de exame pode ser modificada."
            )

        st.markdown("---")
        col_salvar, col_cancelar, _ = st.columns([1, 1, 3])

        with col_salvar:
            submitted = st.form_submit_button(
                "💾 Salvar Alterações",
                use_container_width=True,
                type="primary"
            )
        with col_cancelar:
            cancelar = st.form_submit_button(
                "Cancelar",
                use_container_width=True,
            )

        if cancelar:
            fechar_formularios()
            st.rerun()

        if submitted:
            tipo_exame_id = opcoes_tipos_exame[tipo_exame_selecionado]
            try:
                atualizar_template(
                    template_id     = template_id,
                    tipo_exame_id   = tipo_exame_id,
                    nome            = nome,
                    descricao_exame = descricao_exame,
                )
                st.success(
                    f"✅ Template **{nome}** "
                    f"atualizado com sucesso!"
                )
                fechar_formularios()
                st.rerun()

            except ValueError as e:
                st.error(f"❌ {e}")
            except Exception as e:
                st.error(f"❌ Erro inesperado: {e}")


# ──────────────────────────────────────────────────────
# TABELA DE TEMPLATES
# ──────────────────────────────────────────────────────

def exibir_lista_templates(templates: list):
    """
    Exibe os templates de laudo usando Expanders nativos do Streamlit.
    """
    if not templates:
        st.info("📭 Nenhum template de laudo cadastrado ainda.")
        return

    for template in templates:
        status_icon = "🟢" if template["ativo"] else "🔴"
        label = f"{status_icon} [{template['tipo_exame_codigo']}] {template['nome']} — {template['tipo_exame_nome']}"
        
        with st.expander(label):
            st.markdown(f"**Descrição:** {template['descricao_exame'] or 'Sem descrição.'}")
            
            st.markdown("---")
            c1, c2, c3, c4, _ = st.columns([1.5, 1.2, 1.5, 1.2, 3])
            
            with c1:
                if st.button("⚙️ Gerenciar Seções", key=f"sec_{template['id']}", use_container_width=True):
                    abrir_gerenciar_secoes(template["id"])
                    st.rerun()
            with c2:
                if st.button("✏️ Editar", key=f"edit_{template['id']}", use_container_width=True):
                    abrir_editar_template(template["id"])
                    st.rerun()
            with c3:
                txt_status = "Desativar" if template["ativo"] else "Ativar"
                if st.button(f"🔄 {txt_status}", key=f"stat_{template['id']}", use_container_width=True):
                    try:
                        alternar_status_template(template["id"])
                        st.rerun()
                    except Exception as e: st.error(f"Erro: {e}")
            with c4:
                if st.button("🗑️ Excluir", key=f"del_{template['id']}", use_container_width=True):
                    try:
                        excluir_template(template["id"])
                        st.rerun()
                    except Exception as e: st.error(f"Erro: {e}")
        
@st.dialog("Visualizar Todo o Laudo (Prévia PDF)", width="large")
def modal_visualizar_template(template_id: int):
    """
    Gera um PDF do template (sem substituir placeholders) e exibe no modal.
    """
    try:
        with st.spinner("Gerando PDF..."):
            pdf_bytes = gerar_pdf_template_preview(template_id)
            
            # Codifica o PDF em base64 para exibir no iframe
            base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
            
            # Incorpora o PDF em um iframe
            # Nota: Alguns navegadores podem bloquear o preview de data-uris, 
            # mas é o método mais direto sem salvar arquivo temporário.
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="700" type="application/pdf"></iframe>'
            
            st.markdown(pdf_display, unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"❌ Erro ao gerar pré-visualização em PDF: {e}")
        st.info("Certifique-se de que o Playwright está instalado corretamente (`playwright install chromium`).")
            
    st.markdown(" ")
    if st.button("Fechar", use_container_width=True):
        st.rerun()


# ──────────────────────────────────────────────────────
# GERENCIAMENTO DE SEÇÕES
# ──────────────────────────────────────────────────────


def gerenciar_secoes(template_id: int):
    """
    Interface para gerenciar as seções de um template específico.
    """
    template = buscar_template(template_id)
    if not template:
        st.error("❌ Template de laudo não encontrado.")
        fechar_formularios()
        st.rerun()
        return

    col_tit, col_nav = st.columns([7, 3])
    with col_tit:
        st.subheader(f"⚙️ Gerenciar Seções: {template['nome']}")
        st.caption(f"Tipo de Exame: {template['tipo_exame_nome']}")
    with col_nav:
        if st.button("↩️ Voltar para Templates", use_container_width=True):
            fechar_formularios()
            st.rerun()

    st.markdown("---")

    # Botões de ação
    if st.session_state["secao_modo"] is None:
        col_btn1, col_btn2, _ = st.columns([3, 3, 4])
        with col_btn1:
            if st.button("➕ Adicionar Nova Seção", use_container_width=True, type="primary"):
                abrir_criar_secao()
                st.rerun()
        with col_btn2:
            if st.button("👁️ Visualizar Todo o Laudo", use_container_width=True):
                modal_visualizar_template(template_id)


    # Formulários de seção (criar/editar)
    if st.session_state["secao_modo"] == "criar_secao":
        formulario_criar_secao(template_id)
    elif st.session_state["secao_modo"] == "editar_secao":
        formulario_editar_secao(st.session_state["secao_id_editando"])

    st.markdown("---")

    # Listagem de seções com visual melhorado
    secoes = listar_secoes_template(template_id)
    st.markdown("#### Estrutura do Laudo")
    
    if not secoes:
        st.info("📭 Nenhuma seção cadastrada. Comece adicionando uma acima.")
    else:
        for idx, secao in enumerate(secoes, 1):
            with st.container():
                c_idx, c_info, c_acoes = st.columns([0.6, 7, 2.4], vertical_alignment="center")
                with c_idx:
                    st.markdown(f"<div style='font-size: 1.5rem; font-weight: bold; color: #dee2e6; line-height: 1;'>{idx:02d}</div>", unsafe_allow_html=True)
                with c_info:
                    obrigatoria_badge = f" <span style='color: #f03e3e; font-size: 0.8rem; font-weight: bold; margin-left: 10px;'>[OBRIGATÓRIA]</span>" if secao['obrigatoria'] else ""
                    st.markdown(f"<div style='font-size: 1.1rem; font-weight: 600; line-height: 1; margin-top: -2px;'>{secao['titulo'].upper()}{obrigatoria_badge}</div>", unsafe_allow_html=True)

                with c_acoes:
                    ca1, ca2 = st.columns(2)
                    with ca1:
                        if st.button("✏️", key=f"ed_sec_{secao['id']}", use_container_width=True):
                            abrir_editar_secao(secao["id"])
                            st.rerun()
                    with ca2:
                        if st.button("🗑️", key=f"del_sec_{secao['id']}", use_container_width=True):
                            try:
                                excluir_secao_template(secao["id"])
                                st.rerun()
                            except Exception as e: st.error(f"Erro: {e}")
                st.markdown("<hr style='margin: 10px 0; border: 0; border-top: 1px solid #f8f9fa;'>", unsafe_allow_html=True)


def formulario_criar_secao(template_id: int):
    """
    Formulário para criação de nova seção para um template.
    """
    with st.expander("Ver Placeholders Disponíveis", expanded=False):
        st.markdown(PLACEHOLDERS)

    st.markdown("#### ➕ Nova Seção")
    with st.form("form_criar_secao"):
        titulo = st.text_input(
            "Título da Seção *",
            placeholder="Ex: Preâmbulo, Histórico, Objetivo Pericial"
        )

        if st_jodit:
            config = {
                'minHeight': 300,
                'height': 500,
                'theme': 'default', # Volta para o tema claro
                'allowResizeY': True,
                'style': {
                    'color': '#000000',      # Texto preto
                    'background': '#ffffff'  # Fundo branco
                }
            }
            conteudo_base = st_jodit(
                value="",
                key="criar_secao_conteudo",
                config=config
            )
        else:
            conteudo_base = st.text_area(
                "Conteúdo Padrão (Opcional)",
                placeholder="Texto que aparecerá por padrão nesta seção do laudo.",
                height=300
            )
        
        col_opcoes, col_ordem = st.columns([2, 1])
        with col_opcoes:
            obrigatoria = st.checkbox("Seção Obrigatória", help="Marque se esta seção deve sempre aparecer no laudo.")
        with col_ordem:
            ordem = st.number_input(
                "Ordem de Exibição",
                min_value=1,
                value=1,
                step=1,
                help="Define a ordem em que as seções aparecerão no laudo."
            )

        st.markdown("---")
        col_salvar, col_cancelar, _ = st.columns([1, 1, 3])
        with col_salvar:
            submitted = st.form_submit_button(
                "💾 Salvar Seção",
                use_container_width=True,
                type="primary"
            )
        with col_cancelar:
            cancelar = st.form_submit_button(
                "Cancelar",
                use_container_width=True,
            )

        if cancelar:
            st.session_state["secao_modo"] = None # Fecha o formulário de seção
            st.rerun()

        if submitted:
            try:
                criar_secao_template(
                    template_id   = template_id,
                    titulo        = titulo,
                    conteudo_base = conteudo_base,
                    ordem         = ordem,
                    obrigatoria   = obrigatoria,
                )
                st.success(f"✅ Seção **{titulo}** criada com sucesso!")
                st.session_state["secao_modo"] = None # Fecha o formulário de seção
                st.rerun()
            except ValueError as e:
                st.error(f"❌ {e}")
            except Exception as e:
                st.error(f"❌ Erro inesperado: {e}")


def formulario_editar_secao(secao_id: int):
    """
    Formulário para edição de uma seção de template existente.
    """
    secao = buscar_secao_template(secao_id)
    if not secao:
        st.error("❌ Seção não encontrada.")
        st.session_state["secao_modo"] = None
        st.rerun()
        return

    with st.expander("Ver Placeholders Disponíveis", expanded=False):
        st.markdown(PLACEHOLDERS)

    st.markdown(f"#### ✏️ Editando Seção: {secao['titulo']}")
    with st.form("form_editar_secao"):
        titulo = st.text_input(
            "Título da Seção *",
            value=secao["titulo"]
        )
        
        if st_jodit:
            config = {
                'minHeight': 300,
                'height': 500,
                'theme': 'default', # Volta para o tema claro
                'allowResizeY': True,
                'style': {
                    'color': '#000000',      # Texto preto
                    'background': '#ffffff'  # Fundo branco
                }
            }
            conteudo_base = st_jodit(
                value=secao["conteudo_base"] or "",
                key=f"editar_secao_conteudo_{secao_id}",
                config=config
            )
        else:
            conteudo_base = st.text_area(
                "Conteúdo Padrão (Opcional)",
                value=secao["conteudo_base"] or "",
                height=300
            )
        
        col_opcoes, col_ordem = st.columns([2, 1])
        with col_opcoes:
            obrigatoria = st.checkbox(
                "Seção Obrigatória",
                value=bool(secao["obrigatoria"]),
                help="Marque se esta seção deve sempre aparecer no laudo."
            )
        with col_ordem:
            ordem = st.number_input(
                "Ordem de Exibição",
                min_value=1,
                value=secao["ordem"],
                step=1,
                help="Define a ordem em que as seções aparecerão no laudo."
            )

        st.markdown("---")
        col_salvar, col_cancelar, _ = st.columns([1, 1, 3])
        with col_salvar:
            submitted = st.form_submit_button(
                "💾 Salvar Alterações",
                use_container_width=True,
                type="primary"
            )
        with col_cancelar:
            cancelar = st.form_submit_button(
                "Cancelar",
                use_container_width=True,
            )

        if cancelar:
            st.session_state["secao_modo"] = None # Fecha o formulário de seção
            st.rerun()

        if submitted:
            try:
                atualizar_secao_template(
                    secao_id      = secao_id,
                    titulo        = titulo,
                    conteudo_base = conteudo_base,
                    ordem         = ordem,
                    obrigatoria   = obrigatoria,
                )
                st.success(f"✅ Seção **{titulo}** atualizada com sucesso!")
                st.session_state["secao_modo"] = None # Fecha o formulário de seção
                st.rerun()
            except ValueError as e:
                st.error(f"❌ {e}")
            except Exception as e:
                st.error(f"❌ Erro inesperado: {e}")


# ──────────────────────────────────────────────────────
# PÁGINA PRINCIPAL
# ──────────────────────────────────────────────────────

def main():
    """
    Ponto de entrada da página Templates de Laudo.
    """
    inicializar_estado()

    st.title("📄 Templates de Laudo")
    st.markdown("Gerencie os modelos de laudo e suas seções por tipo de exame.")
    st.divider()

    temp_modo = st.session_state["temp_modo"]
    temp_id_editando = st.session_state["temp_id_editando"]

    # Se estiver gerenciando seções, exibe a interface de seções
    if temp_modo == "gerenciar_secoes":
        gerenciar_secoes(temp_id_editando)
        return

    # ── Formulários de Template ──────────────────────────
    if temp_modo == "criar_template":
        formulario_criar_template()
        st.divider()
    elif temp_modo == "editar_template":
        formulario_editar_template(temp_id_editando)
        st.divider()

    # ── Barra de Ações e Filtros ─────────────────────────
    col_btn, col_search, col_toggle = st.columns([2.5, 4, 3.5])
    
    with col_btn:
        if temp_modo is None:
            if st.button("➕ Novo Template", use_container_width=True, type="primary"):
                abrir_criar_template()
                st.rerun()
    
    with col_search:
        filtro_codigo_exame = st.text_input(
            "Filtrar por Código",
            placeholder="Ex: H-001",
            label_visibility="collapsed"
        )
    
    with col_toggle:
        mostrar_inativos = st.toggle("Mostrar inativos", value=False)

    # ── Listagem de Templates ───────────────────────────
    templates = listar_templates(
        apenas_ativos=not mostrar_inativos,
        codigo_tipo_exame=filtro_codigo_exame
    )
    
    st.info(f"**{len(templates)}** template(s) encontrado(s)")
    st.markdown(" ")

    exibir_lista_templates(templates)


main()
