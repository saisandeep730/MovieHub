import re


def format_file_size(size: int) -> str:
    """Format bytes into a human-readable file size string."""
    if size < 1024:
        return f"{size} B"
    elif size < 1024 ** 2:
        return f"{size / 1024:.1f} KB"
    elif size < 1024 ** 3:
        return f"{size / 1024 ** 2:.1f} MB"
    else:
        return f"{size / 1024 ** 3:.2f} GB"


QUALITY_PATTERNS: list[tuple[str, str]] = [
    (r"4k2160p|2160p|4k\b", "4K"),
    (r"1080p|full\s*hd|fhd", "1080p"),
    (r"720p|hd\b|hdrip", "720p"),
    (r"480p|dvdrip|webrip", "480p"),
    (r"360p", "360p"),
    (r"240p", "240p"),
    (r"144p", "144p"),
]


def detect_quality(filename: str) -> str | None:
    """Detect video quality from a filename using known patterns."""
    lower = filename.lower()
    for pattern, quality in QUALITY_PATTERNS:
        if re.search(pattern, lower):
            return quality
    return None


def parse_file_name(filename: str) -> dict:
    """Parse a Telegram filename into name, extension, and detected quality."""
    *name_parts, ext = filename.rsplit(".", 1) if "." in filename else [filename, ""]
    name = ".".join(name_parts) if name_parts else filename
    quality = detect_quality(filename)
    return {
        "name": name,
        "extension": ext.lower() if ext else "",
        "quality": quality,
    }


YEAR_PATTERN = re.compile(r"\b(19\d{2}|20\d{2})\b")


def extract_year(text: str) -> int | None:
    """Extract a 4-digit year from text, returning the first match or None."""
    match = YEAR_PATTERN.search(text)
    return int(match.group(1)) if match else None


async def generate_movie_id(movie_repo: any) -> str:
    """Generate the next sequential MovieHub ID (MH000001, MH000002, ...)."""
    count = await movie_repo.count()
    return f"MH{count + 1:06d}"
