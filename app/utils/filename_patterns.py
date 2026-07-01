from __future__ import annotations

import re

QUALITY_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b(4320p)\b", re.IGNORECASE),
    re.compile(r"\b(2160p)\b", re.IGNORECASE),
    re.compile(r"\b(1440p)\b", re.IGNORECASE),
    re.compile(r"\b(1080p)\b", re.IGNORECASE),
    re.compile(r"\b(720p)\b", re.IGNORECASE),
    re.compile(r"\b(576p)\b", re.IGNORECASE),
    re.compile(r"\b(480p)\b", re.IGNORECASE),
    re.compile(r"\b(360p)\b", re.IGNORECASE),
    re.compile(r"\b(240p)\b", re.IGNORECASE),
    re.compile(r"\b(4k)\b", re.IGNORECASE),
    re.compile(r"\b(8k)\b", re.IGNORECASE),
    re.compile(r"\b(uhd)\b", re.IGNORECASE),
]

QUALITY_MAP: dict[str, str] = {
    "240p": "240p",
    "360p": "360p",
    "480p": "480p",
    "576p": "576p",
    "720p": "720p",
    "1080p": "1080p",
    "1440p": "1440p",
    "2160p": "4K",
    "4k": "4K",
    "uhd": "4K",
    "4320p": "8K",
    "8k": "8K",
}

LANGUAGE_MAP: dict[str, str] = {
    "hindi": "Hindi",
    "hin": "Hindi",
    "english": "English",
    "eng": "English",
    "tamil": "Tamil",
    "tam": "Tamil",
    "telugu": "Telugu",
    "tel": "Telugu",
    "malayalam": "Malayalam",
    "mal": "Malayalam",
    "kannada": "Kannada",
    "kan": "Kannada",
    "japanese": "Japanese",
    "jap": "Japanese",
    "jp": "Japanese",
    "korean": "Korean",
    "kor": "Korean",
    "chinese": "Chinese",
    "chi": "Chinese",
    "chs": "Chinese",
    "cht": "Chinese",
    "spanish": "Spanish",
    "spa": "Spanish",
    "french": "French",
    "fre": "French",
    "fr": "French",
    "german": "German",
    "ger": "German",
    "de": "German",
    "turkish": "Turkish",
    "tur": "Turkish",
}

_LANG_SORTED: list[tuple[re.Pattern[str], str]] = sorted(
    [(re.compile(rf"\b{re.escape(k)}\b", re.IGNORECASE), v) for k, v in LANGUAGE_MAP.items()],
    key=lambda x: len(x[0].pattern),
    reverse=True,
)

def get_language_patterns() -> list[tuple[re.Pattern[str], str]]:
    return _LANG_SORTED

DUAL_AUDIO_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\bdual[\s_.*/&-]*audio\b", re.IGNORECASE),
    re.compile(r"\bdual\b", re.IGNORECASE),
]

MULTI_AUDIO_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\bmulti[\s_.*/&-]*audio\b", re.IGNORECASE),
    re.compile(r"\bmulti\b", re.IGNORECASE),
]

SEASON_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"\b[Ss](\d{1,2})\s*[Ee][Pp]\s*(\d{1,2})(?:\s*\u2013\s*(\d{1,2})|\s*-\s*(\d{1,2}))?\b"),
    re.compile(r"\b[Ss](\d{1,2})[Ee](\d{1,2})\b"),
    re.compile(r"\b[Ss]eason\s*(\d{1,2})\s*[Ee]pisode\s*(\d{1,2})\b"),
]
