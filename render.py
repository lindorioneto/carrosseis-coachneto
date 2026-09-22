#!/usr/bin/env python3
"""Renderiza um carrossel do Instagram (1080x1350) a partir de slides.json.
Identidade @coach_neto: preto, laranja #FF6D00, branco, chevron e grade."""
import base64, html, json, pathlib

from brand import C, W, H, GRAPHICS, ILUSTRA

BASE = pathlib.Path(__file__).parent
FONTS = BASE / "fonts"
OUT = BASE / "out"


def face(family, file, weight):
    b64 = base64.b64encode((FONTS / file).read_bytes()).decode()
    return (f"@font-face{{font-family:'{family}';font-style:normal;font-weight:{weight};"
            f"font-display:block;src:url(data:font/woff2;base64,{b64}) format('woff2');}}")


FACES = "".join([
    face("Archivo", "archivo-latin-800-normal.woff2", 800),
    face("Archivo", "archivo-latin-700-normal.woff2", 700),
    face("Archivo", "archivo-latin-500-normal.woff2", 500),
    face("Plex", "ibm-plex-sans-latin-400-normal.woff2", 400),
    face("Plex", "ibm-plex-sans-latin-500-normal.woff2", 500),
    face("Plex", "ibm-plex-sans-latin-600-normal.woff2", 600),
    face("Mono", "ibm-plex-mono-latin-500-normal.woff2", 500),
])

