#!/usr/bin/env python3
"""
Generador de la web de Strix Labs (solo Python estándar, sin dependencias).

  python build.py           → genera la web en dist/
  python build.py --serve   → genera y la abre en http://localhost:8000

Contenido editable:
  content/site.json             datos del estudio
  content/apps/<app>.json       ficha de cada app (visible, estado, enlace a Play…)
  content/privacy/<app>.html    política de privacidad de cada app
"""
import html, json, shutil, sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
CONTENT, STATIC, DIST = ROOT / "content", ROOT / "static", ROOT / "dist"

site = json.loads((CONTENT / "site.json").read_text(encoding="utf-8"))
apps = sorted((json.loads(p.read_text(encoding="utf-8")) for p in (CONTENT / "apps").glob("*.json")),
              key=lambda a: a["name"].lower())
visible = [a for a in apps if a.get("visible")]
published = [a for a in visible if a["status"] == "published"]
in_dev = [a for a in visible if a["status"] != "published"]

OWNER = site["owner_name"] or "[NOMBRE Y APELLIDOS DEL TITULAR]"
if not site["owner_name"]:
    print("⚠  Falta owner_name en content/site.json: las políticas de privacidad no son válidas hasta rellenarlo.")
e = html.escape

LOGO = ('<svg class="mark" viewBox="0 0 120 120" aria-hidden="true"><g fill="none" stroke="currentColor" '
        'stroke-linecap="round"><circle cx="36" cy="64" r="22" stroke-width="10"/><circle cx="84" cy="64" r="22" '
        'stroke-width="10"/><path d="M14 30 Q60 12 106 30" stroke-width="8"/></g><path d="M52 94 L68 94 L60 108 Z" '
        'fill="currentColor" stroke="currentColor" stroke-width="3" stroke-linejoin="round"/></svg>')

NAV = [("/", "Inicio"), ("/#apps", "Apps"), ("/estudio/", "Estudio"), ("/contacto/", "Contacto")]


def fill(text: str) -> str:
    return (text.replace("{owner}", e(OWNER)).replace("{email}", e(site["email"]))
                .replace("{location}", e(site["owner_location"])).replace("{updated}", site["updated"]))


def page(path: str, title: str, body: str, description: str = "") -> None:
    full_title = f"{title} · {site['name']}" if title != site["name"] else site["name"]
    desc = e(description or site["description"])
    nav = "".join(f'<a href="{href}">{label}</a>' for href, label in NAV)
    out = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(full_title)}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{e(full_title)}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{site['url']}/img/strixlabs-512.png">
<meta name="theme-color" content="#1B2230">
<link rel="icon" href="/img/favicon.svg" type="image/svg+xml">
<link rel="canonical" href="{site['url']}{path}">
<link rel="stylesheet" href="/css/style.css">
<script>try{{var t=localStorage.getItem('theme');if(t)document.documentElement.dataset.theme=t}}catch(e){{}}</script>
</head>
<body>
<a class="skip" href="#main">Saltar al contenido</a>
<header class="top">
  <div class="wrap bar">
    <a class="brand" href="/" aria-label="{e(site['name'])}, inicio">{LOGO}<span>strix <b>labs</b></span></a>
    <nav aria-label="Principal">{nav}</nav>
    <button class="theme" type="button" aria-label="Cambiar entre tema claro y oscuro"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 3a9 9 0 0 1 0 18z" fill="currentColor"/></svg></button>
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="foot">
  <div class="wrap foot-grid">
    <div><a class="brand small" href="/">{LOGO}<span>strix <b>labs</b></span></a>
      <p class="muted">{e(site['tagline'])}</p></div>
    <div><h2 class="foot-h">Legal</h2>
      <a href="/privacidad/">Privacidad</a><a href="/eliminar-datos/">Eliminar mis datos</a></div>
    <div><h2 class="foot-h">Contacto</h2>
      <a href="mailto:{e(site['email'])}">{e(site['email'])}</a><a href="{site['github']}" rel="noopener">GitHub</a></div>
  </div>
  <p class="wrap muted tiny">© {date.today().year} {e(site['name'])} · Web sin cookies ni rastreadores.</p>
</footer>
<script src="/js/main.js" defer></script>
</body>
</html>
"""
    target = DIST / path.strip("/") / "index.html" if path != "/404.html" else DIST / "404.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(out, encoding="utf-8")


def badge(a) -> str:
    return ('<span class="badge live">Disponible</span>' if a["status"] == "published"
            else '<span class="badge dev">En desarrollo</span>')


def card(a) -> str:
    return f"""<a class="card reveal" href="/apps/{a['slug']}/" style="--app:{a['color']}">
  <span class="app-icon" aria-hidden="true">{a['emoji']}</span>
  <span class="card-body"><span class="card-title">{e(a['name'])}</span>{badge(a)}
  <span class="muted">{e(a['tagline'])}</span></span></a>"""


def play_button(a) -> str:
    if a.get("play_url"):
        return f'<a class="btn primary" href="{e(a["play_url"])}" rel="noopener">Descargar en Google Play</a>'
    return '<span class="btn ghost" aria-disabled="true">Próximamente en Google Play</span>'


def build():
    if DIST.exists():
        shutil.rmtree(DIST)
    shutil.copytree(STATIC, DIST)
    (DIST / ".nojekyll").write_text("")

    # ── Inicio ──
    pub_html = ("".join(card(a) for a in published) if published else
                '<p class="muted reveal">Las primeras apps llegarán pronto a Google Play.</p>')
    page("/", site["name"], f"""
