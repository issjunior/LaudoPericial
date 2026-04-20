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
│  ├── Auth (login/logout)                                │
│  ├── REP (Requisição de Exame Pericial)                 │
│  ├── Tipos de Exame                                    │
│  ├── Solicitantes                                      │
│  ├── Templates                                        │
│  ├── Laudos ⭐ (core)                                   │
│  ├── Dashboard                                         │
│  └── Sistema (backup, busca, etc)                       │
└─────────────────────────────────────────────────────────┘
```

## Legenda de Status

| Símbolo | Significado |
|---------|-------------|
| ✅ | Implantado |
| 🚧 | Parcial |
| ⏳ | Pendente |

## Como Usar

1. **Ler a especificação** antes de implementar nova feature
2. **Verificar status** em `02-funcionalidades.md`
3. **Criar task** em `03-sprints.md` seguindo o modelo
4. **Marcar concluído** após implementar

## Contúdo

### 01 - Tecnologias
- Python 3.13
- Streamlit
- SQLite
- bcrypt
- Estrutura de diretórios
- Padrões de código

### 02 - Funcionalidades
- Auth
- REP
- Tipos de Exame
- Solicitantes
- Templates
- Laudos
- Dashboard
- Sistema

### 03 - Sprints
- Sprint 0: Fundação (já implementado)
- Sprint 1: REP e Cadastros
- Sprint 2: Laudos - Criação e Edição
- Sprint 3: Laudos - Finalização e Export
- Sprint 4: Visualização e Busca
- Sprint 5: Prazos e Alertas
- Sprint 6: Backup e Sistema

---

## Features Recentes (Sprint 2)

| Feature | Arquivo | Descrição |
|--------|--------|-----------|
| Criação automática de Laudo | `services/rep_service.py` | Ao criar REP com tipo que tem template, laudo é criado automaticamente |
| Editor de Laudo | `pages/editor_laudo.py` | Edita seções com placeholders |
| Quill Editor | `pages/editor_laudo.py` | Editor de texto rico em cada seção |
| listar_laudos() | `services/laudo_service.py` | Lista laudos com filtros |

## Issues Conhecidos

| Issue | Descrição | Status |
|-------|-----------|--------|
| Menu Laudos | Expansão automática não funciona | ⏳ Pendente |