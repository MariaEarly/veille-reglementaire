#!/usr/bin/env python3
"""
Veille Réglementaire — Script d'ingestion CLI.
Utilisé par GitHub Actions pour le cron d'ingestion.
Produit un data.json consommé par le dashboard statique.
"""

import json, os, hashlib, re, time, urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

# On réutilise les constantes et fonctions du serveur
# pour éviter la duplication, on importe directement
import importlib.util

SCRIPT_DIR = Path(__file__).parent
DATA_FILE = SCRIPT_DIR / "data.json"

# ---------------------------------------------------------------------------
# SOURCES (identique à veille_server.py)
# ---------------------------------------------------------------------------
SEED_SOURCES = [
    # Autorités FR
    {"name": "AMF - Actualités", "url": "https://www.amf-france.org/fr/flux-rss/display/21", "type": "rss", "category": "autorite_fr"},
    {"name": "AMF - Mises en garde", "url": "https://www.amf-france.org/fr/flux-rss/display/28", "type": "rss", "category": "autorite_fr"},
    {"name": "Tracfin", "url": "https://www.economie.gouv.fr/tracfin/rss", "type": "rss", "category": "autorite_fr"},
    {"name": "DGCCRF", "url": "https://www.economie.gouv.fr/dgccrf/rss", "type": "rss", "category": "autorite_fr"},
    {"name": "DG Trésor", "url": "https://www.tresor.economie.gouv.fr/Flux/Atom/Articles/Home", "type": "rss", "category": "autorite_fr"},
    {"name": "CNIL", "url": "https://www.cnil.fr/fr/rss.xml", "type": "rss", "category": "autorite_fr"},
    {"name": "ANSSI - Alertes", "url": "https://www.cert.ssi.gouv.fr/feed/", "type": "rss", "category": "autorite_fr"},
    # Autorités EU
    {"name": "EBA - European Banking Authority", "url": "https://www.eba.europa.eu/rss.xml", "type": "rss", "category": "autorite_eu"},
    {"name": "ECB - Banking Supervision", "url": "https://www.bankingsupervision.europa.eu/rss/press.html", "type": "rss", "category": "autorite_eu"},
    {"name": "ECB - Press Releases", "url": "https://www.ecb.europa.eu/rss/press.html", "type": "rss", "category": "autorite_eu"},
    {"name": "ECB - Blog", "url": "https://www.ecb.europa.eu/rss/blog.html", "type": "rss", "category": "autorite_eu"},
    {"name": "EDPB - European Data Protection Board", "url": "https://www.edpb.europa.eu/rss_en", "type": "rss", "category": "autorite_eu"},
    {"name": "AMLA - Anti-Money Laundering Authority", "url": "https://www.amla.europa.eu/node/19/rss_en", "type": "rss", "category": "autorite_eu"},
    {"name": "ESMA - European Securities and Markets Authority", "url": "https://www.esma.europa.eu/rss.xml", "type": "rss", "category": "autorite_eu"},
    {"name": "Europol", "url": "https://www.europol.europa.eu/cms/api/rss/news", "type": "rss", "category": "autorite_eu"},
    {"name": "Eurojust", "url": "https://www.eurojust.europa.eu/rss.xml", "type": "rss", "category": "autorite_eu"},
    {"name": "Commission EU - Press", "url": "https://ec.europa.eu/commission/presscorner/api/rss?language=en&pageSize=50", "type": "rss", "category": "autorite_eu"},
    # International
    {"name": "BIS - Speeches", "url": "https://www.bis.org/doclist/cbspeeches.rss", "type": "rss", "category": "autorite_intl"},
    {"name": "BIS - Working Papers", "url": "https://www.bis.org/doclist/wppubls.rss", "type": "rss", "category": "autorite_intl"},
    {"name": "OFAC (US Treasury)", "url": "https://ofac.treasury.gov/rss.xml", "type": "rss", "category": "autorite_intl"},
    {"name": "OpenSanctions", "url": "https://www.opensanctions.org/changelog/rss/", "type": "rss", "category": "autorite_intl"},
    # Justice FR
    {"name": "PNF (Parquet National Financier)", "url": "https://social.numerique.gouv.fr/@pnf.rss", "type": "rss", "category": "autorite_fr"},
    {"name": "Ministère de la Justice (CJIP)", "url": "https://www.justice.gouv.fr/rss.xml", "type": "rss", "category": "autorite_fr"},
    # JORF / Legifrance
    {"name": "JORF - Lois", "url": "https://legifrss.org/latest?nature=LOI", "type": "rss", "category": "autorite_fr"},
    {"name": "JORF - Blanchiment", "url": "https://legifrss.org/latest?q=blanchiment", "type": "rss", "category": "autorite_fr"},
    {"name": "JORF - Financier", "url": "https://legifrss.org/latest?q=financier", "type": "rss", "category": "autorite_fr"},
    {"name": "JORF - Bancaire", "url": "https://legifrss.org/latest?q=bancaire", "type": "rss", "category": "autorite_fr"},
    {"name": "JORF - Gel des avoirs", "url": "https://legifrss.org/latest?q=gel+des+avoirs", "type": "rss", "category": "autorite_fr"},
    {"name": "JORF - Crypto/PSAN", "url": "https://legifrss.org/latest?q=crypto", "type": "rss", "category": "autorite_fr"},
    # Presse spécialisée
    {"name": "Les Echos Finance", "url": "https://www.lesechos.fr/rss/rss_finance.xml", "type": "press", "category": "presse"},
    {"name": "Le Monde Économie", "url": "https://www.lemonde.fr/economie/rss_full.xml", "type": "press", "category": "presse"},
    {"name": "FinCrime Central", "url": "https://fincrimecentral.com/feed/", "type": "press", "category": "presse"},
    {"name": "Financial Crime News", "url": "https://thefinancialcrimenews.com/feed/", "type": "press", "category": "presse"},
    {"name": "GAFI/FATF Statements", "url": "https://www.fatf-gafi.org/rss/fatf-news.xml", "type": "rss", "category": "autorite_intl"},
]

