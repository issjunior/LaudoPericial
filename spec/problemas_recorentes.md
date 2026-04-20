# Problemas Recorrentes — Manual Técnico

## PR-001: Menu Lateral — Expansão Automática

### Sintoma
Seções do menu não expandem automaticamente ao acessar páginas.

### Causa Raiz
**Causa 1:** Falta `st.session_state["_active_page"] = __file__` antes de `renderizar_menu()` em páginas.  
**Causa 2:** Links faltando em `app.py` (`tela_dashboard`) vs `menu.py` (desincronização).

### Solução Rápida

#### Fix 1: Adicionar `_active_page` em Todas as Páginas
**Localização:** Após `st.set_page_config()` em `/pages/*.py`

```python
st.set_page_config(page_title="...", page_icon="...", layout="wide")
st.session_state["_active_page"] = __file__  # ← ADICIONAR AQUI
renderizar_menu()
```

**Sequência obrigatória:**
1. `st.set_page_config()`
2. `st.session_state["_active_page"] = __file__`
3. `renderizar_menu()`

#### Fix 2: Sincronizar Menus
Garantir que `app.py` (tela_dashboard) possui todos os links presentes em `menu.py`.

**Checklist:**
- [ ] REPs: Nova REP, Listar REPs, **Editar REP**
- [ ] Laudos: Vincular Laudo, **Editar Laudo**, **Visualizar Laudo**
- [ ] Cadastros: Tipos de Exame, Solicitantes, Templates, Editor Templates
- [ ] Sistema: Busca, Histórico, Backup, Perfil

### Identificação
```python
# ❌ ERRADO (Menu não expande)
st.set_page_config(...)
renderizar_menu()

# ✅ CORRETO (Menu expande)
st.set_page_config(...)
st.session_state["_active_page"] = __file__
renderizar_menu()
```

### Arquivos Críticos
- `components/menu.py` — Define menu base
- `app.py` → `tela_dashboard()` — Deve ter TODOS os links
- `pages/*.py` — Todas as páginas devem ter `_active_page`

### Teste
1. Acessar página "Editar REP"
2. Verificar se seção "📋 Requisições (REPs)" expande automaticamente
3. ✅ Se expande → corrigido | ❌ Se não → aplicar fix

---

