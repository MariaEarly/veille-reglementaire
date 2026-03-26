from __future__ import annotations

from typing import Optional

KEYWORDS_CRITICAL = {
    "sanction", "sanctions", "gel des avoirs", "embargo", "liste noire", "blacklist",
    "terrorist financing", "financement du terrorisme", "money laundering", "blanchiment",
    "fraude", "fraud", "corruption", "bribery"
}

KEYWORDS_HIGH = {
    "acpr", "amla", "eba", "esma", "fatf", "gafi", "tracfin", "amf",
    "lcb-ft", "aml", "cft", "mica", "dora", "dsp2", "psd2", "dme2",
    "emd2", "6amld", "amlr", "rgpd", "gdpr", "psan", "casp",
    "vigilance", "due diligence", "kyc", "know your customer",
    "ppe", "pep", "personne politiquement exposée",
    "déclaration de soupçon", "suspicious transaction",
    "conformité", "compliance", "régulateur", "regulator",
    "agrément", "license", "autorisation", "supervision"
}

KEYWORDS_MEDIUM = {
    "risque", "risk", "contrôle interne", "internal control",
    "audit", "inspection", "mise en demeure", "enforcement",
    "amende", "fine", "pénalité", "penalty",
    "directive", "règlement", "regulation",
    "consultation", "guideline", "orientations",
    "crypto", "actif numérique", "digital asset",
    "paiement", "payment", "prestataire", "provider",
    "établissement de crédit", "credit institution",
    "banque", "bank", "assurance", "insurance"
}

SOURCE_BONUS = {
    "autorité_fr": 15,
    "autorité_eu": 12,
    "autorité_intl": 10,
    "presse": 3,
    "blog": 0,
    "social": 0,
}

# Social noise patterns: posts matching these are excluded at ingestion
SOCIAL_NOISE_PATTERNS = {
    # Events / webinars
    "join us", "register now", "inscription", "webinar", "webinaire",
    "conférence", "conference", "save the date", "événement", "event",
    "rendez-vous", "participez",
    # HR / recruitment
    "hiring", "recrutement", "we're hiring", "nous recrutons",
    "offre d'emploi", "job", "careers", "rejoignez",
    # Corporate comms / PR
    "happy new year", "bonne année", "meilleurs vœux", "season's greetings",
    "anniversary", "anniversaire", "team photo", "photo d'équipe",
    # Reposts / engagement bait
    "rt @", "retweet", "share if", "partagez si", "like if",
    "follow us", "suivez-nous", "abonnez-vous",
}

SOCIAL_SCORE_CAP = 25


def is_social_noise(title: str, raw_text: Optional[str] = None) -> bool:
    """Check if a social media post is noise (events, HR, reposts, PR)."""
    text = f"{title} {raw_text or ''}".lower()
    for pattern in SOCIAL_NOISE_PATTERNS:
        if pattern in text:
            return True
    return False


def score_item(
    title: str,
    raw_text: Optional[str] = None,
    source_type: Optional[str] = None,
    source_category: Optional[str] = None
) -> int:
    """
    Score an item based on keywords and source category.

    Base: 5 points
    Keywords: +20 (critical), +10 (high), +5 (medium) per hit, capped per category
    Source bonus: based on category mapping
    Social sources: capped at SOCIAL_SCORE_CAP (25) — detection only, not validation
    Max: 100
    """
    text = f"{title} {raw_text or ''}".lower()
    score = 5

    # Count critical keyword hits (capped at 1 per category)
    critical_hits = 0
    for kw in KEYWORDS_CRITICAL:
        if kw in text:
            critical_hits += 1
    if critical_hits > 0:
        score += min(critical_hits, 1) * 20

    # Count high keyword hits (capped at 2 per category)
    high_hits = 0
    for kw in KEYWORDS_HIGH:
        if kw in text:
            high_hits += 1
    if high_hits > 0:
        score += min(high_hits, 2) * 10

    # Count medium keyword hits (capped at 3 per category)
    medium_hits = 0
    for kw in KEYWORDS_MEDIUM:
        if kw in text:
            medium_hits += 1
    if medium_hits > 0:
        score += min(medium_hits, 3) * 5

    # Add source category bonus
    if source_category and source_category in SOURCE_BONUS:
        score += SOURCE_BONUS[source_category]

    # Social sources: cap score — they are detection signals, not validated sources
    if source_type == "social":
        score = min(score, SOCIAL_SCORE_CAP)

    # Cap at 100
    return min(score, 100)
