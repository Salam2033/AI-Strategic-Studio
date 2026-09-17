"""Runtime compatibility and report-output enhancements for AI Strategic Studio."""
import os
import sys
import threading
import re

# Normalize the accidentally concatenated Render variable name.
if not os.environ.get("OPENAI_API_KEY", "").strip():
    for legacy_name in ("OPENAI_API_KEYOPENAI_API_KEY",):
        value = os.environ.get(legacy_name, "").strip()
        if value:
            os.environ["OPENAI_API_KEY"] = value
            break


def _make_social_content(query, analysis):
    text = re.sub(r"\s+", " ", (analysis or "")).strip()
    short = text[:650]
    if len(text) > 650:
        short += "…"
    subject = (query or "موضوع گزارش").strip()
    return {
        "summary": f"خلاصه برای انتشار: {subject}\n{text[:420]}{'…' if len(text) > 420 else ''}",
        "whatsapp": (
            f"📌 گزارش تحلیلی: {subject}\n\n"
            f"🧠 خلاصه:\n{short}\n\n"
            "منبع و داده‌های واقعی پیش از انتشار باید راستی‌آزمایی شوند."
        ),
        "instagram": (
            f"📊 {subject}\n\n"
            f"{short}\n\n"
            "#تحلیل_راهبردی #ژئوپلیتیک #تحلیل_داده"
        ),
        "facebook": (
            f"گزارش تحلیلی — {subject}\n\n"
            f"{short}\n\n"
            "این متن خلاصه تحلیلی است و داده‌ها و منابع باید پیش از انتشار بررسی شوند."
        ),
    }


def _enhance_map_infographic(original, visuals, path):
    """Create a report visual containing both a briefing map and related infographic."""
    from PIL import Image, ImageDraw, ImageFont

    W, H = 1600, 1450
    img = Image.new("RGB", (W, H), (7, 17, 31))
    draw = ImageDraw.Draw(img)
    try:
        title_font = ImageFont.truetype("DejaVuSans.ttf", 38)
        section_font = ImageFont.truetype("DejaVuSans.ttf", 28)
        small = ImageFont.truetype("DejaVuSans.ttf", 22)
    except Exception:
        title_font = section_font = small = ImageFont.load_default()

    draw.text((W - 45, 35), "AI Strategic Studio — نقشه و اینفوگرافیک مرتبط", anchor="ra",
              font=title_font, fill=(220, 235, 255))

    x0, y0, x1, y1 = 120, 115, 1480, 790
    draw.rounded_rectangle((x0, y0, x1, y1), radius=28, outline=(40, 65, 95),
                           width=3, fill=(10, 25, 42))
    for i in range(1, 5):
        yy = y0 + i * (y1 - y0) // 5
        draw.line((x0, yy, x1, yy), fill=(22, 43, 66), width=1)
    for i in range(1, 6):
        xx = x0 + i * (x1 - x0) // 6
        draw.line((xx, y0, xx, y1), fill=(22, 43, 66), width=1)

    coords = getattr(original, "__globals__", {}).get("CITY_COORDS", {})
    locations = (visuals or {}).get("map", {}).get("locations", []) if isinstance(visuals, dict) else []
    fills = {"political": (96, 165, 250), "economic": (52, 211, 153),
             "security": (251, 191, 36), "general": (196, 181, 253)}
    for item in locations[:8]:
        city = str(item.get("city", ""))
        if city not in coords:
            continue
        lat, lon = coords[city]
        px = int(x0 + (lon - 25) / (60 - 25) * (x1 - x0))
        py = int(y1 - (lat - 12) / (45 - 12) * (y1 - y0))
        fill = fills.get(item.get("category", "general"), fills["general"])
        draw.ellipse((px - 13, py - 13, px + 13, py + 13), fill=fill,
                     outline=(235, 245, 255), width=2)
        draw.text((px + 18, py - 10), city, font=small, fill=(235, 245, 255))

    top = 835
    draw.text((W - 45, top), "شاخص‌های کیفی گزارش", anchor="ra",
              font=section_font, fill=(143, 240, 207))
    dims = ((visuals or {}).get("infographic", {}) if isinstance(visuals, dict) else {}).get("dimensions", [])[:6]
    if not dims:
        dims = [{"label": "تحلیل", "score": 50, "note": "شاخص کیفی نمونه؛ آمار واقعی نیست."}]

    y = top + 65
    for item in dims:
        label = str(item.get("label", ""))
        try:
            score = max(0, min(100, int(float(item.get("score", 0)))))
        except Exception:
            score = 0
        note = str(item.get("note", ""))
        draw.text((W - 190, y), label, anchor="ra", font=small, fill=(235, 245, 255))
        bx0, bx1 = 180, W - 230
        draw.rounded_rectangle((bx0, y + 10, bx1, y + 30), radius=10,
                               fill=(20, 42, 66), outline=(40, 65, 95))
        fill_x = bx0 + int((bx1 - bx0) * score / 100)
        if fill_x > bx0:
            draw.rounded_rectangle((bx0, y + 10, fill_x, y + 30), radius=10, fill=(38, 101, 255))
        draw.text((bx1 + 25, y + 4), str(score), font=small, fill=(143, 240, 207))
        if note:
            draw.text((W - 190, y + 40), note[:85], anchor="ra", font=small, fill=(142, 163, 188))
        y += 88

    draw.text((W - 45, H - 35),
              "نقشه شماتیک و شاخص‌ها صرفاً برای ارائه تحلیلی‌اند؛ جایگزین نقشه مرجع یا آمار رسمی نیستند.",
              anchor="rs", font=small, fill=(142, 163, 188))
    img.save(path, format="PNG")


def _patch_app():
    app = sys.modules.get("app")
    if app is None or getattr(app, "_report_features_patched", False):
        return bool(app)
    original_map = getattr(app, "make_map_infographic", None)
    original_build = getattr(app, "build_report_files", None)
    if not original_map or not original_build:
        return False

    def enhanced_map(visuals, path):
        return _enhance_map_infographic(original_map, visuals, path)

    def enhanced_build(req):
        social = _make_social_content(req.query, req.analysis)
        original_analysis = req.analysis or ""
        req.analysis = (
            original_analysis.rstrip()
            + "\n\nمتن‌های آماده انتشار\n\n"
            + "خلاصه کوتاه برای واتس‌اپ و اینستاگرام:\n" + social["summary"]
            + "\n\nواتس‌اپ:\n" + social["whatsapp"]
            + "\n\nاینستاگرام:\n" + social["instagram"]
            + "\n\nفیس‌بوک:\n" + social["facebook"]
        )
        try:
            return original_build(req)
        finally:
            req.analysis = original_analysis

    app.make_map_infographic = enhanced_map
    app.build_report_files = enhanced_build
    app._report_features_patched = True
    return True


def _wait_for_app():
    import time
    for _ in range(120):
        if _patch_app():
            return
        time.sleep(0.05)


threading.Thread(target=_wait_for_app, daemon=True).start()
