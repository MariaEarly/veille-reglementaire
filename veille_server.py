#!/usr/bin/env python3
"""
Veille RÃ©glementaire â Serveur tout-en-un.
Un seul fichier Python : serveur HTTP, ingestion RSS, scoring, stockage JSON.
Fonctionne en local ET en dÃ©ploiement cloud (Render, Railway, etc.)
"""

import json, os, hashlib, re, time, html, base64
from datetime import datetime, timezone, timedelta
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
PORT = int(os.environ.get("PORT", 8001))
HOST = os.environ.get("HOST", "0.0.0.0")
DATA_DIR = Path(__file__).parent
DB_FILE = DATA_DIR / "veille_data.json"
HTML_FILE = DATA_DIR / "veille_dashboard.html"

# Auth : dÃ©finir VEILLE_PASSWORD pour protÃ©ger l'accÃ¨s
# Ex: VEILLE_PASSWORD=mon_mot_de_passe
AUTH_PASSWORD = os.environ.get("VEILLE_PASSWORD", "")

# ---------------------------------------------------------------------------
# SOURCES
# ---------------------------------------------------------------------------
SEED_SOURCES = [
    # AutoritÃ©s FR
    {"name": "ACPR - DerniÃ¨res publications", "url": "https://acpr.banque-france.fr/rss", "type": "rss", "category": "autorite_fr"},
    {"name": "AMF - ActualitÃ©s", "url": "https://www.amf-france.org/fr/rss/actualites.xml", "type": "rss", "category": "autorite_fr"},
    {"name": "Tracfin", "url": "https://www.economie.gouv.fr/tracfin/rss", "type": "rss", "category": "autorite_fr"},
    {"name": "DGCCRF", "url": "https://www.economie.gouv.fr/dgccrf/rss", "type": "rss", "category": "autorite_fr"},
    {"name": "DG TrÃ©sor", "url": "https://www.tresor.economie.gouv.fr/rss", "type": "rss", "category": "autorite_fr"},
    {"name": "CNIL", "url": "https://www.cnil.fr/fr/rss.xml", "type": "rss", "category": "autorite_fr"},
    # AutoritÃ©s EU
    {"name": "EBA - European Banking Authority", "url": "https://www.eba.europa.eu/rss.xml", "type": "rss", "category": "autorite_eu"},
    {"name": "ESMA", "url": "https://www.esma.europa.eu/rss", "type": "rss", "category": "autorite_eu"},
    {"name": "ECB - Banking Supervision", "url": "https://www.bankingsupervision.europa.eu/rss/press.html", "type": "rss", "category": "autorite_eu"},
    {"name": "ECB - Press Releases", "url": "https://www.ecb.europa.eu/rss/press.html", "type": "rss", "category": "autorite_eu"},
    {"name": "ECB - Blog", "url": "https://www.ecb.europa.eu/rss/blog.html", "type": "rss", "category": "autorite_eu"},
    {"name": "EU - EUR-Lex Financial", "url": "https://eur-lex.europa.eu/RSSNewOJ", "type": "rss", "category": "autorite_eu"},
    {"name": "AMLA (EU AML Authority)", "url": "https://www.amla.europa.eu/rss.xml", "type": "rss", "category": "autorite_eu"},
    # International
    {"name": "FATF / GAFI", "url": "https://www.fatf-gafi.org/rss/fatf-news.xml", "type": "rss", "category": "autorite_intl"},
    {"name": "BIS - Bank for International Settlements", "url": "https://www.bis.org/doclist/pressrelease.rss", "type": "rss", "category": "autorite_intl"},
    {"name": "OFAC (US Treasury)", "url": "https://ofac.treasury.gov/rss.xml", "type": "rss", "category": "autorite_intl"},
    {"name": "Egmont Group (FIUs)", "url": "https://egmontgroup.org/feed/", "type": "rss", "category": "autorite_intl"},
    {"name": "OpenSanctions", "url": "https://www.opensanctions.org/changelog/rss/", "type": "rss", "category": "autorite_intl"},
    # Justice FR (PNF, PNACO)
    {"name": "PNF (Parquet National Financier)", "url": "https://social.numerique.gouv.fr/@pnf.rss", "type": "rss", "category": "autorite_fr"},
    {"name": "MinistÃ¨re de la Justice (CJIP)", "url": "https://www.justice.gouv.fr/rss.xml", "type": "rss", "category": "autorite_fr"},
    # Presse spÃ©cialisÃ©e (filtrÃ©e par mots-clÃ©s)
    {"name": "Les Echos Finance", "url": "https://www.lesechos.fr/rss/rss_finance.xml", "type": "press", "category": "presse"},
    {"name": "Le Monde Ãconomie", "url": "https://www.lemonde.fr/economie/rss_full.xml", "type": "press", "category": "presse"},
    {"name": "Reuters Financial Regulation", "url": "https://www.reuters.com/rssFeed/financial-regulation", "type": "press", "category": "presse"},
    {"name": "Compliance Week", "url": "https://www.complianceweek.com/rss", "type": "press", "category": "presse"},
    {"name": "FinCrime Central", "url": "https://fincrimecentral.com/feed/", "type": "press", "category": "presse"},
    {"name": "Financial Crime News", "url": "https://thefinancialcrimenews.com/feed/", "type": "press", "category": "presse"},
]

