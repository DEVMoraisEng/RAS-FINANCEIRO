# -*- coding: utf-8 -*-
"""
extrair_ids_responsavel.py  (RAS FINANCEIRO)
--------------------------------------------
Lista o ID de usuário do Notion de cada pessoa que aparece na coluna
Responsável do banco da RAS Financeiro.

Para que serve: a coluna Responsável é do tipo "Pessoa" (people). A API do
Notion NÃO aceita gravar o nome em texto — só o ID do usuário, no formato
{"people": [{"object": "user", "id": "..."}]}. Então o Apps Script precisa de
um mapa nome curto -> ID (o PEOPLE_IDS do Code.gs).

Por que não usar /v1/users: fora do plano Enterprise esse endpoint devolve
apenas o próprio bot da integração. A saída é ler os IDs a partir das linhas
que JÁ existem no banco — por isso, antes de rodar, preencha o Responsável de
pelo menos uma linha para cada pessoa (Júlio César, Ana Paula, Gustavo,
Lohany) direto no Notion.

USO:
    export NOTION_TOKEN="ntn_xxx"
    python3 extrair_ids_responsavel.py

Depois é só copiar o bloco PEOPLE_IDS impresso no final para o Code.gs.
"""

import os, json, time, unicodedata, urllib.request, urllib.error

TOKEN = os.environ.get("NOTION_TOKEN", "").strip()
DB_ATIV = (os.environ.get("RAS_FIN_DB_ID") or "3bcc5ab532d38038a2cee4d4733f4187").strip()
NOTION_VERSION = "2022-06-28"


def api(method, path, body=None):
    req = urllib.request.Request(
        "https://api.notion.com/v1" + path,
        data=json.dumps(body).encode("utf-8") if body is not None else None,
        method=method)
    req.add_header("Authorization", "Bearer " + TOKEN)
    req.add_header("Notion-Version", NOTION_VERSION)
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise SystemExit("Erro Notion %s: %s" % (e.code, e.read().decode("utf-8")[:400]))


def _sa(s):
    return "".join(c for c in unicodedata.normalize("NFD", s or "")
                   if unicodedata.category(c) != "Mn").lower().strip()


def main():
    if not TOKEN:
        raise SystemExit("Defina NOTION_TOKEN.")

    schema = api("GET", "/databases/%s" % DB_ATIV).get("properties", {})
    setores = []
    if "Setor" in schema:
        t = schema["Setor"].get("type")
        if t in ("select", "status"):
            setores = [o["name"] for o in (schema["Setor"].get(t) or {}).get("options", [])]
    pares = sorted(((_sa(s), s) for s in setores if s), key=lambda p: -len(p[0]))

    def curto(nome):
        k = _sa(nome)
        for chave, original in pares:
            if chave and k.startswith(chave):
                return original
        return nome

    encontrados = {}   # nome curto -> (id, nome completo)
    cursor = None
    while True:
        body = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        data = api("POST", "/databases/%s/query" % DB_ATIV, body)
        for pg in data.get("results", []):
            prop = pg["properties"].get("Responsável") or pg["properties"].get("Responsavel")
            if not prop or prop.get("type") != "people":
                continue
            for p in prop.get("people", []):
                nome = p.get("name", "")
                if nome:
                    encontrados.setdefault(curto(nome), (p.get("id"), nome))
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
        time.sleep(0.15)

    if not encontrados:
        raise SystemExit(
            "Nenhum responsável preenchido no banco ainda.\n"
            "Preencha a coluna Responsável de uma linha por pessoa no Notion e rode de novo.")

    print("Pessoas encontradas:\n")
    for curto_nome, (uid, completo) in sorted(encontrados.items()):
        print("  %-15s %s   (conta: %s)" % (curto_nome, uid, completo))

    faltando = [s for s in setores if s not in encontrados]
    if faltando:
        print("\n[!] Sem ID ainda (nenhuma linha com essa pessoa no Responsável): %s" % faltando)

    print("\n--- cole no Code.gs ---\n")
    print("var PEOPLE_IDS = {")
    linhas = ['  "%s": "%s"' % (k, v[0]) for k, v in sorted(encontrados.items())]
    print(",\n".join(linhas))
    print("};")


if __name__ == "__main__":
    main()
