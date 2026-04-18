# Especificação de Funcionalidades

## Módulo: Autenticação

| ID | Funcionalidade | Descrição | Status |
|----|----------------|-----------|--------|
| AUTH-01 | Login | Autenticação por username + senha | ✅ Implantado |
| AUTH-02 | Logout | Encerrar sessão + página de logout + redirecionar | ✅ Implantado |
| AUTH-03 | Cadastro primeiro usuário | Setup inicial do sistema | ✅ Implantado |
| AUTH-04 | Alterar senha | Usuário troca sua senha | ⏳ Pendente |

---

## Módulo: REP (Requisição de Exame Pericial)

| ID | Funcionalidade | Descrição | Status |
|----|----------------|-----------|--------|
| REP-01 | Criar REP | Registrar nova requisição de exame | ✅ Implantado |
| REP-02 | Listar REP | Listar com filtros (número, tipo, status, data) | ✅ Implantado |
| REP-03 | Editar REP | Alterar dados da REP | ✅ Implantado |
| REP-04 | Excluir REP | Remover REP (verificar laudos vinculados) | ✅ Implantado |
| REP-05 | Mudar status REP | Automático (via laudo) | ✅ Implantado |
| REP-06 | Filtrar REP avançado | Busca por múltiplos critérios | ✅ Implantado |

### Campos REP
- `numero_rep` (único)
- `data_solicitacao`
- `horario_acionamento` / `horario_chegada` / `horario_saida` (exame local)
- `tipo_solicitacao` (BO, Ofício, BO PM, BO PC, CECOMP, Outro)
- `numero_documento` / `data_documento`
- `solicitante_id` (FK)
- `nome_autoridade`
- `tipo_exame_id` (FK)
- `nome_envolvido`
- `local_fato_descricao`
- `latitude` / `longitude` (exame local)
- `status` (Pendente, Em Andamento, Concluído, Arquivado, Cancelado)
- `observacoes`

---

## Módulo: Tipos de Exame

| ID | Funcionalidade | Descrição | Status |
|----|----------------|-----------|--------|
| TE-01 | Criar tipo | Cadastrar novo tipo de exame | ✅ Implantado |
| TE-02 | Listar tipos | Listar com filtros | ✅ Implantado |
| TE-03 | Editar tipo | Alterar dados | ✅ Implantado |
| TE-04 | Ativar/Desativar | Toggle ativo | ✅ Implantado |
| TE-05 | Listar ativos apenas | Filter padrão | ⏳ Pendente |

### Campos Tipo de Exame
- `codigo` (formato X-000, ex: H-001, A-001)
- `nome`
- `descricao`
- `exame_de_local` (boolean - habilita campos de local)
- `ativo` (boolean)

---

## Módulo: Solicitantes

| ID | Funcionalidade | Descrição | Status |
|----|----------------|-----------|--------|
| SOL-01 | Criar solicitante | Cadastrar delegacia/varas | ✅ Implantado |
| SOL-02 | Listar solicitantes | Listar com filtros | ✅ Implantado |
| SOL-03 | Editar solicitante | Alterar dados | ✅ Implantado |
| SOL-04 | Ativar/Desativar | Toggle ativo | ✅ Implantado |

### Campos Solicitante
- `nome`
- `orgao` (Delegacia, Vara, Promotoria)
- `contato` (email/telefone)
- `ativo`

---

## Módulo: Templates

| ID | Funcionalidade | Descrição | Status |
|----|----------------|-----------|--------|
| TPL-01 | Criar template | Vincular a tipo de exame | ✅ Implantado |
| TPL-02 | Listar templates | Listar por tipo | ✅ Implantado |
| TPL-03 | Editar template | Alterar dados | ⏳ Pendente |
| TPL-04 | Ativar/Desativar | Toggle ativo | ✅ Implantado |
| TPL-05 | Criar seção | Adicionar seção ao template | ✅ Implantado |
| TPL-06 | Editar seção | Alterar ordem/conteúdo | ⏳ Pendente |
| TPL-07 | Reordenar seções | Mover ordem das seções | ⏳ Pendente |

### Campos Template
- `tipo_exame_id` (FK)
- `nome`
- `descricao_exame`
- `ativo`

### Campos Seção Template
- `template_id` (FK)
- `titulo`
- `conteudo_base` (texto inicial)
- `ordem`
- `obrigatoria` (boolean)
- `permite_fotos` (boolean)

---

## Módulo: Laudos

| ID | Funcionalidade | Descrição | Status |
|----|----------------|-----------|--------|
| LAU-01 | Criar laudo a partir de REP | Gerar laudo do template + muda REP para "Em Andamento" | ⏳ Parcial |
| LAU-02 | Editar laudo | Editar seções e conteúdo | ⏳ Pendente |
| LAU-03 | Visualizar laudo | Modo leitura | ⏳ Pendente |
| LAU-04 | Upload fotos | Adicionar ilustraciones | ⏳ Pendente |
| LAU-05 | Remover foto | Excluir ilustracao | ⏳ Pendente |
| LAU-06 | Salvar versão | Snapshot do laudo | ⏳ Pendente |
| LAU-07 | Finalizar laudo | Marcar como Finalizado + muda REP para "Concluído" | ⏳ Pendente |
| LAU-08 | Exportar PDF | Gerar documento PDF | ⏳ Pendente |
| LAU-09 | Exportar DOCX | Gerar documento Word | ⏳ Pendente |

### Campos Laudo
- `rep_id` (FK única)
- `template_id` (FK)
- `status` (Rascunho, Em Revisão, Finalizado)
- `versao_atual`

### Campos Seção Laudo
- `laudo_id` (FK)
- `secao_template_id` (FK)
- `titulo` (copiado do template)
- `conteudo` (editável)
- `ordem`
- `obrigatoria`
- `permite_fotos`

### Campos Ilustracao
- `secao_laudo_id` (FK)
- `laudo_id` (FK)
- `numero_figura`
- `legenda`
- `dados_imagem` (BLOB)
- `nome_arquivo`
- `ordem`

---

## Módulo: Dashboard

| ID | Funcionalidade | Descrição | Status |
|----|----------------|-----------|--------|
| DASH-01 | Métricas gerais | REPs Pendentes/Em Andamento/Concluídos | ✅ Implantado |
| DASH-02 | Alertas de prazo | REPs com prazo vencendo | ⏳ Pendente |
| DASH-03 | Gráficos | Evolução temporal | ⏳ Pendente |

---

## Módulo: Sistema

| ID | Funcionalidade | Descrição | Status |
|----|----------------|-----------|--------|
| SIS-01 | Backup database | Exportar arquivo .db | ⏳ Pendente |
| SIS-02 | Restore database | Importar arquivo .db | ⏳ Pendente |
| SIS-03 | Histórico de auditoria | Ver logs de operações | ⏳ Pendente |
| SIS-04 | Busca global | Buscar em todas as tabelas | ⏳ Pendente |
| SIS-05 | Controle de prazos | Calcular e alerts | ⏳ Pendente |

---

## Legenda

- ✅ Implantado - Fully implemented
- ✅ Parcial - Partially implemented (bugs/todos)
- ⏳ Pendente - Not yet implemented