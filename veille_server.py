#!/usr/bin/env python3
"""
Veille Réglementaire — Serveur tout-en-un.
Un seul fichier Python : serveur HTTP, ingestion RSS, scoring, stockage JSON.
Fonctionne en local ET en déploiement cloud (Render, Railway, etc.)
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

# Auth : définir VEILLE_PASSWORD pour protéger l'accès
# Ex: VEILLE_PASSWORD=mon_mot_de_passe
AUTH_PASSWORD = os.environ.get("VEILLE_PASSWORD", "")

# ---------------------------------------------------------------------------
# SOURCES
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
    # International
    {"name": "BIS - Speeches", "url": "https://www.bis.org/doclist/cbspeeches.rss", "type": "rss", "category": "autorite_intl"},
    {"name": "BIS - Working Papers", "url": "https://www.bis.org/doclist/wppubls.rss", "type": "rss", "category": "autorite_intl"},
    {"name": "OFAC (US Treasury)", "url": "https://ofac.treasury.gov/rss.xml", "type": "rss", "category": "autorite_intl"},
    {"name": "OpenSanctions", "url": "https://www.opensanctions.org/changelog/rss/", "type": "rss", "category": "autorite_intl"},
    # Justice FR (PNF, PNACO)
    {"name": "PNF (Parquet National Financier)", "url": "https://social.numerique.gouv.fr/@pnf.rss", "type": "rss", "category": "autorite_fr"},
    {"name": "Ministère de la Justice (CJIP)", "url": "https://www.justice.gouv.fr/rss.xml", "type": "rss", "category": "autorite_fr"},
    # JORF / Legifrance (via legifrss.org — flux non-officiel fiable)
    {"name": "JORF - Lois", "url": "https://legifrss.org/latest?nature=LOI", "type": "rss", "category": "autorite_fr"},
    {"name": "JORF - Blanchiment", "url": "https://legifrss.org/latest?q=blanchiment", "type": "rss", "category": "autorite_fr"},
    {"name": "JORF - Financier", "url": "https://legifrss.org/latest?q=financier", "type": "rss", "category": "autorite_fr"},
    {"name": "JORF - Bancaire", "url": "https://legifrss.org/latest?q=bancaire", "type": "rss", "category": "autorite_fr"},
    {"name": "JORF - Sanctions financières", "url": "https://legifrss.org/latest?q=sanctions+financières+OR+gel+avoirs+OR+embargo", "type": "rss", "category": "autorite_fr"},
    {"name": "JORF - Crypto/PSAN", "url": "https://legifrss.org/latest?q=crypto", "type": "rss", "category": "autorite_fr"},
    # Presse spécialisée (filtrée par mots-clés)
    {"name": "Les Echos Finance", "url": "https://www.lesechos.fr/rss/rss_finance.xml", "type": "press", "category": "presse"},
    {"name": "Le Monde Économie", "url": "https://www.lemonde.fr/economie/rss_full.xml", "type": "press", "category": "presse"},
    {"name": "Reuters Financial Regulation", "url": "https://www.reuters.com/rssFeed/financial-regulation", "type": "press", "category": "presse"},
    {"name": "Compliance Week", "url": "https://www.complianceweek.com/rss", "type": "press", "category": "presse"},
    {"name": "FinCrime Central", "url": "https://fincrimecentral.com/feed/", "type": "press", "category": "presse"},
    {"name": "Financial Crime News", "url": "https://thefinancialcrimenews.com/feed/", "type": "press", "category": "presse"},
    {"name": "GAFI/FATF Statements", "url": "https://www.fatf-gafi.org/rss/fatf-news.xml", "type": "rss", "category": "autorite_intl"},
]

# ---------------------------------------------------------------------------
# SCORING
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
    # CMF / Legifrance / JORF
    "code monétaire", "code monétaire et financier",
    "établissement de crédit", "agrément", "autorisation",
    "prestataire de services d'investissement",
    "démarchage bancaire", "intermédiation bancaire",
    "contrôle prudentiel", "résolution bancaire",
    "abus de marché", "délit d'initié", "insider",
    "obligation de déclaration", "personne politiquement exposée",
    "dispositif lcb", "organe de contrôle",
    "jorf", "journal officiel",
]

# Patterns regex pour mots-clés ambigus (éviter faux positifs)
import re as _re
_REGEX_KEYWORDS = [
    # MiCA : exiger contexte crypto/réglementaire, exclure "MICA Center" militaire
    _re.compile(r'\bmica\b(?![\s-]*center)', _re.IGNORECASE),
]

# Sources cœur compliance : tout leur contenu est pertinent, pas de filtrage
CORE_COMPLIANCE_SOURCES = {
    "AMF - Actualités",
    "AMF - Mises en garde",
    "Tracfin",
    "OFAC (US Treasury)",
    "EBA - European Banking Authority",
    "ECB - Banking Supervision",
    "PNF (Parquet National Financier)",
    "JORF - Blanchiment",
    "JORF - Sanctions financières",
    "ANSSI - Alertes",
}

EXCLUDE_KEYWORDS = [
    "convention collective", "accords départementaux", "accords régionaux",
    "extension d'accords", "extension d'un avenant", "portant extension",
    "ouvriers employés par les entreprises du bâtiment",
    "sécurité sociale", "retraite complémentaire",
    "nucléaire", "interconnexions électriques",
    "transition énergétique", "flash conjoncture",
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


def matches_compliance_keywords(title, text):
    """Retourne True si le titre/texte contient au moins un mot-clé compliance."""
    combined = f"{title} {text}".lower()
    if any(k in combined for k in COMPLIANCE_KEYWORDS):
        return True
    # Vérification regex pour mots-clés ambigus (ex: "mica" mais pas "MICA Center")
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
# ---------------------------------------------------------------------
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
        title = getattr(entry, "title", "") or ""
        link = getattr(entry, "link", "") or ""
        author = getattr(entry, "author", "") or ""
        summary = getattr(entry, "summary", "") or ""
        summary_clean = re.sub(r"<[^>]+>", "", summary)[:500]

        # Si pas de titre (ex: posts Mastodon), utiliser le début du résumé
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

        # Filtrage : les sources cœur compliance passent toujours,
        # toutes les autres doivent matcher au moins un mot-clé
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
        self.send_header("WWW-Authenticate", 'Basic realm="Veille Réglementaire"')
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

        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        qs = parse_qs(parsed.query)

        if path == "/":
            if HTML_FILE.exists():
                content = HTML_FILE.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_error(404, "Dashboard HTML not found")
            return

        data = load_data()

        if path == "/api/items":
            items = data["items"]
            items.sort(key=lambda x: x.get("score", 0), reverse=True)
            self._json_response(items)
            return

        if path == "/api/items/search":
            q = qs.get("q", [""])[0].lower()
            items = [i for i in data["items"] if q in i["title"].lower() or q in i.get("summary", "").lower()]
            items.sort(key=lambda x: x.get("score", 0), reverse=True)
            self._json_response(items)
            return

        if path == "/api/sources":
            self._json_response(data["sources"])
            return

        if path == "/api/early-brief":
            items = [i for i in data["items"] if i.get("early_brief")]
            items.sort(key=lambda x: x.get("score", 0), reverse=True)
            self._json_response(items)
            return

        if path == "/api/digest":
            days = int(qs.get("days", [7])[0])
            cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
            recent = [i for i in data["items"] if i.get("published", "") >= cutoff]
            recent.sort(key=lambda x: x.get("score", 0), reverse=True)
            self._json_response({
                "period_days": days,
                "count": len(recent),
                "top_items": recent[:20],
            })
            return

        self.send_error(404)

    def do_POST(self):
        if not self._check_auth():
            return

        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        data = load_data()

        if path == "/api/seed":
            added = seed_sources(data)
            self._json_response({"added": added})
            return

        if path == "/api/ingest":
            new_count = ingest_all(data)
            self._json_response({"new_items": new_count, "total": len(data["items"])})
            return

        if path == "/api/sources":
            body = json.loads(self._read_body())
            data["sources"].append({
                "name": body.get("name", "Custom"),
                "url": body.get("url", ""),
                "type": body.get("type", "rss"),
                "category": body.get("category", "presse"),
                "active": True,
            })
            save_data(data)
            self._json_response({"ok": True})
            return

        if path == "/api/items":
            body = json.loads(self._read_body())
            items = body if isinstance(body, list) else [body]
            existing_hashes = {it["hash"] for it in data["items"]}
            added = 0
            for item in items:
                h = item.get("hash") or item_hash(item.get("title", ""), item.get("url", ""))
                if h not in existing_hashes:
                    item["hash"] = h
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
                    existing_hashes.add(h)
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

    print(f"Veille Réglementaire — http://{HOST}:{PORT}")
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
