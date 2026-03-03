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

## Prerequisites — Anki MCP

**IMPORTANT**: Before creating any cards, check if an Anki MCP server is available (e.g. `anki-mcp-server`, `clanki`, `mcp-ankiconnect`, or similar). Look for MCP tools that enable Anki operations (creating cards, listing decks, etc.).

If **no Anki MCP server** is configured:
1. **STOP immediately** — do not create any cards
2. Inform the user that an Anki MCP server is required
3. Recommend one of these options:
   - [anki-mcp-server (CamdenClark)](https://github.com/CamdenClark/anki-mcp-server) — TypeScript, AnkiConnect
   - [clanki](https://github.com/jasperket/clanki) — for Claude Desktop
   - [mcp-ankiconnect](https://pypi.org/project/mcp-ankiconnect/) — Python, PyPI
   - [anki-mcp (amidvidy)](https://github.com/amidvidy/anki-mcp) — comprehensive features
4. Explain that the MCP server must be configured in `.mcp.json` or Claude settings

If an Anki MCP server is available, proceed with card creation and upload directly via the MCP.

## Card Design Principles

1. **One concept per card** — each card tests exactly one word or phrase
2. **English→German only** — front is always English, back is always German
3. **Rich context** — each card contains multiple example sentences (around 10) . Try to use diverse angles and conjugations.
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

## Audio Generation

Only the **first 3 example sentences** per card get an audio file. The remaining examples have no audio tag.

### Steps for each card

1. **Read the API key** from `.env` in the project root:
   ```bash
   source .env
   ```

2. **For the first 3 German example sentences only**, generate an audio file:
   - Use the OpenAI TTS API (`tts-1` model, voice `echo` — natural German pronunciation)
   - Name the file using the MD5 hash of the German text to ensure uniqueness:
     ```bash
     GERMAN_TEXT="Ich kaufe einen Apfel."
     FILENAME="anki_$(echo -n "$GERMAN_TEXT" | md5).mp3"
     curl -s \
       -H "Authorization: Bearer $OPENAI_API_KEY" \
       -H "Content-Type: application/json" \
       -d "{\"model\": \"tts-1\", \"input\": \"$GERMAN_TEXT\", \"voice\": \"echo\"}" \
       https://api.openai.com/v1/audio/speech \
       -o "/tmp/$FILENAME"
     ```
   - Store the file in Anki's media folder using the `store_media_file` MCP tool with `path: "/tmp/$FILENAME"` and `filename: "$FILENAME"`

3. **Embed** the sound reference immediately after the first 3 German sentences only:
   `Ich kaufe einen Apfel. [sound:anki_<hash>.mp3]`

   Examples 4–10 appear without any `[sound:...]` tag.

Generate all audio files **before** uploading any cards to Anki. Batch-generate audio for all cards, then upload.

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

1. Upload cards via the Anki MCP server
2. State the total card count
3. Offer to adjust, add more cards, or generate cards for a related topic
