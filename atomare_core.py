#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ATOMARE ZID GENERATOR v3.6.beta (ANTIGO ATOMARE CORE)
# ZID.domus-buguj

"""
ATOMARE ZID GENERATOR  v3.6 - GERADOR UNIFICADO DE IDs & WRAPPER
Validação: MASTERDoc v3.6
Protocolo de Segurança: Zero Risk (HÁ Backup Automático & Safe Write????)
"""

import time
import sys
import argparse
import datetime
import shutil
import os
import io

# Forçar UTF-8 nos streams de entrada e saída para evitar corrupção de acentos
# Helper: Force UTF-8 encoding for standard streams to prevent character encoding issues
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Alfabeto Base36 para Hashing de Alta Entropia
BASE36_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def to_base36(num: int) -> str:
    """Converte um inteiro para string Base36."""
    # PROBLEM: Logic error. If num is 0, this returns the entire 'BASE36_ALPHABET' string instead of "0".
    if num == 0: return "0"
    arr = []
    while num:
        num, rem = divmod(num, len(BASE36_ALPHABET))
        arr.append(BASE36_ALPHABET[rem])
    return "".join(reversed(arr))

def generate_cluster_id(state="111", type_char="N"):
    """
    Gera Cluster-ID no formato canônico: TYPE.STATE.TIMESTAMP.MS
    Exemplo: N.111.221225.103000.123
    """
    now = datetime.datetime.now()
    # Formato DDMMYY
    date_str = now.strftime("%d%m%y")
    # Formato HHMMSS
    time_str = now.strftime("%H%M%S")
    # Milissegundos (3 dígitos) garantem unicidade absoluta
    ms_str = f"{int(now.microsecond / 1000):03d}"
    
    # Return the formatted Cluster ID string
    return f"{type_char}.{state}.{date_str}.{time_str}.{ms_str}"

def generate_nod_id_block(prefix="NOD", content=""):
    """
    Gera o Block-Wrapper do padrão Atomare.
    Formato Híbrido: <span id="PREFIX-HASH" class="nod-start"></span>CONTEÚDO<span class="nod-end"></span>^PREFIX-HASH
    """
    # Timestamp em microssegundos convertido para Base36
    # Generate a high-entropy hash from the current timestamp (microseconds)
    # This minimizes collision probability for ID generation
    timestamp_us = int(time.time() * 1_000_000)
    hash_code = to_base36(timestamp_us)
    unique_id = f"{prefix.upper()}-{hash_code}"
    
    # Componentes da Sintaxe Híbrida
    anchor_start = f'<span id="{unique_id}" class="nod-start"></span>'
    anchor_end = '<span class="nod-end"></span>'
    obsidian_block_id = f"^{unique_id}"
    
    # Lógica: Se houver conteúdo selecionado, envolve-o. Caso contrário, apenas insere a âncora.
    if content:
        # Limpa espaços em branco extras, mas preserva a estrutura interna
        clean_content = content.strip()
        return f"{anchor_start}\n{clean_content}\n{anchor_end} {obsidian_block_id}"
    else:
        # Modo de inserção no cursor (nó vazio/ponto de ancoragem)
        return f"{anchor_start} {obsidian_block_id}"

def safe_backup(file_path):
    """
    Cria uma cópia.bak do arquivo imediatamente antes da operação.
    Protocolo de Risco Zero.
    """
    if file_path and os.path.exists(file_path):
        try:
            # Create a backup with .bak extension before modifying/processing
            shutil.copy2(file_path, file_path + ".bak")
            # Log para stderr (invisível ao usuário a menos que haja erro)
            print(f"Backup de segurança criado: {file_path}.bak", file=sys.stderr)
        except OSError as e:
            # Falha no backup é crítica; abortar para não arriscar o arquivo original
            print(f"FALHA NO BACKUP: {e}. Operação abortada.", file=sys.stderr)
            sys.exit(1)

def main():
    # Initialize argument parser for Command Line Interface
    parser = argparse.ArgumentParser(description="Atomare Core Generator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Comando: cluster (Gerar ID de Arquivo)
    cluster_parser = subparsers.add_parser("cluster")
    cluster_parser.add_argument("--state", default="111")
    cluster_parser.add_argument("--type", default="N")

    # Comando: node (Gerar ID Atômico / Envelopar Seleção)
    node_parser = subparsers.add_parser("node")
    node_parser.add_argument("--prefix", default="NOD")
    # O caminho do arquivo é opcional, usado apenas para disparar o backup
    node_parser.add_argument("--filepath", help="Caminho do arquivo atual para backup", default=None)

    args = parser.parse_args()

    try:
        if args.command == "cluster":
            # Flow for 'cluster': Generate and print the Cluster ID
            print(generate_cluster_id(state=args.state, type_char=args.type), end="")
            
        elif args.command == "node":
            # 1. Trigger Safe Backup (if filepath is provided via arguments)
            if args.filepath:
                safe_backup(args.filepath)
            
            # 2. Read Selection from Stdin (Pipe)
            # Checks if input is coming from a pipe (data stream) rather than interactive terminal
            input_content = ""
            if not sys.stdin.isatty():
                input_content = sys.stdin.read()
            
            # 3. Gerar e Imprimir
            result = generate_nod_id_block(prefix=args.prefix, content=input_content)
            print(result, end="")
            
    except Exception as e:
        # Tratamento de Erro Crítico: Imprime no stderr para acionar o balão vermelho do Obsidian
        print(f"ERRO CRÍTICO ATOMARE: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()