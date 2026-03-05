---
name: anki-language-cards
description: Create German language learning Anki cards. Use when asked to generate vocabulary cards, flashcards for a topic, or language learning material for German.
argument-hint: [topic or word list]
disable-model-invocation: true
---

# Anki Language Card Generator

Generate English→German Anki flashcards. Accepts either:
- A **topic/situation** (e.g. "at the restaurant", "job interview") — generate relevant vocabulary and phrases
- A **word/phrase list** — create cards for each item provided

## Input

`$ARGUMENTS` — a topic, situation, or comma-separated list of words/phrases.

## Anki Connection

Cards are uploaded via **AnkiConnect** (HTTP API on `http://127.0.0.1:8765`). Anki must be open with the AnkiConnect add-on installed.

If an Anki MCP server is available, you may use that instead. Otherwise, use AnkiConnect directly via Python's `urllib.request`.

### AnkiConnect Constants

| Constant | Value |
|----------|-------|
| URL | `http://127.0.0.1:8765` |
| API version | `6` |
| Note model | `Deutsch Vokabel` |
| Anki media folder | `~/Library/Application Support/Anki2/User 1/collection.media/` |

### AnkiConnect API Pattern

```python
import json, urllib.request

def ankiconnect(action, **params):
    payload = json.dumps({"action": action, "version": 6, "params": params}).encode()
    req = urllib.request.Request("http://127.0.0.1:8765", payload)
    resp = urllib.request.urlopen(req, timeout=10)
    result = json.loads(resp.read())
    if result.get("error"):
        raise Exception(f"AnkiConnect error: {result['error']}")
    return result["result"]
```

Key actions:
- `ankiconnect("version")` — test connection
- `ankiconnect("createDeck", deck="Deck Name")` — create deck (always do this before adding notes)
- `ankiconnect("addNote", note={...})` — add a card

## Card Design Principles

1. **One concept per card** — each card tests exactly one word or phrase
2. **English→German only** — front is always English, back is always German
3. **Rich context** — each card contains multiple example sentences (around 10). Try to use diverse angles and conjugations.
4. **Grammar cues** — nouns with article + plural; verbs with full conjugation, regular/irregular classification, past tenses, and usage notes
5. **Categorization** — tag cards by topic and word type

## Card Fields

All field names and metadata inside the cards must be in German. Only English translations are in English.

| Field (in Anki) | Description |
|-----------------|-------------|
| Vorderseite     | English word or phrase |
| Rückseite       | German translation. Always include the article (der/die/das) for nouns. |
| Beispiele       | Multiple example sentences (~10). See format below. |
| Hinweise        | Grammar notes — rich and detailed (see format below). For nouns: article + plural. For verbs: full present-tense conjugation, whether regular/irregular, Perfekt (haben/sein + Partizip II), Präteritum (er-form), and any noteworthy info (separable prefix, reflexive, strong verb class, common collocations, etc.). |
| Schlagwörter    | Space-separated tags: `deutsch::<topic>` + word type (`Substantiv`, `Verb`, `Adjektiv`, `Redewendung`) |

## Workflow

The workflow has 3 phases. Generate scripts for each phase, then run them sequentially.

### Phase 1: Generate Card Content

Create a Python script (`generate_cards_<slug>.py`) that:
1. Reads `OPENAI_API_KEY` from environment
2. Defines a `VOCAB` list of tuples: `(id, german, english, wortart)`
3. Uses OpenAI `gpt-4o-mini` with JSON mode to generate card content
4. Saves incrementally to `cards_<slug>.json` (safe to restart if interrupted)
5. Each card in JSON has: `id`, `vorderseite`, `rückseite`, `beispiele_pairs` (list of `{"en": ..., "de": ...}`), `hinweise`, `wortart`

Run with: `export OPENAI_API_KEY=$(grep OPENAI_API_KEY .env | cut -d= -f2) && python3 generate_cards_<slug>.py`

### Phase 2: Generate Audio

Create a bash script (`generate_audio_<slug>.sh`) that:
1. For each card, generates TTS audio for the **first 3 German example sentences only**
2. Uses OpenAI TTS API: model `tts-1`, voice `echo`
3. Filenames: `anki_<md5 hash of German text>.mp3`
4. Copies files directly to the Anki media folder
5. Skips files that already exist (idempotent)
6. Uses `python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))'` to safely JSON-encode the text for the API call

Run with: `export OPENAI_API_KEY=$(grep OPENAI_API_KEY .env | cut -d= -f2) && bash generate_audio_<slug>.sh`

### Phase 3: Upload to Anki

