# Sistema de Sorteio de Ingressos

Sistema completo de sorteio de ingressos com backend em Python (FastAPI + UV) e frontend em React.

## 🚀 Quick Start com UV

### Instalação Automática

```bash
cd /home/patreze/dev/sorteio
bash install.sh
```

### Iniciar Backend (com UV)

```bash
cd backend
bash start.sh
```

O script vai:
- Instalar UV automaticamente se necessário
- Sincronizar dependências com `uv sync`
- Iniciar o servidor FastAPI

### Iniciar Frontend

```bash
cd frontend
bash start.sh
```

### Acessar Aplicação

Abra o navegador em: **http://localhost:5173**

---

## 📦 Sobre UV

Este projeto usa [UV](https://github.com/astral-sh/uv) - um gerenciador de pacotes Python extremamente rápido escrito em Rust.

**Vantagens:**
- ⚡ 10-100x mais rápido que pip
- 🔒 Lock file automático para reprodutibilidade
- 🎯 Gerenciamento de ambientes virtuais integrado
- 📦 Resolução de dependências mais inteligente

**Comandos UV úteis:**
```bash
uv sync              # Instalar/atualizar dependências
uv add <package>     # Adicionar nova dependência
uv remove <package>  # Remover dependência
uv run <command>     # Executar comando no ambiente virtual
uv pip list          # Listar pacotes instalados
```

---

## 📁 Estrutura do Projeto

```
sorteio/
├── backend/          # API FastAPI com UV
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── database.py
│   ├── pyproject.toml    # Configuração UV
│   ├── uv.lock           # Lock file (gerado automaticamente)
│   └── routers/
└── frontend/         # Interface React
    ├── src/
    ├── package.json
    └── vite.config.js
```

---

## 🔧 Comandos Manuais

### Backend com UV

```bash
cd backend

# Instalar UV (se necessário)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sincronizar dependências
uv sync

# Executar servidor
uv run python main.py
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## 🌐 Endpoints da API

- `POST /api/participants/` - Registrar participante
- `GET /api/participants/` - Listar participantes
- `POST /api/raffles/` - Criar sorteio
- `GET /api/raffles/` - Listar sorteios
- `POST /api/raffles/{id}/assign-tickets` - Atribuir ingressos
- `POST /api/raffles/{id}/draw` - Realizar sorteio

**Documentação interativa:** http://localhost:8000/docs

---

## ✨ Funcionalidades

- ✅ Registro de participantes com validação de email
- ✅ Criação de sorteios
- ✅ Atribuição de ingressos numerados
- ✅ Sorteio aleatório com animação
- ✅ Visualização de vencedores
- ✅ Interface moderna e responsiva
- ✅ Tema escuro com gradientes
- ✅ Animações suaves

---

## 🛠️ Tecnologias

**Backend:**
- FastAPI
- UV (gerenciador de pacotes)
- SQLAlchemy
- SQLite
- Pydantic

**Frontend:**
- React 18
- Vite
- CSS moderno com animações
- Google Fonts (Inter)

---

## 📝 Desenvolvimento

### Adicionar nova dependência no backend

```bash
cd backend
uv add <package-name>
```

Isso vai:
1. Adicionar o pacote ao `pyproject.toml`
2. Atualizar o `uv.lock`
3. Instalar o pacote

### Remover dependência

```bash
uv remove <package-name>
```

---

## 🧪 Testes

### Testar Backend

Acesse: http://localhost:8000/docs

Ou use a página de teste:
```bash
open file://wsl.localhost/Ubuntu/home/patreze/dev/sorteio/test-backend.html
```

### Testar Frontend

1. Registre participantes
2. Crie um sorteio
3. Atribua ingressos
4. Realize o sorteio
5. Veja a animação e o vencedor!

---

## 📄 Licença

MIT
