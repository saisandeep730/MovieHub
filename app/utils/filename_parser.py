from __future__ import annotations

import os
import re
from logging import getLogger

from app.utils.filename_patterns import (
    DUAL_AUDIO_PATTERNS,
    MULTI_AUDIO_PATTERNS,
    QUALITY_MAP,
    QUALITY_PATTERNS,
    SEASON_PATTERNS,
    get_language_patterns,
)
from app.utils.filename_types import ParsedFile

logger = getLogger(__name__)


def _normalize(name: str) -> str:
    name = os.path.splitext(name)[0]
    name = re.sub(r"[._\*/&]", " ", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name


def _extract_se(normalized: str) -> tuple[str | None, str | None, str | None, str]:
    result = normalized
    season: str | None = None
    episode: str | None = None
    episode_end: str | None = None
    for pat in SEASON_PATTERNS:
        m = pat.search(result)
        if m:
            season = m.group(1).zfill(2)
            episode = m.group(2).zfill(2)
            episode_end = None
            if m.lastindex and m.lastindex > 2:
                for gi in range(3, m.lastindex + 1):
                    g = m.group(gi)
                    if g:
                        episode_end = g.zfill(2)
                        break
            result = pat.sub("", result, count=1)
            result = re.sub(r"\s+", " ", result).strip()
            break
    return season, episode, episode_end, result


def _extract_quality(normalized: str) -> tuple[str | None, str]:
    result = normalized
    for pat in QUALITY_PATTERNS:
        m = pat.search(result)
        if m:
            raw = m.group(1).lower()
            display = QUALITY_MAP.get(raw, raw)
            result = pat.sub("", result, count=1)
            result = re.sub(r"\s+", " ", result).strip()
            return display, result
    return None, result


def _detect_dual_multi(normalized: str) -> str | None:
    for pat in DUAL_AUDIO_PATTERNS:
        if pat.search(normalized):
            return "Dual Audio"
    for pat in MULTI_AUDIO_PATTERNS:
        if pat.search(normalized):
            return "Multi Audio"
    return None


def _detect_languages(normalized: str) -> tuple[list[str], str]:
    result = normalized
    found: list[str] = []
    for pat, display in get_language_patterns():
        m = pat.search(result)
        if m:
            found.append(display)
            result = pat.sub("", result, count=1)
            result = re.sub(r"\s+", " ", result).strip()
    seen: list[str] = []
    for lang in found:
        if lang not in seen:
            seen.append(lang)
    return seen, result


def _build_language_label(
    individual: list[str],
    audio_marker: str | None,
) -> str:
    if audio_marker:
        return audio_marker
    if len(individual) >= 3:
        return "Multi Audio"
    if len(individual) == 2:
        return f"{individual[0]} + {individual[1]}"
    if len(individual) == 1:
        return individual[0]
    return ""


def _build_display_name(
    quality: str | None,
    language_label: str,
    season: str | None,
    episode: str | None,
) -> str:
    parts: list[str] = []
    if season is not None and episode is not None:
        parts.append(f"S{season}E{episode}")
    parts.append(quality if quality else "\U0001F937")
    parts.append(language_label if language_label else "\U0001F937")
    return f'\U0001F3AC {" \u2022 ".join(parts)}'


def parse_filename(filename: str) -> ParsedFile:
    raw = filename.strip()
    if not raw:
        return ParsedFile(original_filename="", display_name="")

    normalized = _normalize(raw)

    season, episode, episode_end, after_se = _extract_se(normalized)

    quality, remaining = _extract_quality(after_se if after_se.strip() else normalized)
    missing_quality = quality is None

    audio_marker = _detect_dual_multi(remaining)

    individual_languages, _ = _detect_languages(remaining)
    language_label = _build_language_label(individual_languages, audio_marker)
    missing_language = not language_label

    display_name = _build_display_name(quality, language_label, season, episode)

    result_languages: list[str]
    if audio_marker:
        result_languages = [language_label]
    elif len(individual_languages) >= 3:
        result_languages = list(individual_languages)
    else:
        result_languages = list(individual_languages)

    return ParsedFile(
        original_filename=raw,
        display_name=display_name,
        quality=quality,
        languages=result_languages,
        season=season,
        episode=episode,
        episode_end=episode_end,
        missing_quality=missing_quality,
        missing_language=missing_language,
    )
