Este documento detalha o roadmap de migração do sistema atual para a nova arquitetura desktop baseada em Electron. O planejamento é organizado em Sprints focadas em entregas funcionais incrementais. As Sprints estão ordenadas por importância estrutural e complexidade de negócio.

Ciclo de Vida e Estados (Regras de Negócio)
Durante o desenvolvimento e migração, o ciclo de vida base será governado pelos seguintes status:

REP (Requisição de Exame Pericial): Pendente, Em Andamento, Concluído
Laudo: Em andamento, Concluído, Entregue
Obs.: O laudo já "nasce" com status de Em andamento ao ser vinculado a REP.

Stack Tecnológico Definido
Framework Desktop: Electron + Vite + TypeScript
Frontend: React com TypeScript
Backend: Node.js (Electron Main Process)
Banco de Dados: SQLite (armazenamento local)
Editor de Texto: TinyMCE (Rich Text Editor)
Exportação: electron-pdf (PDF) e docx (DOCX)
Segurança: Criptografia de dados sensíveis, validação de entrada, proteção contra injeção SQL
Logs e Auditoria: Rotação de arquivos com limite de 5 MB
Sincronização Futura: Integração com Google Drive e OneDrive (versão posterior)
Observações Importantes
Reutilização de Código Python
Analise o projeto Python/Streamlit existente para identificar lógica de negócio complexa que possa ser reutilizada. Considere manter componentes críticos em Python e integrá-los via child_process do Electron quando apropriado, em vez de reescrever tudo em TypeScript/JavaScript. Isso reduz riscos e acelera a migração. Exemplos: processamento de dados, cálculos complexos, validações de negócio.

Estrutura de Diretórios Recomendada
projeto/
├── src/
│   ├── main/                    # Electron Main Process (Backend)
│   │   ├── index.ts
│   │   ├── database/            # SQLite e operações de BD
│   │   ├── ipc/                 # Handlers IPC
│   │   ├── security/            # Criptografia e validação
│   │   ├── services/            # Lógica de negócio
│   │   └── utils/
│   ├── preload/                 # Preload scripts (Bridge IPC)
│   │   └── index.ts
│   ├── renderer/                # React Frontend
│   │   ├── App.tsx
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   └── styles/
│   └── shared/                  # Tipos e constantes compartilhadas
├── public/
│   ├── images/                  # Imagens dos laudos (armazenadas localmente)
│   └── assets/
├── python/                      # Scripts Python reutilizáveis (opcional)
│   └── services/
├── vite.config.ts
├── electron-builder.yml
└── package.json
Em caso de dúvidas
Consultar o projeto antigo (Python + Streamlit) para entender as regras de negócio e lógica reutilizável.
Consultar servidores MCPs instalados como por exemplo: context7.
Sprint 0: Fundação, Segurança e Infraestrutura Crítica
Objetivo: Estabelecer a infraestrutura de segurança, validação e recuperação antes de iniciar o desenvolvimento funcional.

[ ] Inicializar projeto Electron + Vite + TypeScript com template recomendado.
[ ] Definir a estrutura de diretórios conforme proposto acima (main/, preload/, renderer/, shared/).
[ ] Configurar TypeScript com strict: true e linting (ESLint + Prettier).
[ ] Implementar criptografia de dados sensíveis (bcrypt para senhas, crypto para dados do perito).
[ ] Estabelecer camada de validação de entrada (sanitização de strings, validação de tipos).
[ ] Implementar proteção contra injeção SQL usando prepared statements e ORM (Prisma ou TypeORM recomendado).
[ ] Configurar a conexão nativa com SQLite no processo Main com suporte a migrations.
[ ] Criar sistema de rotação de logs com limite de 5 MB por arquivo (winston ou pino recomendado).
[ ] Implementar página de Tratamento de Erros e Recuperação (exibir erro, opção de restaurar BD, contato com suporte).
[ ] Estabelecer a ponte IPC de comunicação (Preload) com tipagem TypeScript para funções básicas (ex: ping, logs).
[ ] Criar estrutura base de roteamento e layout padrão (Menu Lateral/Topo) no Frontend React.
[ ] Documentar decisões arquiteturais (ADR) e guia de setup para desenvolvedores.
Documentação do Usuário (Sprint 0): Criar guia técnico interno sobre a arquitetura de segurança, validação de dados e recuperação de erros. Este guia será expandido ao final de cada sprint com funcionalidades específicas.

