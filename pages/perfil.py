# pages/perfil.py
"""
pages/perfil.py
──────────────────────────────────────────────────────
Página de perfil e configurações do usuário.
Permite editar dados pessoais, segurança e preferências.
──────────────────────────────────────────────────────
"""

import sys
import os
import streamlit as st

# Garante que a raiz do projeto está no sys.path
ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from components.menu import renderizar_menu
from core.auth import (
    obter_usuario_logado, 
    exigir_autenticacao, 
    atualizar_usuario, 
    alterar_senha,
    confirmar_senha_critica,
    extrair_username
)

# ──────────────────────────────────────────────────────
# CONFIGURAÇÃO DA PÁGINA
# ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Perfil e Configurações — LaudoPericial",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Defina a página atual na sessão para o menu funcionar corretamente
st.session_state["_active_page"] = __file__

# Renderiza o menu lateral (já exige autenticação)
renderizar_menu()

# ──────────────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────────────
usuario = obter_usuario_logado()

st.title("👤 Perfil e Configurações")
st.markdown("Gerencie seus dados pessoais, configurações de segurança e preferências do sistema.")
st.markdown("---")

# ──────────────────────────────────────────────────────
# ABAS DE CONFIGURAÇÃO
# ──────────────────────────────────────────────────────

tab_dados, tab_seguranca, tab_preferencias = st.tabs([
    "👤 Meus Dados", 
    "🔐 Segurança", 
    "⚙️ Preferências"
])

# ------------------------------------------------------
# ABA: MEUS DADOS
# ------------------------------------------------------
with tab_dados:
    st.subheader("Informações Profissionais")
    
    with st.form("form_dados_pessoais"):
        col1, col2 = st.columns(2)
        
        with col1:
            novo_nome = st.text_input("Nome Completo", value=usuario['nome'], key="perfil_nome")
            nova_matricula = st.text_input("Matrícula", value=usuario['matricula'] or "", key="perfil_matricula")
            
        with col2:
            novo_cargo = st.text_input("Cargo", value=usuario['cargo'], key="perfil_cargo")
            nova_lotacao = st.text_input("Lotação / Unidade", value=usuario['lotacao'], key="perfil_lotacao")
            
        st.markdown("---")
        submitted = st.form_submit_button("Salvar Alterações", type="primary")
        
        if submitted:
            if not novo_nome.strip() or not novo_cargo.strip() or not nova_lotacao.strip():
                st.error("❌ Nome, Cargo e Lotação são obrigatórios.")
            else:
                try:
                    atualizar_usuario(
                        usuario_id=usuario['id'],
                        nome=novo_nome.strip(),
                        cargo=novo_cargo.strip(),
                        matricula=nova_matricula.strip(),
                        lotacao=nova_lotacao.strip(),
                        email=usuario['email'],
                        pasta_exportacao=usuario['pasta_exportacao'],
                        alerta_prazo=bool(usuario['alerta_prazo']),
                        dias_alerta=usuario['dias_alerta']
                    )
                    st.success("✅ Dados atualizados com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Erro ao atualizar: {e}")

# ------------------------------------------------------
# ABA: SEGURANÇA
# ------------------------------------------------------
with tab_seguranca:
    st.subheader("Acesso e Senha")
    
    # --- Atualização de E-mail ---
    with st.expander("📧 Alterar E-mail Institucional", expanded=False):
        with st.form("form_email"):
            st.info(f"Seu e-mail atual é: **{usuario['email']}**")
            novo_email = st.text_input("Novo E-mail", key="perfil_novo_email")
            
            if novo_email:
                username_preview = extrair_username(novo_email)
                st.caption(f"Seu novo usuário de login será: `{username_preview}`")
                
            submitted_email = st.form_submit_button("Atualizar E-mail")
            
            if submitted_email:
                if "@" not in novo_email or "." not in novo_email:
                    st.error("❌ E-mail inválido.")
                else:
                    try:
                        atualizar_usuario(
                            usuario_id=usuario['id'],
                            nome=usuario['nome'],
                            cargo=usuario['cargo'],
                            matricula=usuario['matricula'],
                            lotacao=usuario['lotacao'],
                            email=novo_email.strip().lower(),
                            pasta_exportacao=usuario['pasta_exportacao'],
                            alerta_prazo=bool(usuario['alerta_prazo']),
                            dias_alerta=usuario['dias_alerta']
                        )
                        st.success("✅ E-mail atualizado! O usuário de login foi alterado.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Erro ao atualizar e-mail: {e}")

    st.markdown(" ")
    
    # --- Alteração de Senha ---
    with st.expander("🔐 Alterar Senha de Acesso", expanded=True):
        with st.form("form_senha"):
            senha_atual = st.text_input("Senha Atual", type="password", key="perfil_senha_atual")
            nova_senha = st.text_input("Nova Senha", type="password", key="perfil_nova_senha")
            confirmar_nova = st.text_input("Confirmar Nova Senha", type="password", key="perfil_confirmar_senha")
            
            submitted_senha = st.form_submit_button("Redefinir Senha", type="secondary")
            
            if submitted_senha:
                if not senha_atual or not nova_senha or not confirmar_nova:
                    st.error("❌ Preencha todos os campos de senha.")
                elif nova_senha != confirmar_nova:
                    st.error("❌ A nova senha e a confirmação não coincidem.")
                elif len(nova_senha) < 6:
                    st.error("❌ A nova senha deve ter pelo menos 6 caracteres.")
                else:
                    if confirmar_senha_critica(senha_atual):
                        try:
                            alterar_senha(usuario['id'], nova_senha)
                            st.success("✅ Senha alterada com sucesso!")
                        except Exception as e:
                            st.error(f"❌ Erro ao alterar senha: {e}")
                    else:
                        st.error("❌ Senha atual incorreta.")