# ---------------------------------------------------------------------------
# SCORING (identique à veille_server.py)
# ---------------------------------------------------------------------------
KEYWORDS_CRITICAL = [
    "sanction", "blanchiment", "money laundering", "terrorism financing",
    "financement du terrorisme", "fraude", "fraud", "gel des avoirs",
    "asset freeze", "liste noire", "blacklist", "embargo",
    "déclaration de soupçon", "suspicious transaction"
]
KEYWORDS_HIGH = [
    "acpr", "amf", "tracfin", "lcb-ft", "aml", "cft", "kyc",
    "vigilance", "due diligence", "conformité", "compliance",
    "mica", "dora", "psan", "casp", "crypto", "eba", "esma",
    "fatf", "gafi", "anti-money", "5amld", "6amld", "amla",
    "code monétaire", "agrément", "établissement de crédit",
    "contrôle prudentiel", "résolution bancaire",
]
KEYWORDS_MEDIUM = [
    "risque", "risk", "audit", "contrôle interne", "internal control",
    "directive", "règlement", "regulation", "supervisory",
    "fintech", "regtech", "paiement", "payment", "banque", "bank",
    "identité numérique", "digital identity", "ppe", "pep",
    "correspondant bancaire", "correspondent banking",
]
SOURCE_BONUS = {"autorite_fr": 15, "autorite_eu": 12, "autorite_intl": 10, "presse": 3, "email": 8}

