"""Identidade visual @coach_neto — extraída da arte de marca."""

C = {
    "black":   "#070707",
    "panel":   "#111111",
    "line":    "#262626",
    "white":   "#FFFFFF",
    "muted":   "#9B9B9B",
    "dim":     "#6E6E6E",
    "orange":  "#FF6D00",
    "orange2": "#FF9440",
    "ember":   "#7A3300",
}

W, H = 1080, 1350


def sawtooth(x0, y0, x1, y1, n=6, drop=0.30):
    """Picos agudos a cada série, sobre uma linha de base que DESCE ao longo das semanas.
    Em SVG o y cresce para baixo, então descer a pressão significa aumentar o y."""
    span = (x1 - x0) / n
    rng = y1 - y0
    base_ini = y0 + rng * 0.34          # pressão de repouso no começo
    base_fim = base_ini + rng * drop    # mais baixa (y maior) no fim
    pts = []
    for i in range(n + 1):
        t = i / n
        base = base_ini + (base_fim - base_ini) * t
        x = x0 + span * i
        pts.append((x, base))
        if i < n:
            pts.append((x + span * 0.32, base - rng * 0.30))
            pts.append((x + span * 0.62, base))
    return pts, (x0, base_ini, x1, base_fim)


def path(pts):
    return " ".join(f"{'M' if i == 0 else 'L'}{x:.1f},{y:.1f}" for i, (x, y) in enumerate(pts))


def svg_pressao(w=820, h=380):
    pts, (bx0, by0, bx1, by1) = sawtooth(70, 60, w - 30, h - 70)
    return f'''<svg viewBox="0 0 {w} {h}" width="100%">
  <defs><linearGradient id="g1" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{C['orange']}" stop-opacity=".38"/>
    <stop offset="1" stop-color="{C['orange']}" stop-opacity="0"/>
  </linearGradient></defs>
  <line x1="70" y1="{h-70}" x2="{w-30}" y2="{h-70}" stroke="{C['line']}" stroke-width="2"/>
  <path d="{path(pts)} L{w-30},{h-70} L70,{h-70} Z" fill="url(#g1)"/>
  <path d="{path(pts)}" fill="none" stroke="{C['orange']}" stroke-width="5"
        stroke-linejoin="round" stroke-linecap="round"/>
  <line x1="{bx0}" y1="{by0}" x2="{bx1}" y2="{by1}" stroke="{C['white']}"
        stroke-width="3" stroke-dasharray="12 10" opacity=".9"/>
  <text x="{w-34}" y="{by1+36}" fill="{C['white']}" font-family="Mono" font-size="23"
        text-anchor="end" letter-spacing="2">PRESSÃO DE REPOUSO</text>
  <text x="70" y="44" fill="{C['orange']}" font-family="Mono" font-size="23"
        letter-spacing="2">PICOS DURANTE AS SÉRIES</text>
  <text x="70" y="{h-28}" fill="{C['dim']}" font-family="Mono" font-size="22"
        letter-spacing="2">SEMANAS DE TREINO &#8594;</text>
</svg>'''


def svg_forest(w=820, h=300):
    """Escala do tamanho de efeito com intervalo de confiança."""
    x0, x1 = 90, w - 60
    lo, hi = -1.2, 0.1                      # domínio do eixo
    sx = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)
    y = 132
    ticks = [-1.2, -0.9, -0.6, -0.3, 0.0]
    tk = "".join(
        f'<line x1="{sx(t):.1f}" y1="{y+46}" x2="{sx(t):.1f}" y2="{y+60}" stroke="{C["line"]}" stroke-width="2"/>'
        f'<text x="{sx(t):.1f}" y="{y+96}" fill="{C["dim"]}" font-family="Mono" font-size="22" '
        f'text-anchor="middle">{("%.1f" % t).replace("-","−").replace(".",",")}</text>'
        for t in ticks)
    return f'''<svg viewBox="0 0 {w} {h}" width="100%">
  <line x1="{x0}" y1="{y+46}" x2="{x1}" y2="{y+46}" stroke="{C['line']}" stroke-width="2"/>
  {tk}
  <line x1="{sx(0):.1f}" y1="34" x2="{sx(0):.1f}" y2="{y+46}" stroke="{C['dim']}"
        stroke-width="2" stroke-dasharray="8 8"/>
  <text x="{sx(0)-16:.1f}" y="30" fill="{C['dim']}" font-family="Mono" font-size="21"
        text-anchor="end">SEM EFEITO</text>
  <line x1="{sx(-1.06):.1f}" y1="{y}" x2="{sx(-0.48):.1f}" y2="{y}"
        stroke="{C['orange']}" stroke-width="8" stroke-linecap="round" opacity=".45"/>
  <line x1="{sx(-1.06):.1f}" y1="{y-26}" x2="{sx(-1.06):.1f}" y2="{y+26}" stroke="{C['orange']}" stroke-width="5"/>
  <line x1="{sx(-0.48):.1f}" y1="{y-26}" x2="{sx(-0.48):.1f}" y2="{y+26}" stroke="{C['orange']}" stroke-width="5"/>
  <circle cx="{sx(-0.77):.1f}" cy="{y}" r="19" fill="{C['orange']}"/>
  <text x="{sx(-0.77):.1f}" y="{y-44}" fill="{C['white']}" font-family="Archivo" font-weight="800"
        font-size="40" text-anchor="middle">&#8722;0,77</text>
  <text x="{x0}" y="{h-14}" fill="{C['dim']}" font-family="Mono" font-size="21"
        letter-spacing="1">TAMANHO DE EFEITO (SMD) E INTERVALO DE CONFIANÇA 95%</text>
</svg>'''


