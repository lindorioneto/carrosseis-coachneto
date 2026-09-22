#!/usr/bin/env python3
"""Diz qual post a agenda manda publicar hoje. Imprime vazio se nao houver nada.

A agenda vive em agenda.json e so recebe posts ja aprovados pelo Lindorio:

    [{"data": "2026-09-23", "post": "posts/hipertensos-exercicios.json"}]

A data e sempre em UTC, que e o fuso do runner do GitHub. Como os posts saem
as 11h de Cuiaba (UTC-4), ou seja 15h UTC, o dia UTC e o mesmo dia local.
"""
import datetime
import json
import os
import pathlib

BASE = pathlib.Path(__file__).parent


def post_de(dia):
    arq = BASE / "agenda.json"
    if not arq.exists():
        return ""
    itens = json.loads(arq.read_text(encoding="utf-8"))
    for item in itens:
        if item.get("data") == dia:
            caminho = item.get("post", "")
            if caminho and (BASE / caminho).exists():
                return caminho
            return ""
    return ""


if __name__ == "__main__":
    hoje = os.environ.get("DATA") or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    print(post_de(hoje))