COMPLIANCE_KEYWORDS = [
    "lcb-ft", "aml", "blanchiment", "money laundering", "sanction",
    "conformité", "compliance", "fraude", "fraud", "régulat",
    "acpr", "amf", "tracfin", "fatf", "gafi", "kyc", "vigilance",
    "crypto", "psan", "dora", "gel des avoirs", "terroris",
    "anti-money", "financement du terrorisme", "embargo",
    "supervisory", "banking supervision", "eba", "esma",
    "lutte contre le blanchiment", "abus de marché", "market abuse",
    "devoir de vigilance", "loi sapin", "lanceur d'alerte",
    "whistleblow", "beneficial owner", "bénéficiaire effectif",
    "asset freeze", "liste noire", "blacklist", "amla",
    "prudenti", "solvabilité", "solvency", "capital requirement",
    "payment service", "services de paiement", "monnaie électronique",
    "e-money", "financement participatif", "crowdfunding",
    "code monétaire", "code monétaire et financier",
    "établissement de crédit", "agrément", "autorisation",
    "prestataire de services d'investissement",
    "démarchage bancaire", "intermédiation bancaire",
    "contrôle prudentiel", "résolution bancaire",
    "abus de marché", "délit d'initié", "insider",
    "obligation de déclaration", "personne politiquement exposée",
    "dispositif lcb", "organe de contrôle",
    "jorf", "journal officiel",
    # AMF enforcement actions
    "composition administrative", "commission des sanctions",
    "sanction disciplinaire", "manquement", "grief",
    # Banking instruments
    "chèques irréguliers", "fichier national des chèques",
    "interdit bancaire", "fcc", "ficp",
]

_REGEX_KEYWORDS = [
    re.compile(r'\bmica\b(?![\s-]*center)', re.IGNORECASE),
]

CORE_COMPLIANCE_SOURCES = {
    "AMF - Mises en garde",
    "Tracfin",
    "OFAC (US Treasury)",
    "PNF (Parquet National Financier)",
    "JORF - Blanchiment",
    "JORF - Gel des avoirs",
    "GAFI/FATF Statements",
    "FinCrime Central",
    "Financial Crime News",
    "AMLA - Anti-Money Laundering Authority",
    "ESMA - European Securities and Markets Authority",
}
# Sources qui passent mais avec filtre léger (keyword compliance)
# AMF Actualités, EBA, ECB, ANSSI, etc. = doivent matcher des keywords

# Mots-clés d'exclusion : si présents dans titre+summary, l'article est rejeté
EXCLUDE_KEYWORDS = [
    # Conventions collectives / droit du travail
    "convention collective", "accords départementaux", "accords régionaux",
    "extension d'accords", "extension d'un avenant", "portant extension",
    "ouvriers employés par les entreprises du bâtiment",
    "branche ferroviaire", "ferroviaire",
    "travail dissimulé", "droit du travail", "code du travail",
    "livraison de repas", "coursiers", "livreurs",
    "sécurité sociale", "retraite complémentaire",
    # Macroéconomie / conjoncture
    "flash conjoncture", "conjoncture pays", "conjoncture france",
    "réserves de change", "réserves nettes", "réserves officielles",
    "interconnexions électriques", "transition énergétique",
    "commerce extérieur", "investissement en construction",
    "croissance modérée", "production dans l'industrie",
    "nucléaire",
    # Tech changelogs
    "format change", "changelog", "release notes",
    # Épargne / investisseurs particuliers (pas compliance)
    "épargne salariale", "épargne retraite", "guide pédagogique de l'épargne",
    "baromètre", "investisseurs particuliers", "tableau de bord des investisseurs",
    # AMF corporate HR
    "égalité femmes-hommes", "index égalité",
    # DG Trésor hors périmètre
    "base industrielle", "industrie de défense",
    "objectif afrique", "prêt garanti par l'état",
    # DGCCRF consumer protection
    "date butoir", "pratiques commerciales", "intermarché", "supermarché",
    "grande distribution", "centrale d'achats",
    # ESG/durabilité (sauf si aussi compliance)
    "durabilité", "préférences de durabilité", "esg",
    "risques climatiques", "climate risk", "nature-related",
    # IP
    "propriété intellectuelle", "contrefaçon", "anti-contrefaçon",
    # CVE / vulnérabilités techniques (bruit ANSSI)
    "vulnérabilité dans", "vulnérabilités dans", "multiples vulnérabilités",
    "bulletin d'actualité certfr",
    # Divers hors périmètre
    "jeux olympiques", "paralympiques",
    "inauguration", "laboratory", "laboratoire",
    "book review", "thriller",
    # Géopolitique générale sans lien compliance
    "standing with ukraine", "resilience, growth and stability",
    "small island developing",
]


