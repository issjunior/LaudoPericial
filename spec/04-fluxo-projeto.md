# Fluxo do Projeto

O fluxo do **Laudo Pericial** foi descrito abaixo conforme o comportamento atual implementado no sistema (status e transições reais).

---

## 1. Preparação (Configurações Administrativas)
Antes da operação, o sistema depende destes cadastros:
- **Tipos de Exame**: classificam o tipo de perícia.
- **Templates de Exame**: vinculados a um tipo de exame; definem seções padrão do laudo.
- **Solicitantes**: órgãos requisitantes.

---

## 2. Ciclo de Vida da REP (Requisição de Exame Pericial)
A REP é o ponto de entrada do processo.

1. **Criação da REP**
   - A REP é criada com status inicial **`Pendente`**.
   - Atualmente, o tipo de exame pode estar ausente no momento da criação.

2. **Ajustes na REP**
   - A REP pode ser editada antes do laudo.
   - Em cenários específicos de edição, o status pode ser ajustado para **`Em Andamento`**.

3. **Início do trabalho pericial**
   - Quando um laudo é criado para a REP, o status da REP é atualizado para **`Em Andamento`**.

---

## 3. Ciclo de Vida do Laudo
O laudo é criado sempre com template definido.

1. **Abertura do Laudo**
   - O usuário escolhe um **Template** (associado ao tipo de exame da REP).
   - As seções do template são copiadas para o laudo.
   - O laudo nasce em **`Em Andamento`**.
   - A REP vinculada passa para **`Em Andamento`**.

2. **Edição e elaboração**
   - O perito preenche e salva seções.
   - O sistema mantém snapshots de versão.

3. **Finalização**
   - O laudo pode ser marcado como **`Finalizado`**.

4. **Entrega**
   - O laudo pode ser marcado como **`Entregue`**.

---

## 4. Resumo de Status

### Status da REP
| Status | Significado |
| :--- | :--- |
| **Pendente** | REP cadastrada, sem laudo iniciado. |
| **Em Andamento** | REP com trabalho pericial em curso (normalmente após criação do laudo). |
| **Concluído** | Status final da REP disponível no sistema. |

### Status do Laudo
| Status | Significado |
| :--- | :--- |
| **Em Andamento** | Laudo em edição. |
| **Finalizado** | Laudo encerrado tecnicamente. |
| **Entregue** | Laudo marcado como entregue. |

---

## 5. Fluxo Lógico Atual
1. **Cadastro base**: `Tipo de Exame` -> `Template` -> `Seções`.
2. **Operação**: `REP (Pendente)` -> `Criar Laudo (com Template)`.
3. **Execução**: `Laudo (Em Andamento)` + `REP (Em Andamento)`.
4. **Fechamento do laudo**: `Laudo (Em Andamento)` -> `Laudo (Finalizado)`.
5. **Entrega**: `Laudo (Finalizado ou Em Andamento, conforme regra atual de serviço)` -> `Laudo (Entregue)`.

---

## 6. Observações de Comportamento Atual
- O nome oficial de status final do **laudo** no sistema é **`Finalizado`** (não `Concluído`).
- O nome oficial de status final da **REP** no sistema é **`Concluído`**.
- A sincronização automática **REP -> Concluído** depende do caminho usado para finalizar laudo. No fluxo atual da página de edição, a mudança principal ocorre no status do laudo.
