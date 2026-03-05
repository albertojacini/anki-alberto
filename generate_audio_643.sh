#!/usr/bin/env bash
# Generates TTS audio for the first 3 German examples of each card in cards_643.json
# and copies them directly into the Anki media folder.

set -euo pipefail

CARDS_JSON="/Users/albertojacini/Projects/anki-alberto/cards_643.json"
ANKI_MEDIA="/Users/albertojacini/Library/Application Support/Anki2/User 1/collection.media"
OPENAI_API_KEY="${OPENAI_API_KEY:-}"

if [[ -z "$OPENAI_API_KEY" ]]; then
  echo "ERROR: OPENAI_API_KEY is not set. Source your .env first."
  exit 1
fi

if [[ ! -f "$CARDS_JSON" ]]; then
  echo "ERROR: $CARDS_JSON not found."
  exit 1
fi

TOTAL=$(jq 'length' "$CARDS_JSON")
echo "Processing $TOTAL cards..."

for i in $(seq 0 $((TOTAL - 1))); do
  CARD_ID=$(jq -r ".[$i].id" "$CARDS_JSON")

  for j in 0 1 2; do
    GERMAN_TEXT=$(jq -r ".[$i].beispiele_pairs[$j].de" "$CARDS_JSON")

    if [[ "$GERMAN_TEXT" == "null" || -z "$GERMAN_TEXT" ]]; then
      echo "  Card $CARD_ID example $j: no text, skipping"
      continue
    fi

    HASH=$(echo -n "$GERMAN_TEXT" | md5)
    FILENAME="anki_${HASH}.mp3"
    DEST="$ANKI_MEDIA/$FILENAME"

    if [[ -f "$DEST" ]]; then
      echo "  [$((i+1))/$TOTAL] Card $CARD_ID ex$j: already exists, skipping ($FILENAME)"
      continue
    fi

    echo "  [$((i+1))/$TOTAL] Card $CARD_ID ex$j: generating audio..."
    TMP_FILE="/tmp/$FILENAME"

    HTTP_STATUS=$(curl -s -w "%{http_code}" -o "$TMP_FILE" \
      -H "Authorization: Bearer $OPENAI_API_KEY" \
      -H "Content-Type: application/json" \
      -d "{\"model\": \"tts-1\", \"input\": $(echo -n "$GERMAN_TEXT" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))'), \"voice\": \"echo\"}" \
      "https://api.openai.com/v1/audio/speech")

    if [[ "$HTTP_STATUS" == "200" ]]; then
      cp "$TMP_FILE" "$DEST"
      echo "    -> saved $FILENAME"
    else
      echo "    ERROR: HTTP $HTTP_STATUS for: $GERMAN_TEXT"
      cat "$TMP_FILE" || true
    fi

    # Small delay to avoid rate limiting
    sleep 0.2
  done
done

echo ""
echo "Done! Audio generation complete."
