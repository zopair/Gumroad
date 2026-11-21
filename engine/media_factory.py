"""Media factory: multi-source TTS + 9:16 visuals + FFmpeg kinetic renderer.

Output: output/final_short.mp4 (1080x1920, H.264/AAC, loudness-normalised, faststart).

Fallback chains (each one ends in a 100% local provider, so rendering never fails):
  Voice : edge-tts (voice A) -> edge-tts (voice B) -> gTTS -> espeak-ng -> pyttsx3 -> silence
  Visual: Pollinations (rate-aware) -> Openverse (CC) -> Wikimedia Commons -> procedural gradient art
"""
from __future__ import annotations

import asyncio
import concurrent.futures as cf
import hashlib
import io
import logging
import math
import os
import random
import re
import shutil
import subprocess
import time
import urllib.parse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFilter, ImageFont, features

from . import resolver

log = logging.getLogger("relaymind.media")

W, H = 1080, 1920
FPS = 30
SRC_W, SRC_H = 1404, 2496          # 1.3x canvas: headroom for Ken Burns motion
IMAGE_BUDGET_S = float(os.environ.get("RELAYMIND_IMAGE_BUDGET", "80"))
IMAGE_WORKERS = 3

VOICES = {
    "en": ["en-US-AriaNeural", "en-US-GuyNeural", "en-US-JennyNeural"],
    "ar": ["ar-EG-SalmaNeural", "ar-EG-ShakirNeural", "ar-SA-ZariyahNeural"],
}
PALETTES = [
    ((255, 0, 128), (40, 0, 90)), ((0, 200, 255), (10, 20, 80)), ((255, 140, 0), (120, 0, 40)),
    ((0, 255, 170), (0, 50, 70)), ((255, 220, 0), (200, 30, 90)), ((150, 80, 255), (10, 0, 40)),
]
FONT_CANDIDATES = {
    "en": [
        "/usr/share/fonts/truetype/noto/NotoSans-Black.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/ubuntu/Ubuntu-B.ttf",
    ],
    "ar": [
        "/usr/share/fonts/truetype/noto/NotoSansArabic-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoNaskhArabic-Bold.ttf",
        "/usr/share/fonts/truetype/kacst/KacstBook.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",   # DejaVu covers Arabic glyphs
    ],
}
FONT_DOWNLOADS = {  # open-source (OFL) fonts, fetched only if no system font is found
    "ar": "https://raw.githubusercontent.com/notofonts/notofonts.github.io/main/fonts/NotoSansArabic/hinted/ttf/NotoSansArabic-Bold.ttf",
    "en": "https://raw.githubusercontent.com/notofonts/notofonts.github.io/main/fonts/NotoSans/hinted/ttf/NotoSans-Bold.ttf",
}


# --------------------------------------------------------------------------- #
# FFmpeg helpers
# --------------------------------------------------------------------------- #
def ffmpeg_bin() -> str:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg  # bundled static build, pip-cached in CI
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError("FFmpeg not found (install ffmpeg or imageio-ffmpeg)") from exc


def run_ff(args: list[str], timeout: int = 180) -> None:
    cmd = [ffmpeg_bin(), "-hide_banner", "-loglevel", "error", "-y", *args]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if p.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {p.stderr[-800:]}")


def media_duration(path: str) -> float:
    p = subprocess.run([ffmpeg_bin(), "-hide_banner", "-i", path], capture_output=True, text=True)
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", p.stderr)
    if not m:
        return 0.0
    h, mi, s = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(s)


# --------------------------------------------------------------------------- #
# Fonts & text shaping (English LTR + Arabic RTL)
# --------------------------------------------------------------------------- #
_FONT_CACHE: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}


def _font_path(lang: str, workdir: Path) -> Optional[str]:
    for p in FONT_CANDIDATES.get(lang, []) + FONT_CANDIDATES["en"]:
        if os.path.exists(p):
            return p
    target = workdir / f"font_{lang}.ttf"
    if target.exists():
        return str(target)
    try:
        r = resolver.request_with_retry("GET", FONT_DOWNLOADS[lang], attempts=2, timeout=20)
        if r.ok and len(r.content) > 10_000:
            target.write_bytes(r.content)
            return str(target)
    except Exception as exc:  # noqa: BLE001
        log.warning("font download failed: %s", exc)
    return None


