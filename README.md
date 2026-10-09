# Diamond System — Atomare ZID Generator

Gerador de identificadores únicos para notas em Markdown/Obsidian, escrito em Python puro (sem dependências).

Ele faz duas coisas:

- **`cluster`**: gera um ID de arquivo no formato `TYPE.STATE.DDMMYY.HHMMSS.ms`, por exemplo `N.111.221225.103000.123`.
- **`node`**: gera um ID atômico de bloco (timestamp em microssegundos convertido para Base36) e, se receber texto via stdin, envolve esse trecho em âncoras HTML + block-id do Obsidian:

  ```html
  <span id="NOD-HN225JT4KJ" class="nod-start"></span>
  Trecho selecionado
  <span class="nod-end"></span> ^NOD-HN225JT4KJ
  ```

  Com `--filepath`, cria antes um backup `arquivo.bak` e aborta se o backup falhar.

Erros são enviados para o stderr com o prefixo `ERRO CRÍTICO ATOMARE`, o que permite que plugins do Obsidian que executam comandos de shell exibam o erro como notificação.

## Como rodar

Requer Python 3.8+.

```bash
# ID de arquivo
python3 atomare_core.py cluster
python3 atomare_core.py cluster --type P --state 222

# ID de bloco envolvendo um texto
echo "Texto qualquer" | python3 atomare_core.py node --prefix NOD

# Âncora vazia, com backup prévio da nota
python3 atomare_core.py node --prefix IDEIA --filepath caminho/da/nota.md < /dev/null
```

Mais exemplos (todos com dados fictícios) em [`examples/`](examples/):

```bash
bash examples/uso.sh
```

## Testes

```bash
python3 -m unittest discover -s tests -v
```

## Arquivos

| Arquivo | Descrição |
|---|---|
| `atomare_core.py` | Script principal (v3.6.beta). |
| `atomare_zid_generator.py` | Mesmo código com o nome novo da ferramenta; hoje é idêntico a `atomare_core.py` e mantido por compatibilidade com atalhos existentes. |
| `tests/` | Testes unitários e de CLI (biblioteca padrão `unittest`). |
| `examples/` | Nota de exemplo e script de uso, com conteúdo fictício. |

## Status

Beta (v3.6). Uso pessoal, integrado a um vault do Obsidian. Este repositório contém só o gerador de IDs; nenhuma nota do vault foi publicada.

## Limitações

- **Unicidade baseada em relógio:** os IDs vêm do horário local (`cluster`, resolução de milissegundos) e de `time.time()` (`node`, microssegundos). Duas chamadas no mesmo instante, ou um ajuste do relógio para trás, podem gerar IDs repetidos. Não há verificação de colisão.
- **Fuso horário:** o `cluster` usa o horário local, sem indicação de fuso, e o formato `DDMMYY` não ordena cronologicamente como texto.
- **Backup simples:** o `.bak` é sobrescrito a cada execução e só é feito quando `--filepath` é informado. O script não escreve na nota; quem insere o resultado é o editor.
- **Streams forçados para UTF-8:** o módulo reconfigura `stdin`/`stdout`/`stderr` ao ser importado, então foi pensado para uso via linha de comando, não como biblioteca.
- Sem empacotamento (`pip install`), sem CI.