Create a Python script (`upload_cards_<slug>.py`) that:
1. Reads `cards_<slug>.json`
2. Creates the deck via `createDeck` (always, to ensure it exists)
3. Builds the `Beispiele` field: first 3 pairs get `[sound:anki_<md5>.mp3]` tags, remaining pairs don't
4. Uploads each card via `addNote` with `allowDuplicate: False, duplicateScope: "deck"`
5. Tags: `["deutsch::<deck-slug>", "<wortart>"]`

Run with: `python3 upload_cards_<slug>.py`

## Audio Generation Details

Only the **first 3 example sentences** per card get an audio file. The remaining examples have no audio tag.

- **API**: OpenAI TTS (`tts-1` model, voice `echo`)
- **API key**: from `.env` in the project root (`OPENAI_API_KEY=...`)
- **Filename**: `anki_$(echo -n "$GERMAN_TEXT" | md5).mp3`
- **Destination**: directly to `~/Library/Application Support/Anki2/User 1/collection.media/`

Generate all audio files **before** uploading any cards to Anki.

### Examples field format

Examples are structured so the user can cover the German translation with their finger to guess it. Each example has two lines — the English translation first, then the German version on the next line. Only the **first 3** have a `[sound:...]` tag; the rest do not. Separate examples with a blank line.

```
I'm buying an apple.
Ich kaufe einen Apfel. [sound:anki_<hash>.mp3]

Can I pay by card?
Kann ich mit Karte bezahlen? [sound:anki_<hash>.mp3]

The apples are fresh today.
Die Äpfel sind heute frisch. [sound:anki_<hash>.mp3]

He ate the whole apple.
Er hat den ganzen Apfel gegessen.

She cut the apple into slices.
Sie hat den Apfel in Scheiben geschnitten.
```

### Full card example

Input: `/anki-language-cards grocery shopping`

**Card 1:**
- Vorderseite: `the apple`
- Rückseite: `der Apfel`
- Beispiele:
```
I'm buying an apple.
Ich kaufe einen Apfel. [sound:anki_abc123.mp3]

The apples are fresh today.
Die Äpfel sind heute frisch. [sound:anki_def456.mp3]

Do you have organic apples?
Haben Sie Bio-Äpfel? [sound:anki_ghi789.mp3]

He ate the whole apple.
Er hat den ganzen Apfel gegessen.

She cut the apple into slices.
Sie hat den Apfel in Scheiben geschnitten.

The apple fell from the tree.
Der Apfel ist vom Baum gefallen.

Would you like an apple?
Möchtest du einen Apfel?

I prefer red apples.
Ich bevorzuge rote Äpfel.

The apple tastes sweet.
Der Apfel schmeckt süß.

We picked apples in the garden.
Wir haben im Garten Äpfel gepflückt.
```
- Hinweise: `der Apfel, die Äpfel`
- Schlagwörter: `deutsch::Einkaufen Substantiv`

**Card 2:**
- Vorderseite: `to pay`
- Rückseite: `bezahlen`
- Beispiele:
```
I'd like to pay by card.
Ich möchte mit Karte bezahlen. [sound:anki_efa123.mp3]

Where can I pay?
Wo kann ich bezahlen? [sound:anki_ghb456.mp3]

He already paid.
Er hat schon bezahlt. [sound:anki_icc789.mp3]

She pays her rent every month.
Sie bezahlt jeden Monat ihre Miete.

Do I pay here or at the counter?
Bezahle ich hier oder an der Kasse?

We paid for dinner.
Wir haben das Abendessen bezahlt.

Can you pay in cash?
Kannst du bar bezahlen?

I forgot to pay the bill.
Ich habe vergessen, die Rechnung zu bezahlen.

They paid too much.
Sie haben zu viel bezahlt.

You pay at the end.
Du bezahlst am Ende.
```
- Hinweise: `regelmäßiges Verb | Präsens: ich bezahle, du bezahlst, er bezahlt, wir bezahlen, ihr bezahlt, sie bezahlen | Perfekt: hat bezahlt | Präteritum: er bezahlte | Infinitiv mit zu: zu bezahlen | oft mit Akkusativ: "die Rechnung bezahlen", "den Betrag bezahlen"`
- Schlagwörter: `deutsch::Einkaufen Verb`

## Rules

- For a **topic**: generate 10-20 of the most useful/common words and phrases
- For a **word list**: create cards for every item provided
- Use natural, conversational example sentences (A2-B1 level)
- For nouns, always include the article on the German side (der/die/das)
- For separable verbs, show the separated form in the examples
- All card field names, tags, and grammar notes in German
- Only English translations in English

## After Generating

1. Upload cards via AnkiConnect (ensure Anki is open)
2. State the total card count
3. Offer to adjust, add more cards, or generate cards for a related topic