# ---------------------------------------------------------------------------
# SCORING
# ---------------------------------------------------------------------------
KEYWORDS_CRITICAL = [
    "sanction", "blanchiment", "money laundering", "terrorism financing",
    "financement du terrorisme", "fraude", "fraud", "gel des avoirs",
    "asset freeze", "liste noire", "blacklist", "embargo",
    "dÃ©claration de soupÃ§on", "suspicious transaction"
]
KEYWORDS_HIGH = [
    "acpr", "amf", "tracfin", "lcb-ft", "aml", "cft", "kyc",
    "vigilance", "due diligence", "conformitÃ©", "compliance",
    "mica", "dora", "psan", "casp", "crypto", "eba", "esma",
    "fatf", "gafi", "anti-money", "5amld", "6amld", "amla",
]
KEYWORDS_MEDIUM = [
    "risque", "risk", "audit", "contrÃ´le interne", "internal control",
    "directive", "rÃ¨glement", "regulation", "supervisory",
    "fintech", "regtech", "paiement", "payment", "banque", "bank",
    "identitÃ© numÃ©rique", "digital identity", "ppe", "pep",
    "correspondant bancaire", "correspondent banking",
]
SOURCE_BONUS = {"autorite_fr": 15, "autorite_eu": 12, "autorite_intl": 10, "presse": 3, "email": 8}

COMPLIANCE_KEYWORDS = [
    "lcb-ft", "aml", "blanchiment", "money laundering", "sanction",
    "conformitÃ©", "compliance", "fraude", "fraud", "rÃ©gulat",
    "acpr", "amf", "tracfin", "fatf", "gafi", "kyc", "vigilance",
    "crypto", "psan", "dora", "gel des avoirs", "terroris",
    "anti-money", "financement du terrorisme", "embargo",
    "supervisory", "banking supervision", "eba", "esma",
    "lutte contre le blanchiment", "abus de marchÃ©", "market abuse",
    "devoir de vigilance", "loi sapin", "lanceur d'alerte",
    "whistleblow", "beneficial owner", "bÃ©nÃ©ficiaire effectif",
    "asset freeze", "liste noire", "blacklist", "amla",
    "prudenti", "solvabilitÃ©", "solvency", "capital requirement",
    "payment service", "services de paiement", "monnaie Ã©lectronique",
    "e-money", "financement participatif", "crowdfunding",
]

# Patterns regex pour mots-clÃ©s ambigus (Ã©viter faux positifs)
import re as _re
_REGEX_KEYWORDS = [
    # MiCA : exiger contexte crypto/rÃ©glementaire, exclure "MICA Center" militaire
    _re.compile(r'\bmica\b(?![\s-]*center)', _re.IGNORECASE),
]

# Sources cÅur compliance : tout leur contenu est pertinent, pas de filtrage
CORE_COMPLIANCE_SOURCES = {
    "ACPR - DerniÃ¨res publications",
    "AMF - ActualitÃ©s",
    "Tracfin",
    "FATF / GAFI",
    "AMLA (EU AML Authority)",
    "OFAC (US Treasury)",
    "EBA - European Banking Authority",
    "ESMA",
    "ECB - Banking Supervision",
    "PNF (Parquet National Financier)",
}


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


def matches_compliance_keywords(title, text):
    """Retourne True si le titre/texte contient au moins un mot-clÃ© compliance."""
    combined = f{title} {text}".lower()
    if any(k in combined for k in COMPLIANCE_KEYWORDS):
        return True
    # VÃ©rification regex pour mots-clÃ©s ambigus (ex: "mica" mais pas "MICA Center")
    full = f"{title} {text}"
    if any(pat.search(full) for pat in _REGEX_KEYWORDS):
        return True
    return False


# ---------------------------------------------------------------------------
# DATA STORE (JSON file)
# ---------------------------------------------------------------------------
def load_data():
    if DB_FILE.exists():
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {"sources": [], "items": []}


