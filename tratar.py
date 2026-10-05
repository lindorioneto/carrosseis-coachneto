#!/usr/bin/env python3
"""Prepara uma foto para as artes @coach_neto.

Tratamento natural: a foto mantem a propria cor, com a saturacao puxada para
baixo e um leve escurecimento, para o texto poder sentar em cima. Devolve um
PNG com alfa que derrete no preto pela esquerda e nas pontas de cima e de baixo.

    python3 tratar.py entrada.jpg assets/saida.png [foco_x] [zoom] [sat] [brilho]

foco_x: 0 a 1, onde fica o centro do recorte (padrao 0.5)
zoom:   1.0 usa a altura inteira; menor aproxima (padrao 1.0)
sat:    1.0 e a cor original; 0.70 e o padrao. Baixe para 0.45 a 0.55 quando a
        foto tiver uma peca de roupa ou uma parede muito berrante.
brilho: 0.92 e o padrao. Suba um pouco em foto muito escura.
"""
import sys
import numpy as np
from PIL import Image, ImageEnhance

LARG, ALT = 680, 880
SAT, BRILHO = 0.70, 0.92


def recortar(im, foco_x=0.5, zoom=1.0):
    W, H = im.size
    alt = int(H * zoom)
    larg = int(alt * LARG / ALT)
    if larg > W:
        larg, alt = W, int(W * ALT / LARG)
    x0 = int(np.clip(W * foco_x - larg / 2, 0, W - larg))
    y0 = int(np.clip(H * 0.5 - alt / 2, 0, max(0, H - alt)))
    return im.crop((x0, y0, x0 + larg, y0 + alt)).resize((LARG, ALT), Image.LANCZOS)


def bordas(h, w):
    """Alfa: derrete pela esquerda e nas pontas de cima e de baixo."""
    xs = np.linspace(0, 1, w)[None, :]
    ys = np.linspace(0, 1, h)[:, None]
    a = np.clip((xs - 0.02) / 0.32, 0, 1) * np.ones((h, 1))
    return a * np.clip(np.minimum(ys / 0.09, (1 - ys) / 0.10), 0, 1)


def tratar(entrada, saida, foco_x=0.5, zoom=1.0, sat=SAT, brilho=BRILHO):
    im = recortar(Image.open(entrada).convert("RGB"), foco_x, zoom)
    im = ImageEnhance.Color(im).enhance(sat)
    im = ImageEnhance.Brightness(im).enhance(brilho)
    arr = np.asarray(im).astype(np.float32)
    alfa = bordas(*arr.shape[:2]) * 255
    Image.fromarray(np.dstack([arr, alfa]).astype(np.uint8), "RGBA").save(saida, optimize=True)
    print(f"{saida}  sat {sat}  brilho {brilho}")


if __name__ == "__main__":
    tratar(sys.argv[1], sys.argv[2],
           float(sys.argv[3]) if len(sys.argv) > 3 else 0.5,
           float(sys.argv[4]) if len(sys.argv) > 4 else 1.0,
           float(sys.argv[5]) if len(sys.argv) > 5 else SAT,
           float(sys.argv[6]) if len(sys.argv) > 6 else BRILHO)