def get_font(lang: str, size: int, workdir: Path):
    key = (lang, size)
    if key not in _FONT_CACHE:
        path = _font_path(lang, workdir)
        try:
            _FONT_CACHE[key] = ImageFont.truetype(path, size) if path else ImageFont.load_default(size)
        except Exception:  # noqa: BLE001
            _FONT_CACHE[key] = ImageFont.load_default(size)
    return _FONT_CACHE[key]


HAS_RAQM = features.check("raqm")


def shape(text: str, lang: str) -> str:
    """Without libraqm, Arabic must be reshaped + bidi-reordered manually."""
    if lang != "ar" or HAS_RAQM:
        return text
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display
        return get_display(arabic_reshaper.reshape(text))
    except Exception:  # noqa: BLE001
        return text


def _draw_kwargs(lang: str) -> dict:
    if lang == "ar" and HAS_RAQM:
        return {"direction": "rtl", "language": "ar"}
    return {}


def wrap_text(text: str, font, max_w: int, lang: str) -> list[str]:
    words, lines, cur = text.split(), [], ""
    probe = ImageDraw.Draw(Image.new("L", (10, 10)))
    for w in words:
        cand = (cur + " " + w).strip()
        if probe.textlength(shape(cand, lang), font=font, **_draw_kwargs(lang)) <= max_w or not cur:
            cur = cand
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# --------------------------------------------------------------------------- #
# Voice synthesis chain
# --------------------------------------------------------------------------- #
def _to_wav(src: str, dst: str) -> None:
    run_ff(["-i", src, "-ac", "1", "-ar", "44100", "-af", "silenceremove=start_periods=1:start_threshold=-50dB", dst])


def _edge(text: str, voice: str, out: str) -> str:
    import edge_tts

    async def go():
        await edge_tts.Communicate(text, voice, rate="+6%").save(out)

    asyncio.run(asyncio.wait_for(go(), timeout=40))
    return out


def _gtts(text: str, lang: str, out: str) -> str:
    from gtts import gTTS
    gTTS(text=text, lang="ar" if lang == "ar" else "en").save(out)
    return out


def _espeak(text: str, lang: str, out: str) -> str:
    exe = shutil.which("espeak-ng") or shutil.which("espeak")
    if not exe:
        raise RuntimeError("espeak-ng not installed")
    subprocess.run([exe, "-v", "ar" if lang == "ar" else "en-us", "-s", "165", "-w", out, text],
                   check=True, capture_output=True, timeout=60)
    return out


def _pyttsx3(text: str, out: str) -> str:
    import pyttsx3
    eng = pyttsx3.init()
    eng.save_to_file(text, out)
    eng.runAndWait()
    return out


def _silence(text: str, out: str) -> str:
    dur = max(2.0, len(text.split()) / 2.6)
    run_ff(["-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", f"{dur:.2f}", out])
    return out


def synthesize(text: str, lang: str, out_wav: str, voice: Optional[str] = None) -> str:
    """Return provider name; writes a normalised mono WAV to out_wav."""
    base = out_wav[:-4]
    voices = ([voice] if voice else []) + [v for v in VOICES.get(lang, VOICES["en"]) if v != voice]
    providers = []
    if not resolver.offline():
        providers += [(f"edge-tts:{v}", (lambda v=v: _edge(text, v, f"{base}_{v}.mp3"))) for v in voices[:2]]
        providers.append(("gtts", lambda: _gtts(text, lang, f"{base}_g.mp3")))
    providers += [
        ("espeak-ng", lambda: _espeak(text, lang, f"{base}_e.wav")),
        ("pyttsx3", lambda: _pyttsx3(text, f"{base}_p.wav")),
        ("silence", lambda: _silence(text, f"{base}_s.wav")),
    ]

    def valid(path):
        return path and os.path.exists(path) and os.path.getsize(path) > 1500 and media_duration(path) > 0.4

    name, path = resolver.run_chain("tts", providers, validate=valid)
    _to_wav(path, out_wav)
    if media_duration(out_wav) < 0.4:  # silenceremove ate everything -> keep raw
        run_ff(["-i", path, "-ac", "1", "-ar", "44100", out_wav])
    return name


# --------------------------------------------------------------------------- #
# Visual generation chain
# --------------------------------------------------------------------------- #
def cover_fit(img: Image.Image, w: int = SRC_W, h: int = SRC_H) -> Image.Image:
    img = img.convert("RGB")
    scale = max(w / img.width, h / img.height)
    img = img.resize((max(w, int(img.width * scale + 0.5)), max(h, int(img.height * scale + 0.5))), Image.LANCZOS)
    left, top = (img.width - w) // 2, (img.height - h) // 2
    return img.crop((left, top, left + w, top + h))