# ------------------------------------------------------
# ABA: PREFERÊNCIAS
# ------------------------------------------------------
with tab_preferencias:
    st.subheader("Configurações do Sistema")
    
    with st.form("form_preferencias"):
        st.markdown("### 💾 Exportação")
        st.write("Defina a pasta padrão onde os laudos (Word/PDF) serão salvos.")
        
        # Inicializa o valor no session_state se ainda não existir
        if "perfil_caminho_exportacao" not in st.session_state:
            st.session_state["perfil_caminho_exportacao"] = usuario['pasta_exportacao'] or ""
            
        # Colunas: Botão primeiro, depois o Input (mantendo a ordem solicitada)
        col_btn, col_path = st.columns([1, 4])
        
        with col_btn:
            st.write("") # Pequeno espaço para alinhamento
            if st.form_submit_button("📁 Escolher..."):
                try:
                    import subprocess
                    import platform
                    sistema = platform.system()
                    caminho_selecionado = None
                    
                    if sistema == "Windows":
                        ps_script = "$app = New-Object -ComObject Shell.Application; $folder = $app.BrowseForFolder(0, 'Selecione a pasta de exportação', 0, 0x11); if ($folder) { $folder.Self.Path }"
                        result = subprocess.run(["powershell", "-Command", ps_script], capture_output=True, text=True, encoding="latin-1")
                        caminho_selecionado = result.stdout.strip()
                    elif sistema == "Darwin":
                        as_script = 'POSIX path of (choose folder with prompt "Selecione a pasta de exportação")'
                        result = subprocess.run(["osascript", "-e", as_script], capture_output=True, text=True)
                        caminho_selecionado = result.stdout.strip()
                    elif sistema == "Linux":
                        try:
                            result = subprocess.run(["zenity", "--file-selection", "--directory", "--title=Selecione a pasta de exportação"], capture_output=True, text=True)
                            caminho_selecionado = result.stdout.strip()
                        except FileNotFoundError:
                            st.error("Zenity não encontrado.")
                    
                    if caminho_selecionado:
                        st.session_state["perfil_caminho_exportacao"] = os.path.abspath(caminho_selecionado)
                        st.rerun()
                except Exception as e:
                    st.error(f"Erro: {e}")

        with col_path:
            pasta_exp = st.text_input(
                "Caminho da Pasta", 
                key="perfil_caminho_exportacao",
                label_visibility="collapsed",
                placeholder="Ex: C:/Usuarios/Documentos/Laudos"
            )
        
        st.markdown("---")
        st.markdown("### ⏰ Prazos e Alertas")
        
        col_alert, col_dias = st.columns([1, 1])
        
        with col_alert:
            hab_alerta = st.checkbox(
                "Habilitar alertas de prazo", 
                value=bool(usuario['alerta_prazo']),
                help="Se ativado, o sistema destacará REPs que estão próximas do vencimento.",
                key="perfil_hab_alerta"
            )
            
        with col_dias:
            dias_ant = st.number_input(
                "Dias de antecedência para o alerta",
                min_value=1,
                max_value=30,
                value=usuario['dias_alerta'] or 3,
                key="perfil_dias_alerta"
            )
            
        st.markdown(" ")
        submitted_pref = st.form_submit_button("Salvar Preferências", type="primary")
        
        if submitted_pref:
            try:
                atualizar_usuario(
                    usuario_id=usuario['id'],
                    nome=usuario['nome'],
                    cargo=usuario['cargo'],
                    matricula=usuario['matricula'],
                    lotacao=usuario['lotacao'],
                    email=usuario['email'],
                    pasta_exportacao=pasta_exp.strip(),
                    alerta_prazo=hab_alerta,
                    dias_alerta=dias_ant
                )
                
                st.success("✅ Preferências salvas!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erro ao salvar preferências: {e}")
