# Fluxo do Projeto

O fluxo do projeto **Laudo Pericial** é estruturado para garantir a rastreabilidade desde a solicitação inicial até a entrega do documento final. Abaixo, detalho cada etapa do processo e os estados (status) envolvidos.

---

## 1. Preparação (Configurações Administrativas)
Antes de iniciar um atendimento, o sistema deve estar alimentado com as bases que estruturam o laudo:
*   **Tipos de Exame:** Cadastro do tipo de perícia (ex: *Homicídio, Acidente de Trânsito, Incêndio*). Cada tipo define se é um exame de local (exige coordenadas/horários) ou documental.
*   **Templates de Exame:** Vinculados a um *Tipo de Exame*. O template contém as **Seções** padrão (ex: *Preâmbulo, Histórico, Exames, Conclusão*) que guiarão o perito.
*   **Solicitantes:** Cadastro de delegacias, varas judiciais ou órgãos requisitantes.

---

## 2. Ciclo de Vida da REP (Requisição de Exame Pericial)
A REP é o ponto de partida de qualquer trabalho pericial.

1.  **Criação da REP:** O perito registra os dados da requisição (número da requisição, documento oficial, solicitante e envolvidos).
    *   **Vínculo Obrigatório:** Cada REP deve ser vinculada a um **Tipo de Exame**.
    *   **Status Inicial:** `Pendente`.
2.  **Início do Trabalho:** Ao decidir iniciar a escrita, o perito cria um Laudo a partir daquela REP.

---

## 3. Ciclo de Vida do Laudo
O laudo é o documento técnico onde o perito materializa seus exames.

1.  **Abertura do Laudo:** O sistema solicita a escolha de um **Template** (filtrado pelo tipo de exame da REP).
    *   Nesse momento, as seções do template são **copiadas** para o laudo (tornando-se editáveis sem alterar o modelo original).
    *   **Status do Laudo:** `Em Andamento`.
    *   **Status da REP (Automático):** Muda de `Pendente` para `Em Andamento`.
2.  **Edição e Elaboração:** O perito preenche o conteúdo de cada seção, anexa fotos (ilustrações) e salva versões de segurança.
3.  **Conclusão do Laudo:** Após a revisão, o perito finaliza o documento.
    *   **Status do Laudo:** `Finalizado`.
    *   **Status da REP (Automático):** Muda para `Concluído`.
4.  **Entrega (Opcional):** Após a exportação em PDF e envio ao órgão, o status pode ser alterado para documentar a remessa.
    *   **Status do Laudo:** `Entregue`.

---

## 4. Resumo de Status

### Status da REP (Requisição)
| Status | Significado |
| :--- | :--- |
| **Pendente** | REP cadastrada, mas nenhum laudo foi iniciado para ela. |
| **Em Andamento** | Existe um laudo vinculado que está sendo escrito. |
| **Concluído** | O laudo vinculado foi marcado como finalizado. |

### Status do LAUDO
| Status | Significado |
| :--- | :--- |
| **Em Andamento** | O perito está editando o conteúdo e seções. |
| **Finalizado** | O laudo está pronto para exportação e não deve sofrer alterações maiores. |
| **Entregue** | O documento já foi enviado oficialmente ao solicitante. |

---

## 5. Fluxograma Lógico
1.  **Cadastro:** `Tipo de Exame` ➔ `Template` ➔ `Seções`.
2.  **Operação:** `REP (Pendente)` ➔ `Criar Laudo` ➔ `Vincular Template`.
3.  **Execução:** `Laudo (Em Andamento)` + `REP (Em Andamento)`.
4.  **Fechamento:** `Finalizar Laudo` ➔ `Laudo (Finalizado)` + `REP (Concluído)`.