def _validate_image(data: bytes) -> Image.Image:
    if len(data) < 8_000:
        raise ValueError("image too small")
    img = Image.open(io.BytesIO(data))
    img.load()
    if img.width < 256 or img.height < 256:
        raise ValueError("image resolution too low")
    return img


def _pollinations(prompt: str, seed: int, template: str) -> Image.Image:
    if not resolver.pollinations_slot():
        raise RuntimeError("free slot cooling down (1 image / 45 s)")
    url = template.format(prompt=urllib.parse.quote(prompt[:380]), w=768, h=1344, seed=seed)
    headers = {}
    if os.environ.get("POLLINATIONS_TOKEN"):  # optional free registered key
        headers["Authorization"] = "Bearer " + os.environ["POLLINATIONS_TOKEN"]
    r = resolver.request_with_retry("GET", url, attempts=1, timeout=50, headers=headers)
    if r.status_code == 402:
        m = re.search(r"every (\d+) seconds", r.text)
        resolver.pollinations_backoff(float(m.group(1)) if m else 46)
        raise RuntimeError("HTTP 402 FREE_LIMIT")
    if r.status_code != 200 or not r.headers.get("content-type", "").startswith("image"):
        raise RuntimeError(f"HTTP {r.status_code}")
    return _validate_image(r.content)


_STOP = set("""a an the and or of to in on for with without is are was were be been your you my our their this
that these those how why what when who which make makes made get gets best top tips ways thing things about into
from by at as it its can will just more most very really secret secrets nobody tells people smartest""".split())


def keywords(text: str) -> list[str]:
    """Search queries from most to least specific, e.g. 'octopus ocean' -> ['octopus ocean','octopus','ocean']."""
    words = [w for w in re.findall(r"[^\W\d_]{3,}", text.lower()) if w not in _STOP]
    words = list(dict.fromkeys(words))[:4]
    out = []
    if len(words) >= 2:
        out.append(" ".join(words[:2]))
    out += sorted(words, key=len, reverse=True)
    return out or [text[:30]]


_OV_CACHE: dict[str, list] = {}
_OV_LOCK = __import__("threading").Lock()
_USED_URLS: set[str] = set()
CREDITS: list[dict] = []


def _openverse(query: str, idx: int) -> Image.Image:
    for q in keywords(query):
        with _OV_LOCK:
            if q not in _OV_CACHE:
                r = resolver.request_with_retry(
                    "GET", resolver.OPENVERSE_API, attempts=2, timeout=20,
                    params={"q": q, "page_size": 20, "aspect_ratio": "tall", "mature": "false",
                            "license_type": "commercial,modification"})
                _OV_CACHE[q] = r.json().get("results", []) if r.ok else []
            results = list(_OV_CACHE[q])
        for item in results[idx % 5:] + results[: idx % 5]:
            url = item.get("url")
            with _OV_LOCK:
                if not url or url in _USED_URLS:
                    continue
                _USED_URLS.add(url)
            try:
                img_r = resolver.request_with_retry("GET", url, attempts=1, timeout=15)
                if img_r.ok:
                    img = _validate_image(img_r.content)
                    CREDITS.append({"title": item.get("title"), "creator": item.get("creator"),
                                    "license": f"CC {item.get('license', '').upper()} {item.get('license_version', '')}".strip(),
                                    "source": item.get("foreign_landing_url")})
                    return img
            except Exception:  # noqa: BLE001
                continue
    raise RuntimeError("no Openverse image")


