#!/bin/bash

echo "🎯 Iniciando Backend com UV - Sistema de Sorteio"
echo "================================================="

cd "$(dirname "$0")"

# Verificar se uv está instalado
if ! command -v uv &> /dev/null; then
    echo "⚠️  UV não encontrado. Instalando..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

echo "📦 Sincronizando dependências com UV..."
uv sync

echo ""
echo "🚀 Iniciando servidor FastAPI..."
echo ""
echo "Backend rodando em: http://localhost:8000"
echo "Documentação API: http://localhost:8000/docs"
echo ""
echo "Pressione Ctrl+C para parar o servidor"
echo "================================================="
echo ""

# Executar com uv run
uv run python main.py
