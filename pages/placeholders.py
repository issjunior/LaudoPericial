"""
pages/placeholders.py
──────────────────────────────────────────────────────
Página de referência e gerenciamento de Placeholders.
Lista todos os placeholders do sistema por categoria e
permite ao usuário criar/remover placeholders personalizados.
──────────────────────────────────────────────────────
"""

import sys
import os
import json
from pathlib import Path
import streamlit as st

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from components.menu import renderizar_menu

# ──────────────────────────────────────────────────────
# CONSTANTES E DADOS DOS PLACEHOLDERS DO SISTEMA
# ──────────────────────────────────────────────────────

PLACEHOLDERS_FILE = Path(ROOT) / "data" / "custom_placeholders.json"

# Definição centralizada de todos os placeholders do sistema, agrupados por categoria
PLACEHOLDERS_SISTEMA = [
    {
        "categoria": "📋 Dados da REP",
        "descricao": "Informações da Requisição de Exame Pericial",
        "cor": "#1971c2",
        "itens": [
            {"placeholder": "{{numero_rep}}",      "descricao": "Número da REP",                   "exemplo": "REP-2024-001"},
            {"placeholder": "{{data_solicitacao}}", "descricao": "Data da solicitação (YYYY-MM-DD)", "exemplo": "2024-12-25"},
            {"placeholder": "{{tipo_exame}}",       "descricao": "Nome do tipo de exame",           "exemplo": "Necropsia"},
            {"placeholder": "{{tipo_exame_codigo}}","descricao": "Código do tipo de exame",         "exemplo": "H-001"},
            {"placeholder": "{{nome_envolvido}}",   "descricao": "Nome do envolvido / vítima",      "exemplo": "João da Silva"},
            {"placeholder": "{{local_fato}}",       "descricao": "Descrição do local do fato",      "exemplo": "Rua das Flores, 123"},
            {"placeholder": "{{horario_acionamento}}","descricao": "Horário de acionamento (HH:MM)", "exemplo": "14:30"},
            {"placeholder": "{{horario_chegada}}",  "descricao": "Horário de chegada ao local",     "exemplo": "15:00"},
            {"placeholder": "{{horario_saida}}",    "descricao": "Horário de saída do local",       "exemplo": "17:45"},
            {"placeholder": "{{latitude}}",         "descricao": "Latitude do local",               "exemplo": "-15.7801"},
            {"placeholder": "{{longitude}}",        "descricao": "Longitude do local",              "exemplo": "-47.9292"},
        ],
    },
    {
        "categoria": "🏛️ Dados do Solicitante",
        "descricao": "Informações sobre o órgão e autoridade solicitante",
        "cor": "#2f9e44",
        "itens": [
            {"placeholder": "{{solicitante}}",      "descricao": "Nome do órgão solicitante",        "exemplo": "Delegacia de Homicídios"},
            {"placeholder": "{{solicitante_orgao}}", "descricao": "Órgão do solicitante",            "exemplo": "Polícia Civil"},
            {"placeholder": "{{nome_autoridade}}",  "descricao": "Nome da autoridade solicitante",   "exemplo": "Del. Maria Souza"},
        ],
    },
    {
        "categoria": "📝 Detalhes da Solicitação",
        "descricao": "Dados do documento que originou a requisição",
        "cor": "#e67700",
        "itens": [
            {"placeholder": "{{tipo_solicitacao}}", "descricao": "Tipo do documento (BO, Ofício...)", "exemplo": "Ofício"},
            {"placeholder": "{{numero_documento}}", "descricao": "Número do documento",            "exemplo": "12345/2024"},
            {"placeholder": "{{data_documento}}",   "descricao": "Data do documento (YYYY-MM-DD)", "exemplo": "2024-12-20"},
        ],
    },
    {
        "categoria": "👤 Dados do Perito",
        "descricao": "Informações do perito responsável (do perfil do usuário logado)",
        "cor": "#862e9c",
        "itens": [
            {"placeholder": "{{perito_nome}}",      "descricao": "Nome completo do perito",    "exemplo": "Carlos Alberto Pereira"},
            {"placeholder": "{{perito_matricula}}", "descricao": "Matrícula funcional do perito","exemplo": "123456"},
            {"placeholder": "{{perito_cargo}}",     "descricao": "Cargo do perito",            "exemplo": "Perito Criminal"},
            {"placeholder": "{{perito_lotacao}}",   "descricao": "Lotação / unidade do perito","exemplo": "IML – Brasília/DF"},
            {"placeholder": "{{cidade}}",           "descricao": "Cidade (igual à lotação)",   "exemplo": "Brasília/DF"},
        ],
    },
    {
        "categoria": "📑 Cabeçalho do Laudo",
        "descricao": "Placeholders disponíveis especificamente no cabeçalho do documento",
        "cor": "#c92a2a",
        "itens": [
            {"placeholder": "{{numero_rep}}",       "descricao": "Número da REP",              "exemplo": "REP-2024-001"},
            {"placeholder": "{{data_solicitacao}}", "descricao": "Data da solicitação",         "exemplo": "2024-12-25"},
            {"placeholder": "{{tipo_exame}}",       "descricao": "Nome do tipo de exame",      "exemplo": "Necropsia"},
            {"placeholder": "{{tipo_exame_codigo}}","descricao": "Código do tipo de exame",    "exemplo": "H-001"},
        ],
    },
]

# ──────────────────────────────────────────────────────
# FUNÇÕES DE PERSISTÊNCIA (PLACEHOLDERS PERSONALIZADOS)
# ──────────────────────────────────────────────────────

def carregar_personalizados() -> list:
    if PLACEHOLDERS_FILE.exists():
        try:
            with open(PLACEHOLDERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def salvar_personalizados(lista: list):
    PLACEHOLDERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PLACEHOLDERS_FILE, "w", encoding="utf-8") as f:
        json.dump(lista, f, ensure_ascii=False, indent=2)


# ──────────────────────────────────────────────────────
# CSS CUSTOMIZADO
# ──────────────────────────────────────────────────────

CSS = """
<style>
/* 🗂️ Cartão de categoria 🗂️ */
.ph-card {
    background: var(--background-color, #ffffff08);
    border: 1px solid rgba(255,255,255,0.08);
    border-left: 4px solid var(--cat-color, #1971c2);
    border-radius: 10px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.5rem;
}
.ph-card-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 0.5rem;
}
.ph-cat-title {
    font-size: 1rem;
    font-weight: 700;
    margin: 0;
}
.ph-cat-desc {
    font-size: 0.8rem;
    opacity: 0.65;
    margin: 0;
}

/* 📋 Linha de placeholder 📋 */
.ph-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.4rem 0.5rem;
    border-radius: 6px;
    transition: background 0.15s;
    cursor: default;
}
.ph-row:hover {
    background: rgba(255,255,255,0.05);
}
.ph-badge {
    font-family: 'Courier New', monospace;
    font-size: 0.82rem;
    font-weight: 600;
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 5px;
    padding: 2px 8px;
    white-space: nowrap;
    min-width: 220px;
    color: #74c0fc;
}
.ph-desc {
    font-size: 0.85rem;
    flex: 1;
    opacity: 0.85;
}
.ph-exemplo {
    font-size: 0.78rem;
    opacity: 0.5;
    font-style: italic;
    white-space: nowrap;
}

/* 🎨 Tag personalizado 🎨 */
.ph-custom-badge {
    font-family: 'Courier New', monospace;
    font-size: 0.82rem;
    font-weight: 600;
    background: rgba(134, 46, 156, 0.15);
    border: 1px solid rgba(134, 46, 156, 0.4);
    border-radius: 5px;
    padding: 2px 8px;
    color: #cc5de8;
}

/* 🔍 Seção de busca 🔍 */
.search-hint {
    font-size: 0.78rem;
    opacity: 0.5;
    margin-top: 0.25rem;
}
</style>
"""

# ──────────────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ──────────────────────────────────────────────────────

st.set_page_config(
    page_title="Placeholders – LaudoPericial",
    page_icon="🧩",
    layout="wide",
)

