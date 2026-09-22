#!/usr/bin/env python3
"""Converte uma imagem qualquer para a identidade @coach_neto.

Detecta o fundo pelos cantos, recorta em retrato, mapeia a luminância para o
duotone preto -> brasa -> laranja -> creme e devolve um PNG com alfa que
derrete no preto pela esquerda.

    python3 tratar.py entrada.jpg assets/saida.png [foco_x] [zoom]

foco_x: 0 a 1, onde fica o centro do recorte (padrão 0.5)
zoom:   1.0 usa a altura inteira; menor aproxima (padrão 1.0)
"""
import sys
import numpy as np
from PIL import Image, ImageOps, ImageFilter

LARG, ALT = 680, 880
PARADAS = [(0.00, (7, 7, 7)), (0.42, (90, 34, 4)), (0.72, (255, 109, 0)), (1.00, (255, 214, 170))]


def recortar(im, foco_x=0.5, zoom=1.0):
    W, H = im.size
    alt = int(H * zoom)
    larg = int(alt * LARG / ALT)
    if larg > W:
        larg, alt = W, int(W * ALT / LARG)
    x0 = int(np.clip(W * foco_x - larg / 2, 0, W - larg))
    y0 = int(np.clip(H * 0.5 - alt / 2, 0, max(0, H - alt)))
    return im.crop((x0, y0, x0 + larg, y0 + alt)).resize((LARG, ALT), Image.LANCZOS)


def mascara(arr):
    """Alfa do sujeito. Se os cantos concordam, o fundo é chapado: mascara por
    distância de cor. Senão, cai na luminância."""
    h, w, _ = arr.shape
    c = 40
    cantos = np.concatenate([arr[:c, :c].reshape(-1, 3), arr[:c, -c:].reshape(-1, 3),
                             arr[-c:, :c].reshape(-1, 3), arr[-c:, -c:].reshape(-1, 3)])
    fundo = np.median(cantos, axis=0)
    espalhado = np.median(np.abs(cantos - fundo))
    lum = arr.mean(axis=2) / 255.0

    if espalhado < 16:                                   # fundo chapado
        dist = np.linalg.norm(arr - fundo, axis=2) / 255.0
        a = np.clip((dist - 0.07) / 0.30, 0, 1)
        a = np.asarray(Image.fromarray((a * 255).astype(np.uint8))
                       .filter(ImageFilter.GaussianBlur(2.5))) / 255.0
        return np.clip(a ** 0.8, 0, 1), True
    return np.clip((lum - 0.08) / 0.55, 0, 1) ** 0.85, False


def tratar(entrada, saida, foco_x=0.5, zoom=1.0):
    im = recortar(Image.open(entrada).convert("RGB"), foco_x, zoom)
    arr = np.asarray(im).astype(np.float32)
    alpha, chapado = mascara(arr)

    g = ImageOps.autocontrast(im.convert("L"), cutoff=(1, 2))
    a = np.asarray(g).astype(np.float32) / 255.0
    if chapado:                       # sem fundo competindo, pode abrir o contraste
        a = np.clip((a - 0.12) / 0.80, 0, 1)

    rgb = np.zeros(a.shape + (3,), np.float32)
    for (p0, c0), (p1, c1) in zip(PARADAS, PARADAS[1:]):
        m = (a >= p0) & (a <= p1)
        t = np.zeros_like(a)
        t[m] = (a[m] - p0) / (p1 - p0)
        for i in range(3):
            rgb[..., i][m] = c0[i] + (c1[i] - c0[i]) * t[m]

    xs = np.linspace(0, 1, a.shape[1])[None, :]
    ys = np.linspace(0, 1, a.shape[0])[:, None]
    alpha = alpha * np.clip((xs - 0.02) / 0.32, 0, 1)                 # derrete a esquerda
    alpha = alpha * np.clip(np.minimum(ys / 0.09, (1 - ys) / 0.10), 0, 1)

    out = np.dstack([rgb, alpha * 255]).astype(np.uint8)
    Image.fromarray(out, "RGBA").filter(ImageFilter.SMOOTH).save(saida, optimize=True)
    print(f"{saida}  fundo {'chapado' if chapado else 'complexo'}")


if __name__ == "__main__":
    tratar(sys.argv[1], sys.argv[2],
           float(sys.argv[3]) if len(sys.argv) > 3 else 0.5,
           float(sys.argv[4]) if len(sys.argv) > 4 else 1.0)