CSS = f"""
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px}}
body{{background:{C['black']};color:{C['white']};font-family:'Plex',sans-serif;
  -webkit-font-smoothing:antialiased}}

.slide{{position:relative;width:{W}px;height:{H}px;padding:78px 84px 68px;
  display:flex;flex-direction:column;overflow:hidden;background:{C['black']}}}

/* textura de grade da arte de marca */
.grid{{position:absolute;inset:0;opacity:.5;
  background-image:linear-gradient(rgba(255,255,255,.045) 1px,transparent 1px),
                   linear-gradient(90deg,rgba(255,255,255,.045) 1px,transparent 1px);
  background-size:76px 76px}}
.vignette{{position:absolute;inset:0;
  background:radial-gradient(120% 78% at 50% 0%,rgba(255,109,0,.10) 0%,rgba(7,7,7,0) 60%)}}

/* chevron da marca, em marca d'agua */
.chev{{position:absolute;right:-240px;top:50%;transform:translateY(-50%);
  width:600px;height:880px;opacity:.085}}
.chev svg{{width:100%;height:100%}}

/* foto tratada, sangrando pela direita — como a coluna na arte de marca */
.foto{{position:absolute;right:0;top:0;height:100%;width:68%;z-index:1;overflow:hidden}}
.foto img{{height:100%;width:100%;object-fit:cover;object-position:52% 50%;opacity:.92}}
.foto::after{{content:"";position:absolute;inset:0;
  background:linear-gradient(90deg,{C['black']} 12%,rgba(7,7,7,.78) 44%,rgba(7,7,7,.12) 86%,rgba(7,7,7,0) 100%)}}
.slide.com-foto .body{{padding-right:300px}}
.slide.com-foto h1{{font-size:88px}}

/* ilustracao de apoio, a direita — como a coluna na arte de marca */
.ilustra{{position:absolute;right:-30px;top:50%;transform:translateY(-50%);
  width:400px;opacity:.9;z-index:2}}
.ilustra svg{{width:100%;height:auto}}
.slide.com-ilustra .body{{padding-right:330px}}

.topbar{{display:flex;justify-content:space-between;align-items:center;
  font-family:'Mono',monospace;font-weight:500;font-size:22px;letter-spacing:.16em;
  color:{C['dim']};text-transform:uppercase;position:relative;z-index:3}}
.topbar .n{{color:{C['orange']}}}

.body{{flex:1;display:flex;flex-direction:column;justify-content:center;
  position:relative;z-index:3;padding:46px 0}}

.eyebrow{{font-family:'Mono',monospace;font-weight:500;font-size:24px;letter-spacing:.34em;
  color:{C['white']};text-transform:uppercase;margin-bottom:26px}}
.rule{{width:96px;height:7px;background:{C['orange']};margin-bottom:38px}}

h1{{font-family:'Archivo',sans-serif;font-weight:800;font-size:98px;line-height:.98;
  letter-spacing:-.035em;text-transform:uppercase;text-wrap:balance}}
h1 em{{font-style:normal;color:{C['orange']}}}
h2{{font-family:'Archivo',sans-serif;font-weight:800;font-size:60px;line-height:1.04;
  letter-spacing:-.028em;text-transform:uppercase;margin-bottom:34px;text-wrap:balance}}
h2 em{{font-style:normal;color:{C['orange']}}}

.sub{{font-size:35px;line-height:1.42;color:{C['muted']};margin-top:36px;max-width:24ch}}
.corpo{{font-size:36px;line-height:1.48;color:#D8D8D8}}

.destaque{{margin-top:40px;background:{C['panel']};border-left:7px solid {C['orange']};
  padding:32px 36px;font-size:32px;line-height:1.42;font-weight:500;color:{C['white']}}}

ul{{list-style:none;display:flex;flex-direction:column;gap:20px}}
li{{display:flex;gap:26px;align-items:center;font-size:35px;line-height:1.3;color:#D8D8D8}}
li b{{flex:none;width:52px;height:52px;background:{C['orange']};color:{C['black']};
  font-family:'Archivo',sans-serif;font-weight:800;font-size:27px;
  display:flex;align-items:center;justify-content:center}}

.graf{{margin:14px 0 6px}}
.kicker{{font-family:'Mono',monospace;font-weight:500;font-size:22px;letter-spacing:.18em;
  color:{C['orange']};text-transform:uppercase;margin-bottom:24px;line-height:1.5}}
.legenda{{font-size:36px;line-height:1.36;margin-top:26px;max-width:22ch;font-weight:500}}
.nota{{font-family:'Mono',monospace;font-size:21px;line-height:1.65;color:{C['dim']};
  margin-top:28px;padding-top:24px;border-top:1px solid {C['line']}}}

.refs{{display:flex;flex-direction:column;gap:30px}}
.ref{{border-top:1px solid {C['line']};padding-top:24px}}
.ref .rot{{font-family:'Mono',monospace;font-size:20px;letter-spacing:.18em;
  color:{C['orange']};text-transform:uppercase;margin-bottom:12px}}
.ref .txt{{font-size:28px;line-height:1.42;color:#D8D8D8}}
.aviso{{margin-top:44px;font-size:23px;line-height:1.5;color:{C['dim']};
  background:{C['panel']};padding:24px 28px;border-left:4px solid {C['line']}}}

.cta h1{{font-size:86px;line-height:.94}}
.metodo{{font-family:'Mono',monospace;font-weight:500;font-size:26px;letter-spacing:.44em;
  color:{C['white']};text-transform:uppercase;margin-bottom:24px}}
.acao{{display:inline-flex;align-items:center;gap:18px;align-self:flex-start;
  background:{C['orange']};color:{C['black']};font-family:'Archivo',sans-serif;
  font-weight:800;font-size:34px;letter-spacing:-.01em;text-transform:uppercase;
  padding:24px 38px;margin-top:46px}}
.acao i{{font-style:normal;font-size:38px;line-height:1}}
.oferta{{font-size:33px;line-height:1.4;color:#D8D8D8;margin-top:36px;max-width:23ch}}
.lock{{margin-top:30px}}
.lock small{{display:block;font-family:'Mono',monospace;font-weight:500;font-size:25px;
  letter-spacing:.3em;color:{C['muted']}}}

.foot{{display:flex;justify-content:space-between;align-items:center;position:relative;z-index:3;
  font-family:'Mono',monospace;font-size:22px;letter-spacing:.16em;color:{C['dim']};
  text-transform:uppercase}}
.foot b{{font-family:'Archivo',sans-serif;font-weight:800;font-size:26px;letter-spacing:-.01em;
  color:{C['white']};text-transform:none}}
.foot b span{{color:{C['orange']}}}
.arraste{{color:{C['orange']}}}
"""

CHEVRON = (f'<svg viewBox="0 0 300 460" fill="none">'
           f'<path d="M40 20 L250 230 L40 440" stroke="{C["orange"]}" stroke-width="30"/></svg>')


def esc(t):
    return html.escape(t).replace("\n", "<br>").replace("[", "<em>").replace("]", "</em>")


