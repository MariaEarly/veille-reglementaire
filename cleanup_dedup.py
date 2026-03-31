#!/usr/bin/env python3
"""
One-time cleanup script: remove duplicates (multi-level) and re-apply off-topic filters
on existing data.json.
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(__file__))

from ingest import (
    normalize_title, normalize_title_short, normalize_url,
    is_off_topic_for_compliance, matches_compliance_keywords,
    CORE_COMPLIANCE_SOURCES, EXCLUDE_KEYWORDS, DATA_FILE, score_item, apply_time_decay,
    detect_doc_type, classify_action
)


def _pick_best(existing, candidate):
    """Return the better item to keep (higher score, or early_brief flag)."""
    if candidate.get("early_brief") and not existing.get("early_brief"):
        return candidate
    if candidate.get("score", 0) > existing.get("score", 0):
        return candidate
    return existing


def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = data["items"]
    total_before = len(items)
    print(f"Before cleanup: {total_before} items")

    # --- Pass 1a: Title-based dedup (10 words, keep highest-score) ---
    by_title = {}
    for item in items:
        norm = normalize_title(item.get("title", ""))
        if not norm:
            norm = item.get("hash", "")
        if norm not in by_title:
            by_title[norm] = item
        else:
            by_title[norm] = _pick_best(by_title[norm], item)

    after_title = list(by_title.values())
    dup_title = total_before - len(after_title)
    print(f"Pass 1a (title 10-word dedup): removed {dup_title} -> {len(after_title)} items")

    # --- Pass 1b: URL-path dedup ---
    by_url = {}
    no_url = []
    for item in after_title:
        url = normalize_url(item.get("url", ""))
        if not url:
            no_url.append(item)
            continue
        if url not in by_url:
            by_url[url] = item
        else:
            by_url[url] = _pick_best(by_url[url], item)

    after_url = list(by_url.values()) + no_url
    dup_url = len(after_title) - len(after_url)
    print(f"Pass 1b (URL-path dedup): removed {dup_url} -> {len(after_url)} items")

    # --- Pass 1c: Short title dedup (6 words, cross-source) ---
    by_short = {}
    for item in after_url:
        norm_short = normalize_title_short(item.get("title", ""))
        if not norm_short or len(norm_short) <= 20:
            # Too short to be meaningful — keep it, use hash as key
            by_short[item.get("hash", id(item))] = item
            continue
        if norm_short not in by_short:
            by_short[norm_short] = item
        else:
            by_short[norm_short] = _pick_best(by_short[norm_short], item)

    after_short = list(by_short.values())
    dup_short = len(after_url) - len(after_short)
    print(f"Pass 1c (short 6-word cross-source dedup): removed {dup_short} -> {len(after_short)} items")

    # --- Pass 2: Re-apply off-topic filters ---
    clean = []
    noise_removed = 0
    for item in after_short:
        title = item.get("title", "")
        summary = item.get("summary", "")
        source = item.get("source_name", "")
        combined = f"{title} {summary}".lower()

        if item.get("early_brief"):
            clean.append(item)
            continue

        if any(ex in combined for ex in EXCLUDE_KEYWORDS):
            noise_removed += 1
            continue

        if is_off_topic_for_compliance(title, summary, source):
            noise_removed += 1
            continue

        if source not in CORE_COMPLIANCE_SOURCES:
            if not matches_compliance_keywords(title, summary):
                noise_removed += 1
                continue

        clean.append(item)

    print(f"Pass 2 (noise filter): removed {noise_removed} off-topic -> {len(clean)} items")

    # --- Pass 3: Re-score ---
    for item in clean:
        title = item.get("title", "")
        summary = item.get("summary", "")
        category = item.get("category", "")
        published = item.get("published", "")

        base_score, breakdown = score_item(title, summary, category)
        final_score, decay_label = apply_time_decay(base_score, published)
        item["score"] = final_score
        item["score_breakdown"] = f"{breakdown} | {decay_label}"

        if "doc_type" not in item:
            item["doc_type"] = detect_doc_type(title)
            item["action_class"] = classify_action(item["doc_type"], title, final_score)

    _geo_prio = {"autorite_fr": 3, "autorite_eu": 2, "jurisprudence": 2, "autorite_intl": 1, "presse": 0, "social": 0, "email": 0}
    clean.sort(key=lambda x: (x.get("score", 0), _geo_prio.get(x.get("category", ""), 0), x.get("published", "")), reverse=True)

    data["items"] = clean

    from datetime import datetime, timezone
    data["last_update"] = datetime.now(timezone.utc).isoformat()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)

    total_removed = total_before - len(clean)
    print(f"\nTotal removed: {total_removed} ({dup_title} title + {dup_url} URL + {dup_short} cross-source + {noise_removed} noise)")
    print(f"Final: {len(clean)} items")
    print(f"File size: {DATA_FILE.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
