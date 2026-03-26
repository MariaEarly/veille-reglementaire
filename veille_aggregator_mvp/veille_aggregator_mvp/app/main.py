from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .database import Base, engine, get_db
from .models import Item, Source
from .schemas import ItemOut, ItemPatch, ManualItemCreate, SourceCreate, SourceOut
from .rss import parse_rss_feed
from .press_fetch import fetch_press_feed
from .social_fetch import fetch_social_feed
from .gmail_fetch import fetch_gmail_items, is_configured as gmail_configured
from .scoring import score_item, is_social_noise
from .dedupe import make_duplicate_group
from .ui import render_dashboard

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Veille Aggregator")

# ---------------------------------------------------------------------------
# Pre-configured sources
# ---------------------------------------------------------------------------

SEED_SOURCES = [
    # Autorités françaises
    {"name": "ACPR - Actualités", "source_type": "rss", "url": "https://acpr.banque-france.fr/rss", "category": "autorité_fr"},
    {"name": "AMF - Actualités", "source_type": "rss", "url": "https://www.amf-france.org/fr/rss/actualites", "category": "autorité_fr"},
    {"name": "Tracfin - Publications", "source_type": "rss", "url": "https://www.economie.gouv.fr/tracfin/rss", "category": "autorité_fr"},
    {"name": "Banque de France", "source_type": "rss", "url": "https://www.banque-france.fr/rss", "category": "autorité_fr"},
    {"name": "DG Trésor", "source_type": "rss", "url": "https://www.tresor.economie.gouv.fr/Articles/rss", "category": "autorité_fr"},
    {"name": "Légifrance - JORF", "source_type": "rss", "url": "https://www.legifrance.gouv.fr/eli/jo/rss", "category": "autorité_fr"},

    # Autorités européennes
    {"name": "EBA - News", "source_type": "rss", "url": "https://www.eba.europa.eu/rss-feeds", "category": "autorité_eu"},
    {"name": "ESMA - News", "source_type": "rss", "url": "https://www.esma.europa.eu/rss", "category": "autorité_eu"},
    {"name": "AMLA", "source_type": "rss", "url": "https://www.amla.europa.eu/rss_en", "category": "autorité_eu"},
    {"name": "EUR-Lex - Derniers actes", "source_type": "rss", "url": "https://eur-lex.europa.eu/rss/act-rss.xml", "category": "autorité_eu"},
    {"name": "Commission EU - Finance", "source_type": "rss", "url": "https://finance.ec.europa.eu/rss_en", "category": "autorité_eu"},
    {"name": "BCE - Communiqués", "source_type": "rss", "url": "https://www.ecb.europa.eu/rss/press.html", "category": "autorité_eu"},
    {"name": "Conseil de l'UE - Communiqués", "source_type": "rss", "url": "https://www.consilium.europa.eu/en/press/press-releases/rss.xml", "category": "autorité_eu"},
    {"name": "Parlement EU - ECON", "source_type": "rss", "url": "https://www.europarl.europa.eu/rss/committee/econ/en.xml", "category": "autorité_eu"},
    {"name": "CSSF Luxembourg (AML/CFT)", "source_type": "rss", "url": "https://www.cssf.lu/en/feed/publications?content_keyword=aml-cft", "category": "autorité_eu"},

    # Autorités internationales
    {"name": "FATF / GAFI", "source_type": "rss", "url": "https://www.fatf-gafi.org/en/rss.xml", "category": "autorité_intl"},
    {"name": "Comité de Bâle", "source_type": "rss", "url": "https://www.bis.org/bcbs/bcbsrss.xml", "category": "autorité_intl"},
    {"name": "BRI / BIS", "source_type": "rss", "url": "https://www.bis.org/doclist/allrss.rss", "category": "autorité_intl"},
    # Note: OFAC RSS retiré le 31/01/2025. Alternative: RSS.app sur https://ofac.treasury.gov/recent-actions
    # ou email GovDelivery. Slot RSS.app disponible si besoin.

    # Presse spécialisée (filtrée par mots-clés conformité)
    {"name": "Les Echos - Finance", "source_type": "press", "url": "https://syndication.lesechos.fr/rss/rss_finance_marches.xml", "category": "presse"},
    {"name": "L'AGEFI", "source_type": "press", "url": "https://www.agefi.fr/rss", "category": "presse"},
    {"name": "Le Monde - Économie", "source_type": "press", "url": "https://www.lemonde.fr/economie/rss_full.xml", "category": "presse"},
    {"name": "Reuters - Financial Regulation", "source_type": "press", "url": "https://www.reutersagency.com/feed/", "category": "presse"},

    # Gmail (unique entry, configured via env vars)
    {"name": "Gmail - Newsletters", "source_type": "gmail", "url": None, "category": "email"},

    # Social feeds via RSS.app (Basic plan, 9/15 feeds used)
    # X (Twitter)
    {"name": "AMF France (X)", "source_type": "social", "url": "https://rss.app/feeds/bCPK9N5ApKDZ18Dy.xml", "category": "social"},
    {"name": "EBA (X)", "source_type": "social", "url": "https://rss.app/feeds/QviSp2dr0dtYvtzf.xml", "category": "social"},
    {"name": "ESMA (X)", "source_type": "social", "url": "https://rss.app/feeds/Ux1qsUgczt11vW30.xml", "category": "social"},
    {"name": "FATF/GAFI (X)", "source_type": "social", "url": "https://rss.app/feeds/PxhJ61P1z3aEDvd1.xml", "category": "social"},
    {"name": "BCE/ECB (X)", "source_type": "social", "url": "https://rss.app/feeds/o0xNXN8unJh9rSkU.xml", "category": "social"},
    {"name": "Commission EU Finance (X)", "source_type": "social", "url": "https://rss.app/feeds/7IN64UeEwhae0u54.xml", "category": "social"},
    {"name": "Banque de France (X)", "source_type": "social", "url": "https://rss.app/feeds/7s2zaEUmEv4749Jp.xml", "category": "social"},
    # LinkedIn
    {"name": "Tracfin (LinkedIn)", "source_type": "social", "url": "https://rss.app/feeds/QrJZllVNrJvGjRbb.xml", "category": "social"},
    {"name": "EBA (LinkedIn)", "source_type": "social", "url": "https://rss.app/feeds/DI2CHpgDUF6UWXmk.xml", "category": "social"},
    # Note: ESMA LinkedIn & FATF LinkedIn failed on RSS.app (no posts found)
    # Note: ACPR has no dedicated X account (uses Banque de France), Tracfin has no X account
]