def score_item(title, text, category):
    combined = f"{title} {text}".lower()
    s = 0
    if any(k in combined for k in KEYWORDS_CRITICAL):
        s += 20
    hits = sum(1 for k in KEYWORDS_HIGH if k in combined)
    s += min(hits, 2) * 10
    hits = sum(1 for k in KEYWORDS_MEDIUM if k in combined)
    s += min(hits, 3) * 5
    s += SOURCE_BONUS.get(category, 0)
    return min(s, 100)


# ---------------------------------------------------------------------------
# CLASSIFICATION
# ---------------------------------------------------------------------------
def detect_doc_type(title):
    """Détecte le type de texte réglementaire à partir du titre."""
    t = title.lower().strip()
    if t.startswith("décret") or "décret n°" in t or "décret du" in t:
        return "DÉCRET"
    if t.startswith("arrêté") or "arrêté du" in t:
        return "ARRÊTÉ"
    if t.startswith("avis") or "avis du" in t or "avis de" in t:
        return "AVIS"
    if t.startswith("ordonnance") or "ordonnance n°" in t:
        return "ORDONNANCE"
    if t.startswith("loi") or "loi n°" in t:
        return "LOI"
    if t.startswith("directive") or "directive (ue)" in t:
        return "DIRECTIVE"
    if t.startswith("règlement") or "règlement (ue)" in t or "règlement délégué" in t:
        return "RÈGLEMENT"
    if any(k in t for k in ["communiqué", "press release", "communiqué de presse"]):
        return "COMMUNIQUÉ"
    if any(k in t for k in ["consultation", "appel à contribution", "call for"]):
        return "CONSULTATION"
    if any(k in t for k in ["sanction", "mise en garde", "warning", "décision de la commission"]):
        return "SANCTION"
    if any(k in t for k in ["lignes directrices", "guidelines", "orientations"]):
        return "GUIDELINES"
    if any(k in t for k in ["rapport", "report", "étude", "study"]):
        return "RAPPORT"
    return None


def classify_action(doc_type, title, score):
    """Classifie un article : 'action' (nécessite une action) ou 'info' (informatif)."""
    t = title.lower()
    # Types qui nécessitent typiquement une action
    action_types = {"DÉCRET", "ARRÊTÉ", "ORDONNANCE", "LOI", "DIRECTIVE", "RÈGLEMENT", "SANCTION"}
    if doc_type in action_types:
        return "action"
    # Mots-clés d'action dans le titre
    action_words = [
        "obligation", "mise en demeure", "entrée en vigueur", "date limite",
        "nouvelles exigences", "new requirements", "doit", "must",
        "amende", "fine", "pénalité", "penalty", "interdiction",
    ]
    if any(w in t for w in action_words):
        return "action"
    # Consultations = action (il faut potentiellement répondre)
    if doc_type == "CONSULTATION":
        return "action"
    return "info"


def matches_compliance_keywords(title, text):
    combined = f"{title} {text}".lower()
    if any(k in combined for k in COMPLIANCE_KEYWORDS):
        return True
    full = f"{title} {text}"
    if any(pat.search(full) for pat in _REGEX_KEYWORDS):
        return True
    return False


