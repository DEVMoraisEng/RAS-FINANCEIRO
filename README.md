# RAS FINANCEIRO

Reunião de Alinhamento Semanal do Departamento Financeiro — Morais Engenharia e Construção.

Mesma arquitetura da RAS geral: Python lê o Notion via GitHub Actions, publica JSON estático em `dist/`, e o `index.html` consome esse JSON. Nenhum token aparece no navegador.

**Banco de dados:** ATIVIDADES RAS FINANCEIRO — `3bcc5ab5-32d3-8038-a2ce-e4d4733f4187`

## O que mudou em relação ao RAS-SEMANAL

- Aba **Obras** removida por completo (view, modal, JS, `data_obras.json`, workflows).
- Setores agora são pessoas: **Júlio César, Ana Paula, Gustavo, Lohany**. Cada quadro tem um responsável fixo — a própria pessoa do setor.
- As opções de Setor não estão mais fixas no código. O `fetch_ras.py` lê o schema do Notion e publica `setorOptions` no JSON; o site usa exatamente aquilo. Criar, renomear ou remover uma pessoa no Notion reflete no site sozinho, com a acentuação de lá — site e Notion não têm como divergir.
- `WRITE_ENDPOINT` está vazio de propósito (ver abaixo).

## Passos para colocar no ar

### 1. Criar o repositório

Suba estes arquivos em um repositório novo (ex.: `RAS-FINANCEIRO`), branch `main`.
Confirme que os workflows ficaram em `.github/workflows/` — não na raiz de `.github/`.

### 2. Secret

Em *Settings → Secrets and variables → Actions*, criar:

| Nome | Valor |
|---|---|
| `NOTION_TOKEN` | o token da integração |

Só esse. O ID do banco não é credencial e já está no código.

### 3. Compartilhar o banco com a integração

No Notion, abrir o banco → `···` → *Conexões* → adicionar a integração. Sem isso a API devolve 404.

### 4. Conferir as opções do Notion

```bash
export NOTION_TOKEN="..."
python3 verificar_status.py
```

O site oferece estes Status: **A Fazer, Em Andamento, Pendente, Concluído, Continuidade da Semana Anterior**. Se a coluna for do tipo `status` (e não `select`), a API **não cria opção nova** — todas precisam existir no Notion, escritas exatamente igual. Pelas imagens que você mandou já estão todas lá.

### 5. Primeiro fetch

*Actions → RAS Financeiro - atualizar dados → Run workflow.* Isso gera `dist/data_atividades.json`. Enquanto esse arquivo não existir, o site mostra dados de exemplo e avisa isso no rodapé.

### 6. GitHub Pages

*Settings → Pages →* branch `main`, pasta `/ (root)`.

### 7. Escrita no Notion (Apps Script) — pendente

`WRITE_ENDPOINT` está `""`, então o site abre em **modo leitura**: as edições aparecem na tela mas não sobem para o Notion.

Não dá para reaproveitar a URL do Apps Script do RAS-SEMANAL: aquele script escreve no banco de Atividades da RAS geral, e as atividades do Financeiro cairiam no banco errado. É preciso um Apps Script novo apontando para `3bcc5ab5...`.

Para montar esse `Code.gs` faltam os IDs de usuário do Notion das quatro pessoas (a coluna Responsável é do tipo Pessoa e a API só aceita ID, não nome). Para obtê-los:

1. No Notion, preencher o Responsável de pelo menos uma linha por pessoa.
2. Rodar:

```bash
export NOTION_TOKEN="..."
python3 extrair_ids_responsavel.py
```

O script imprime o bloco `PEOPLE_IDS` pronto para colar no `Code.gs`.

Lembrando: ao publicar o Apps Script, use sempre *Gerenciar implantações → Nova versão*, nunca "Nova implantação" — senão a URL muda e o site para de escrever.

## Arquivos

| Arquivo | Função |
|---|---|
| `index.html` | O site (single file) |
| `fetch_ras.py` | Lê o Notion → gera `dist/data_atividades.json` |
| `rollover_semana.py` | Domingo à noite: empurra o não concluído para a semana nova com status "Continuidade da Semana Anterior" |
| `verificar_status.py` | Compara as opções do site com as do Notion (só lê, não altera) |
| `extrair_ids_responsavel.py` | Extrai os IDs de usuário para o `PEOPLE_IDS` do Apps Script |