# ---------------------------------------------------------------------------
# Helper: ingest entries into DB
# ---------------------------------------------------------------------------

def _ingest_entries(entries: list[dict], source: Source, db: Session) -> int:
    """Insert parsed entries into DB. Returns count of new items created."""
    created = 0
    for entry in entries:
        duplicate_group = make_duplicate_group(entry["title"], entry.get("url"))
        exists = db.query(Item).filter(Item.duplicate_group == duplicate_group).first()
        if exists:
            continue

        computed_score = score_item(
            entry["title"],
            entry.get("raw_text"),
            source.source_type,
            source.category,
        )

        # Social items always start as "new" — they are detection signals
        if source.source_type == "social":
            item_status = "new"
        else:
            item_status = "important" if computed_score >= 40 else "new"

        item = Item(
            source_id=source.id,
            source_name=source.name,
            source_type=source.source_type,
            url=entry.get("url"),
            title=entry["title"],
            author=entry.get("author"),
            published_at=entry.get("published_at"),
            raw_text=entry.get("raw_text"),
            summary=entry.get("summary"),
            tags=None,
            score=computed_score,
            category=source.category,
            duplicate_group=duplicate_group,
            status=item_status,
        )
        db.add(item)
        created += 1

    return created


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def dashboard():
    return HTMLResponse(render_dashboard())


@app.get("/health")
def health():
    return {"status": "ok", "service": "veille-aggregator", "gmail_configured": gmail_configured()}


# --- Sources ---

@app.get("/sources", response_model=list[SourceOut])
def list_sources(db: Session = Depends(get_db)):
    return db.query(Source).order_by(Source.id.desc()).all()


@app.post("/sources", response_model=SourceOut)
def create_source(payload: SourceCreate, db: Session = Depends(get_db)):
    source = Source(**payload.model_dump())
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


@app.delete("/sources/{source_id}")
def delete_source(source_id: int, db: Session = Depends(get_db)):
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    db.delete(source)
    db.commit()
    return {"deleted": source_id}


@app.post("/sources/seed")
def seed_sources(db: Session = Depends(get_db)):
    """Seed pre-configured sources if they don't exist."""
    created = 0
    for seed in SEED_SOURCES:
        # For Gmail, check by name instead of URL
        if seed["source_type"] == "gmail":
            exists = db.query(Source).filter(Source.source_type == "gmail").first()
        else:
            exists = db.query(Source).filter(Source.url == seed["url"]).first()
        if not exists:
            source = Source(**seed)
            db.add(source)
            created += 1

    db.commit()
    return {"seeded": created, "total_seed_sources": len(SEED_SOURCES)}


# --- Ingestion ---

@app.post("/ingest/rss/{source_id}")
def ingest_rss(source_id: int, db: Session = Depends(get_db)):
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    if source.source_type not in ("rss", "press", "social"):
        raise HTTPException(status_code=400, detail="Source is not RSS/press/social")
    if not source.url:
        raise HTTPException(status_code=400, detail="Source has no URL")

    if source.source_type == "press":
        entries = fetch_press_feed(source.url, source.name)
    elif source.source_type == "social":
        entries = fetch_social_feed(source.url, source.name)
    else:
        entries = parse_rss_feed(source.url)

    created = _ingest_entries(entries, source, db)
    db.commit()
    return {"created": created, "parsed": len(entries)}


@app.post("/ingest/gmail")
def ingest_gmail(db: Session = Depends(get_db)):
    """Ingest emails from Gmail that match regulatory keywords."""
    if not gmail_configured():
        raise HTTPException(
            status_code=400,
            detail="Gmail non configuré. Définir GMAIL_USER et GMAIL_APP_PASSWORD."
        )

    source = db.query(Source).filter(Source.source_type == "gmail").first()
    if not source:
        source = Source(name="Gmail - Newsletters", source_type="gmail", category="email")
        db.add(source)
        db.commit()
        db.refresh(source)

    try:
        entries = fetch_gmail_items(days_back=7, max_emails=100)
    except ConnectionError as e:
        raise HTTPException(status_code=502, detail=str(e))

    created = _ingest_entries(entries, source, db)
    db.commit()
    return {"created": created, "parsed": len(entries)}


@app.post("/ingest/all")
def ingest_all(db: Session = Depends(get_db)):
    """Ingest ALL active sources: RSS, press, and Gmail."""
    sources = db.query(Source).filter(Source.is_active == True).all()

    total_created = 0
    total_parsed = 0
    results = []

    for source in sources:
        try:
            if source.source_type == "rss" and source.url:
                entries = parse_rss_feed(source.url)
            elif source.source_type == "press" and source.url:
                entries = fetch_press_feed(source.url, source.name)
            elif source.source_type == "social" and source.url:
                entries = fetch_social_feed(source.url, source.name)
            elif source.source_type == "gmail" and gmail_configured():
                entries = fetch_gmail_items(days_back=7, max_emails=100)
            else:
                results.append({
                    "source_id": source.id,
                    "source_name": source.name,
                    "skipped": True,
                    "reason": "not configured" if source.source_type == "gmail" else "no URL"
                })
                continue

            created = _ingest_entries(entries, source, db)
            db.commit()
            total_created += created
            total_parsed += len(entries)
            results.append({
                "source_id": source.id,
                "source_name": source.name,
                "created": created,
                "parsed": len(entries),
            })
        except Exception as e:
            results.append({
                "source_id": source.id,
                "source_name": source.name,
                "error": str(e),
            })

    return {
        "sources_processed": len(sources),
        "total_created": total_created,
        "total_parsed": total_parsed,
        "details": results,
    }


# --- Items ---

