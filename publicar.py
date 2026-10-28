#!/usr/bin/env python3
"""Publica um carrossel no Instagram via API do Instagram (login do Instagram).

Fluxo em três etapas, como a Meta exige:
  1. um container de mídia por imagem  (is_carousel_item=true)
  2. um container do carrossel         (media_type=CAROUSEL, children=...)
  3. a publicação                      (/me/media_publish)

O token vem da variável de ambiente IG_TOKEN (Secret do repositório).
As imagens são servidas pelo raw.githubusercontent.com deste próprio repositório.

TRAVA CONTRA POST DUPLICADO
Antes de publicar, este script confere duas coisas, nesta ordem:
  1. publicado.json, o registro no próprio repositório de tudo que já foi ao ar;
  2. os posts recentes da conta no Instagram, comparando o título da legenda.
Se qualquer uma das duas disser que o carrossel já saiu, ele não publica de novo
e encerra com sucesso. Depois de publicar, grava o slug em publicado.json e dá
push, para que qualquer execução posterior (inclusive um cron atrasado) veja que
o trabalho já foi feito. Isso existe porque em 26/10/2026 o post saiu duas vezes:
a publicação manual das 16h18 e o cron atrasado das 20h21 fizeram o mesmo post.
"""
import datetime
import json
import os
import pathlib
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://graph.instagram.com/v23.0"
BASE = pathlib.Path(__file__).parent


def chamar(metodo, caminho, **params):
    token = os.environ.get("IG_TOKEN", "").strip()
    if not token:
        sys.exit("ERRO: a variável IG_TOKEN não está definida (confira o Secret do repositório).")
    params["access_token"] = token
    url = f"{API}/{caminho}"
    dados = urllib.parse.urlencode(params).encode()
    req = (urllib.request.Request(url, data=dados, method="POST") if metodo == "POST"
           else urllib.request.Request(f"{url}?{dados.decode()}"))
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        corpo = e.read().decode()[:900]
        sys.exit(f"ERRO {e.code} em {caminho}\n{corpo}")


def esperar_container(cid, limite=24):
    """A Meta baixa a mídia de forma assíncrona; só publica quando estiver FINISHED."""
    for tentativa in range(limite):
        r = chamar("GET", cid, fields="status_code,status")
        estado = r.get("status_code")
        if estado == "FINISHED":
            return
        if estado == "ERROR":
            sys.exit(f"ERRO: a Meta não conseguiu processar a mídia. {r.get('status')}")
        time.sleep(5)
    sys.exit("ERRO: tempo esgotado esperando a Meta processar a mídia.")


# ---------------------------------------------------------------- trava
REGISTRO = BASE / "publicado.json"
IDENT = ["-c", "user.name=coachneto-bot", "-c", "user.email=actions@github.com"]


def git(*args):
    return subprocess.run(["git", "-C", str(BASE), *args],
                          capture_output=True, text=True)


def chamar_tolerante(metodo, caminho, **params):
    """Como chamar(), mas devolve None em vez de abortar quando a API falha."""
    try:
        return chamar(metodo, caminho, **params)
    except SystemExit:
        return None


def ler_registro():
    if not REGISTRO.exists():
        return []
    try:
        dados = json.loads(REGISTRO.read_text(encoding="utf-8"))
        return dados if isinstance(dados, list) else []
    except json.JSONDecodeError:
        print("AVISO: publicado.json esta ilegivel; tratando como vazio.")
        return []


def titulo(legenda):
    """A primeira linha nao vazia da legenda, que e o titulo do carrossel."""
    for linha in (legenda or "").splitlines():
        if linha.strip():
            return " ".join(linha.strip().lower().split())
    return ""


def no_registro(slug):
    for item in ler_registro():
        if item.get("slug") == slug:
            return item
    return None


