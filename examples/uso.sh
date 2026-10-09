#!/usr/bin/env bash
# Exemplos de uso com dados fictícios. Rode a partir da raiz do repositório.
set -euo pipefail

echo "# Cluster-ID padrão (TYPE.STATE.DDMMYY.HHMMSS.ms):"
python3 atomare_core.py cluster; echo

echo "# Cluster-ID com tipo e estado customizados:"
python3 atomare_core.py cluster --type P --state 222; echo

echo "# Envolver um trecho vindo de pipe:"
echo "Lista de compras fictícia: pão, café, frutas." | python3 atomare_core.py node --prefix NOD; echo

echo "# Âncora vazia (sem stdin):"
python3 atomare_core.py node --prefix IDEIA < /dev/null; echo
