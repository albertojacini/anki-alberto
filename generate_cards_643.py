#!/usr/bin/env python3
"""
Generates Anki card content for the 643 vocabulary list using OpenAI API.
Saves to cards_643.json incrementally — safe to restart if interrupted.
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

CARDS_JSON = Path("/Users/albertojacini/Projects/anki-alberto/cards_643.json")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

if not OPENAI_API_KEY:
    print("ERROR: OPENAI_API_KEY not set")
    sys.exit(1)

client = OpenAI(api_key=OPENAI_API_KEY)

VOCAB = [
    (1, "sich befinden", "to be located/in", "Verb"),
    (2, "vorproduziert", "pre-produced", "Adjektiv"),
    (3, "aufnehmen", "to record", "Verb"),
    (4, "der Ausdruck", "expression", "Substantiv"),
    (5, "mitbringen", "to bring along", "Verb"),
    (6, "unterwegs", "out and about / on the way", "Adverb"),
    (7, "der Wochenendausflug", "weekend trip", "Substantiv"),
    (8, "die Fähre", "ferry", "Substantiv"),
    (9, "die Seele baumeln lassen", "to unwind / to let your soul dangle (colloq)", "Redewendung"),
    (10, "die Fährfahrt", "ferry ride", "Substantiv"),
    (11, "unfassbar", "unbelievable / incredibly", "Adjektiv"),
    (12, "stehenbleiben", "to stand still / to stop", "Verb"),
    (13, "baumeln", "to dangle / to hang loosely", "Verb"),
    (14, "der Rückspiegel", "rearview mirror", "Substantiv"),
    (15, "das Duftbäumchen", "car air freshener (little tree)", "Substantiv"),
    (16, "der Schmuck", "jewelry / ornaments", "Substantiv"),
    (17, "der Tannenbaum", "Christmas tree / fir tree", "Substantiv"),
    (18, "das Gewicht", "weight", "Substantiv"),
    (19, "der Faden", "thread", "Substantiv"),
    (20, "runterhängen", "to hang down", "Verb"),
    (21, "die Seele", "soul", "Substantiv"),
    (22, "abspielen", "to play (media) / to take place", "Verb"),
    (23, "das Gehirn", "brain", "Substantiv"),
    (24, "philosophisch", "philosophical", "Adjektiv"),
    (25, "religiös", "religious", "Adjektiv"),
    (26, "der Gedanke", "thought", "Substantiv"),
    (27, "genießen", "to enjoy", "Verb"),
    (28, "sich erholen", "to recover / to relax", "Verb"),
    (29, "der Hafen", "harbor / port", "Substantiv"),
    (30, "fasziniert", "fascinated", "Adjektiv"),
    (31, "erreichen", "to achieve / to reach", "Verb"),
    (32, "der Zustand", "state / condition", "Substantiv"),
    (33, "das Lüftchen", "gentle breeze", "Substantiv"),
    (34, "keinen Wunsch offen haben", "to have everything you could wish for (colloq)", "Redewendung"),
    (35, "das Lieblingssegment", "favorite segment", "Substantiv"),
    (36, "die Einleitung", "introduction", "Substantiv"),
    (37, "bewerten", "to evaluate / to rate", "Verb"),
    (38, "das Zitat", "quote / quotation", "Substantiv"),
    (39, "scheinen", "to seem / to appear / to shine", "Verb"),
    (40, "zumindest", "at least", "Adverb"),
    (41, "die Oberfläche", "surface", "Substantiv"),
    (42, "emotionslos", "emotionless", "Adjektiv"),
    (43, "eine ganze Menge", "a whole lot / quite a lot (colloq)", "Redewendung"),
    (44, "zögern", "to hesitate", "Verb"),
    (45, "kompliziert", "complicated", "Adjektiv"),
    (46, "die Unterhaltung", "conversation / entertainment", "Substantiv"),
    (47, "die Wahrheit", "truth", "Substantiv"),
    (48, "der Eindruck", "impression", "Substantiv"),
    (49, "wiedergeben", "to convey / to express / to reproduce", "Verb"),
    (50, "unbedingt", "absolutely / necessarily / by all means", "Adverb"),
    (51, "persönlich", "personal / personally", "Adjektiv"),
    (52, "letztlich", "ultimately / in the end", "Adverb"),
    (53, "das Ergebnis", "result / outcome", "Substantiv"),
    (54, "vorbereiten", "to prepare", "Verb"),
    (55, "die Schadenfreude", "schadenfreude / malicious joy", "Substantiv"),
    (56, "der Schaden", "damage / harm", "Substantiv"),
    (57, "zustimmen", "to agree / to consent", "Verb"),
    (58, "ausrutschen", "to slip / to skid", "Verb"),
    (59, "die Bananenschale", "banana peel", "Substantiv"),
    (60, "verletzt", "injured / hurt / offended", "Adjektiv"),
    (61, "die Traurigkeit", "sadness", "Substantiv"),
    (62, "der Blick", "glance / look / sight / view", "Substantiv"),
    (64, "tief", "deep / deeply / low", "Adjektiv"),
    (65, "überhaupt", "at all / in general / anyway", "Adverb"),
    (66, "selten", "rarely / seldom / rare", "Adverb"),
    (67, "die Trauer", "grief / sorrow / mourning", "Substantiv"),
    (68, "zu schätzen wissen", "to appreciate / to value", "Redewendung"),
    (69, "auf der anderen Seite", "on the other hand", "Redewendung"),
    (70, "das Zeichen", "sign / signal / symbol", "Substantiv"),
    (71, "geliebt", "beloved / loved", "Adjektiv"),
    (72, "die Wut", "rage / anger / fury", "Substantiv"),
    (73, "wütend", "angry / furious", "Adjektiv"),
    (74, "kanalisieren", "to channel / to direct", "Verb"),
    (75, "kämpfen", "to fight / to struggle", "Verb"),
    (76, "empfinden", "to feel / to sense / to perceive", "Verb"),
    (77, "der Hass", "hatred / hate", "Substantiv"),
    (78, "hassen", "to hate", "Verb"),
    (79, "das Gefühl", "feeling / emotion / sense", "Substantiv"),
    (80, "leidtun", "to feel sorry / to regret", "Verb"),
    (81, "schieflaufen", "to go wrong / to go awry", "Verb"),
    (82, "schrecklich", "terrible / dreadful / awful", "Adjektiv"),
    (83, "produktiv", "productive", "Adjektiv"),
    (84, "komisch", "weird / funny / strange", "Adjektiv"),
    (85, "um ... herum", "around / surrounding", "Phrase"),
    (86, "sowieso", "anyway / in any case / regardless", "Adverb"),
    (87, "irgendwie", "somehow / in some way", "Adverb"),
    (88, "die Gleichgültigkeit", "indifference / apathy", "Substantiv"),
    (89, "das Gegenteil", "opposite / contrary", "Substantiv"),
    (90, "um etwas gehen", "to be about something / to concern something", "Redewendung"),
    (91, "steuern", "to control / to steer / to navigate", "Verb"),
    (92, "deswegen", "therefore / that's why / because of that", "Adverb"),
    (93, "nachgucken", "to check / to look up / to look again", "Verb"),
    (94, "meinen", "to mean / to think / to believe", "Verb"),
    (95, "jedenfalls", "in any case / at any rate / anyway", "Adverb"),
    (96, "die Beleidigung", "insult / offense", "Substantiv"),
    (97, "keine Rolle spielen", "to be irrelevant / to not matter (colloq)", "Redewendung"),
    (98, "nerven", "to annoy / to get on one's nerves", "Verb"),
    (99, "gleichgültig", "indifferent / apathetic", "Adjektiv"),
    (100, "störend", "disturbing / annoying / disruptive", "Adjektiv"),
    (101, "sich beschweren", "to complain / to file a complaint", "Verb"),
    (102, "die Angst", "fear / anxiety / fright", "Substantiv"),
    (103, "sich fürchten", "to be afraid / to fear", "Verb"),
    (105, "überwinden", "to overcome / to get over", "Verb"),
    (106, "zurückhalten", "to hold back / to restrain / to withhold", "Verb"),
    (107, "andererseits", "on the other hand / on the other side", "Adverb"),
    (108, "überlebenswichtig", "vital for survival / crucial", "Adjektiv"),
    (109, "die Klippe", "cliff / rocky coast", "Substantiv"),
    (110, "das Gen", "gene", "Substantiv"),
    (111, "runterpurzeln", "to tumble down / to fall down", "Verb"),
    (112, "schützen", "to protect / to shield", "Verb"),
    (113, "der Löwe", "lion", "Substantiv"),
    (114, "die Spinne", "spider", "Substantiv"),
    (115, "im Zweifelsfall", "in case of doubt / if in doubt", "Redewendung"),
    (116, "vermeiden", "to avoid / to prevent", "Verb"),
    (117, "der Dschungel", "jungle", "Substantiv"),
    (118, "verreisen", "to travel / to go on a trip", "Verb"),
    (119, "die Fahrradtour", "bike tour / cycling trip", "Substantiv"),
    (120, "sich beschäftigen", "to keep oneself busy / to occupy oneself / to deal with", "Verb"),
    (121, "letztens", "recently / the other day / lately", "Adverb"),
    (122, "erwähnen", "to mention / to bring up", "Verb"),
    (123, "die Scham", "shame / embarrassment", "Substantiv"),
    (124, "blockieren", "to block / to obstruct", "Verb"),
    (125, "dazu", "in addition / about that / for it / to it", "Adverb"),
    (126, "die Beobachtung", "observation / finding", "Substantiv"),
    (127, "ziemlich", "quite / rather / fairly", "Adverb"),
    (128, "der Vergleich", "comparison / analogy", "Substantiv"),
    (129, "das Schuldgefühl", "feeling of guilt / guilty conscience", "Substantiv"),
    (130, "schuldig", "guilty / to blame / owing", "Adjektiv"),
    (131, "sich verhalten", "to behave / to act / to conduct oneself", "Verb"),
    (132, "die Voraussetzung", "prerequisite / requirement / condition", "Substantiv"),
    (133, "etwas geraderücken", "to set something straight / to correct something", "Redewendung"),
    (134, "der Schmerz", "pain / ache / grief", "Substantiv"),
    (135, "spüren", "to feel / to sense / to notice", "Verb"),
    (136, "abspeichern", "to save (data) / to store", "Verb"),
    (137, "die Langeweile", "boredom", "Substantiv"),
    (138, "sich langweilen", "to be bored", "Verb"),
    (139, "gelangweilt", "bored", "Adjektiv"),
    (140, "feiern", "to celebrate / to party", "Verb"),
    (141, "bewusst", "consciously / aware / deliberate", "Adjektiv"),
    (142, "wobei", "however / while / whereby / in doing so", "Adverb"),
    (143, "demnächst", "soon / shortly / coming up", "Adverb"),
    (144, "die Blitzrunde", "quick round / lightning round", "Substantiv"),
    (145, "die Eifersucht", "jealousy", "Substantiv"),
    (146, "eifersüchtig", "jealous", "Adjektiv"),
    (147, "drehen", "to film / to shoot (a video) / to turn / to rotate", "Verb"),
    (148, "die Enttäuschung", "disappointment", "Substantiv"),
    (149, "enttäuscht", "disappointed", "Adjektiv"),
    (150, "die Erwartung", "expectation", "Substantiv"),
    (151, "niedrig", "low / short / humble", "Adjektiv"),
    (152, "aufschreiben", "to write down / to note down", "Verb"),
    (153, "das Erwartungsmanagement", "expectation management", "Substantiv"),
    (154, "der Spruch", "saying / motto / quote / slogan", "Substantiv"),
    (155, "der Stolz", "pride", "Substantiv"),
    (156, "stolz", "proud", "Adjektiv"),
    (157, "ausführen", "to elaborate / to carry out / to execute", "Verb"),
    (158, "die Neugier", "curiosity", "Substantiv"),
    (159, "neugierig", "curious / nosy", "Adjektiv"),
    (160, "die Unsicherheit", "uncertainty / insecurity", "Substantiv"),
    (161, "das Manifest", "manifesto", "Substantiv"),
    (162, "die Sicherheit", "security / safety / certainty", "Substantiv"),
    (163, "erkennen", "to recognize / to identify / to realize", "Verb"),
    (164, "der Gewinn", "benefit / gain / profit / prize", "Substantiv"),
    (165, "die Eigenschaft", "trait / characteristic / property / quality", "Substantiv"),
    (166, "sympathisch", "likeable / nice / pleasant", "Adjektiv"),
    (167, "verspüren", "to feel / to sense / to experience", "Verb"),
    (168, "die Neugierde", "curiosity (variant of Neugier)", "Substantiv"),
    (169, "der Zuhörer", "listener / audience member", "Substantiv"),
    (170, "völlig", "completely / totally / utterly", "Adverb"),
    (171, "zufällig", "by chance / random / accidental", "Adjektiv"),
    (172, "untersuchen", "to examine / to investigate / to analyze", "Verb"),
    (173, "jemanden um etwas bitten", "to ask someone for something", "Redewendung"),
    (174, "vorlesen", "to read aloud / to read to someone", "Verb"),
    (175, "definieren", "to define", "Verb"),
    (176, "weiterverfolgen", "to continue to pursue / to follow up on", "Verb"),
    (177, "durchgehen", "to go through / to run through", "Verb"),
    (178, "weitermachen", "to carry on / to continue / to keep going", "Verb"),
    (179, "plötzlich", "suddenly / all of a sudden", "Adverb"),
    (180, "die Schlafroutine", "sleep routine", "Substantiv"),
    (181, "die Drohne", "drone", "Substantiv"),
    (182, "abbrechen", "to break off / to stop / to abort / to cancel", "Verb"),
    (183, "ungefähr", "approximately / about / roughly", "Adverb"),
    (184, "zurückkommen", "to return / to come back", "Verb"),
    (185, "die Hoffnung", "hope / hope for", "Substantiv"),
    (186, "überlegen", "to think about / to consider / to reflect", "Verb"),
    (187, "tatsächlich", "indeed / actually / really / in fact", "Adverb"),
    (188, "reinnehmen", "to include / to take in / to incorporate (colloq)", "Verb"),
    (189, "der Bildschirm", "screen / monitor / display", "Substantiv"),
    (190, "sich aufregen", "to get upset / to get worked up / to get agitated", "Verb"),
    (191, "der Zweifelsfall", "case of doubt / doubtful case", "Substantiv"),
    (192, "versenken", "to sink / to crash / to lose (colloq)", "Verb"),
    (193, "kritisch", "critical / skeptical / crucial", "Adjektiv"),
    (194, "die Sprachnachricht", "voice message", "Substantiv"),
    (195, "unterschiedlich", "various / different / varying", "Adjektiv"),
    (196, "der Kontrollwahn", "obsession with control / control mania", "Substantiv"),
    (197, "das Äquivalent", "equivalent", "Substantiv"),
    (198, "selbstreflektiert", "self-reflective / self-aware", "Adjektiv"),
    (199, "aus Versehen", "by mistake / accidentally", "Redewendung"),
    (200, "unerwartet", "unexpectedly / unexpected", "Adjektiv"),
    (201, "furchtbar", "terrible / dreadful / awful", "Adjektiv"),
    (202, "aufeinander zu", "toward each other / approaching each other", "Phrase"),
    (203, "gewiss", "certain / sure / definite", "Adjektiv"),
    (204, "die Peinlichkeit", "embarrassment / awkwardness", "Substantiv"),
    (205, "verbinden", "to connect / to link / to unite / to bandage", "Verb"),
    (206, "trotzdem", "nevertheless / still / nonetheless / despite that", "Adverb"),
    (207, "unangenehm", "unpleasant / uncomfortable / awkward", "Adjektiv"),
    (208, "der Muskelkater", "muscle soreness (DOMS)", "Substantiv"),
    (209, "geil", "amazing / cool / awesome (colloq, vulgar/slang)", "Adjektiv"),
    (210, "vorhaben", "to intend / to plan / to have planned", "Verb"),
    (211, "anstrengend", "exhausting / tiring / strenuous", "Adjektiv"),
    (212, "sich anfühlen", "to feel (like) / to feel to the touch", "Verb"),
    (213, "unglaublich", "incredibly / unbelievably / amazing", "Adjektiv"),
    (214, "absetzen", "to put down / to set down / to deduct / to take off", "Verb"),
    (215, "vorbeigehen", "to pass by / to walk past / to go by", "Verb"),
    (216, "der Ofen", "oven / stove / furnace", "Substantiv"),
    (217, "abschließen", "to lock / to conclude / to finish / to close", "Verb"),
    (218, "der Kontrollzwang", "compulsion to control / obsessive need to control", "Substantiv"),
    (219, "die Lösung", "solution / answer / resolution", "Substantiv"),
    (220, "das Korrektiv", "corrective (measure) / corrective factor", "Substantiv"),
    (221, "die Türklinke", "door handle / door knob", "Substantiv"),
    (222, "rütteln", "to shake / to rattle / to jolt", "Verb"),
    (223, "jemanden auslachen", "to laugh at someone / to mock someone", "Verb"),
    (224, "die Kontrollgabe", "gift/ability of control", "Substantiv"),
    (225, "klassisch", "classic / classical / typical", "Adjektiv"),
    (226, "ab und an", "every now and then / from time to time", "Redewendung"),
    (227, "der Überblick", "overview / survey / big picture", "Substantiv"),
    (228, "grundsätzlich", "generally / in principle / fundamentally", "Adverb"),
    (229, "nervig", "annoying / irritating", "Adjektiv"),
    (230, "labern", "to chatter / to babble / to talk nonsense (colloq)", "Verb"),
    (231, "etwas anhaben", "to wear something / to have something on", "Verb"),
    (233, "andersrum", "the other way around / reversed / the opposite way", "Adverb"),
    (234, "der Abschluss", "conclusion / end / degree / deal / closure", "Substantiv"),
    (235, "die Dankbarkeit", "gratitude / thankfulness", "Substantiv"),
    (236, "dankbar", "grateful / thankful", "Adjektiv"),
    (237, "retten", "to save / to rescue", "Verb"),
    (238, "gemeinsam", "together / jointly / shared / in common", "Adjektiv"),
    (239, "unterstützen", "to support / to assist / to back up", "Verb"),
    (240, "gleichzeitig", "at the same time / simultaneously", "Adverb"),
    (241, "die Übung", "exercise / practice / drill", "Substantiv"),
    (242, "der Zugang", "access / entry / approach", "Substantiv"),
    (243, "die Lernplattform", "learning platform", "Substantiv"),
    (244, "ausprobieren", "to try out / to test / to experiment with", "Verb"),
    (245, "das Risiko", "risk", "Substantiv"),
    (246, "fröhlich", "cheerful / happy / merry", "Adjektiv"),
]

SYSTEM_PROMPT = """You are a German language expert creating Anki flashcards.
Generate natural, conversational German sentences at A2-B1 level.
Respond ONLY with valid JSON, no additional text."""

def make_prompt(num, german, english, wortart):
    return f"""Create an Anki flashcard for the German vocabulary item: "{german}" ({english})

Return a JSON object with exactly these fields:
{{
  "id": {num},
  "vorderseite": "<English — nouns: 'the X', verbs: 'to X', adjectives/adverbs: just the word>",
  "rückseite": "<German — nouns with article: 'der/die/das X', verbs: infinitive, adjectives: base form>",
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
