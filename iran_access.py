"""Network-resilience wrapper for AI Strategic Studio.

Keeps the application logic unchanged while serving browser-critical Leaflet
assets from the app's own origin. This reduces the dashboard's dependence on
third-party CDN access from restricted networks and preserves the existing
Render/OpenAI backend architecture.
"""
from __future__ import annotations

import time
import urllib.request

from fastapi import FastAPI, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse

from source_app import app as upstream_app

LEAFLET_VERSION = "1.9.4"
REMOTE = "https://unpkg.com/leaflet@%s/dist/leaflet.%s"
CACHE_TTL = 86400

_cache: dict[str, tuple[float, bytes]] = {}


def _get_asset(kind: str) -> bytes:
    now = time.time()
    hit = _cache.get(kind)
    if hit and now - hit[0] < CACHE_TTL:
        return hit[1]
    url = REMOTE % (LEAFLET_VERSION, kind)
    req = urllib.request.Request(url, headers={"User-Agent": "AI-Strategic-Studio/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        data = r.read()
    _cache[kind] = (now, data)
    return data


class SameOriginHTMLMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        content_type = response.headers.get("content-type", "")
        if "text/html" not in content_type:
            return response
        body = b""
        async for chunk in response.body_iterator:
            body += chunk
        text = body.decode("utf-8", errors="replace")
        text = text.replace(
            f"https://unpkg.com/leaflet@{LEAFLET_VERSION}/dist/leaflet.css",
            "/local-assets/leaflet.css",
        )
        text = text.replace(
            f"https://unpkg.com/leaflet@{LEAFLET_VERSION}/dist/leaflet.js",
            "/local-assets/leaflet.js",
        )
        return StarletteResponse(
            content=text.encode("utf-8"),
            status_code=response.status_code,
            headers={k: v for k, v in response.headers.items() if k.lower() != "content-length"},
            media_type="text/html",
        )


app = FastAPI(title="AI Strategic Studio — Network Resilience Gateway")
app.add_middleware(SameOriginHTMLMiddleware)


@app.get("/local-assets/leaflet.css")
def leaflet_css():
    try:
        return Response(_get_asset("css"), media_type="text/css", headers={"Cache-Control": "public, max-age=86400"})
    except Exception:
        # Minimal fallback so the rest of the dashboard remains usable even if
        # the upstream CDN is temporarily unreachable from the server.
        fallback = ".leaflet-container{position:relative;overflow:hidden}.leaflet-pane,.leaflet-control{position:absolute}.leaflet-top{top:0}.leaflet-left{left:0}.leaflet-bottom{bottom:0}.leaflet-right{right:0}.leaflet-control{z-index:800}.leaflet-control-attribution{font-size:11px;background:#fff8;padding:2px 5px}.leaflet-container img{max-width:none!important}"
        return Response(fallback, media_type="text/css", headers={"Cache-Control": "public, max-age=300"})


@app.get("/local-assets/leaflet.js")
def leaflet_js():
    try:
        return Response(_get_asset("js"), media_type="application/javascript", headers={"Cache-Control": "public, max-age=86400"})
    except Exception as exc:
        return Response(
            "window.__leafletUnavailable=true;console.warn('Leaflet asset unavailable:',%r);" % str(exc),
            media_type="application/javascript",
            status_code=200,
        )


# Preserve every existing dashboard/API route.
app.mount("/", upstream_app)