<section class="hero">
  <div class="wrap hero-grid">
    <div class="reveal">
      <p class="eyebrow">Estudio independiente de apps Android</p>
      <h1>{e(site['tagline'])}</h1>
      <p class="lead">{e(site['description'])}</p>
      <div class="actions"><a class="btn primary" href="#apps">Ver las apps</a>
        <a class="btn ghost" href="/estudio/">Cómo trabajamos</a></div>
    </div>
    <div class="hero-mark reveal" aria-hidden="true">{LOGO}</div>
  </div>
</section>
<section class="wrap principles">
  <div class="reveal"><h2>Privadas</h2><p>Tus datos se quedan en tu móvil. Sin cuentas obligatorias, sin rastreo y sin vender nada a nadie.</p></div>
  <div class="reveal"><h2>Ligeras</h2><p>Apps pequeñas y rápidas que hacen una cosa y la hacen bien, también sin conexión.</p></div>
  <div class="reveal"><h2>Cuidadas</h2><p>Diseño sencillo, modo oscuro, accesibles y mantenidas con regularidad.</p></div>
</section>
<section class="wrap" id="apps">
  <h2 class="section-title reveal">Apps publicadas</h2>
  <div class="grid">{pub_html}</div>
  <h2 class="section-title reveal">En desarrollo</h2>
  <div class="grid">{''.join(card(a) for a in in_dev)}</div>
</section>""")

    # ── Fichas de app ──
    for a in visible:
        feats = "".join(f"<li>{e(f)}</li>" for f in a["features"])
        has_policy = (CONTENT / "privacy" / f"{a['slug']}.html").exists()
        page(f"/apps/{a['slug']}/", a["name"], f"""
<section class="wrap app-hero reveal" style="--app:{a['color']}">
  <span class="app-icon big" aria-hidden="true">{a['emoji']}</span>
  <div><h1>{e(a['name'])}</h1>{badge(a)}<p class="lead">{e(a['tagline'])}</p>
  <div class="actions">{play_button(a)}</div></div>
</section>
<section class="wrap prose reveal">
  <p>{e(a['description'])}</p>
  <h2>Qué puedes hacer</h2><ul class="checks">{feats}</ul>
  <h2>Privacidad</h2>
  <p>{'<a href="/privacidad/' + a['slug'] + '/">Política de privacidad de ' + e(a['name']) + '</a> · ' if has_policy else ''}<a href="/eliminar-datos/#{a['slug']}">Eliminar mis datos</a></p>
  <p class="muted tiny">Paquete Android: <code>{e(a['package'])}</code></p>
</section>""", a["description"])

    # ── Privacidad ──
    common = fill((CONTENT / "privacy" / "_comun.html").read_text(encoding="utf-8"))
    policy_links = []
    for a in apps:
        f = CONTENT / "privacy" / f"{a['slug']}.html"
        if not f.exists():
            continue
        policy_links.append(f'<li><a href="/privacidad/{a["slug"]}/">{e(a["name"])}</a></li>')
        page(f"/privacidad/{a['slug']}/", f"Privacidad de {a['name']}", f"""
<article class="wrap prose">
  <p class="eyebrow">Política de privacidad</p><h1>{e(a['name'])}</h1>
  <p class="muted">Última actualización: {site['updated']}</p>
  {fill(f.read_text(encoding='utf-8'))}
  {common}
</article>""", f"Política de privacidad de {a['name']}")

    page("/privacidad/", "Privacidad", f"""
<article class="wrap prose">
  <h1>Privacidad</h1>
  <p class="lead">Cada app tiene su propia política. Todas siguen la misma idea: recoger lo mínimo y que tus datos se queden en tu móvil.</p>
  <ul>{''.join(policy_links)}</ul>
  <h2>Esta web</h2>
  <p>Esta web es estática y está alojada en GitHub Pages. <strong>No usa cookies, analítica ni rastreadores.</strong> Solo guarda en tu navegador (almacenamiento local) si prefieres el tema claro u oscuro, y ese dato no sale de tu dispositivo.</p>
  <p>Como cualquier servidor web, GitHub puede registrar datos técnicos de la conexión (como la dirección IP) por motivos de seguridad. Más información en la <a href="https://docs.github.com/es/site-policy/privacy-policies/github-general-privacy-statement" rel="noopener">declaración de privacidad de GitHub</a>.</p>
  <p>Responsable: {e(OWNER)} · <a href="mailto:{e(site['email'])}">{e(site['email'])}</a></p>
