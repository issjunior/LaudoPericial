# Especificação SDD - LaudoPericial

Documentação de especificação seguindo filosofia SDD (Spec-Driven Development).

## Arquivos de documentação

| Arquivo | Descrição |
|---------|-----------|
| [01-tecnologias.md](spec/01-tecnologias.md) | Stack tecnológico e estrutura |
| [02-funcionalidades.md](spec/02-funcionalidades.md) | Lista completa de funcionalidades por módulo |
| [03-sprints.md](spec/03-sprints.md) | Planejamento de sprints e tasks |

## Visão Geral

```
┌─────────────────────────────────────────────────────────┐
│                   LaudoPericial                         │
├─────────────────────────────────────────────────────────┤
│  Tech Stack: Python 3.13 + Streamlit + SQLite           │
│                                                         │
│  Módulos:                                               │
│  ├── Auth (login/logout/alterar senha)                  │
│  ├── REP (Requisição de Exame Pericial)                 │
│  ├── Tipos de Exame                                     │
│  ├── Solicitantes                                       │
│  ├── Templates de laudos a depender do tipo de exame    │
│  ├── Laudos ⭐ (core)                                  │
│  ├── Dashboard (métricas + prazos)                      │
│  └── Sistema (backup, busca, perfil)                    │
└─────────────────────────────────────────────────────────┘
```
## Conteúdo

### 01 - Tecnologias
- Python 3.13
- Streamlit
- SQLite
- bcrypt
- streamlit-jodit (editor de texto)
- Playwright/Chromium (geração PDF)

### 02 - Resumo de Funcionalidades
- **Auth**: Login, Logout, Alterar senha
- **REP**: CRUD completo, filtros, status automático
- **Tipos de Exame**: CRUD, ativo/inativo
- **Solicitantes**: CRUD, ativo/inativo
- **Templates**: CRUD com seções, reordenação
- **Laudos**: CRUD completo, versões, exportar PDF
- **Dashboard**: Métricas, prazos
- **Sistema**: Backup, Restore, Busca, Histórico, Perfil

---

## Execução Local

### 1. Criar ambiente virtual

```bash
python -m venv venv
.\venv\Scripts\Activate
```

### 2. Instalar dependências

```bash
pip install -r requirements.txt
```

### 3. Instalar Chromium (para geração de PDF)

```bash
playwright install chromium
```

### 4. Executar o app

```bash
streamlit run app.py
```