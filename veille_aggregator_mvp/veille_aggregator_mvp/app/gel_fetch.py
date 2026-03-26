"""
Module gel des avoirs — Ingestion via l'API publique DG Trésor.

Interroge l'API ENGEL (gels-avoirs.dgtresor.gouv.fr) pour détecter
les nouvelles publications du registre national de gel des avoirs.
Génère un item par publication détectée.

Doc API : https://gels-avoirs.dgtresor.gouv.fr/ApiPublic/index.html
"""

import logging
from datetime import datetime, timezone
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

GEL_API_BASE = "https://gels-avoirs.dgtresor.gouv.fr/ApiPublic/api/v1/publication"
USER_AGENT = "EarlyBrief-VeilleAggregator/1.0 (contact: maria.garcia1403@gmail.com)"


def fetch_gel_avoirs(last_known_date: Optional[str] = None) -> list[dict]:
    """
    Check for new publications on the national freeze register.

    Args:
        last_known_date: ISO date string of the last known publication.
            If None, always fetches the latest publication.

    Returns:
        List of items (0 or 1 typically) if a new publication is detected.
    """
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}

    try:
        # Step 1: Check latest publication date
        resp_date = httpx.get(
            f"{GEL_API_BASE}/derniere-publication-date",
            headers=headers,
            timeout=30,
        )
        resp_date.raise_for_status()
        pub_date_raw = resp_date.text.strip().strip('"')

        # If we already know this publication, skip
        if last_known_date and pub_date_raw == last_known_date:
            return []

        # Step 2: Fetch the latest publication details (JSON stream)
        resp_data = httpx.get(
            f"{GEL_API_BASE}/derniere-publication-flux-json",
            headers=headers,
            timeout=60,
        )
        resp_data.raise_for_status()
        data = resp_data.json()

        # Extract summary stats from the publication
        registres = data if isinstance(data, list) else data.get("Registres", data.get("registres", []))
        n_registres = len(registres) if isinstance(registres, list) else 0

        # Count persons/entities across registres
        n_personnes = 0
        n_entites = 0
        for reg in (registres if isinstance(registres, list) else []):
            identites = reg.get("Identites", reg.get("identites", []))
            for ident in identites:
                nature = ident.get("Nature", ident.get("nature", ""))
                if nature == "Personne physique":
                    n_personnes += 1
                else:
                    n_entites += 1

        # Build the item
        try:
            pub_date = datetime.fromisoformat(pub_date_raw.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            pub_date = datetime.now(timezone.utc)

        summary = (
            f"Mise à jour du registre national des gels des avoirs "
            f"publiée le {pub_date.strftime('%d/%m/%Y')}. "
            f"{n_registres} registre(s) actif(s), "
            f"{n_personnes} personne(s) physique(s), "
            f"{n_entites} entité(s)."
        )

        return [{
            "title": f"Registre national des gels — Publication du {pub_date.strftime('%d/%m/%Y')}",
            "url": "https://gels-avoirs.dgtresor.gouv.fr/List",
            "author": "DG Trésor",
            "published_at": pub_date,
            "summary": summary,
            "raw_text": summary,
            "_gel_pub_date": pub_date_raw,  # Store for next check
        }]

    except httpx.HTTPStatusError as e:
        logger.warning(f"Gel des avoirs API HTTP error: {e.response.status_code}")
        return []
    except Exception as e:
        logger.warning(f"Gel des avoirs API error: {e}")
        return []
