#!/usr/bin/env python3
"""Publica um carrossel no Instagram via API do Instagram (login do Instagram).

Fluxo em três etapas, como a Meta exige:
  1. um container de mídia por imagem  (is_carousel_item=true)
  2. um container do carrossel         (media_type=CAROUSEL, children=...)
  3. a publicação                      (/me/media_publish)

O token vem da variável de ambiente IG_TOKEN (Secret do repositório).
As imagens são servidas pelo raw.githubusercontent.com deste próprio repositório.
"""
import json
import os
import pathlib
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


def main():
    post = pathlib.Path(sys.argv[1])
    dados = json.loads(post.read_text(encoding="utf-8"))
    slug = dados["slug"]

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

    if os.environ.get("MODO") == "ensaio":
        print("Modo ensaio: container pronto, publicação NÃO efetuada.")
        return

    pub = chamar("POST", "me/media_publish", creation_id=carrossel["id"])
    print(f"PUBLICADO. id da mídia: {pub.get('id')}")


if __name__ == "__main__":
    main()
