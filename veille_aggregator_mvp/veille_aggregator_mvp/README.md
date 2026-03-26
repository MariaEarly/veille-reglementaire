# Veille Réglementaire — Agrégateur

Agrégateur de sources pour la veille en conformité financière (LCB-FT, sanctions, réglementation).

## Fonctionnalités

- **19 sources pré-configurées** : autorités FR (ACPR, AMF, Tracfin, BdF, DG Trésor, Légifrance), EU (EBA, ESMA, BCE, EUR-Lex, Commission EU), internationales (FATF, Comité de Bâle, BRI), presse (Les Echos, Le Monde, AGEFI, Reuters)
- **Gmail IMAP** : scan automatique des newsletters réglementaires (filtrage par mots-clés LCB-FT)
- **Presse filtrée** : seuls les articles pertinents conformité sont retenus
- **Scoring intelligent** à 3 niveaux (critique, haut, moyen) + bonus par catégorie source
- **Recherche plein texte** et filtres (catégorie, statut, score)
- **Marquage Early Brief** pour la newsletter
- **Bouton Rafraîchir** : un clic pour ingérer toutes les sources

## Installation

```bash
cd veille_aggregator_mvp
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python reset_db.py
uvicorn app.main:app --reload
```

Ouvrir http://127.0.0.1:8000/

## Configuration Gmail (optionnel)

```bash
export GMAIL_USER=ton.email@gmail.com
export GMAIL_APP_PASSWORD="xxxx xxxx xxxx xxxx"
```

Pour créer un App Password : https://myaccount.google.com/apppasswords

## Utilisation

- **macOS** : double-cliquer `start_veille_ui.command` / `stop_veille_ui.command`
- **Dans le navigateur** : cliquer 🔄 Rafraîchir pour ingérer toutes les sources

## Architecture

```
app/
├── main.py          # Routes FastAPI + ingestion
├── models.py        # Modèles SQLAlchemy
├── schemas.py       # Validation Pydantic
├── database.py      # Configuration SQLite
├── rss.py           # Parser RSS
├── press_fetch.py   # Fetch presse filtrée par mots-clés
├── gmail_fetch.py   # Fetch Gmail IMAP filtré
├── scoring.py       # Scoring 3 niveaux
├── dedupe.py        # Déduplication SHA1
└── ui.py            # Dashboard HTML complet
```