def is_off_topic_for_compliance(title, summary, source_name):
    """
    Filter out articles that are off-topic for financial compliance (LCB-FT, sanctions, AML).
    Returns True if the article should be excluded.
    """
    combined = f"{title} {summary}".lower()
    src = source_name.lower()

    # ── AMF: exclude investor education, corporate news, savings guides ──
    if "amf" in src:
        off_topic = [
            "baromètre", "investisseurs particuliers", "éducation financière",
            "égalité femmes-hommes", "index égalité", "gender", "rh", "ressources humaines",
            "épargne salariale", "épargne retraite", "guide pédagogique",
            "fonds commun", "sicav", "lettre epargne info",
            "typologie des intervenants", "typologie des acteurs",
        ]
        if any(k in combined for k in off_topic):
            return True

    # ── DG Trésor: exclude macro/industrial/geopolitics ──
    if "trésor" in src or "tresor" in src:
        off_topic = [
            "réserves de change", "réserves nettes", "réserves officielles",
            "base industrielle", "industrie de défense", "conjoncture", "croissance",
            "flash conjoncture", "commerce extérieur", "investissement en construction",
            "production dans l'industrie", "objectif afrique", "interconnexions",
            "nucléaire", "transition énergétique", "propriété intellectuelle",
            "prêt garanti", "label isr", "g7 finances",
        ]
        if any(k in combined for k in off_topic):
            return True

    # ── OpenSanctions: exclude technical changelogs ──
    if "opensanctions" in src:
        off_topic = ["format change", "changelog", "release notes", "version", "update"]
        if any(k in combined for k in off_topic):
            return True

    # ── DGCCRF: ALL content excluded (consumer protection, not financial compliance) ──
    if "dgccrf" in src:
        return True

    # ── BIS Speeches: exclude unless specifically about AML/sanctions/supervision/compliance ──
    if "bis" in src and "speech" in src:
        must_match = [
            "money laundering", "blanchiment", "sanction", "aml", "cft",
            "compliance", "conformité", "supervision", "prudenti",
            "anti-money", "terrorist financing", "financement du terrorisme",
            "lcb", "kyc", "due diligence", "fatf", "gafi",
            "stablecoin", "crypto", "digital currency", "cbdc",
            "payment", "paiement", "bank regulation", "capital requirement",
            "resolution", "deposit insurance", "systemic risk",
        ]
        if not any(k in combined for k in must_match):
            return True

    # ── ECB speeches/interviews: exclude general macro, keep supervision-specific ──
    if "ecb" in src:
        # Exclude climate/nature/general speeches
        off_topic = [
            "climate", "nature", "biodiversity", "green transition",
            "competitiveness", "competition", "growth and stability",
        ]
        if any(k in combined for k in off_topic):
            if not any(k in combined for k in ["supervision", "prudenti", "aml", "compliance", "sanction"]):
                return True

    # ── ANSSI: only keep DORA/NIS2/compliance-related alerts ──
    if "anssi" in src:
        must_match = [
            "dora", "nis2", "nis 2", "directive nis", "résilience opérationnelle",
            "opérateur d'importance vitale", "oiv", "secteur bancaire",
            "secteur financier", "note d'alerte", "alerte de sécurité",
        ]
        # Exclude generic CVE bulletins
        generic_cve = ["vulnérabilité dans", "vulnérabilités dans", "bulletin d'actualité certfr"]
        if any(k in combined for k in generic_cve):
            if not any(k in combined for k in must_match):
                return True

    # ── Le Monde / Les Echos: exclude labor law, consumer, general economics ──
    if "le monde" in src or "les echos" in src:
        off_topic = [
            "travail dissimulé", "droit du travail", "livraison",
            "coursiers", "livreurs", "foodora", "deliveroo", "uber eats",
            "grève", "manifestation", "retraite", "chômage",
        ]
        if any(k in combined for k in off_topic):
            return True

    # ── JORF Sanctions / JORF Lois: exclude conventions collectives, non-financial ──
    if "jorf" in src:
        off_topic = [
            "convention collective", "portant extension", "accords départementaux",
            "accords régionaux", "branche ferroviaire", "bâtiment",
            "jeux olympiques", "paralympiques", "sport",
        ]
        if any(k in combined for k in off_topic):
            return True

    # ── Financial Crime News: exclude book reviews, non-news ──
    if "financial crime" in src or "fincrime" in src:
        off_topic = ["thriller", "book review", "novel", "fiction"]
        if any(k in combined for k in off_topic):
            return True

    # ── ESMA: only keep compliance/enforcement/MiCA/market abuse ──
    if "esma" in src:
        must_match = [
            "aml", "money laundering", "blanchiment", "sanction", "compliance",
            "conformité", "mica", "dora", "market abuse", "abus de marché",
            "enforcement", "supervisory", "supervision", "investor protection",
            "crypto", "sustainable finance", "benchmark", "transparency",
            "short selling", "prospectus", "mifid", "emir", "ucits", "aifmd",
            "guidelines", "consultation", "q&a", "opinion", "technical standard",
        ]
        if not any(k in combined for k in must_match):
            return True

    # ── Europol: only keep financial crime related ──
    if "europol" in src:
        must_match = [
            "money laundering", "financial crime", "fraud", "terrorism financing",
            "asset recovery", "cryptocurrency", "dark web", "cybercrime",
            "sanctions", "organised crime", "criminal network", "blanchiment",
        ]
        if not any(k in combined for k in must_match):
            return True

    # ── Commission EU: only keep sanctions/AML/financial regulation ──
    if "commission eu" in src:
        must_match = [
            "sanction", "restrictive measures", "anti-money laundering", "aml",
            "financial services", "banking", "payment", "crypto", "mica", "dora",
            "capital markets", "market abuse", "compliance", "regulation",
        ]
        if not any(k in combined for k in must_match):
            return True

    return False