def _wikimedia(query: str) -> Image.Image:
    for q in keywords(query):
        params = {"action": "query", "format": "json", "generator": "search", "gsrnamespace": 6,
                  "gsrsearch": f"{q} filetype:bitmap", "gsrlimit": 10, "prop": "imageinfo",
                  "iiprop": "url|size|mime|extmetadata", "iiurlwidth": 1080}
        r = resolver.request_with_retry("GET", resolver.WIKIMEDIA_API, params=params, attempts=2, timeout=20)
        pages = list((r.json().get("query") or {}).get("pages", {}).values()) if r.ok else []
        pages.sort(key=lambda p: -((p.get("imageinfo") or [{}])[0].get("height", 0)
                                   / max(1, (p.get("imageinfo") or [{}])[0].get("width", 1))))
        for p in pages:
            info = (p.get("imageinfo") or [{}])[0]
            url = info.get("thumburl") or info.get("url")
            if info.get("mime") not in ("image/jpeg", "image/png", "image/webp") or not url:
                continue
            with _OV_LOCK:
                if url in _USED_URLS:
                    continue
                _USED_URLS.add(url)
            img_r = resolver.request_with_retry("GET", url, attempts=1, timeout=20)
            if img_r.ok:
                img = _validate_image(img_r.content)
                meta = info.get("extmetadata") or {}
                CREDITS.append({"title": p.get("title"), "creator": re.sub("<[^>]+>", "", (meta.get("Artist") or {}).get("value", ""))[:80],
                                "license": (meta.get("LicenseShortName") or {}).get("value", ""),
                                "source": info.get("descriptionurl")})
                return img
    raise RuntimeError("no suitable Commons image")


