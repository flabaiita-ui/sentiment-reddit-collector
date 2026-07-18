"""
Modulo condiviso per i collector del progetto "Raccolta".

Schema dati unificato (una riga JSON per record, file .jsonl):
{
  "source": "reddit" | "apewisdom" | "4chan_biz" | "bluesky" | "telegram",
  "collected_at": "2026-07-16T14:32:00+00:00",  # quando l'abbiamo raccolto noi
  "created_at": "2026-07-16T12:01:00+00:00" | null,  # quando il post/messaggio
                                                        # e' stato creato sulla piattaforma
  "query_or_context": "wallstreetbets" | "$AAPL" | "@canale_esempio" | ...,
  "external_id": "id univoco sulla piattaforma di origine, per dedup",
  "author": "username o null se anonimo/non disponibile",
  "text": "testo grezzo del post/messaggio",
  "engagement": { ... metriche specifiche della fonte, es. score/likes/mentions ... },
  "raw": { ... payload originale completo, per riprocessare senza rifare la chiamata ... }
}

Percorso di output di default: ./data/raw/<source>/<YYYY-MM-DD>.jsonl
Cambialo impostando la variabile d'ambiente RACCOLTA_DATA_DIR (es. quando sara'
confermato il percorso della cartella di sync Drive sul Pi):

    export RACCOLTA_DATA_DIR="/percorso/della/cartella/drive/sync"
"""
import os
import json
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_DATA_DIR = "./data/raw"


def get_data_dir():
    return Path(os.environ.get("RACCOLTA_DATA_DIR", DEFAULT_DATA_DIR))


def write_record(source, record):
    """
    Scrive un singolo record nel file jsonl del giorno per quella fonte.
    Aggiunge automaticamente 'source' e 'collected_at' se mancanti.
    Ritorna il path del file scritto.
    """
    record = dict(record)  # copia, non mutare l'originale del chiamante
    record.setdefault("source", source)
    record.setdefault("collected_at", datetime.now(timezone.utc).isoformat())

    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out_dir = get_data_dir() / source
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{day}.jsonl"

    with open(out_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    return out_path


def write_records(source, records):
    """Scrive piu' record, ritorna il set di path scritti (di solito uno solo)."""
    paths = set()
    for r in records:
        paths.add(str(write_record(source, r)))
    return paths
