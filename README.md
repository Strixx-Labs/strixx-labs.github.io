# Strix Labs — Web

Web estática del estudio: https://strixx-labs.github.io

Generada con un script de Python sin dependencias (`build.py`). Sin cookies, sin analítica, sin servidor.

## Ver en local

```powershell
cd D:\StrixxLabs\web
python build.py --serve
```
Abre http://localhost:8000 (Ctrl+C para parar).

## Editar

| Qué | Dónde |
|---|---|
| Datos del estudio (nombre del titular, correo…) | `content/site.json` |
| Ficha de una app (texto, estado, enlace de Play, visible) | `content/apps/<app>.json` |
| Política de privacidad de una app | `content/privacy/<app>.html` (`{owner}`, `{email}` se rellenan solos) |
| Textos comunes de las políticas (derechos, contacto) | `content/privacy/_comun.html` |
| Diseño | `static/css/style.css` |

Al publicar una app: en su JSON pon `"status": "published"` y `"play_url": "https://play.google.com/store/apps/details?id=<paquete>"`.

## Publicar

Cada `git push` a `main` publica la web automáticamente (GitHub Actions → Pages).