def procedural_art(seed: int, w: int = SRC_W, h: int = SRC_H) -> Image.Image:
    """High-contrast animated-looking gradient art; fully offline."""
    rnd = random.Random(seed)
    c1, c2 = PALETTES[seed % len(PALETTES)]
    small_w, small_h = w // 4, h // 4
    grad = Image.new("RGB", (small_w, small_h))
    px = grad.load()
    ang = rnd.uniform(0, math.pi)
    ca, sa = math.cos(ang), math.sin(ang)
    for y in range(small_h):
        for x in range(small_w):
            t = ((x / small_w - .5) * ca + (y / small_h - .5) * sa) + .5
            t = min(1, max(0, t))
            px[x, y] = tuple(int(c1[i] * (1 - t) + c2[i] * t) for i in range(3))
    img = grad.resize((w, h), Image.BICUBIC)
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    for _ in range(14):
        r = rnd.randint(w // 10, w // 2)
        x, y = rnd.randint(-r, w), rnd.randint(-r, h)
        col = (255, 255, 255, rnd.randint(18, 55)) if rnd.random() < .6 else (*c1, rnd.randint(40, 90))
        d.ellipse((x, y, x + r, y + r), fill=col)
    for _ in range(6):
        y = rnd.randint(0, h)
        d.line((0, y, w, y + rnd.randint(-400, 400)), fill=(255, 255, 255, 40), width=rnd.randint(3, 14))
    overlay = overlay.filter(ImageFilter.GaussianBlur(28))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    return img


def make_visual(scene: dict, idx: int, out_path: str, topic_seed: int) -> str:
    seed = (topic_seed + idx * 7919) % 2_000_000_000
    providers = []
    if not resolver.offline():
        for j, tpl in enumerate(resolver.IMAGE_ENDPOINTS):
            providers.append((f"pollinations#{j}", lambda tpl=tpl: _pollinations(scene["visual"], seed, tpl)))
        kw = scene.get("keyword") or scene["visual"][:60]
        if re.search(r"[A-Za-z]{3,}", kw):  # stock search needs English keywords
            providers.append(("openverse", lambda: _openverse(kw, idx)))
            providers.append(("wikimedia", lambda: _wikimedia(kw)))
    providers.append(("procedural", lambda: procedural_art(seed)))
    name, img = resolver.run_chain(f"image#{idx}", providers, validate=lambda i: i is not None)
    img = cover_fit(img)
    if name != "procedural":  # subtle grade for subtitle legibility
        shade = Image.new("RGB", img.size, (0, 0, 0))
        img = Image.blend(img, shade, 0.12)
    img.save(out_path, quality=92)
    return name


# --------------------------------------------------------------------------- #
# Subtitles / kinetic typography
# --------------------------------------------------------------------------- #
def chunk_words(text: str, size: int = 3) -> list[str]:
    words = text.split()
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= size or re.search(r"[.!?،؟:;]$", w):
            chunks.append(" ".join(cur))
            cur = []
    if cur:
        chunks.append(" ".join(cur))
    return chunks or [text]


def render_caption(text: str, lang: str, out_path: str, workdir: Path, *, accent=(255, 214, 0),
                   size: int = 92, y_center: float = 0.66, boxed: bool = True) -> None:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    font = get_font(lang, size, workdir)
    kw = _draw_kwargs(lang)
    upper = text if lang == "ar" else text.upper()
    lines = wrap_text(upper, font, W - 160, lang)
    line_h = int(size * (1.5 if lang == "ar" else 1.25))
    total = line_h * len(lines)
    y0 = int(H * y_center - total / 2)
    shaped = [shape(line, lang) for line in lines]
    widths = [d.textlength(s, font=font, **kw) for s in shaped]
    if boxed:  # draw every box first so no box can cover a previous line
        pad = 22
        for i, tw in enumerate(widths):
            x, y = (W - tw) / 2, y0 + i * line_h
            d.rounded_rectangle((x - pad, y - 8, x + tw + pad, y + line_h + 2), radius=26, fill=(0, 0, 0, 150))
    for i, (s, tw) in enumerate(zip(shaped, widths)):
        d.text(((W - tw) / 2, y0 + i * line_h), s, font=font, fill=(255, 255, 255, 255), stroke_width=6,
               stroke_fill=(0, 0, 0, 255), **kw)
    y = y0 + total
    # accent underline bar = kinetic emphasis
    d.rounded_rectangle((W / 2 - 90, y + 14, W / 2 + 90, y + 26), radius=6, fill=(*accent, 255))
    img.save(out_path)


# --------------------------------------------------------------------------- #
# Scene + final assembly
# --------------------------------------------------------------------------- #
MOTIONS = ["zoom_in", "pan_up", "zoom_out", "pan_left", "zoom_in_tl", "pan_right"]


def _zoompan(motion: str, frames: int) -> str:
    n = max(frames - 1, 1)
    p = f"(on/{n})"
    z, x, y = "1.0", "(iw-iw/zoom)/2", "(ih-ih/zoom)/2"
    if motion == "zoom_in":
        z = f"1.0+0.16*{p}"
    elif motion == "zoom_out":
        z = f"1.16-0.16*{p}"
    elif motion == "zoom_in_tl":
        z, x, y = f"1.0+0.14*{p}", f"(iw-iw/zoom)*0.3", f"(ih-ih/zoom)*0.3"
    elif motion == "pan_up":
        z, y = "1.12", f"(ih-ih/zoom)*(1-{p})"
    elif motion == "pan_left":
        z, x = "1.12", f"(iw-iw/zoom)*(1-{p})"
    elif motion == "pan_right":
        z, x = "1.12", f"(iw-iw/zoom)*{p}"
    return f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={W}x{H}:fps={FPS}"


@dataclass
class SceneAsset:
    idx: int
    text: str
    image: str = ""
    audio: str = ""
    duration: float = 0.0
    voice_provider: str = ""
    image_provider: str = ""
    captions: list = field(default_factory=list)  # (png, start, end)


def render_scene(a: SceneAsset, out: str, offset: float, total: float, motion: str, is_hook: bool,
                 hook_png: Optional[str]) -> None:
    frames = int(round(a.duration * FPS))
    inputs = ["-i", a.image]
    for png, _, _ in a.captions:
        inputs += ["-i", png]
    hook_idx = None
    if is_hook and hook_png:
        inputs += ["-i", hook_png]
        hook_idx = len(a.captions) + 1
    inputs += ["-i", a.audio]
    audio_idx = len(a.captions) + 1 + (1 if hook_idx else 0)
    fg = [f"[0:v]{_zoompan(motion, frames)},setsar=1,format=yuv420p[bg]"]
    last = "bg"
    if hook_idx:
        fg.append(f"[{last}][{hook_idx}:v]overlay=0:0:enable='lt(t,{min(2.4, a.duration):.2f})'[vh]")
        last = "vh"
    for i, (_, st, en) in enumerate(a.captions, start=1):
        tag = f"v{i}"
        fg.append(f"[{last}][{i}:v]overlay=0:0:enable='between(t,{st:.3f},{en:.3f})'[{tag}]")
        last = tag
    # retention progress bar across the whole video
    fg.append(f"color=c=0xFFD600:s={W}x12:r={FPS}[bar]")
    fg.append(f"[{last}][bar]overlay=x='-W+W*(t+{offset:.3f})/{total:.3f}':y=0:shortest=1[vout]")
    fg.append(f"[{audio_idx}:a]apad,atrim=0:{a.duration:.3f},aformat=sample_rates=44100:channel_layouts=stereo[aout]")
    args = inputs + ["-filter_complex", ";".join(fg), "-map", "[vout]", "-map", "[aout]",
                     "-t", f"{a.duration:.3f}", "-r", str(FPS),
                     "-c:v", "libx264", "-preset", os.environ.get("RELAYMIND_PRESET", "veryfast"),
                     "-crf", "22", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", out]
    run_ff(args, timeout=240)


def build_video(script: dict, out_dir: str = "output", voice: Optional[str] = None) -> dict:
    t0 = time.time()
    lang = script.get("lang", "en")
    outp = Path(out_dir)
    work = outp / "work"
    work.mkdir(parents=True, exist_ok=True)
    topic_seed = int(hashlib.sha256(script["title"].encode()).hexdigest()[:8], 16)
    scenes = [SceneAsset(i, s["text"]) for i, s in enumerate(script["scenes"])]

    # 1) voices + visuals in parallel (network-bound); visuals are time-boxed
    with cf.ThreadPoolExecutor(max_workers=4) as tts_pool, cf.ThreadPoolExecutor(IMAGE_WORKERS) as img_pool:
        tts_f = {tts_pool.submit(synthesize, a.text, lang, str(work / f"a{a.idx}.wav"), voice): a for a in scenes}
        img_f = {img_pool.submit(make_visual, script["scenes"][a.idx], a.idx, str(work / f"i{a.idx}.jpg"),
                                 topic_seed): a for a in scenes}
        for f, a in tts_f.items():
            a.audio = str(work / f"a{a.idx}.wav")
            a.voice_provider = f.result()
            a.duration = round(media_duration(a.audio) + 0.35, 3)
        deadline = t0 + IMAGE_BUDGET_S
        for f, a in img_f.items():
            a.image = str(work / f"i{a.idx}.jpg")
            try:
                a.image_provider = f.result(timeout=max(1, deadline - time.time()))
            except Exception as exc:  # noqa: BLE001  timeout or chain failure -> local art
                log.warning("visual %d fell back to procedural: %s", a.idx, exc)
                cover_fit(procedural_art(topic_seed + a.idx)).save(a.image, quality=92)
                a.image_provider = "procedural(timeout)"
        img_pool.shutdown(wait=False, cancel_futures=True)
    log.info("assets ready in %.1fs", time.time() - t0)

    # 2) captions (kinetic word-chunks timed by character weight)
    accent_cycle = [(255, 214, 0), (0, 229, 255), (255, 64, 129), (118, 255, 3)]
    for a in scenes:
        chunks = chunk_words(a.text, 3)
        weights = [max(len(c), 4) for c in chunks]
        speak = max(a.duration - 0.35, 0.5)
        t = 0.0
        for k, (c, wgt) in enumerate(zip(chunks, weights)):
            span = speak * wgt / sum(weights)
            png = str(work / f"c{a.idx}_{k}.png")
            render_caption(c, lang, png, work, accent=accent_cycle[(a.idx + k) % 4])
            end = a.duration if k == len(chunks) - 1 else t + span
            a.captions.append((png, t, end))
            t += span
    hook_png = str(work / "hook.png")
    render_caption(script.get("title", "")[:70], lang, hook_png, work, size=78, y_center=0.2,
                   accent=(255, 255, 255))

    # 3) render scenes
    total = sum(a.duration for a in scenes)
    parts, offset = [], 0.0
    for a in scenes:
        part = str(work / f"s{a.idx}.mp4")
        render_scene(a, part, offset, total, MOTIONS[a.idx % len(MOTIONS)], a.idx == 0, hook_png)
        parts.append(part)
        offset += a.duration
    log.info("scenes rendered in %.1fs", time.time() - t0)

    # 4) concat + loudness normalisation (EBU R128, -14 LUFS for social)
    lst = work / "concat.txt"
    lst.write_text("".join(f"file '{Path(p).resolve().as_posix()}'\n" for p in parts))
    joined = str(work / "joined.mp4")
    run_ff(["-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", joined])
    final = str(outp / "final_short.mp4")
    run_ff(["-i", joined, "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
            "-ar", "44100", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", final])
    # poster frame for previews
    Image.open(scenes[0].image).resize((540, 960)).save(str(outp / "poster.jpg"), quality=85)

    return {
        "video": final,
        "duration": round(media_duration(final), 2),
        "size_mb": round(os.path.getsize(final) / 1_048_576, 2),
        "render_seconds": round(time.time() - t0, 1),
        "credits": CREDITS,
        "scenes": [{"idx": a.idx, "voice": a.voice_provider, "image": a.image_provider,
                    "duration": a.duration} for a in scenes],
    }
