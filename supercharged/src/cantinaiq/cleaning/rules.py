"""Pure helpers for cleaning transformations (no Polars I/O)."""

from __future__ import annotations

import ast
import re

_YEAR_RE = re.compile(r"\b(19\d{2}|20\d{2})\b")


def parse_tuple_string(value: str) -> str:
    """Unwrap `"('Italy',)"` → `"Italy"`. Leave plain strings alone."""
    if not value:
        return ""
    s = value.strip()
    if s.startswith("(") and s.endswith(")"):
        try:
            parsed = ast.literal_eval(s)
        except (ValueError, SyntaxError):
            return s
        if isinstance(parsed, tuple) and parsed:
            return str(parsed[0])
    return s


_ENCODING_MAP: dict[str, str] = {
    "Ã«": "ë",
    "Ã¨": "è",
    "Ã©": "é",
    "Ã ": "à",
    "Ã¹": "ù",
    "Ã²": "ò",
    "Ã³": "ó",
    "Ã¬": "ì",
    "Ã­": "í",
    "Ãª": "ê",
    "Ã®": "î",
    "Ã´": "ô",
    "Ã»": "û",
    "Ã§": "ç",
    "Ã±": "ñ",
}


def fix_encoding(value: str) -> str:
    """Fix UTF-8-bytes-read-as-Latin-1 mojibake on diacritics."""
    if not value:
        return value
    out = value
    for bad, good in _ENCODING_MAP.items():
        out = out.replace(bad, good)
    return out


def normalise_wine_name(name: str) -> str:
    """Collapse whitespace and lowercase — for dedupe key construction."""
    if not name:
        return ""
    return " ".join(name.split()).lower()


def extract_vintage(name: str) -> int | None:
    """Pull a four-digit 19xx/20xx year out of a wine name, else None."""
    if not name:
        return None
    m = _YEAR_RE.search(name)
    return int(m.group(1)) if m else None
