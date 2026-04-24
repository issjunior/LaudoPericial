# Planejamento de Sprints

## Sprint 0: Fundação (✅ IMPLEMENTADA)

**Objetivo**: Setup inicial e funcionalidades core já operacionais.

| ID | Task | Módulo | Responsável | Status |
|----|------|--------|-------------|--------|
| T00.1 | Setup projeto Python + Streamlit | Sistema | ✅ |
| T00.2 | Estrutura de banco de dados (11 tabelas) | Database | ✅ |
| T00.3 | Autenticação bcrypt (login/logout/cadastro + página login/logout) | Auth | ✅ |
| T00.4 | Menu de navegação | UI | ✅ |
| T00.5 | Dashboard com métricas | Dashboard | ✅ |

---

## Status de REP

| Status | Descrição | Transição |
|--------|-----------|-----------|
| **Pendente** | REP aguardando início do laudo | Estado inicial |
| **Em Andamento** | Laudo em elaboração | automaticamene ao criar laudo |
| **Concluído** | Laudo finalizado | ao finalizar laudo |

### Lógica de Prazos (Dashboard)

O sistema calcula automaticamente o status de prazo com base na `data_solicitacao`:

- **Prazo Padrão**: 10 dias para completar um laudo
- **Prazo Vencendo**: REP ativa (Pendente/Em Andamento) com 7-10 dias desde a solicitação
- **Em Atraso**: REP ativa com mais de 10 dias desde a solicitação

Constantes em `app.py:298-299`:
```python
PRAZO_PADRAO_DIAS = 10        # Prazo total para uma REP
DIAS_PARA_ALERTA_VENCENDO = 3 # Quantos dias antes do prazo para alertar "Vencendo"
```

---

## Sprint 1: REP e Cadastros (✅ IMPLEMENTADA)

**Objetivo**: GERENCIAMENTO DE REPs E CADASTROS BASE.

| ID | Task | Módulo | Responsável | Status |
|----|------|--------|-------------|--------|
| T01.1 | Criar REP (formulário completo) | REP | ✅ |
| T01.2 | Listar REP (com filtros) | REP | ✅ |
| T01.3 | CRUD Tipos de Exame | TiposExame | ✅ |
| T01.4 | CRUD Solicitantes | Solicitantes | ✅ |
| T01.5 | CRUD Templates | Templates | ✅ |
| T01.6 | CRUD Seções Template | Templates | ✅ |
| T01.7 | **Editar REP** | REP | ✅ |
| T01.8 | Excluir REP (com verificação) | REP | ✅ |
| T01.9 | Status automático REP | Automático via laudo (Pendente→Em Andamento→Concluído) | ✅ |

**Duração**: 1 sprint (2 semanas)
**Prioridade**: ALTA

---

## Sprint 2: Laudos - Criação e Edição (✅ IMPLEMENTADA)

**Objetivo**: FLUXO PRINCIPAL - CRIAR LAUDOS A PARTIR DE REPs.

| ID | Task | Módulo | Responsável | Status |
|----|------|--------|-------------|--------|
| T02.1 | Vincular Laudo a REP: criação automática ao criar REP se existir template (+ menu manual) | Laudos | ✅ |
| T02.2 | Editor de Laudo: page editor_laudo.py + menu + editar seções com placeholders | Laudos | ✅ |
| T02.3 | Editor de texto Quill/Jodit em cada seção (com numeração) | Laudos | ✅ |
| T02.4 | Salvar versão (snapshot) | Laudos | ✅ |
| T02.5 | Carregar versão anterior | Laudos | ✅ |
| T02.6 | Listar e restaurar versões | Laudos | ✅ |
| T02.7 | Excluir versão | Laudos | ✅ |
| T02.8 | Preâmbulo/cabeçalho automático | Generators | ✅ |
| T02.9 | Placeholders em seções (substituição automática no PDF) | Laudos | ✅ |
| T02.10 | Finalizar laudo (muda REP→Concluído) | Laudos | ✅ |

**Duração**: 2 sprints (4 semanas)
**Prioridade**: CRÍTICA (funcionalidade core)

---

## Sprint 3: Laudos - Export PDF (✅ IMPLEMENTADA)

**Objetivo**: COMPLETAR E EXPORTAR LAUDOS.

| ID | Task | Módulo | Responsável | Status |
|----|------|--------|-------------|--------|
| T03.1 | Playwright setup (Chromium) | Generators | ✅ |
| T03.2 | HTML builder (construção do documento) | Generators | ✅ |
| T03.3 | Exportar PDF | Generators | ✅ |
| T03.4 | Visualizar PDF | Laudos | ✅ |
| T03.5 | Download PDF | Laudos | ✅ |

**Duração**: 1 sprint (2 semanas)
**Prioridade**: ALTA

---

## Sprint 4: Visualização e Busca (✅ IMPLEMENTADA)

**Objetivo**: CONSULTAS E VISUALIZAÇÃO DE LAUDOS.

| ID | Task | Módulo | Responsável | Status |
|----|------|--------|-------------|--------|
| T04.1 | Visualizar laudo (leitura) | Laudos | ✅ |
| T04.2 | Listar laudos (com filtros) | Laudos | ✅ |
| T04.3 | Busca global | Sistema | ✅ |
| T04.4 | Histórico de auditoria (UI) | Sistema | ✅ |
| T04.5 | Detalhe REP | REP | ✅ |

**Duração**: 1 sprint (2 semanas)
**Prioridade**: MÉDIA

---

## Sprint 5: Backup e Sistema (✅ IMPLEMENTADA)

**Objetivo**: UTILIDADES E MANUTENÇÃO.

| ID | Task | Módulo | Responsável | Status |
|----|------|--------|-------------|--------|
| T05.1 | Backup database (exportar .db) | Sistema | ✅ |
| T05.2 | Restore database (importar .db) | Sistema | ✅ |
| T05.3 | Perfil usuário (alterar senha) | Sistema | ✅ |
| T05.4 | Perfil usuário (alterar dados) | Sistema | ✅ |
| T05.5 | Primeiro acesso (setup inicial) | Sistema | ✅ |
| T05.6 | Importar banco existente | Sistema | ✅ |

**Duração**: 1 sprint (2 semanas)
**Prioridade**: ALTA

---

## Sprint 6: Prazos e Alertas (🚧 PARCIAL)

**Objetivo**: CONTROLE DE PRAZOS LEGAIS.

| ID | Task | Módulo | Responsável | Status |
|----|------|--------|-------------|--------|
| T06.1 | Calcular prazo automático | Sistema | ✅ |
| T06.2 | Alertas de prazo (dashboard) | Dashboard | ✅ |
| T06.3 | Badge de prazo na lista | REP | ✅ |
| T06.4 | Notificações | Sistema | ⏳ |
| T06.5 | Configurar alerta por usuário | Sistema | ⏳ |

**Duração**: 1 sprint (2 semanas)
**Prioridade**: ALTA

---

## Sprint 7: Fotos e Ilustrações (⏳ PENDENTE)

**Objetivo**: ADICIONAR IMAGENS AOS LAUDOS.

| ID | Task | Módulo | Responsável | Status |
|----|------|--------|-------------|--------|
| T07.1 | Upload de fotos/ilustrações | Laudos | ⏳ |
| T07.2 | Remover foto | Laudos | ⏳ |
| T07.3 | Legendas | Laudos | ⏳ |
| T07.4 | Incorporar no PDF | Generators | ⏳ |

**Duração**: 1 sprint (2 semanas)
**Prioridade**: MÉDIA

---

## Sprint 8: Export DOCX/ODT (⏳ PENDENTE)

**Objetivo**: EXPORTAÇÃO ALTERNATIVA.

| ID | Task | Módulo | Responsável | Status |
|----|------|--------|-------------|--------|
| T08.1 | Exportar DOCX | Generators | ⏳ |
| T08.2 | Exportar ODT | Generators | ⏳ |

**Duração**: 1 sprint (2 semanas)
**Prioridade**: BAIXA

---

## Resumo por Prioridade

| Prioridade | Tasks | Sprints |
|------------|-------|---------|
| Crítica | T02.x | Sprint 2 |
| Alta | T01.x, T03.x, T05.x, T06.x | Sprints 1, 3, 5, 6 |
| Média | T04.x | Sprint 4 |
| Baixa | T07.x, T08.x | Sprints 7, 8 |

---

## Roadmap Visual

```
Sprint 0    Sprint 1    Sprint 2    Sprint 3    Sprint 4    Sprint 5    Sprint 6    Sprint 7    Sprint 8
   ✅         ✅         ✅         ✅         ✅         ✅         🚧         ⏳          ⏳
 Fund/    REP+Cads   Laudos    Export    Visual    Backup    Prazos    Fotos     Export
           Edit REP  Editor    PDF      Audit    Perfil   Alerts            DOCX/ODT
                               Assin                                    Config
```

---

## Critério de Ready

Cada task está "ready" quando:
- ✅ Implementada a lógica em `services/`
- ✅ Criada/atualizada a página em `pages/`
- ✅ Adicionados testes se aplicável
- ✅ Funcionando em ambiente local