Sprint 1: Fundação e Arquitetura Base
Objetivo: Estabelecer a infraestrutura do novo aplicativo Electron, garantindo a comunicação correta entre as janelas e o banco de dados com segurança.

[ ] Validar template Electron + Vite + TypeScript inicializado na Sprint 0.
[ ] Configurar o banco de dados SQLite com migrations automáticas (Prisma ou similar).
[ ] Implementar schema inicial do banco (tabelas: users, reps, laudos, solicitantes, tipos_exame, templates_exame, placeholders, logs_auditoria).
[ ] Estabelecer padrão de IPC tipado com TypeScript (definir interfaces para requisições e respostas).
[ ] Criar handlers IPC básicos no Main Process (ping, health check, logs).
[ ] Implementar sistema de validação de entrada centralizado para todos os IPC calls.
[ ] Configurar proteção contra injeção SQL com prepared statements em todas as queries.
[ ] Criar página de erro com opção de recuperação (restaurar backup, limpar cache, reiniciar app).
[ ] Testes unitários básicos para funções de validação e segurança.
Documentação do Usuário (Sprint 1): Manual técnico sobre a inicialização do aplicativo, estrutura de segurança implementada e como reportar erros.

Sprint 2: Perfil do Perito e Cadastros Estruturais de Apoio
Objetivo: Desenvolver os cadastros base essenciais e o perfil local do perito, validando o fluxo de gravação no banco.

[ ] Implementar tabela SQLite para armazenar Perfil do Perito (Nome, Cargo, Matrícula, Lotação, Assinatura Digital - opcional).
[ ] Criar tela de configuração/edição do Perfil do Perito com validação de entrada.
[ ] Criptografar dados sensíveis do perfil antes de armazenar no SQLite.
[ ] Implementar comandos IPC e UI para o CRUD de "Solicitantes" (Órgãos, Varas, Delegacias).
[ ] Implementar comandos IPC e UI para o gerenciamento de "Modelos de Cabeçalho" dos laudos (armazenar em SQLite).
[ ] Implementar comandos IPC para listagem, criação e edição de "Tipos de Exame".
[ ] Desenvolver formulário de cadastro/edição de "Tipos de Exame" com validação.
[ ] Implementar comandos IPC para o CRUD de "Templates de Exame" (relacionados ao Tipo).
[ ] Desenvolver a interface (UI) para gerenciamento e edição de Templates de Exames (e suas respectivas seções).
[ ] Testes de integração para fluxos de CRUD.
Análise de Reutilização Python: Verificar se o projeto Python possui lógica de validação de dados ou processamento de templates que possa ser reutilizada via child_process. Se houver, documentar a interface de integração.

Documentação do Usuário (Sprint 2): Manual do usuário cobrindo: como configurar o perfil do perito, como criar e gerenciar solicitantes, tipos de exame e templates de exame. Inclua capturas de tela e fluxos passo a passo.

Sprint 3: Gestão de Requisições (REP)
Objetivo: Permitir o registro, a listagem e o controle do ciclo de vida das Requisições de Exame Pericial com performance otimizada.