def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def item_hash(title, url):
    return hashlib.sha1(f"{title}|{url}".encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# RSS INGESTION
# ---------------------------------------------------------------------------
def fetch_rss(url, source_name, source_type, category):
    try:
        import feedparser
    except ImportError:
        print("ERROR: feedparser not installed. Run: pip3 install feedparser")
        return []

    try:
        feed = feedparser.parse(url)
    except Exception as e:
        print(f"  Error fetching {source_name}: {e}")
        return []

    items = []
    for entry in feed.entries[:50]:
        title = getattr(entry, "title", "Sans titre") or "Sans titre"
        link = getattr(entry, "link", "") or ""
        author = getattr(entry, "author", "") or ""
        summary = getattr(entry, "summary", "") or ""
        summary_clean = re.sub(r"<[^>]+>", "", summary)[:500]

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

        # Filtrage : les sources cÅur compliance passent toujours,
        # toutes les autres doivent matcher au moins un mot-clÃ©
        if source_name not in CORE_COMPLIANCE_SOURCES:
            if not matches_compliance_keywords(title, summary_clean):
                continue

        sc = score_item(title, summary_clean, category)

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
            "status": "new",
            "early_brief": False,
        })

    return items


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
        print(f"    -> {len(items)} parsed, new items added so far: {new_count}")

    save_data(data)
    return new_count


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
    if added:
        save_data(data)
    return added


