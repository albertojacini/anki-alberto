#!/usr/bin/env python3
"""
Reads cards_du1.json (with audio hashes already embedded) and uploads all cards
to Anki via AnkiConnect HTTP API directly.
"""

import json
import hashlib
import urllib.request
import sys

CARDS_JSON = "/Users/albertojacini/Projects/anki-alberto/cards_du1.json"
DECK_NAME = "Deutschunterricht für Alberto 1"
MODEL_NAME = "Deutsch Vokabel"
ANKICONNECT_URL = "http://127.0.0.1:8765"


def ankiconnect(action, **params):
    payload = json.dumps({"action": action, "version": 6, "params": params}).encode()
    req = urllib.request.Request(ANKICONNECT_URL, payload)
    resp = urllib.request.urlopen(req, timeout=10)
    result = json.loads(resp.read())
    if result.get("error"):
        raise Exception(f"AnkiConnect error: {result['error']}")
    return result["result"]


def md5(text):
    return hashlib.md5(text.encode()).hexdigest()


def build_beispiele(pairs):
    """Build the Beispiele field: 10 pairs, first 3 with [sound:...] tags."""
    lines = []
    for i, pair in enumerate(pairs[:10]):
        en = pair["en"]
        de = pair["de"]
        if i < 3:
            hash_ = md5(de)
            filename = f"anki_{hash_}.mp3"
            lines.append(f"{en}\n{de} [sound:{filename}]")
        else:
            lines.append(f"{en}\n{de}")
    return "\n\n".join(lines)


def main():
    with open(CARDS_JSON, "r", encoding="utf-8") as f:
        cards = json.load(f)

    print(f"Loaded {len(cards)} cards from JSON")

    # Test AnkiConnect connection
    try:
        version = ankiconnect("version")
        print(f"AnkiConnect version: {version}")
    except Exception as e:
        print(f"ERROR: Cannot connect to AnkiConnect: {e}")
        print("Make sure Anki is open with the AnkiConnect add-on installed.")
        sys.exit(1)

    success = 0
    errors = 0

    for i, card in enumerate(cards):
        vorderseite = card["vorderseite"]
        rückseite = card["rückseite"]
        beispiele = build_beispiele(card["beispiele_pairs"])
        hinweise = card["hinweise"]
        wortart = card.get("wortart", "")
        tags = [f"deutsch::Deutschunterricht-1", wortart]

        note = {
            "deckName": DECK_NAME,
            "modelName": MODEL_NAME,
            "fields": {
                "Vorderseite": vorderseite,
                "Rückseite": rückseite,
                "Beispiele": beispiele,
                "Hinweise": hinweise,
            },
            "tags": tags,
            "options": {
                "allowDuplicate": False,
                "duplicateScope": "deck",
            },
        }

        try:
            note_id = ankiconnect("addNote", note=note)
            print(f"  [{i+1}/{len(cards)}] Added: {vorderseite} → {rückseite} (id={note_id})")
            success += 1
        except Exception as e:
            print(f"  [{i+1}/{len(cards)}] ERROR for '{vorderseite}': {e}")
            errors += 1

    print(f"\nDone! {success} cards added, {errors} errors.")


if __name__ == "__main__":
    main()