[ ] Implementar consultas e operações IPC para gerenciar as REPs no SQLite com índices para performance.
[ ] Construir o painel principal (Dashboard/Listagem) de REPs com ordenação, filtros (por status/data) e paginação.
[ ] Implementar virtual scrolling para listas grandes (se houver muitas REPs).
[ ] Criar o formulário de Nova REP, conectando aos catálogos de "Tipos de Exame" e "Solicitantes".
[ ] Estabelecer a mecânica de alteração de Status de uma REP (ex: Pendente → Em Andamento → Concluído).
[ ] Registrar todas as alterações de status no Histórico/Auditoria (com timestamp e usuário).
[ ] Implementar busca rápida por número de REP ou solicitante.
[ ] Testes de performance para listagem com 1000+ REPs.
Documentação do Usuário (Sprint 3): Guia completo sobre o fluxo de requisições: como criar uma nova REP, como alterar status, como filtrar e buscar REPs, e como visualizar o histórico de alterações.

Sprint 4: Núcleo do Sistema - Edição de Laudos
Objetivo: O coração do aplicativo. Uma interface robusta para digitação e formatação do texto final com suporte a imagens locais.

[ ] Integrar TinyMCE no React/Frontend com configuração customizada (fonte, tamanho, cores, tabelas, listas).
[ ] Criar a tela principal de "Edição de Laudo", obrigatoriamente vinculada a uma REP ativa.
[ ] Implementar carregamento do texto base ("Template de Exame") quando um Laudo for iniciado.
[ ] Implementar sistema de salvamento contínuo (Auto-save) do documento no SQLite via IPC (a cada 30 segundos ou após mudança).
[ ] Implementar sistema de "Snapshots" para guardar as 3 últimas versões do laudo (Backup de desfazer) no SQLite.
[ ] Suporte à inserção de Ilustrações/Imagens diretamente nas seções do laudo:
[ ] Armazenar apenas o caminho local das imagens (ex: public/images/laudo_123_img_001.jpg).
[ ] Criar pasta de imagens por REP/Laudo para organização.
[ ] Incluir imagens no backup/restauração (compactar pasta de imagens junto com BD).
[ ] Renderizar o "Modelo de Cabeçalho" configurado acima do laudo de forma visual.
[ ] Implementar painel de propriedades do Laudo (Status: Em andamento / Concluído / Entregue).
[ ] Indicador visual de "Documento Modificado" (asterisco no título).
[ ] Testes de performance para edição com documentos grandes (10+ MB de texto).
Documentação do Usuário (Sprint 4): Manual detalhado sobre a edição de laudos: como usar o editor TinyMCE, como inserir imagens, como usar templates, como o auto-save funciona, e como acessar versões anteriores do documento.

Sprint 5: Motor de Placeholders e Dinamismo
Objetivo: Automatizar as informações repetitivas dos laudos usando variáveis substituíveis armazenadas no SQLite.

[ ] Mapear todos os placeholders do sistema relacionados aos dados da REP e do Perito (ex: [NUMERO_REP], [PERITO_NOME], [DATA_HOJE], [SOLICITANTE]).
[ ] Criar tabela SQLite para armazenar Placeholders Customizados (nome, valor, descrição, data_criacao).
[ ] Implementar página de "Gerenciamento de Placeholders Customizados" para termos criados pelo próprio usuário.
[ ] Construir o interpretador (parser) para substituir [NOME_DO_PLACEHOLDER] pelo valor real no momento da exportação ou visualização.
[ ] Integrar um painel lateral ou menu suspenso dentro do Editor de Laudos para inserção fácil de placeholders no texto.
[ ] Suportar placeholders com formatação condicional (ex: [PERITO_NOME_MAIUSCULA]).
[ ] Testes para garantir que placeholders não quebrem a formatação do TinyMCE.
Análise de Reutilização Python: Verificar se o projeto Python possui um motor de placeholders que possa ser reutilizado ou adaptado.

Documentação do Usuário (Sprint 5): Guia sobre como usar placeholders: lista completa de placeholders disponíveis, como criar placeholders customizados, como inseri-los no laudo, e exemplos de uso.

Sprint 6: Assistência Inteligente (IA) - Opcional e Configurável
Objetivo: Prover suporte à escrita através de modelos de linguagem (LLMs) via API, com fallback gracioso se nenhuma API estiver configurada.