def item_hash(title, url):
    return hashlib.sha1(f"{title}|{url}".encode()).hexdigest()[:16]


def summarize_item(title, summary, source_name):
    """Generate AI-powered 1-line French summary for compliance relevance."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return None

    try:
        prompt = (
            f"Écris UNE phrase de max 100 caractères, en français, sans markdown ni formatage. "
            f"Explique en quoi cet article concerne la conformité financière. "
            f"Si non pertinent, écris 'Hors périmètre compliance'. "
            f"Titre: {title}\nRésumé: {summary[:300]}\nSource: {source_name}"
        )

        payload = {
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": 150,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            method="POST"
        )

        response = urllib.request.urlopen(req, timeout=10)
        result = json.loads(response.read().decode("utf-8"))

        if result.get("content") and len(result["content"]) > 0:
            return result["content"][0].get("text", "").strip()
        return None

    except Exception as e:
        print(f"    AI summary error for '{title[:50]}...': {e}")
        return None


# ---------------------------------------------------------------------------
# DATA
# ---------------------------------------------------------------------------
def load_data():
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"sources": [], "items": [], "last_update": None}


def save_data(data):
    data["last_update"] = datetime.now(timezone.utc).isoformat()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


# ---------------------------------------------------------------------------
# INGESTION
# ---------------------------------------------------------------------------
def fetch_rss(url, source_name, source_type, category):
    import feedparser
    import urllib.request
    import urllib.parse

    try:
        # Encode URL properly (handle accented characters like è in query params)
        parsed = urllib.parse.urlparse(url)
        safe_url = urllib.parse.urlunparse(parsed._replace(
            path=urllib.parse.quote(parsed.path, safe='/'),
            query=urllib.parse.quote(parsed.query, safe='=&+')
        ))
        # Timeout 15s par flux pour éviter les workflows GitHub Actions trop longs
        req = urllib.request.Request(safe_url, headers={"User-Agent": "EarlyBrief-Veille/1.0"})
        response = urllib.request.urlopen(req, timeout=15)
        feed = feedparser.parse(response.read())
    except Exception as e:
        print(f"  Timeout/error {source_name}: {e}")
        return []

    items = []
    for entry in feed.entries[:50]:
        title = getattr(entry, "title", "") or ""
        link = getattr(entry, "link", "") or ""
        author = getattr(entry, "author", "") or ""
        summary = getattr(entry, "summary", "") or ""
        summary_clean = re.sub(r"<[^>]+>", "", summary)[:500]

        if not title.strip() or title == "Sans titre":
            words = summary_clean.split()
            title = " ".join(words[:12]) + ("…" if len(words) > 12 else "") if words else "Sans titre"

        published = None
        for attr in ("published_parsed", "updated_parsed"):
            tp = getattr(entry, attr, None)
            if tp:
                try:
                    published = datetime(*tp[:6]).isoformat()
                except Exception:
                    pass
                break
        if not published:
            published = datetime.now(timezone.utc).isoformat()

        # Exclure le bruit évident (conventions collectives, etc.)
        combined_lower = f"{title} {summary_clean}".lower()
        if any(ex in combined_lower for ex in EXCLUDE_KEYWORDS):
            continue

        # Source-specific off-topic filter (applies to ALL sources)
        if is_off_topic_for_compliance(title, summary_clean, source_name):
            continue

        # Non-core sources must also match compliance keywords
        if source_name not in CORE_COMPLIANCE_SOURCES:
            if not matches_compliance_keywords(title, summary_clean):
                continue

        sc = score_item(title, summary_clean, category)
        doc_type = detect_doc_type(title)
        action_class = classify_action(doc_type, title, sc)

        items.append({
            "hash": item_hash(title, link),
            "source_name": source_name,
            "source_type": source_type,
            "category": category,
            "title": title,
            "url": link,
            "author": author,
            "published": published,
            "summary": summary_clean,
            "score": sc,
            "doc_type": doc_type,
            "action_class": action_class,
            "status": "new",
            "early_brief": False,
            "ai_summary": None,
        })

    return items


def seed_sources(data):
    existing_urls = {s["url"] for s in data["sources"]}
    added = 0
    for src in SEED_SOURCES:
        if src["url"] not in existing_urls:
            data["sources"].append({
                "name": src["name"],
                "url": src["url"],
                "type": src["type"],
                "category": src["category"],
                "active": True,
            })
            added += 1
    return added


def ingest_all(data):
    new_count = 0
    existing_hashes = {it["hash"] for it in data["items"]}

    for src in data["sources"]:
        if not src.get("active", True):
            continue
        print(f"  Fetching: {src['name']}...")
        items = fetch_rss(src["url"], src["name"], src["type"], src["category"])
        for item in items:
            if item["hash"] not in existing_hashes:
                data["items"].append(item)
                existing_hashes.add(item["hash"])
                new_count += 1
        print(f"    -> {len(items)} parsed, {new_count} new")

    # Also scrape non-RSS sources
    try:
        from scraper import scrape_all
        print("\n  --- HTML Scraping ---")
        scraped = scrape_all()
        for item in scraped:
            if item["hash"] not in existing_hashes:
                data["items"].append(item)
                existing_hashes.add(item["hash"])
                new_count += 1
        print(f"    -> {len(scraped)} scraped, {new_count} total new")
    except ImportError:
        print("  scraper.py not found, skipping HTML scraping")
    except Exception as e:
        print(f"  Scraper error: {e}")

    return new_count


def prune_old_items(data, max_age_days=30):
    """Supprime les articles de plus de max_age_days jours (sauf early_brief)."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=max_age_days)).isoformat()
    before = len(data["items"])
    data["items"] = [
        it for it in data["items"]
        if it.get("early_brief") or it.get("published", "") >= cutoff
    ]
    removed = before - len(data["items"])
    if removed:
        print(f"  Pruned {removed} articles older than {max_age_days} days")
    return removed