</article>""")

    # ── Eliminar datos ──
    del_items = {
        "ximitask": """<p><strong>Desde la app:</strong> <em>Ajustes › Hogar compartido › Salir del hogar</em>. Se elimina tu identificador anónimo y, si eres el último miembro, se borran de la nube todos los datos del hogar. Los datos de tu móvil se borran al desinstalar la app.</p>""",
        "freshlist": """<p><strong>Desde la app:</strong> borra la lista compartida en tu móvil para salir de ella; tu nombre deja de aparecer y la lista sigue para los demás miembros.</p>""",
        "wakeup": """<p>WakeUp no guarda datos fuera de tu móvil. Desinstalar la app borra todo.</p>""",
    }
    blocks = "".join(f"""<section id="{a['slug']}"><h2>{e(a['name'])}</h2>{del_items.get(a['slug'], '')}</section>"""
                     for a in apps if a["slug"] in del_items)
    page("/eliminar-datos/", "Eliminar mis datos", f"""
<article class="wrap prose">
  <h1>Eliminar mis datos</h1>
  <p class="lead">Nuestras apps no tienen cuentas con correo ni contraseña. Así puedes borrar lo que se haya guardado fuera de tu móvil.</p>
  {blocks}
  <h2>Solicitud por correo</h2>
  <p>Si prefieres que lo hagamos nosotros, o quieres borrar por completo una lista u hogar compartido, escribe a <a href="mailto:{e(site['email'])}?subject=Eliminar%20mis%20datos">{e(site['email'])}</a> indicando la app y el código de invitación de la lista u hogar. Lo eliminaremos en un plazo máximo de 30 días y te confirmaremos el borrado.</p>
</article>""")

    # ── Estudio ──
    page("/estudio/", "Estudio", f"""
<article class="wrap prose">
  <p class="eyebrow">Sobre Strix Labs</p>
  <h1>Un estudio pequeño, a propósito.</h1>
  <p class="lead">Strix Labs es un proyecto independiente de una sola persona, en {e(site['owner_location'])}. <em>Strix</em> es el nombre científico del cárabo: una lechuza que ve en la oscuridad y no hace ruido. Así queremos que sean nuestras apps.</p>
  <h2>Cómo trabajamos</h2>
  <ul class="checks">
    <li>Primero, que funcione sin conexión y sin crear cuenta.</li>
    <li>Ningún dato sale del móvil si no hace falta para lo que tú has pedido.</li>
    <li>Sin publicidad intrusiva ni suscripciones sin un valor real.</li>
    <li>Código mantenido, actualizado a las últimas versiones de Android.</li>
  </ul>
  <h2>Desarrollador</h2>
  <p>{e(OWNER)} · Strix Labs<br>{e(site['owner_location'])}<br><a href="mailto:{e(site['email'])}">{e(site['email'])}</a></p>
</article>""")

    # ── Contacto ──
    page("/contacto/", "Contacto", f"""
<article class="wrap prose">
  <h1>Contacto</h1>
  <p class="lead">¿Una idea, un fallo o una duda sobre tus datos? Escríbenos.</p>
  <p><a class="btn primary" href="mailto:{e(site['email'])}">{e(site['email'])}</a></p>
  <p class="muted">Respondemos normalmente en pocos días. Si es sobre un fallo, indica la app, la versión (en <em>Ajustes</em>) y el modelo de tu móvil.</p>
</article>""")

    page("/404.html", "Página no encontrada", """
<article class="wrap prose"><h1>No encontramos esta página</h1>
<p><a class="btn primary" href="/">Volver al inicio</a></p></article>""")

    # sitemap
    urls = ["/", "/estudio/", "/contacto/", "/privacidad/", "/eliminar-datos/"]
    urls += [f"/apps/{a['slug']}/" for a in visible]
    urls += [f"/privacidad/{a['slug']}/" for a in apps if (CONTENT / "privacy" / f"{a['slug']}.html").exists()]
    (DIST / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + "".join(f"<url><loc>{site['url']}{u}</loc></url>" for u in urls) + "</urlset>\n", encoding="utf-8")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {site['url']}/sitemap.xml\n")
    print(f"✓ Web generada en {DIST} ({len(urls)} páginas)")


if __name__ == "__main__":
    build()
    if "--serve" in sys.argv:
        import functools, http.server, webbrowser
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(DIST))
        print("→ http://localhost:8000  (Ctrl+C para parar)")
        webbrowser.open("http://localhost:8000")
        http.server.ThreadingHTTPServer(("localhost", 8000), handler).serve_forever()