[ ] Implementar tela de configurações para o usuário inserir suas próprias chaves de API (Groq e Gemini) de forma segura (criptografar no SQLite).
[ ] Se nenhuma API for configurada, o sistema funciona normalmente sem a aba de IA (não exibir opção).
[ ] Integrar a comunicação com a API da Groq (reutilizar implementação do projeto Python se disponível via child_process).
[ ] Integrar a comunicação com a API do Gemini (reutilizar implementação do projeto Python se disponível via child_process).
[ ] Desenvolver aba/painel de "Assistente IA" pareado ao Editor de Laudos (visível apenas se API configurada).
[ ] Implementar botões rápidos de ação: "Corrigir Gramática", "Melhorar Texto", "Resumir", "Expandir".
[ ] Criar funcionalidade de aplicar o texto gerado pela IA diretamente no cursor do editor TinyMCE.
[ ] Implementar indicador de "Processando IA" com opção de cancelar.
[ ] Tratamento de erros para falhas de API (timeout, chave inválida, etc.).
[ ] Testes com diferentes modelos de IA.
Análise de Reutilização Python: O projeto Python provavelmente possui integração com Groq e Gemini. Considere manter esses serviços em Python e chamar via child_process para reutilizar lógica testada.

Documentação do Usuário (Sprint 6): Guia sobre como configurar chaves de API, como usar o assistente IA, quais ações estão disponíveis, e como a IA pode ajudar na escrita de laudos. Incluir dicas de prompts eficazes.

Sprint 7: Exportação e Documento Final
Objetivo: Finalizar o fluxo da perícia permitindo gerar o produto consumível (PDF, Word e ODT) com imagens locais incluídas.

[ ] Implementar geração nativa de PDF usando electron-pdf, mantendo formatação, estilos CSS e as imagens originais do Laudo.
[ ] Garantir que imagens locais (armazenadas em public/images/) sejam incluídas no PDF final.
[ ] Integrar biblioteca docx para conversão de HTML/JSON para DOCX (Microsoft Word).
[ ] Garantir que imagens locais sejam incluídas no arquivo DOCX.
[ ] Integrar biblioteca para conversão de HTML/JSON para ODT (Open Document Text).
[ ] Garantir que imagens locais sejam incluídas no arquivo ODT.
[ ] Construir interface de pré-visualização (Print Preview) antes da exportação.
[ ] Implementar botão de exportação final na tela do Laudo com opções (PDF, DOCX, ODT, múltiplos).
[ ] Adicionar metadados ao PDF (Título, Autor - Perito, Data de Criação).
[ ] Testes de exportação com documentos contendo múltiplas imagens e formatações complexas em todos os formatos.
Documentação do Usuário (Sprint 7): Manual sobre como exportar laudos em PDF, Word e ODT, como visualizar antes de exportar, e como as imagens são incluídas nos documentos finais em todos os formatos suportados.

Sprint 8: Histórico, Auditoria e Backup/Restauração
Objetivo: Implementar rastreamento completo de eventos e funcionalidade robusta de backup/restauração com suporte a imagens.

[ ] Desenvolver o painel de Histórico / Log de Auditoria, capaz de traçar cronologicamente todos os eventos desde a criação da REP até a conclusão ou entrega do Laudo.
[ ] O Histórico deve registrar alterações críticas (ex: alterações de status, modificações de conteúdo, alterações de lacres de entrada e saída).
[ ] O Histórico deve registrar eventos de sistema (Abertura de Laudo, Salvamento, Exportação, Login - se houver, Logout, fechamentos abruptos do aplicativo).
[ ] Implementar rotação de logs com limite de 5 MB por arquivo (winston ou pino). Arquivos antigos são compactados e arquivados.
[ ] Retenção mínima: últimos 06 meses de logs (considerar compactação para economizar espaço).
[ ] Implementar ferramenta de Backup/Restauração de banco de dados:
[ ] Exportar: Compactar BD SQLite + pasta de imagens (public/images/) em arquivo ZIP.
[ ] Importar: Descompactar ZIP, validar integridade do BD, restaurar imagens na pasta correta.
[ ] Opção de backup manual (botão no painel de configurações).
[ ] Opção de backup automático (diário, semanal - configurável).
[ ] Preparar infraestrutura para sincronização futura com nuvem (Google Drive, OneDrive):
[ ] Criar interface de configuração de credenciais (não implementar integração ainda).
[ ] Documentar arquitetura para versão futura.
[ ] Testes de backup/restauração com diferentes tamanhos de BD e quantidade de imagens.
Documentação do Usuário (Sprint 8): Guia completo sobre o histórico de auditoria, como visualizar logs, como fazer backup manual, como restaurar de um backup, e como será a sincronização com nuvem (versão futura).

