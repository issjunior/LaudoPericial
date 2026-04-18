# 🔍 LaudoPericial

**Sistema de gestão e confecção de laudos periciais criminais**

Desenvolvido para a Polícia Científica do Paraná, LaudoPericial é uma plataforma completa para criar, editar, gerenciar e exportar laudos periciais de forma segura e eficiente.

---

## 📊 Status de Desenvolvimento

**Progresso geral:** 28% (Sprint 0 + Sprint 1)

```
Sprint 0 ✅ | Sprint 1 ✅ | Sprint 2 ⏳ | Sprint 3 ⏳ | Sprint 4 ⏳ | Sprint 5 ⏳ | Sprint 6 ⏳
Fundação   | REPs      | Laudos    | Export    | Busca    | Prazos   | Sistema
Completo   | Completo  | Iniciado  | Planejado | Planejado| Planejado| Planejado
```

---

## ✅ Funcionalidades Implementadas

### 🔐 Autenticação e Acesso
- ✅ Login seguro com criptografia
- ✅ Logout e fim de sessão
- ✅ Configuração inicial (primeiro usuário)
- ✅ Controle de acesso por usuário

### 📋 Requisições de Exame (REP)
- ✅ Criar novas requisições de exame
- ✅ Listar com filtros avançados
- ✅ Editar dados das requisições
- ✅ Excluir requisições
- ✅ Controle automático de status
- ✅ Detalhes completos de cada requisição

### 🏢 Cadastros Base
- ✅ Gerenciar tipos de exame
- ✅ Cadastro de solicitantes (delegacias, varas, etc)
- ✅ Criar e gerenciar templates de laudos
- ✅ Estrutura de seções para templates

### 📊 Dashboard
- ✅ Métricas gerais (requisições pendentes, em andamento, concluídas)
- ✅ Visão rápida do fluxo de trabalho
- ✅ Resumo de atividades

---

## 🚀 Próximas Features (Roadmap)

### 📄 Sprint 2: Editor de Laudos (Em Progresso)
- Criar laudo a partir da requisição
- **Editor visual e intuitivo** para escrever laudos
- Salvar versões anteriores
- Upload de fotos e ilustrações
- Validação automática de campos obrigatórios

### 📤 Sprint 3: Exportação
- Gerar **PDF profissional** com formatação
- Exportar em **Word** para edição
- Exportar em **OpenDocument** (compatibilidade)
- Geração automática de preâmbulo

### 🔍 Sprint 4: Visualização e Busca
- Visualizar laudos em modo leitura
- Busca global no sistema
- Histórico de alterações
- Detalhes completos de requisições

### ⏰ Sprint 5: Prazos e Alertas
- Cálculo automático de prazos legais
- Alertas na dashboard
- Notificações de urgência
- Configuração de lembretes

### 🛠️ Sprint 6: Melhorias Finais
- Alterar senha do usuário
- Limpeza de dados antigos
- Relatórios e estatísticas
- Melhorias gerais

---

## 🛠️ Stack Técnico

| Componente | Tecnologia |
|-----------|-----------|
| **Linguagem** | Python 3.13 |
| **Interface** | Streamlit (web app interativo) |
| **Banco de Dados** | SQLite com criptografia |
| **Autenticação** | bcrypt (criptografia de senhas) |
| **Segurança** | Variáveis de ambiente (.env) |

---

## 🚀 Como Usar

### Requisitos
- Python 3.13+
- pip (gerenciador de pacotes)

### Instalação Rápida

```bash
# 1. Clone o repositório
git clone https://github.com/issjunior/laudopericial.git
cd laudopericial

# 2. Crie um ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute o aplicativo
streamlit run app.py
```

O sistema abrirá automaticamente em `http://localhost:8501`

### Primeiro Acesso
1. Crie sua conta administrativa (primeira vez)
2. Faça login
3. Configure tipos de exame, solicitantes e templates
4. Comece a criar requisições e laudos

---

## 📁 Estrutura do Projeto

```
LaudoPericial/
├── app.py                    # Entrada principal
├── pages/                    # Páginas do aplicativo
│   ├── 00_login.py          # Autenticação
│   ├── 01_dashboard.py      # Dashboard
│   ├── nova_rep.py          # Criar requisição
│   ├── listar_rep.py        # Listar requisições
│   ├── editor_laudo.py      # Editor de laudo (em desenvolvimento)
│   └── ...
├── services/                # Lógica de negócio
│   ├── rep_service.py       # Requisições
│   ├── laudo_service.py     # Laudos
│   ├── template_service.py  # Templates
│   └── ...
├── database/                # Banco de dados
│   ├── db.py               # Conexão
│   └── models.py           # Estrutura das tabelas
├── generators/              # Exportação (PDF, Word, etc)
└── spec/                    # Documentação técnica
```

---

## 🔒 Segurança

- **Senhas criptografadas** com bcrypt
- **Banco de dados criptografado** com SQLite
- **Variáveis sensíveis** em `.env` (não versionado)
- **Sistema privado** — uso restrito

---

## 📝 Roadmap Visual

```
Q1 2026  →  Sprint 0 ✅ (Fundação)
         →  Sprint 1 ✅ (Requisições)

Q2 2026  →  Sprint 2 ⏳ (Editor)
         →  Sprint 3 ⏳ (Exportação)

Q3 2026  →  Sprint 4 ⏳ (Busca)
         →  Sprint 5 ⏳ (Prazos)

Q4 2026  →  Sprint 6 ⏳ (Finalizações)
```

---

## 🐛 Problemas Conhecidos

| Problema | Status |
|----------|--------|
| Menu "Editar REP" aparece após clicar em outra página | ⏳ Pendente |

---

## 📚 Documentação

Para informações técnicas detalhadas, consulte:
- [`spec/01-tecnologias.md`](spec/01-tecnologias.md) — Stack e estrutura
- [`spec/02-funcionalidades.md`](spec/02-funcionalidades.md) — Funcionalidades por módulo
- [`spec/03-sprints.md`](spec/03-sprints.md) — Planejamento detalhado

---

## 📧 Sobre

**Desenvolvido para:** Polícia Científica do Paraná  
**Uso restrito:** Sistema privado

---

**Última atualização:** Abril 2026