from typing import Optional
import hashlib


def make_duplicate_group(title: str, url: Optional[str] = None) -> str:
    base = (title.strip().lower() + "|" + (url or "").strip().lower()).encode("utf-8")
    return hashlib.sha1(base).hexdigest()[:16]
