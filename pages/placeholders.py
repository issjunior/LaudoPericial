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
import streamlit as st

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from components.menu import renderizar_menu
from services.placeholders_custom_service import (
    listar_placeholders_custom,
    salvar_placeholders_custom,
)

# ──────────────────────────────────────────────────────
# CONSTANTES E DADOS DOS PLACEHOLDERS DO SISTEMA
# ──────────────────────────────────────────────────────

# Definição centralizada de todos os placeholders do sistema, agrupados por categoria
PLACEHOLDERS_SISTEMA = [
    {
        "categoria": "📋 Dados REP/Laudo",
        "descricao": "Informações da REP e do cabeçalho do laudo",
        "cor": "#1971c2",
        "itens": [
            {"placeholder": "{{numero_rep}}",      "descricao": "Número da REP",                   "exemplo": "REP-2024-001"},
            {"placeholder": "{{data_solicitacao}}", "descricao": "Data da solicitação (DD/MM/AAAA)", "exemplo": "25/12/2024"},
            {"placeholder": "{{tipo_exame}}",       "descricao": "Nome do tipo de exame",           "exemplo": "Necropsia"},
            {"placeholder": "{{tipo_exame_codigo}}","descricao": "Código do tipo de exame",         "exemplo": "H-001"},
            {"placeholder": "{{nome_envolvido}}",   "descricao": "Nome do envolvido / vítima",      "exemplo": "João da Silva"},
            {"placeholder": "{{observacoes}}",      "descricao": "Observações adicionais da REP",    "exemplo": "Sem alterações relevantes no local."},
            {"placeholder": "{{local_fato}}",       "descricao": "Descrição do local do fato",      "exemplo": "Rua das Flores, 123"},
            {"placeholder": "{{horario_acionamento}}","descricao": "Horário de acionamento (HH:MM)", "exemplo": "14:30"},
            {"placeholder": "{{horario_chegada}}",  "descricao": "Horário de chegada ao local",     "exemplo": "15:00"},
            {"placeholder": "{{horario_saida}}",    "descricao": "Horário de saída do local",       "exemplo": "17:45"},
            {"placeholder": "{{latitude}}",         "descricao": "Latitude do local",               "exemplo": "-15.7801"},
            {"placeholder": "{{longitude}}",        "descricao": "Longitude do local",              "exemplo": "-47.9292"},
        ],
    },
    {
        "categoria": "📄 Dados do Template",
        "descricao": "Informações do template de laudo vinculado",
        "cor": "#5f3dc4",
        "itens": [
            {"placeholder": "{{template_nome}}",      "descricao": "Nome do template de laudo",         "exemplo": "Local de Morte"},
            {"placeholder": "{{template_descricao}}", "descricao": "Descrição do template de laudo",    "exemplo": "Exame em local de morte violenta"},
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
            {"placeholder": "{{tipo_solicitacao}}", "descricao": "Tipo do documento (BO, Oficio...)", "exemplo": "Oficio"},
            {"placeholder": "{{numero_documento}}", "descricao": "Número do documento",            "exemplo": "12345/2024"},
            {"placeholder": "{{data_documento}}",   "descricao": "Data do documento (DD/MM/AAAA)", "exemplo": "20/12/2024"},
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
]

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

st.markdown(
    "Estes placeholders são preenchidos automaticamente pelo sistema com base nos dados da "
    "REP e do perfil do perito. Eles **não podem** ser editados."
)
st.markdown(" ")
abas_categoria = st.tabs([cat["categoria"] for cat in PLACEHOLDERS_SISTEMA] + ["🎨 Placeholders Personalizados"])

for aba, cat in zip(abas_categoria, PLACEHOLDERS_SISTEMA):
    with aba:
        st.markdown(
            f'<div class="ph-card" style="--cat-color: {cat["cor"]};">'
            f'<div class="ph-card-header">'
            f'<p class="ph-cat-title">{cat["categoria"]}</p>'
            f'</div>'
            f'<p class="ph-cat-desc">{cat["descricao"]}</p>'
            f'</div>',
            unsafe_allow_html=True
        )

        for item in cat["itens"]:
            col_badge, col_desc, col_ex = st.columns([3, 5, 3])
            with col_badge:
                st.markdown(f'<span class="ph-badge">{item["placeholder"]}</span>', unsafe_allow_html=True)
            with col_desc:
                st.markdown(f'<span class="ph-desc">{item["descricao"]}</span>', unsafe_allow_html=True)
            with col_ex:
                st.markdown(f'<span class="ph-exemplo">ex: {item["exemplo"]}</span>', unsafe_allow_html=True)

with abas_categoria[-1]:
    personalizados = listar_placeholders_custom()
    placeholders_sistema_nomes = {
        item["placeholder"].replace("{{", "").replace("}}", "")
        for cat in PLACEHOLDERS_SISTEMA
        for item in cat["itens"]
    }

    if "ph_editando_idx" not in st.session_state:
        st.session_state["ph_editando_idx"] = None

    st.markdown(
        "Crie seus próprios placeholders para uso em textos recorrentes. "
        "Eles funcionam da **mesma forma** que os do sistema – basta usar `{{nome_do_placeholder}}`."
    )
    st.info(
        "✅ Placeholders personalizados são substituídos automaticamente na geração do PDF.",
        icon="ℹ️",
    )
    st.markdown(" ")

    if personalizados:
        st.markdown(f"**{len(personalizados)}** placeholder(s) cadastrado(s):")
        for idx, ph in enumerate(personalizados):
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
                            "Valor *",
                            value=ph.get("valor", ""),
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
                            st.error("🚫 O valor é obrigatório.")
                        elif nome_clean in placeholders_sistema_nomes:
                            st.error(f"🚫 `{nome_clean}` é reservado para placeholders do sistema.")
                        elif nome_clean != ph.get("nome") and any(p.get("nome") == nome_clean for i, p in enumerate(personalizados) if i != idx):
                            st.warning(f"⚠️ Já existe um placeholder com o nome `{nome_clean}`.")
                        else:
                            personalizados[idx] = {
                                "nome": nome_clean,
                                "valor": edit_desc.strip(),
                                "exemplo": edit_ex.strip(),
                            }
                            salvar_placeholders_custom(personalizados)
                            st.session_state["ph_editando_idx"] = None
                            st.success(f"✅ Placeholder `{{{{{nome_clean}}}}}` atualizado!")
                            st.rerun()
            else:
                col_badge, col_desc, col_ex, col_edit, col_del = st.columns([3, 4, 3, 0.6, 0.6])
                with col_badge:
                    st.markdown(
                        f'<span class="ph-custom-badge">{{{{{ph.get("nome", "")}}}}}</span>',
                        unsafe_allow_html=True,
                    )
                with col_desc:
                    st.markdown(f"**Valor:** {ph.get('valor', '—')}")
                with col_ex:
                    st.caption(f"ex: {ph.get('exemplo', '—')}")
                with col_edit:
                    if st.button("✏️", key=f"edit_custom_{idx}", help="Editar este placeholder"):
                        st.session_state["ph_editando_idx"] = idx
                        st.rerun()
                with col_del:
                    if st.button("🗑️", key=f"del_custom_{idx}", help="Remover este placeholder"):
                        personalizados.pop(idx)
                        salvar_placeholders_custom(personalizados)
                        if st.session_state["ph_editando_idx"] == idx:
                            st.session_state["ph_editando_idx"] = None
                        st.rerun()

        st.divider()
    else:
        st.info("💡 Nenhum placeholder personalizado cadastrado ainda.")
        st.markdown(" ")

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
                    "Valor *",
                    placeholder="Ex: TESTE, CONFIDENCIAL, etc.",
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
                    st.error("🚫 O valor é obrigatório.")
                elif nome_clean in placeholders_sistema_nomes:
                    st.error(f"🚫 `{nome_clean}` é reservado para placeholders do sistema.")
                elif any(p.get("nome") == nome_clean for p in personalizados):
                    st.warning(f"⚠️ Já existe um placeholder com o nome `{nome_clean}`.")
                else:
                    personalizados.append({
                        "nome": nome_clean,
                        "valor": descricao.strip(),
                        "exemplo": exemplo.strip(),
                    })
                    salvar_placeholders_custom(personalizados)
                    st.success(f"✅ Placeholder `{{{{{nome_clean}}}}}` adicionado com sucesso!")
                    st.rerun()
