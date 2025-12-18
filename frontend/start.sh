#!/bin/bash

echo "🎨 Iniciando Frontend - Sistema de Sorteio"
echo "==========================================="

cd "$(dirname "$0")"

# Verificar se as dependências estão instaladas
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependências..."
    npm install --silent
fi

echo "🚀 Iniciando servidor Vite..."
echo ""
echo "Frontend rodando em: http://localhost:5173"
echo ""
echo "Pressione Ctrl+C para parar o servidor"
echo "==========================================="
echo ""

npm run dev
