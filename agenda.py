#!/usr/bin/env python3
"""Diz qual post a agenda manda publicar hoje. Imprime vazio se nao houver nada.

A agenda vive em agenda.json e so recebe posts ja aprovados pelo Lindorio:

    [{"data": "2026-09-23", "post": "posts/hipertensos-exercicios.json"}]

A data e a de Cuiaba (UTC-4, sem horario de verao desde 2019), nao a do
runner do GitHub (UTC). O cron do GitHub chega a atrasar 4 a 8 horas: em 02/11
o post das 11h so saiu as 19h. Se a data fosse em UTC, uma execucao depois
das 20h de Cuiaba ja cairia no dia seguinte e o post do dia ficaria sem sair.
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
    cuiaba = datetime.timezone(datetime.timedelta(hours=-4))
    hoje = os.environ.get("DATA") or datetime.datetime.now(cuiaba).strftime("%Y-%m-%d")
    print(post_de(hoje))
