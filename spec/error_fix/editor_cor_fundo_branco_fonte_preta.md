# Correção: Editor Jodit com fundo branco e fonte preta

## Problema
O editor de texto (Jodit) nas páginas do sistema estava herdando o tema escuro do Streamlit ou outras configurações, resultando em:
- Fundo escuro dificultando a visualização
- Cor da fonte clara (branca/cinza) prejudicando a legibilidade
- Contraste inadequado para trabalho prolongado

## Solução
Utilizar os parâmetros nativos de configuração do Jodit para forçar cores específicas.

### Configuração correta
```python
config = {
    'minHeight': 250,
    'height': 300,
    'theme': 'default',
    'defaultLineHeight': 1,
    'allowResizeY': True,
    'allowResizeX': True,
    'enableDragAndDropFileToEditor': False,
    'style': {
        'color': '#000000',      # Força o texto a ser preto
        'background': '#ffffff'  # Força o fundo a ser branco
    }
}
```

### Arquivos afetados
1. **pages/editor_laudo.py** (linhas 51-54)
   - Já tinha a configuração implementada
   - Configuração global `JODIT_CONFIG`

2. **pages/cabecalho.py** (linhas 100-103)
   - Implementada em 29/04/2026
   - Configuração específica do editor de cabeçalho

## Por que não usar CSS externo?
1. **Menos confiável**: O CSS pode ser sobrescrito por estilos do Jodit ou do Streamlit
2. **Performance**: Configuração nativa é mais eficiente
3. **Manutenção**: Parâmetros do Jodit são mais estáveis que seletores CSS

## Fallback para textarea padrão
Quando o Jodit não está disponível, o sistema usa `st.text_area()`. Para também forçar cores:
```python
# Adicionar estilos CSS para o textarea padrão
st.markdown("""
<style>
.stTextArea textarea {
    background-color: white !important;
    color: black !important;
}
</style>
""", unsafe_allow_html=True)
```

## Validação
- ✅ Fundo sempre branco (`#ffffff`)
- ✅ Fonte sempre preta (`#000000`)
- ✅ Boa legibilidade e contraste
- ✅ Compatível com qualquer tema do Streamlit

## Referências
- Documentação do Jodit: opção `style` no construtor
- Exemplo no código: `pages/editor_laudo.py` (configuração `JODIT_CONFIG`)

---