renderizar_menu()
st.markdown(CSS, unsafe_allow_html=True)

# ──────────────────────────────────────────────────────
# CABEÇALHO
# ──────────────────────────────────────────────────────

st.title("🧩 Placeholders")
st.markdown(
    "Referência de todos os **placeholders** disponíveis para uso nos Templates de Laudo. "
    "Copie o código e cole diretamente no conteúdo de uma seção – os valores serão substituídos "
    "automaticamente ao gerar o PDF."
)
st.divider()

# ──────────────────────────────────────────────────────
# ABAS PRINCIPAIS
# ──────────────────────────────────────────────────────

tab_sistema, tab_personalizados = st.tabs(["🏛️ Placeholders do Sistema", "🎨 Placeholders Personalizados"])

with tab_sistema:
    st.markdown(
        "Estes placeholders são preenchidos automaticamente pelo sistema com base nos dados da "
        "REP e do perfil do perito. Eles **não podem** ser editados."
    )
    st.markdown(" ")

    for cat in PLACEHOLDERS_SISTEMA:
        # Card de categoria
        st.markdown(
            f'<div class="ph-card" style="--cat-color: {cat["cor"]};">'
            f'<div class="ph-card-header">'
            f'<p class="ph-cat-title">{cat["categoria"]}</p>'
            f'</div>'
            f'<p class="ph-cat-desc">{cat["descricao"]}</p>'
            f'</div>',
            unsafe_allow_html=True
        )

        # Listagem dos itens
        for item in cat["itens"]:
            col_badge, col_desc, col_ex = st.columns([3, 5, 3])
            with col_badge:
                st.markdown(f'<span class="ph-badge">{item["placeholder"]}</span>', unsafe_allow_html=True)
            with col_desc:
                st.markdown(f'<span class="ph-desc">{item["descricao"]}</span>', unsafe_allow_html=True)
            with col_ex:
                st.markdown(f'<span class="ph-exemplo">ex: {item["exemplo"]}</span>', unsafe_allow_html=True)
        
        st.markdown('<div style="margin-bottom: 2rem;"></div>', unsafe_allow_html=True)