def no_instagram(legenda):
    """Procura o mesmo titulo entre os posts recentes da conta.

    Falha fechada de proposito: se a API nao responder, o script aborta em vez
    de publicar no escuro. Um post que nao saiu se resolve rodando de novo; um
    post duplicado tem de ser apagado na mao.
    """
    alvo = titulo(legenda)
    if not alvo:
        return None
    r = chamar_tolerante("GET", "me/media", fields="id,caption,timestamp", limit="15")
    if r is None:
        sys.exit("ERRO: nao consegui listar os posts recentes para conferir duplicata. "
                 "Nada foi publicado. Rode de novo quando a API do Instagram responder.")
    for m in r.get("data", []):
        if titulo(m.get("caption")) == alvo:
            return m
    return None


def gravar_registro(slug, post, media_id):
    itens = ler_registro()
    itens.append({
        "slug": slug,
        "post": str(post),
        "data": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"),
        "quando": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "media_id": media_id,
        "run": os.environ.get("GITHUB_RUN_ID", ""),
    })
    REGISTRO.write_text(json.dumps(itens, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
    git("add", "publicado.json")
    if git("diff", "--cached", "--quiet").returncode == 0:
        return
    git(*IDENT, "commit", "-m", f"registro: {slug} publicado no Instagram")
    for tentativa in range(4):
        if git("push").returncode == 0:
            print("Registro gravado em publicado.json.")
            return
        git(*IDENT, "pull", "--rebase", "--autostash")
    print("AVISO: publiquei, mas nao consegui dar push em publicado.json. "
          "A conferencia no Instagram ainda protege contra duplicata.")


def main():
    post = pathlib.Path(sys.argv[1])
    dados = json.loads(post.read_text(encoding="utf-8"))
    slug = dados["slug"]
    ensaio = os.environ.get("MODO") == "ensaio"

    if not ensaio:
        feito = no_registro(slug)
        if feito:
            print(f"JA PUBLICADO: {slug} saiu em {feito.get('quando', feito.get('data'))} "
                  f"(media {feito.get('media_id')}). Nao vou publicar de novo.")
            return

    repo = os.environ.get("GITHUB_REPOSITORY")
    ref = os.environ.get("MEDIA_REF", "main")
    if not repo:
        sys.exit("ERRO: GITHUB_REPOSITORY não definido (rode isto pelo GitHub Actions).")
    raiz = f"https://raw.githubusercontent.com/{repo}/{ref}/media/{slug}"

    imagens = sorted((BASE / "media" / slug).glob("slide-*.jpg"))
    if not 2 <= len(imagens) <= 10:
        sys.exit(f"ERRO: um carrossel aceita de 2 a 10 imagens; encontrei {len(imagens)}.")

    quem = chamar("GET", "me", fields="user_id,username")
    print(f"Conta autenticada: @{quem.get('username')}")

    if not ensaio:
        igual = no_instagram(dados["legenda"])
        if igual:
            print(f"JA PUBLICADO: a conta ja tem um post com este titulo "
                  f"(media {igual.get('id')}, de {igual.get('timestamp')}). "
                  f"Nao vou publicar de novo.")
            return

    filhos = []
    for img in imagens:
        url = f"{raiz}/{img.name}"
        r = chamar("POST", "me/media", image_url=url, is_carousel_item="true")
        filhos.append(r["id"])
        print(f"  container criado para {img.name}")

    for cid in filhos:
        esperar_container(cid)

    carrossel = chamar("POST", "me/media", media_type="CAROUSEL",
                       children=",".join(filhos), caption=dados["legenda"])
    esperar_container(carrossel["id"])

    if ensaio:
        print("Modo ensaio: container pronto, publicação NÃO efetuada.")
        return

    pub = chamar("POST", "me/media_publish", creation_id=carrossel["id"])
    print(f"PUBLICADO. id da mídia: {pub.get('id')}")
    gravar_registro(slug, post, pub.get("id"))


if __name__ == "__main__":
    main()
