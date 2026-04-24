# Especificação SDD - LaudoPericial

Documentação de especificação seguindo filosofia SDD (Spec-Driven Development).

## Arquivos

| Arquivo | Descrição |
|---------|-----------|
| [01-tecnologias.md](./01-tecnologias.md) | Stack tecnológico e estrutura |
| [02-funcionalidades.md](./02-funcionalidades.md) | Lista completa de funcionalidades por módulo |
| [03-sprints.md](./03-sprints.md) | Planejamento de sprints e tasks |

## Visão Geral

```
┌─────────────────────────────────────────────────────────┐
│                   LaudoPericial                         │
├─────────────────────────────────────────────────────────┤
│  Tech Stack: Python 3.13 + Streamlit + SQLite           │
│                                                         │
│  Módulos:                                               │
│  ├── Auth (login/logout/alterar senha)                     │
│  ├── REP (Requisição de Exame Pericial)                   │
│  ├── Tipos de Exame                                    │
│  ├── Solicitantes                                      │
│  ├── Templates (com seções)                           │
│  ├── Laudos ⭐ (core)                                │
│  ├── Dashboard (métricas + prazos)                      │
│  └── Sistema (backup, busca, perfil)                    │
└─────────────────────────────────────────────────────────┘
```

## Legenda de Status

| Símbolo | Significado |
|---------|-------------|
| ✅ | Implantado |
| 🚧 | Parcial |
| ⏳ | Pendente |

## Conteúdo

### 01 - Tecnologias
- Python 3.13
- Streamlit
- SQLite
- bcrypt
- streamlit-jodit (editor de texto)
- Playwright/Chromium (geração PDF)

### 02 - Funcionalidades
- **Auth**: Login, Logout, Alterar senha
- **REP**: CRUD completo, filtros, status automático
- **Tipos de Exame**: CRUD, ativo/inativo
- **Solicitantes**: CRUD, ativo/inativo
- **Templates**: CRUD com seções, reordenação
- **Laudos**: CRUD completo, versões, exportar PDF
- **Dashboard**: Métricas, prazos
- **Sistema**: Backup, Restore, Busca, Histórico, Perfil

### 03 - Sprints
- Sprint 0: Fundação (✅)
- Sprint 1: REP e Cadastros (✅)
- Sprint 2: Laudos - Criação e Edição (✅)
- Sprint 3: Laudos - Export PDF (✅)
- Sprint 4: Visualização e Busca (✅)
- Sprint 5: Backup e Sistema (✅)
- Sprint 6: Prazos e Alertas (🚧)
- Sprint 7: Fotos e Ilustrações (⏳)
- Sprint 8: Export DOCX/ODT (⏳)

---
