from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ParsedFile:
    original_filename: str
    display_name: str
    quality: str | None = None
    languages: list[str] = field(default_factory=list)
    season: str | None = None
    episode: str | None = None
    episode_end: str | None = None
    missing_quality: bool = False
    missing_language: bool = False
    use_original_filename: bool = False
    file_size: int = 0
    mime_type: str | None = None
    use_original_filename: bool = False
    file_id: str | None = None
    file_unique_id: str | None = None