@app.post("/items/manual", response_model=ItemOut)
def add_manual_item(payload: ManualItemCreate, db: Session = Depends(get_db)):
    duplicate_group = make_duplicate_group(payload.title, payload.url)
    computed_score = score_item(payload.title, payload.raw_text, payload.source_type)

    item = Item(
        source_name=payload.source_name,
        source_type=payload.source_type,
        url=payload.url,
        title=payload.title,
        author=None,
        published_at=datetime.utcnow(),
        raw_text=payload.raw_text,
        summary=payload.summary,
        tags=payload.tags,
        score=computed_score,
        duplicate_group=duplicate_group,
        status="important" if computed_score >= 40 else "new",
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.get("/items", response_model=list[ItemOut])
def list_items(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Item)
    if status:
        query = query.filter(Item.status == status)
    return query.order_by(Item.published_at.desc().nullslast(), Item.id.desc()).all()


@app.patch("/items/{item_id}")
def patch_item(item_id: int, payload: ItemPatch, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if payload.status is not None:
        item.status = payload.status
    if payload.early_brief is not None:
        item.early_brief = payload.early_brief

    db.commit()
    db.refresh(item)
    return item


@app.get("/items/search")
def search_items(q: str, db: Session = Depends(get_db)):
    search_term = f"%{q}%"
    items = (
        db.query(Item)
        .filter(or_(
            Item.title.ilike(search_term),
            Item.raw_text.ilike(search_term),
        ))
        .order_by(Item.score.desc(), Item.published_at.desc().nullslast())
        .all()
    )
    return items


@app.get("/early-brief", response_model=list[ItemOut])
def early_brief_queue(db: Session = Depends(get_db)):
    return (
        db.query(Item)
        .filter(Item.early_brief == True)
        .order_by(Item.score.desc(), Item.published_at.desc().nullslast())
        .all()
    )


@app.post("/correlate")
def correlate_social(db: Session = Depends(get_db)):
    """
    Correlate social signals with official sources.

    For each social item, search for an official item with similar title
    (via duplicate_group or keyword overlap). If found, upgrade the social
    item's score and status — it's now a validated signal.
    """
    social_items = (
        db.query(Item)
        .filter(Item.source_type == "social", Item.status == "new")
        .all()
    )

    upgraded = 0
    for social in social_items:
        # Look for an official source item with the same duplicate_group
        official = (
            db.query(Item)
            .filter(
                Item.source_type != "social",
                Item.duplicate_group == social.duplicate_group,
            )
            .first()
        )

        if not official:
            # Fallback: fuzzy match on title keywords (3+ word overlap)
            social_words = set(social.title.lower().split())
            # Remove common stop words
            stop = {"le", "la", "les", "de", "du", "des", "un", "une", "et", "en", "à",
                    "the", "of", "and", "in", "for", "on", "a", "an", "to", "is"}
            social_words -= stop
            if len(social_words) < 3:
                continue

            candidates = (
                db.query(Item)
                .filter(Item.source_type != "social")
                .order_by(Item.published_at.desc().nullslast())
                .limit(200)
                .all()
            )
            for cand in candidates:
                cand_words = set(cand.title.lower().split()) - stop
                overlap = social_words & cand_words
                if len(overlap) >= 3:
                    official = cand
                    break

        if official:
            # Upgrade: take the official score, promote status
            social.score = official.score
            social.status = "important"
            upgraded += 1

    db.commit()
    return {"social_checked": len(social_items), "upgraded": upgraded}


@app.get("/digest")
def digest(days: int = 7, db: Session = Depends(get_db)):
    since = datetime.utcnow() - timedelta(days=days)
    items = (
        db.query(Item)
        .filter((Item.published_at == None) | (Item.published_at >= since))
        .order_by(Item.score.desc(), Item.published_at.desc().nullslast())
        .all()
    )

    return {
        "period_days": days,
        "count": len(items),
        "top_items": [
            {
                "title": item.title,
                "source_name": item.source_name,
                "score": item.score,
                "summary": item.summary,
                "url": item.url,
            }
            for item in items[:30]
        ],
    }
