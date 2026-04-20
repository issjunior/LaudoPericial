# Planejamento: API Jodit para Extração de Conteúdo

## Objetivo

Substituir o parse de HTML atual (em `gerador_pdf.py`) por uma extração via API nativa do Jodit, obtendo estrutura mais robusta e confiável para geração de PDF.

## Motivation

O método atual de geração de PDF:
1. Usa `limpar_html()` para stripping de tags
2. Usa `formatar_texto()` para reinterpretar estilos
3. Frágil a mudanças no formato HTML

A API do Jodit oferece acesso direto à estrutura dos blocos, eliminando a necessidade de parsear HTML.

---

## Fases de Implementação

### Fase 1: Pesquisa e Prototipagem

| Item | Descrição | Status |
|------|-----------|--------|
| 1.1 | Estudar API Jodit: `editor.blocks`, `editor.selection`, `editor.dom` | Pending |
| 1.2 | Identificar métodos para extrair: texto, negrito, itálico, headings, listas, imagens | Pending |
| 1.3 | Criar prototype JS para testar extração via console do navegador | Pending |
| 1.4 | Documentar API endpoints que serão usados | Pending |

### Fase 2: Implementação no Frontend

| Item | Descrição | Status |
|------|-----------|--------|
| 2.1 | Criar componente Streamlit wrapper para Jodit com acesso à API | Pending |
| 2.2 | Implementar listener para extrair estrutura em tempo real | Pending |
| 2.3 | Criar função JS de conversão: Editor → JSON estrutura | Pending |
| 2.4 | Adicionar campo `conteudo_estruturado` no banco (JSON) | Pending |

### Fase 3: Backend e Integração

| Item | Descrição | Status |
|------|-----------|--------|
| 3.1 | Adaptar `gerador_pdf.py` para consumir JSON estruturado | Pending |
| 3.2 | Criar novo módulo: `parser_jodit_json.py` | Pending |
| 3.3 | Implementar mapeamento JSON → ReportLab flowables | Pending |
| 3.4 | Testes de integração Editor → PDF | Pending |

### Fase 4: Migração e homolação

| Item | Descrição | Status |
|------|-----------|--------|
| 4.1 | Migar dados existentes (HTML → JSON) | Pending |
| 4.2 | Homologação com usuários | Pending |
| 4.3 | Toggle para modo híbrido (HTML/JSON) durante transição | Pending |
| 4.4 | Remover código antigo de parse HTML | Pending |

---

## Estrutura JSON Proposta

```json
{
  "versao": 1,
  "blocos": [
    {
      "tipo": "heading",
      "nivel": 2,
      "texto": "Título da Seção",
      "estilos": ["bold"]
    },
    {
      "tipo": "paragrafo",
      "texto": "Conteúdo do parágrafo...",
      "estilos": []
    },
    {
      "tipo": "imagem",
      "src": "base64:...",
      "alt": "Descrição",
      "largura": 400
    }
  ]
}
```

### Tipos de bloco suportados

| Tipo | Descrição | Campos extras |
|------|-----------|---------------|
| `heading` | Título (h1-h6) | `nivel` (1-6) |
| `paragrafo` | Parágrafo normal | - |
| `lista_ordenada` | Lista com números | `itens` |
| `lista_nao_ordenada` | Lista com bullets | `itens` |
| `imagem` | Imagem inline | `src`, `alt`, `largura`, `altura` |
| `citacao` | Bloco de citação | - |

### Estilosinline

| Estilo | Descrição |
|--------|-----------|
| `bold` | Negrito |
| `italic` | Itálico |
| `underline` | Sublinhado |

---

## Arquivos a Criar/Modificar

### Novos arquivos

| Arquivo | Descrição |
|---------|-----------|
| `components/editor_jodit_v2.py` | Editor com API integrada |
| `services/parser_estructura.py` | Parser JSON → ReportLab |
| `services/conversor_jodit_json.js` | Script JS para extração |
| `migrations/add_coluna_estrutura.py` | Migration banco |

### Arquivos a modificar

| Arquivo | Modificação |
|---------|-------------|
| `database/models.py` | Adicionar campo `conteudo_estrutura` |
| `services/gerador_pdf.py` | Usar novo parser |
| `pages/editor_laudo.py` | Integrar novo editor |

---

## Critérios de Aceitação

- [ ] PDF gerado mantém mesma formatação do editor
- [ ] Negrito, itálico, títulos preservados
- [ ] Imagens renderizadas no PDF
- [ ] Listas rendering corretas
- [ ] Dados migrados sem perda
- [ ] Sem regressões no fluxo atual

---

## Riscos e Mitigações

| Risco | Mitigação |
|-------|-----------|
| API Jodit mudar entre versões | Fixar versão usada no requirements |
| Dados legados não migram corretamente | Criar script de migração com validação |
| Performance degrade | Testes de carga antes de homologar |

---

## Referências

- Jodit GitHub: https://github.com/xdan/jodit
- Jodit Docs: https://xdsoft.net/jodit/docs/
- API Reference: https://xdsoft.net/jodit/docs/api/