def slide_html(s, i, total, meta):
    top = (f'<div class="topbar"><span>{esc(meta["handle"])}</span>'
           f'<span><span class="n">{i:02d}</span> / {total:02d}</span></div>')
    lock = '<b>COACH<span>NETO</span></b>'
    foot = f'<div class="foot"><span>{esc(meta["serie"])}</span>{lock}</div>'
    t = s["tipo"]

    if t == "capa":
        body = (f'<div class="eyebrow">{esc(s["eyebrow"])}</div><div class="rule"></div>'
                f'<h1>{esc(s["titulo"])}</h1><p class="sub">{esc(s["sub"])}</p>')
        foot = (f'<div class="foot"><span class="arraste">arraste &#8594;</span>{lock}</div>')

    elif t == "conteudo":
        body = f'<h2>{esc(s["titulo"])}</h2>'
        if s.get("grafico"):
            body += f'<div class="graf">{GRAPHICS[s["grafico"]]()}</div>'
        if s.get("corpo"):
            body += f'<p class="corpo">{esc(s["corpo"])}</p>'
        if s.get("lista"):
            body += "<ul>" + "".join(
                f'<li><b>{n:02d}</b><span>{esc(x)}</span></li>'
                for n, x in enumerate(s["lista"], 1)) + "</ul>"
        if s.get("destaque"):
            body += f'<div class="destaque">{esc(s["destaque"])}</div>'

    elif t == "dado":
        body = (f'<div class="kicker">{esc(s["kicker"])}</div>'
                f'<div class="graf">{GRAPHICS[s["grafico"]]()}</div>'
                f'<p class="legenda">{esc(s["legenda"])}</p>'
                f'<p class="nota">{esc(s["nota"])}</p>')

    elif t == "referencia":
        body = f'<h2>{esc(s["titulo"])}</h2><div class="refs">'
        for r in s["refs"]:
            body += (f'<div class="ref"><div class="rot">{esc(r["rot"])}</div>'
                     f'<div class="txt">{esc(r["txt"])}</div></div>')
        body += f'</div><div class="aviso">{esc(s["aviso"])}</div>'

    else:  # cta
        body = (f'<div class="metodo">{esc(s["metodo"])}</div>'
                f'<h1>{esc(s["titulo"])}</h1><div class="rule" style="margin:34px 0 0"></div>'
                f'<p class="oferta">{esc(s["oferta"])}</p>'
                f'<div class="acao">{esc(s["acao"])}<i>&#8594;</i></div>'
                f'<div class="lock"><small>{esc(s["handle"])}</small></div>')

    ilus = ""
    if s.get("ilustracao"):
        ilus = f'<div class="ilustra">{ILUSTRA[s["ilustracao"]]()}</div>'
    if s.get("foto"):
        dados = base64.b64encode((BASE / "assets" / s["foto"]).read_bytes()).decode()
        ilus += f'<div class="foto"><img src="data:image/png;base64,{dados}"></div>'

    cls = "slide cta" if t == "cta" else "slide"
    if s.get("ilustracao"):
        cls += " com-ilustra"
    if s.get("foto"):
        cls += " com-foto"
    return (f'<!doctype html><meta charset="utf-8"><style>{FACES}{CSS}</style>'
            f'<div class="{cls}"><div class="grid"></div><div class="vignette"></div>'
            f'<div class="chev">{CHEVRON}</div>{ilus}{top}'
            f'<div class="body">{body}</div>{foot}</div>')


def main():
    import sys
    post = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else BASE / "posts" / "exemplo.json"
    data = json.loads(post.read_text(encoding="utf-8"))
    meta = {k: data[k] for k in ("serie", "edicao", "handle")}
    slides = data["slides"]
    out = BASE / "media" / data["slug"]
    out.mkdir(parents=True, exist_ok=True)

    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        br = p.chromium.launch()
        pg = br.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        for i, s in enumerate(slides, 1):
            pg.set_content(slide_html(s, i, len(slides), meta), wait_until="load")
            pg.wait_for_timeout(200)
            pg.screenshot(path=str(out / f"slide-{i:02d}.jpg"), type="jpeg", quality=92)
            print("gerado", out.name + "/" + f"slide-{i:02d}.jpg")
        br.close()


if __name__ == "__main__":
    main()