with tab_personalizados:
    personalizados = carregar_personalizados()

    # 💡 Estado de edição 💡
    if "ph_editando_idx" not in st.session_state:
        st.session_state["ph_editando_idx"] = None

    st.markdown(
        "Crie seus próprios placeholders para uso em textos recorrentes. "
        "Eles funcionam da **mesma forma** que os do sistema – basta usar `{{nome_do_placeholder}}`."
    )
    st.info(
        "⚠️ **Atenção:** placeholders personalizados ainda não são substituídos automaticamente "
        "pelo gerador de PDF. Esta seção serve como **catálogo de referência** para a equipe.",
        icon="ℹ️",
    )
    st.markdown(" ")

    # 📋 Listagem dos personalizados 📋
    if personalizados:
        st.markdown(f"**{len(personalizados)}** placeholder(s) cadastrado(s):")
        for idx, ph in enumerate(personalizados):

            # Modo edição inline
            if st.session_state["ph_editando_idx"] == idx:
                with st.form(f"form_edit_ph_{idx}"):
                    st.markdown(f"**📝 Editando** `{{{{{ph.get('nome', '')}}}}}` :")
                    col_e1, col_e2, col_e3 = st.columns([2, 3, 3])
                    with col_e1:
                        edit_nome = st.text_input(
                            "Nome *",
                            value=ph.get("nome", ""),
                            help="Digite apenas o nome interno, sem chaves.",
                        )
                    with col_e2:
                        edit_desc = st.text_input(
                            "Descrição *",
                            value=ph.get("descricao", ""),
                        )
                    with col_e3:
                        edit_ex = st.text_input(
                            "Exemplo de valor",
                            value=ph.get("exemplo", ""),
                        )
                    
                    col_salvar, col_cancelar, _ = st.columns([1, 1, 5])
                    with col_salvar:
                        salvar = st.form_submit_button("💾 Salvar", type="primary", use_container_width=True)
                    with col_cancelar:
                        cancelar = st.form_submit_button("Cancelar", use_container_width=True)

                    if cancelar:
                        st.session_state["ph_editando_idx"] = None
                        st.rerun()

                    if salvar:
                        nome_clean = edit_nome.strip().lower().replace(" ", "_")
                        if not nome_clean:
                            st.error("🚫 O nome do placeholder é obrigatório.")
                        elif not edit_desc.strip():
                            st.error("🚫 A descrição é obrigatória.")
                        # Verifica se o nome já existe em OUTRO placeholder
                        elif nome_clean != ph.get("nome") and any(p.get("nome") == nome_clean for i, p in enumerate(personalizados) if i != idx):
                            st.warning(f"⚠️ Já existe um placeholder com o nome `{nome_clean}`.")
                        else:
                            personalizados[idx] = {
                                "nome": nome_clean,
                                "descricao": edit_desc.strip(),
                                "exemplo": edit_ex.strip(),
                            }
                            salvar_personalizados(personalizados)
                            st.session_state["ph_editando_idx"] = None
                            st.success(f"✅ Placeholder `{{{{{nome_clean}}}}}` atualizado!")
                            st.rerun()

            # Modo visualização normal
            else:
                col_badge, col_desc, col_ex, col_edit, col_del = st.columns([3, 4, 3, 0.6, 0.6])
                with col_badge:
                    st.markdown(
                        f'<span class="ph-custom-badge">{{{{{ph.get("nome", "")}}}}}</span>',
                        unsafe_allow_html=True,
                    )
                with col_desc:
                    st.markdown(f"**{ph.get('descricao', '—')}**")
                with col_ex:
                    st.caption(f"ex: {ph.get('exemplo', '—')}")
                with col_edit:
                    if st.button("✏️", key=f"edit_custom_{idx}", help="Editar este placeholder"):
                        st.session_state["ph_editando_idx"] = idx
                        st.rerun()
                with col_del:
                    if st.button("🗑️", key=f"del_custom_{idx}", help="Remover este placeholder"):
                        personalizados.pop(idx)
                        salvar_personalizados(personalizados)
                        if st.session_state["ph_editando_idx"] == idx:
                            st.session_state["ph_editando_idx"] = None
                        st.rerun()

        st.divider()
    else:
        st.info("💡 Nenhum placeholder personalizado cadastrado ainda.")
        st.markdown(" ")

    # ➕ Formulário para adicionar ➕
    # Só exibe se não estiver editando nenhum item
    if st.session_state["ph_editando_idx"] is None:
        st.markdown("#### ✨ Adicionar Novo Placeholder")
        with st.form("form_add_placeholder", clear_on_submit=True):
            col_nome, col_desc, col_ex = st.columns([2, 3, 3])
            with col_nome:
                nome = st.text_input(
                    "Nome *",
                    placeholder="nome_perito_adjunto",
                    help="Digite apenas o nome interno, sem chaves. O sistema adicionará {{ }} automaticamente.",
                )
            with col_desc:
                descricao = st.text_input(
                    "Descrição *",
                    placeholder="Explicação do que se refere o placeholder",
                )
            with col_ex:
                exemplo = st.text_input(
                    "Exemplo de valor",
                    placeholder="Fulano de tal",
                )

            submitted = st.form_submit_button("➕ Adicionar", type="primary", use_container_width=False)

            if submitted:
                nome_clean = nome.strip().lower().replace(" ", "_")
                if not nome_clean:
                    st.error("🚫 O nome do placeholder é obrigatório.")
                elif not descricao.strip():
                    st.error("🚫 A descrição é obrigatória.")
                elif any(p.get("nome") == nome_clean for p in personalizados):
                    st.warning(f"⚠️ Já existe um placeholder com o nome `{nome_clean}`.")
                else:
                    personalizados.append({
                        "nome": nome_clean,
                        "descricao": descricao.strip(),
                        "exemplo": exemplo.strip(),
                    })
                    salvar_personalizados(personalizados)
                    st.success(f"✅ Placeholder `{{{{{nome_clean}}}}}` adicionado com sucesso!")
                    st.rerun()
