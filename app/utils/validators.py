import re
import unicodedata


def normalize_title(title: str) -> str:
    """Normalize a movie title for consistent search and indexing.

    - Lowercase
    - Strip leading/trailing whitespace
    - Collapse multiple spaces
    - Remove punctuation except hyphens and apostrophes
    - Normalize unicode characters (NFKC)
    """
    normalized = unicodedata.normalize("NFKC", title)
    normalized = normalized.lower().strip()
    normalized = re.sub(r"[^\w\s\-']", "", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized


def sanitize_search_query(query: str) -> str:
    """Prepare a user query for text search by removing noise characters."""
    cleaned = unicodedata.normalize("NFKC", query)
    cleaned = re.sub(r"[^\w\s]", "", cleaned)
    cleaned = cleaned.strip().lower()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned
