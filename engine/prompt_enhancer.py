"""Silent prompt enhancer: raw idea -> viral short-form script + 9:16 visual prompts.

Primary: keyless Pollinations text API (OpenAI-compatible), then an optional custom
endpoint, then GitHub Models (retired 2026-07-30, kept as a last quick attempt).
Fallback: deterministic local template engine, so a script ALWAYS exists.
"""
from __future__ import annotations

import hashlib
import json
import logging
import re
from typing import Any

from . import resolver

log = logging.getLogger("relaymind.enhancer")

MIN_SCENES, MAX_SCENES = 4, 8

SYSTEM_PROMPT = """You are a world-class short-form video scriptwriter (TikTok, Reels, Shorts).
Turn the user's idea into a high-retention vertical video script of 25-45 seconds.
Rules:
- Scene 1 is a scroll-stopping HOOK (max 12 words): a bold claim, question or surprising fact.
- 5 to 7 scenes total. Each scene narration is 1-2 short spoken sentences (max 25 words).
- Build curiosity, deliver concrete value, end with a clear call to action.
- Write narration in LANGUAGE. Use simple conversational words.
- For each scene write "visual": a vivid English image prompt for a vertical 9:16 photo,
  cinematic lighting, no text, no logos, no watermarks.
- Also return "keyword": one or two English words describing the scene subject.
Return ONLY JSON: {"title": str, "hook": str, "scenes": [{"text": str, "visual": str, "keyword": str}],
"hashtags": [str], "caption": str}"""

LANG_NAMES = {"en": "English", "ar": "Egyptian-friendly Modern Standard Arabic"}

STYLE_SUFFIX = ", vertical 9:16 composition, cinematic lighting, ultra detailed, sharp focus, no text"


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.M).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, flags=re.S)
        if not m:
            raise
        return json.loads(m.group(0))


def normalize(script: dict[str, Any], topic: str, lang: str) -> dict[str, Any]:
    """Validate & repair any script (LLM or local) into the canonical schema."""
    scenes = []
    for s in script.get("scenes") or []:
        if isinstance(s, str):
            s = {"text": s}
        text = str(s.get("text") or s.get("narration") or "").strip()
        if not text:
            continue
        visual = str(s.get("visual") or s.get("image_prompt") or topic).strip()
        if "9:16" not in visual:
            visual += STYLE_SUFFIX
        scenes.append({"text": text[:260], "visual": visual[:400],
                       "keyword": str(s.get("keyword") or topic).strip()[:40]})
    hook = str(script.get("hook") or "").strip()
    if hook and scenes and hook[:20].lower() not in scenes[0]["text"].lower():
        scenes.insert(0, {"text": hook[:200], "visual": scenes[0]["visual"], "keyword": scenes[0]["keyword"]})
    if len(scenes) < MIN_SCENES:
        return local_script(topic, lang)
    scenes = scenes[:MAX_SCENES]
    tags = [("#" + t.lstrip("#").replace(" ", "")) for t in (script.get("hashtags") or []) if str(t).strip()]
    title = str(script.get("title") or topic).strip()[:90]
    return {
        "title": title,
        "hook": str(script.get("hook") or scenes[0]["text"]).strip(),
        "scenes": scenes,
        "hashtags": tags[:8] or ["#shorts", "#viral", "#learn"],
        "caption": str(script.get("caption") or title).strip()[:900],
        "lang": lang,
        "source": script.get("source", "llm"),
    }


# --------------------------------------------------------------------------- #
# Deterministic local fallback (no network)
# --------------------------------------------------------------------------- #
_EN = [
    "Stop scrolling: here is what nobody tells you about {t}.",
    "Most people get {t} completely wrong, and it costs them every single day.",
    "The first secret is simple: start small, but start today.",
    "Second, focus on the one action that gives you eighty percent of the results.",
    "Third, track your progress so every small win keeps you moving.",
    "Do this for just seven days and you will feel the difference with {t}.",
    "Follow for more, and share this with someone who needs it.",
]
_AR = [
    "استنى لحظة، ده اللي محدش بيقولك عليه عن {t}.",
    "معظم الناس بيفهموا {t} غلط، وده بيكلفهم كتير كل يوم.",
    "أول سر بسيط جدا: ابدأ صغير، لكن ابدأ النهارده.",
    "تاني حاجة: ركز على الخطوة الواحدة اللي بتجيب أغلب النتيجة.",
    "تالت حاجة: تابع تقدمك، وكل نجاح صغير هيدفعك لقدام.",
    "جرب ده سبع أيام بس، وهتحس بالفرق في {t}.",
    "تابعنا للمزيد، وابعت الفيديو ده لحد محتاجه.",
]
_VISUALS = [
    "dramatic close-up portrait of a person looking surprised, neon rim light",
    "moody cinematic street scene at blue hour, shallow depth of field",
    "hands planting a small seedling in rich soil, golden hour",
    "minimalist desk with a single glowing lamp, focused atmosphere",
    "upward staircase made of light in a dark futuristic space",
    "sunrise over a mountain summit, epic wide view",
    "crowd of happy people sharing phones, warm bokeh lights",
]


def local_script(topic: str, lang: str = "en") -> dict[str, Any]:
    t = topic.strip().rstrip(".!?؟")
    if lang == "en" and t[:1].isupper() and not t[:2].isupper():
        t = t[0].lower() + t[1:]
    t = t or ("هذا الموضوع" if lang == "ar" else "this topic")
    lines = _AR if lang == "ar" else _EN
    seed = int(hashlib.sha256(t.encode()).hexdigest(), 16)
    scenes = []
    for i, line in enumerate(lines):
        v = _VISUALS[(i + seed) % len(_VISUALS)]
        scenes.append({"text": line.format(t=t), "visual": f"{t}, {v}{STYLE_SUFFIX}", "keyword": t[:40]})
    return {
        "title": t[:90], "hook": scenes[0]["text"], "scenes": scenes,
        "hashtags": ["#shorts", "#reels", "#tips", "#" + re.sub(r"\W+", "", t)[:24] or "#learn"],
        "caption": scenes[0]["text"], "lang": lang, "source": "local",
    }


def enhance(topic: str, lang: str = "en", token: str = "") -> dict[str, Any]:
    """Return a normalized script dict. Never raises."""
    topic = (topic or "").strip()[:600] or "a surprising life hack"
    lang = lang if lang in LANG_NAMES else "en"
    # The browser may have pre-enhanced the idea and passed the JSON in TOPIC.
    if topic.startswith("{"):
        try:
            pre = _extract_json(topic)
            if pre.get("scenes"):
                pre.setdefault("source", "browser")
                return normalize(pre, pre.get("title", "video"), lang)
        except Exception:  # noqa: BLE001
            pass
    if not resolver.offline():
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT.replace("LANGUAGE", LANG_NAMES[lang])},
            {"role": "user", "content": f"Idea: {topic}"},
        ]
        try:
            model, content = resolver.chat_completion(messages, token)
            data = _extract_json(content)
            data["source"] = model
            script = normalize(data, topic, lang)
            log.info("script by %s: %d scenes", model, len(script["scenes"]))
            return script
        except Exception as exc:  # noqa: BLE001
            log.warning("LLM enhancement failed, using local fallback: %s", exc)
    return local_script(topic, lang)
