# 🎭 Playwright Instagram Scraper

## O que mudou?

Substituímos o **Instaloader** (API) por **Playwright** (navegador real).

## Por que Playwright?

- ✅ **Controla um navegador Chrome real**
- ✅ **Instagram não consegue detectar como bot**
- ✅ **Funciona 100% como se você estivesse navegando**
- ✅ **Bypassa todas as proteções anti-bot**

## Como instalar

```bash
cd backend

# Instalar dependências
uv sync

# Instalar navegadores do Playwright
uv run playwright install chromium
```

## Como funciona

1. **Abre um navegador Chrome real** (você pode ver ele funcionando!)
2. **Navega para o post do Instagram**
3. **Rola a página** para carregar todos os comentários
4. **Extrai os dados** como um humano faria
5. **Fecha o navegador**

## Configuração

Por padrão, o navegador abre **visível** (`headless=False`) para você ver o que está acontecendo.

Para rodar invisível (mais rápido), edite `playwright_scraper.py`:
```python
await self.init_browser(headless=True)  # Invisível
```

## Testando

```bash
cd backend
uv run python main.py
```

Depois, no frontend, tente coletar comentários. Você verá o navegador Chrome abrir automaticamente!

## Vantagens

- ✅ **100% indetectável** - É um navegador real
- ✅ **Sem rate limits** - Instagram não bloqueia
- ✅ **Sem checkpoints** - Funciona sem login
- ✅ **Coleta TODOS os comentários** - Rola a página automaticamente

## Desvantagens

- ⚠️ **Mais lento** - Precisa abrir navegador (5-10 segundos)
- ⚠️ **Usa mais memória** - Chrome consome RAM
- ⚠️ **Precisa instalar navegadores** - `playwright install`

## Próximos passos

1. Instale os navegadores: `uv run playwright install chromium`
2. Reinicie o backend
3. Teste coletar comentários!
