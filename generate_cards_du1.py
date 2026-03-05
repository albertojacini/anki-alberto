#!/usr/bin/env python3
"""
Generates Anki card content for Deutschunterricht für Alberto 1 using OpenAI API.
Saves to cards_du1.json incrementally — safe to restart if interrupted.
"""

import json
import os
import sys
import time
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    print("Installing openai...")
    os.system(f"{sys.executable} -m pip install openai -q")
    from openai import OpenAI

CARDS_JSON = Path("/Users/albertojacini/Projects/anki-alberto/cards_du1.json")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

if not OPENAI_API_KEY:
    print("ERROR: OPENAI_API_KEY not set")
    sys.exit(1)

client = OpenAI(api_key=OPENAI_API_KEY)

VOCAB = [
    (1, "wegen", "because of / due to", "Präposition"),
    (2, "die Erfahrung", "experience", "Substantiv"),
    (3, "der Verkehr", "traffic", "Substantiv"),
    (4, "früher / früheren", "earlier / former / previous", "Adjektiv"),
    (5, "die Vorstellung", "idea / concept / performance / imagination", "Substantiv"),
    (6, "laufen", "to run / to walk / to go (e.g. Die Vorstellung lief gut = The show went well)", "Verb"),
    (7, "übersteigen", "to exceed / to surpass / to go beyond", "Verb"),
    (8, "offen", "open (adjective)", "Adjektiv"),
    (9, "geschlossen", "closed", "Adjektiv"),
    (10, "öffnen", "to open", "Verb"),
    (11, "schließen", "to close / to shut / to lock", "Verb"),
    (12, "die Absage", "rejection / cancellation / refusal", "Substantiv"),
    (13, "erhalten", "to receive / to get / to obtain", "Verb"),
    (14, "schätzen", "to estimate / to appreciate / to value", "Verb"),
    (15, "die Stärke", "strength / strong point", "Substantiv"),
    (16, "unterschiedlich", "different / various / varying", "Adjektiv"),
    (17, "sich bewerben", "to apply (for a job/position)", "Verb"),
    (18, "langfristig", "long-term (opposite: kurzfristig = short-term)", "Adjektiv"),
    (19, "die Aufgabe", "task / assignment / duty / job", "Substantiv"),
]

SYSTEM_PROMPT = """You are a German language expert creating Anki flashcards.
Generate natural, conversational German sentences at A2-B1 level.
Respond ONLY with valid JSON, no additional text."""

def make_prompt(num, german, english, wortart):
    return f"""Create an Anki flashcard for the German vocabulary item: "{german}" ({english})

Return a JSON object with exactly these fields:
{{
  "id": {num},
  "vorderseite": "<English — nouns: 'the X', verbs: 'to X', adjectives/adverbs: just the word, prepositions: just the word>",
  "rückseite": "<German — nouns with article: 'der/die/das X', verbs: infinitive, adjectives: base form, prepositions: the word>",
  "beispiele_pairs": [
    {{"en": "<English sentence>", "de": "<German sentence>"}},
    ... (exactly 10 pairs, diverse tenses/persons/cases, natural A2-B1)
  ],
  "hinweise": "<Grammar notes>",
  "wortart": "{wortart}"
}}

For hinweise:
- Nouns: "der/die/das X, die Xs (plural)" — note irregular plurals
- Verbs: "ich X, du Xs, er X, wir Xen, ihr Xt, sie Xen | Perfekt: hat/ist + Partizip II | Präteritum: er Xte/X | regelmäßig/unregelmäßig | [separable/reflexive notes] | [collocations]"
- Adjectives/adverbs: usage note + common collocations + comparatives if useful
- Prepositions: case governance (Genitiv/Dativ/Akkusativ) + common usage patterns
- Phrases/Redewendungen: structure, register (ugs=colloquial), usage context

For separable verbs, show the separation in example sentences (e.g., "Er nimmt das Gespräch auf").
Respond with ONLY the JSON object."""


def load_existing():
    if CARDS_JSON.exists():
        with open(CARDS_JSON) as f:
            return {c["id"]: c for c in json.load(f)}
    return {}


def save_all(cards_dict):
    cards_list = sorted(cards_dict.values(), key=lambda c: c["id"])
    with open(CARDS_JSON, "w", encoding="utf-8") as f:
        json.dump(cards_list, f, ensure_ascii=False, indent=2)


def main():
    existing = load_existing()
    print(f"Loaded {len(existing)} existing cards. Need {len(VOCAB)} total.")

    for i, (num, german, english, wortart) in enumerate(VOCAB):
        if num in existing:
            print(f"  [{i+1}/{len(VOCAB)}] #{num} {german} — already done, skipping")
            continue

        print(f"  [{i+1}/{len(VOCAB)}] #{num} {german}...", end=" ", flush=True)

        for attempt in range(3):
            try:
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": make_prompt(num, german, english, wortart)},
                    ],
                    temperature=0.7,
                    max_tokens=2000,
                    response_format={"type": "json_object"},
                )
                card = json.loads(resp.choices[0].message.content)
                existing[num] = card
                save_all(existing)
                print(f"✓ {card['vorderseite']} → {card['rückseite']}")
                break
            except Exception as e:
                print(f"  attempt {attempt+1} failed: {e}")
                if attempt < 2:
                    time.sleep(2)
        else:
            print(f"  FAILED after 3 attempts, skipping")

        # Small delay to avoid rate limits
        time.sleep(0.3)

    print(f"\nDone! {len(existing)} cards saved to {CARDS_JSON}")


if __name__ == "__main__":
    main()
