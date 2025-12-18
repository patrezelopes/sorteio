#!/bin/bash

echo "🚀 Instalação Rápida com UV - Sistema de Sorteio"
echo "=================================================="
echo ""

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Diretório base
BASE_DIR="/home/patreze/dev/sorteio"

# Verificar se uv está instalado
echo -e "${YELLOW}[1/3] Verificando UV...${NC}"
if command -v uv &> /dev/null; then
    echo -e "${GREEN}✓ UV encontrado: $(uv --version)${NC}"
else
    echo -e "${YELLOW}⚠️  UV não encontrado. Instalando...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
    echo -e "${GREEN}✓ UV instalado com sucesso!${NC}"
fi

# Verificar Node.js
echo -e "${YELLOW}[2/3] Verificando Node.js...${NC}"
if command -v node &> /dev/null; then
    echo -e "${GREEN}✓ Node.js encontrado: $(node --version)${NC}"
else
    echo -e "${RED}✗ Node.js não encontrado!${NC}"
    exit 1
fi

# Instalar dependências do backend com UV
echo -e "${YELLOW}[3/3] Instalando dependências com UV...${NC}"
cd "$BASE_DIR/backend"
uv sync
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dependências do backend instaladas (UV)${NC}"
else
    echo -e "${RED}✗ Erro ao instalar dependências do backend${NC}"
    exit 1
fi

# Instalar dependências do frontend
echo -e "${YELLOW}[4/4] Instalando dependências do frontend...${NC}"
cd "$BASE_DIR/frontend"
npm install --silent
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Dependências do frontend instaladas${NC}"
else
    echo -e "${RED}✗ Erro ao instalar dependências do frontend${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}=================================================="
echo "✅ Instalação concluída com UV!"
echo "=================================================="
echo ""
echo -e "${BLUE}Para iniciar a aplicação, execute:${NC}"
echo ""
echo "  Terminal 1 (Backend com UV):"
echo "  $ cd $BASE_DIR/backend && bash start.sh"
echo ""
echo "  Terminal 2 (Frontend):"
echo "  $ cd $BASE_DIR/frontend && bash start.sh"
echo ""
echo "Depois acesse: http://localhost:5173"
echo -e "${NC}"