def svg_escala(w=820, h=250):
    x0, x1 = 70, w - 60
    stop = x0 + (x1 - x0) * 0.62
    return f'''<svg viewBox="0 0 {w} {h}" width="100%">
  <defs><linearGradient id="g2" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{C['ember']}"/><stop offset="1" stop-color="{C['orange']}"/>
  </linearGradient></defs>
  <rect x="{x0}" y="104" width="{x1-x0}" height="26" rx="13" fill="{C['line']}"/>
  <rect x="{x0}" y="104" width="{stop-x0}" height="26" rx="13" fill="url(#g2)"/>
  <circle cx="{stop}" cy="117" r="24" fill="{C['white']}"/>
  <text x="{stop}" y="76" fill="{C['white']}" font-family="Archivo" font-weight="800"
        font-size="30" text-anchor="middle">PARE AQUI</text>
  <text x="{x0}" y="186" fill="{C['dim']}" font-family="Mono" font-size="23">LEVE</text>
  <text x="{stop}" y="186" fill="{C['orange']}" font-family="Mono" font-size="23"
        text-anchor="middle">FADIGA MODERADA</text>
  <text x="{x1}" y="186" fill="{C['dim']}" font-family="Mono" font-size="23"
        text-anchor="end">FALHA</text>
  <line x1="{x1-46}" y1="96" x2="{x1-10}" y2="138" stroke="{C['dim']}" stroke-width="5"/>
  <line x1="{x1-10}" y1="96" x2="{x1-46}" y2="138" stroke="{C['dim']}" stroke-width="5"/>
</svg>'''


def svg_mmhg(w=820, h=330):
    """Queda da pressao de repouso em mmHg, com intervalo de confianca."""
    x0, x1 = 78, w - 150
    lim = 12.0                                    # escala do eixo, em mmHg
    px = lambda v: x0 + (v / lim) * (x1 - x0)
    barras = [("SISTÓLICA", 8.2, 10.9, 5.5, 108), ("DIASTÓLICA", 4.1, 6.3, 1.9, 208)]
    out = []
    for rot, val, lo, hi, y in barras:
        out.append(f'<text x="{x0}" y="{y-26}" fill="{C["dim"]}" font-family="Mono" '
                   f'font-size="22" letter-spacing="2">{rot}</text>')
        out.append(f'<rect x="{x0}" y="{y}" width="{px(val)-x0:.1f}" height="44" '
                   f'fill="{C["orange"]}"/>')
        out.append(f'<line x1="{px(hi):.1f}" y1="{y+22}" x2="{px(lo):.1f}" y2="{y+22}" '
                   f'stroke="{C["black"]}" stroke-width="3" opacity=".55"/>')
        for b in (lo, hi):
            out.append(f'<line x1="{px(b):.1f}" y1="{y+8}" x2="{px(b):.1f}" y2="{y+36}" '
                       f'stroke="{C["black"]}" stroke-width="3" opacity=".55"/>')
        out.append(f'<text x="{px(val)+22:.1f}" y="{y+37}" fill="{C["white"]}" '
                   f'font-family="Archivo" font-weight="800" font-size="40">'
                   f'&#8722;{("%.1f" % val).replace(".", ",")}</text>')
    return f'''<svg viewBox="0 0 {w} {h}" width="100%">
  {"".join(out)}
  <text x="{x0}" y="{h-26}" fill="{C['dim']}" font-family="Mono" font-size="21"
        letter-spacing="1">QUEDA DA PRESSÃO DE REPOUSO, EM mmHg · BARRA ESCURA = IC 95%</text>
</svg>'''


GRAPHICS = {"pressao": svg_pressao, "forest": svg_forest,
            "escala": svg_escala, "mmhg": svg_mmhg}
