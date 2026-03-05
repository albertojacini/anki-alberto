#!/usr/bin/env python3
"""Generates extra cards to append to cards_du1.json."""

import json
import os
import sys
import time
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    os.system(f"{sys.executable} -m pip install openai -q")
    from openai import OpenAI

CARDS_JSON = Path("/Users/albertojacini/Projects/anki-alberto/cards_du1.json")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
    print("ERROR: OPENAI_API_KEY not set"); sys.exit(1)

client = OpenAI(api_key=OPENAI_API_KEY)

VOCAB = [
    (20, "hoch", "high / tall", "Adjektiv"),
    (21, "niedrig", "low", "Adjektiv"),
    (22, "eng / schmal", "narrow", "Adjektiv"),
    (23, "breit / weit", "wide / broad", "Adjektiv"),
]

SYSTEM_PROMPT = """You are a German language expert creating Anki flashcards.
Generate natural, conversational German sentences at A2-B1 level.
Respond ONLY with valid JSON, no additional text."""

def make_prompt(num, german, english, wortart):
    return f"""Create an Anki flashcard for the German vocabulary item: "{german}" ({english})

Return a JSON object with exactly these fields:
{{
  "id": {num},
  "vorderseite": "<English — adjectives: just the word>",
  "rückseite": "<German — base form>",
  "beispiele_pairs": [
    {{"en": "<English sentence>", "de": "<German sentence>"}},
    ... (exactly 10 pairs, diverse tenses/persons/cases, natural A2-B1)
  ],
  "hinweise": "<Grammar notes: usage note + common collocations + comparatives (Komparativ/Superlativ) + opposite (Gegenteil)>",
  "wortart": "{wortart}"
}}

Respond with ONLY the JSON object."""

def main():
    with open(CARDS_JSON) as f:
        existing_list = json.load(f)
    existing = {c["id"]: c for c in existing_list}
    print(f"Loaded {len(existing)} existing cards.")

    for i, (num, german, english, wortart) in enumerate(VOCAB):
        if num in existing:
            print(f"  #{num} {german} — already done, skipping")
            continue
        print(f"  #{num} {german}...", end=" ", flush=True)
        for attempt in range(3):
            try:
                resp = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": make_prompt(num, german, english, wortart)},
                    ],
                    temperature=0.7, max_tokens=2000,
                    response_format={"type": "json_object"},
                )
                card = json.loads(resp.choices[0].message.content)
                existing[num] = card
                cards_list = sorted(existing.values(), key=lambda c: c["id"])
                with open(CARDS_JSON, "w", encoding="utf-8") as f:
                    json.dump(cards_list, f, ensure_ascii=False, indent=2)
                print(f"✓ {card['vorderseite']} → {card['rückseite']}")
                break
            except Exception as e:
                print(f"  attempt {attempt+1} failed: {e}")
                if attempt < 2: time.sleep(2)
        else:
            print("  FAILED after 3 attempts")
        time.sleep(0.3)
    print(f"\nDone! {len(existing)} total cards in {CARDS_JSON}")

if __name__ == "__main__":
    main()
