# Placeholders para Composição do Laudo

Este documento lista todos os placeholders disponíveis para usar na redação do Laudo Pericial.
Os valores são substituídos automaticamente na geração do PDF.

## Como Usar

Copiar o placeholder desejado e colar no texto da seção do Template de Laudo.
Exemplo: "No dia {{data_solicitacao}}, através do {{tipo_solicitacao}} nº {{numero_documento}}..."

---

## 1. Dados da REP (Requisição de Exame Pericial)

| Variável | Placeholder | Descrição | Fonte |
|----------|----------|-----------|-------|
| `numero_rep` | `{{numero_rep}}` | Número da REP | nova_rep.py |
| `data_solicitacao` | `{{data_solicitacao}}` | Data da solicitação (YYYY-MM-DD) | nova_rep.py |
| `tipo_exame` | `{{tipo_exame}}` | Nome do tipo de exame | nova_rep.py |
| `nome_envolvido` | `{{nome_envolvido}}` | Nome do envolvido/vítima | nova_rep.py |
| `local_fato` | `{{local_fato}}` | Descrição do local do fato | nova_rep.py |
| `horario_acionamento` | `{{horario_acionamento}}` | Horário de acionamento (HH:MM) | nova_rep.py |
| `horario_chegada` | `{{horario_chegada}}` | Horário de chegada ao local (HH:MM) | nova_rep.py |
| `horario_saida` | `{{horario_saida}}` | Horário de saída do local (HH:MM) | nova_rep.py |
| `latitude` | `{{latitude}}` | Latitude do local | nova_rep.py |
| `longitude` | `{{longitude}}` | Longitude do local | nova_rep.py |

---

## 2. Dados do Solicitante

| Variável | Placeholder | Descrição | Fonte |
|----------|----------|-----------|-------|
| `solicitante` | `{{solicitante}}` | Nome do órgão solicitante | nova_rep.py |
| `solicitante_orgao` | `{{solicitante_orgao}}` | Órgão do solicitante | nova_rep.py |
| `nome_autoridade` | `{{nome_autoridade}}` | Nome da autoridade solicitante | nova_rep.py |

---

## 3. Detalhes da Solicitação

| Variável | Placeholder | Descrição | Fonte |
|----------|----------|-----------|-------|
| `tipo_solicitacao` | `{{tipo_solicitacao}}` | Tipo de documento (BO, Ofício, BO PM, BO PC, CECOMP, Outro) | nova_rep.py |
| `numero_documento` | `{{numero_documento}}` | Número do documento | nova_rep.py |
| `data_documento` | `{{data_documento}}` | Data do documento (YYYY-MM-DD) | nova_rep.py |

---

## 4. Dados do Perito (Usuário)

| Variável | Placeholder | Descrição | Fonte |
|----------|----------|-----------|-------|
| `perito_nome` | `{{perito_nome}}` | Nome do perito responsável | Cadastro de usuários |
| `perito_matricula` | `{{perito_matricula}}` | Matrícula do perito | Cadastro de usuários |
| `perito_cargo` | `{{perito_cargo}}` | Cargo do perito | Cadastro de usuários |
| `perito_lotacao` | `{{perito_lotacao}}` | Lotação do perito | Cadastro de usuários |

---

## 5. Dados do Laudo

| Variável | Placeholder | Descrição | Fonte |
|----------|----------|-----------|-------|
| `laudo_status` | `{{laudo_status}}` | Status do laudo (Rascunho, Em Revisão, Finalizado) | editor_laudo.py |
| `laudo_versao` | `{{laudo_versao}}` | Versão atual do laudo | editor_laudo.py |
| `laudo_data_emissao` | `{{laudo_data_emissao}}` | Data de emissão do laudo | gerador_pdf.py |

---

## 6. Dados do Template

| Variável | Placeholder | Descrição | Fonte |
|----------|----------|-----------|-------|
| `template_descricao` | `{{template_descricao}}` | Descrição do exame do template | gerenciar_templates.py |

---

## Exemplo de Uso

No preâmbulo do Template:

> No dia {{data_solicitacao}}, através do {{tipo_solicitacao}} nº {{numero_documento}}, الصادر pela {{autoridade}} do {{solicitante_orgao}}, fui requisitado para realizar exame pericial do tipo {{tipo_exame}}, tendo como finalidade apurar os fatos relativos ao occurrences envolvendo {{nome_envolvido}}.

Resultado no PDF:

> No dia 2024-12-25, através do BO nº 12345/2024, emitido pela Delegado João da Silva do Delegación de Homicídios, fui requisitado para realizar exame pericial do tipo Necropsia, tendo como finalidade apurar os fatos relativos ao occurrences envolvendo João da Silva.

---

## Implementação

Os placeholders são substituídos na função `substituir_placeholders()` em:
- `services/gerador_pdf.py`

Os dados são buscados em:
- `services/rep_service.py` (dados da REP)
- `services/laudo_service.py` (dados do laudo)
- `database/db.py` (dados do usuário/perito)