# ---------------------------------------------------------------------------
# HTTP SERVER
# ---------------------------------------------------------------------------
class VeilleHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        pass

    def _check_auth(self):
        """Check Basic Auth if VEILLE_PASSWORD is set. Returns True if OK."""
        if not AUTH_PASSWORD:
            return True
        auth_header = self.headers.get("Authorization", "")
        if not auth_header.startswith("Basic "):
            self._send_auth_required()
            return False
        try:
            decoded = base64.b64decode(auth_header[6:]).decode("utf-8")
            user, pwd = decoded.split(":", 1)
            if pwd == AUTH_PASSWORD:
                return True
        except Exception:
            pass
        self._send_auth_required()
        return False

    def _send_auth_required(self):
        self.send_response(401)
        self.send_header("WWW-Authenticate", 'Basic realm="Veille RÃ©glementaire"')
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"<h1>Mot de passe requis</h1>")

    def _json_response(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(length) if length else b""

    def do_GET(self):
        if not self._check_auth():
            return
\ÙYH\\ÙJÙ[]
B]H\ÙY]Ý\
ÈHÜÈ\ÈH\ÙWÜ\Ê\ÙY]Y\JBY]OHÈYSÑSK^\ÝÊ
NÛÛ[HSÑSKXYØ]\Ê
BÙ[Ù[Ü\ÜÛÙJ
BÙ[Ù[ÚXY\ÛÛ[U\H^Ú[ÈÚ\Ù]]]NBÙ[Ù[ÚXY\ÛÛ[S[ÝÝ[ÛÛ[
JJBÙ[Ù[ÚXY\ØXÚKPÛÛÛËXØXÚKË\ÝÜK]\Ý\][Y]HBÙ[[ÚXY\Ê
BÙ[Ù[KÜ]JÛÛ[
B[ÙNÙ[Ù[Ù\Ü

\ÚØ\SÝÝ[B]\]HHØYÙ]J
BY]OHØ\KÚ][\È][\ÈH]VÈ][\ÈB][\ËÛÜ
Ù^O[[XHÙ]
ØÛÜH
K]\ÙOUYJBÙ[ÚÛÛÜ\ÜÛÙJ][\ÊB]\Y]OHØ\KÚ][\ËÜÙX\ÚHH\ËÙ]
HÈJVÌKÝÙ\
B][\ÈHÚHÜH[]VÈ][\ÈHYH[VÈ]HKÝÙ\
HÜH[KÙ]
Ý[[X\HKÝÙ\
WB][\ËÛÜ
Ù^O[[XHÙ]
ØÛÜH
K]\ÙOUYJBÙ[ÚÛÛÜ\ÜÛÙJ][\ÊB]\Y]OHØ\KÜÛÝ\Ù\ÈÙ[ÚÛÛÜ\ÜÛÙJ]VÈÛÝ\Ù\ÈJB]\Y]OHØ\KÙX\KXYY][\ÈHÚÜH[]VÈ][\ÈHYKÙ]
X\WØYYWB][\ËÛÜ
Ù^O[[XHÙ]
ØÛÜH
K]\ÙOUYJBÙ[ÚÛÛÜ\ÜÛÙJ][\ÊB]\Y]OHØ\KÙYÙ\Ý^\ÈH[
\ËÙ]
^\ÈÍ×JVÌJBÝ]ÙH
]][YKÝÊ[Y^ÛK]ÊHH[YY[J^\ÏY^\ÊJK\ÛÙÜX]

BXÙ[HÚHÜH[]VÈ][\ÈHYKÙ]
X\ÚYHHÝ]ÙBXÙ[ÛÜ
Ù^O[[XHÙ]
ØÛÜH
K]\ÙOUYJBÙ[ÚÛÛÜ\ÜÛÙJÂ\[ÙÙ^\È^\ËÛÝ[[XÙ[
KÜÚ][\ÈXÙ[ÎKJB]\Ù[Ù[Ù\Ü

BY×ÔÔÕ
Ù[NYÝÙ[ØÚXÚ×Ø]]

N]\\ÙYH\\ÙJÙ[]
B]H\ÙY]Ý\
ÈB]HHØYÙ]J
BY]OHØ\KÜÙYYYYHÙYYÜÛÝ\Ù\Ê]JBÙ[ÚÛÛÜ\ÜÛÙJÈYYYYJB]\Y]OHØ\KÚ[Ù\Ý]×ØÛÝ[H[Ù\ÝØ[
]JBÙ[ÚÛÛÜ\ÜÛÙJÈ]×Ú][\È]×ØÛÝ[Ý[[]VÈ][\ÈJ_JB]\Y]OHØ\KÜÛÝ\Ù\ÈÙHHÛÛØYÊÙ[ÜXYØÙJ
JB]VÈÛÝ\Ù\ÈK\[
Â[YHÙKÙ]
[YHÝ\ÝÛHK\ÙKÙ]
\K\HÙKÙ]
\HÜÈKØ]YÛÜHÙKÙ]
Ø]YÛÜH\ÜÙHKXÝ]HYKJBØ]WÙ]J]JBÙ[ÚÛÛÜ\ÜÛÙJÈÚÈY_JB]\Y]OHØ\KÚ][\ÈÙHHÛÛØYÊÙ[ÜXYØÙJ
JB][\ÈHÙHY\Ú[Ý[ÙJÙK\Ý
H[ÙHØÙWB^\Ý[×Ú\Ú\ÈHÚ]È\ÚHÜ][]VÈ][\È_BYYHÜ][H[][\ÎH][KÙ]
ish") or item_hash(item.get("title", ""), item.get("url", ""))
                if h not in existing_hashes:
                    item["hash"] = h"
                    item.setdefault("source_type", "email")
                    item.setdefault("category", "email")
                    item.setdefault("status", "new")
                    item.setdefault("early_brief", False)
                    if "score" not in item:
                        item["score"] = score_item(
                            item.get("title", ""),
                            item.get("summary", ""),
                            item.get("category", "email"),
                        )
                    data["items"].append(item)
                    existing_hashes.add(i)
                    added += 1
            if added:
                save_data(data)
            self._json_response({"added": added, "total": len(data["items"])})
            return

        self.send_error(404)

    def do_PATCH(self):
        if not self._check_auth():
            return

        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        data = load_data()

        if path.startswith("/api/items/"):
            item_id = path.split("/")[-1]
            body = json.loads(self._read_body())
            for item in data["items"]:
                if item["hash"] == item_id:
                    if "status" in body:
                        item["status"] = body["status"]
                    if "early_brief" in body:
                        item["early_brief"] = body["early_brief"]
                    save_data(data)
                    self._json_response(item)
                    return
            self.send_error(404, "Item not found")
            return

        self.send_error(404)

    def do_DELETE(self):
        if not self._check_auth():
            return

        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        data = load_data()

        if path.startswith("/api/sources/"):
            try:
                idx = int(path.split("/")[-1])
                if 0 <= idx < len(data["sources"]):
                    removed = data["sources"].pop(idx)
                    save_data(data)
                    self._json_response({"removed": removed["name"]})
                    return
            except (ValueError, IndexError):
                pass
            self.send_error(404, "Source not found")
            return

        self.send_error(404)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    data = load_data()
    if not data["sources"]:
        print("First run: seeding sources...")
        seed_sources(data)

    print(f"Veille RÃªglementaire  â http://{HOST}:{PORT}")
    print(f"  {len(data['sources'])} sources, {len(data['items'])} articles")
    if AUTH_PASSWORD:
        print("  Protected by password")
    print("  Ctrl+C to stop\n")

    server = HTTPServer((HOST, PORT), VeilleHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()


if __name__ == "__main__":
    main()