# ---------------------------------------------------------------------------
# RETROACTIVE PURGE — clean existing items against current filters
# ---------------------------------------------------------------------------
def _should_purge_existing(item):
    """Returns True if an existing item should be removed (off-topic)."""
    title = item.get("title", "")
    summary = item.get("summary", "")
    source = item.get("source_name", "")
    combined = f"{title} {summary}".lower()

    # 1. AI already flagged as off-topic
    ai = (item.get("ai_summary") or "").lower()
    if "hors périmètre" in ai or "non pertinent" in ai or "pas pertinent" in ai:
        # Don't purge if user marked as early_brief
        if not item.get("early_brief"):
            return True

    # 2. Matches current EXCLUDE_KEYWORDS
    if any(ex in combined for ex in EXCLUDE_KEYWORDS):
        if not item.get("early_brief"):
            return True

    # 3. Matches source-specific off-topic filter
    if is_off_topic_for_compliance(title, summary, source):
        if not item.get("early_brief"):
            return True

    # 4. Non-core sources that don't match compliance keywords
    if source not in CORE_COMPLIANCE_SOURCES:
        if not matches_compliance_keywords(title, summary):
            if not item.get("early_brief"):
                return True

    return False


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print(f"Veille Réglementaire — Ingestion {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)

    data = load_data()
    print(f"Loaded: {len(data['sources'])} sources, {len(data['items'])} existing items")

    # Seed sources if needed
    added = seed_sources(data)
    if added:
        print(f"Seeded {added} new sources")

    # Enrich existing items with new fields (doc_type, action_class)
    enriched = 0
    for item in data["items"]:
        if "doc_type" not in item:
            item["doc_type"] = detect_doc_type(item.get("title", ""))
            item["action_class"] = classify_action(item["doc_type"], item.get("title", ""), item.get("score", 0))
            enriched += 1
        item.setdefault("ai_summary", None)
        # Reset summaries that are too long (bad prompt from v1)
        if item.get("ai_summary") and len(item["ai_summary"]) > 150:
            item["ai_summary"] = None
    if enriched:
        print(f"Enriched {enriched} existing items with doc_type/action_class")

    # Purge existing off-topic items (retroactive filter cleanup)
    before_purge = len(data["items"])
    data["items"] = [
        it for it in data["items"]
        if not _should_purge_existing(it)
    ]
    purged = before_purge - len(data["items"])
    if purged:
        print(f"Purged {purged} off-topic items from existing data")

    # Ingest
    new_count = ingest_all(data)
    print(f"\nIngested {new_count} new articles")

    # AI summarization: process items without ai_summary (limit to 50 per run for cost control)
    items_to_summarize = [
        item for item in data["items"]
        if item.get("ai_summary") is None
    ][:50]
    if items_to_summarize:
        print(f"\nGenerating AI summaries for {len(items_to_summarize)} items...")
        for idx, item in enumerate(items_to_summarize, 1):
            summary_result = summarize_item(
                item.get("title", ""),
                item.get("summary", ""),
                item.get("source_name", "")
            )
            if summary_result:
                item["ai_summary"] = summary_result
                print(f"  [{idx}/{len(items_to_summarize)}] {item['source_name']}: {summary_result[:60]}...")
            else:
                print(f"  [{idx}/{len(items_to_summarize)}] {item['source_name']}: skipped")
            time.sleep(0.1)  # Brief delay between calls

    # Prune old articles to keep data.json manageable
    prune_old_items(data, max_age_days=30)

    # Sort by score desc for the dashboard
    data["items"].sort(key=lambda x: x.get("score", 0), reverse=True)

    # Save
    save_data(data)
    print(f"\nSaved: {len(data['items'])} total articles")
    print(f"File size: {DATA_FILE.stat().st_size / 1024:.1f} KB")
    print("Done.")


if __name__ == "__main__":
    main()