Sprint 9: Otimização de Performance e Experiência do Usuário
Objetivo: Refinar a aplicação para máxima performance e usabilidade, garantindo uma experiência fluida mesmo com grandes volumes de dados.

[ ] Análise de Performance: Perfil da aplicação para identificar gargalos (renderização, queries SQL, IPC calls).
[ ] Otimizar queries SQLite com índices apropriados (REP, Laudo, Placeholders).
[ ] Implementar lazy loading para componentes pesados (editor TinyMCE, pré-visualização de PDF).
[ ] Otimizar renderização React com React.memo, useMemo, useCallback onde apropriado.
[ ] Implementar debouncing para auto-save (evitar salvamentos excessivos).
[ ] Otimizar carregamento de imagens (lazy load, compressão).
[ ] Refinar as interfaces visuais:
[ ] Hover states em botões e links.
[ ] Loading spinners em operações assíncronas.
[ ] Modais de confirmação para ações críticas (deletar REP, descartar alterações).
[ ] Animações fluídas (transições de página, fade-ins).
[ ] Feedback visual para sucesso/erro de operações.
[ ] Implementar atalhos de teclado comuns (Ctrl+S para salvar, Ctrl+Z para desfazer, etc.).
[ ] Testes de performance com 5000+ REPs e 1000+ Laudos no BD.
[ ] Testes de usabilidade com usuários reais (se possível).
Documentação do Usuário (Sprint 9): Guia de atalhos de teclado, dicas de performance (como manter o app rápido), e feedback sobre melhorias de UX implementadas.

Sprint 10: Utilidades, Polimento Final e Distribuição
Objetivo: Preparar a aplicação para ser entregue aos usuários finais com máxima qualidade e documentação completa.

[ ] Refinar todas as interfaces visuais com design system consistente (cores, tipografia, espaçamento).
[ ] Implementar tema claro/escuro (opcional, mas recomendado).
[ ] Criar página "Sobre" com informações da versão, licença, contato de suporte.
[ ] Implementar verificação de atualizações (electron-updater).
[ ] Configurar as diretrizes de empacotamento no electron-builder.yml:
[ ] Ícone da aplicação.
[ ] Informações de produto (nome, versão, descrição).
[ ] Certificação de código (se aplicável).
[ ] Realizar compilação (Build) final gerando o instalador .exe (Setup) para Windows.
[ ] Gerar também versão portável (.exe standalone) se desejado.
[ ] Criar guia de instalação e desinstalação.
[ ] Testes finais de instalação em máquina limpa (sem dependências pré-instaladas).
[ ] Documentação técnica completa (README, guia de desenvolvimento, guia de contribuição).
Documentação do Usuário (Sprint 10): Manual completo do usuário cobrindo todas as funcionalidades, guia de instalação, guia de resolução de problemas comuns, e contato para suporte. Incluir vídeos tutoriais se possível.

Documentação Consolidada por Sprint
Ao final de cada sprint, será gerado um Manual de Usuário Incremental que documenta:

Funcionalidades implementadas naquela sprint.
Fluxos de procedimento passo a passo com capturas de tela.
Dicas e boas práticas.
Troubleshooting para problemas comuns.
Estes manuais serão consolidados em um Manual Completo do Usuário ao final da Sprint 10.