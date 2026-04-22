# Playwright/Chromium - Deploy

## Instalação no Servidor

São dependentes entre si:
editor_laudo.py → gerador_pdf_playwright.py → html_builder.py → playwright_client.py → chromium/

### 1. Criar ambiente virtual

```bash
python -m venv venv
venv\Scripts\pip install -r requirements.txt
```

### 2. Instalar Playwright

```bash
venv\Scripts\pip install playwright
venv\Scripts\playwright install chromium
```

### 3. Copiar Chromium para o projeto (opcional)

Para não depender do Playwright driver no deploy:

```bash
# Copiar do diretório do Playwright para o projeto
xcopy "%LOCALAPPDATA%\ms-playwright\chromium-1208\chrome-win64\*" "chromium\" /E /I /Y
```

O código em `services/playwright_client.py` já procura nesta ordem:
1. `chromium/chrome.exe` (projeto)
2. `%LOCALAPPDATA%\ms-playwright\chromium-1208\chrome-win64\chrome.exe`
3. Chrome do sistema

## Configuração Deploy

### Variáveis de ambiente

```bash
# Opcional: forçar caminho do Chromium
set CHROMIUM_PATH=C:\caminho\para\chromium\chrome.exe
```

### Permissões

O Chromium precisa de permissão de execução. Em servidores Windows Server, pode ser necessário:
- Adicionar usuário do app pool à pasta do Chromium
- Configurar perfil de usuário para conta de serviço

## Troubleshooting

### Erro: NotImplementedError

Python 3.13 + asyncio no Windows. Solução: usar subprocess (já implementado em `playwright_client.py`).

### PDF não gera

Verificar:
- Arquivo `chrome.exe` existe
- Permissões de leitura/escrita na pasta temp
- Firewall não bloqueando Chrome

### Timeout

Aumentar timeout em `playwright_client.py`:

```python
subprocess.run(cmd, capture_output=True, timeout=60)  # 60 segundos
```