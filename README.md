# Compiler-Style Comic Dialogue Analyzer & Character Popularity Engine

A compiler-inspired front-end pipeline for comic book dialogue analysis. The pipeline replaces the conventional syntactic CFG parser with high-precision lexical pattern matching and an integrated **Character Popularity Module**.

---

## Architecture

```
Dialogue File (Speaker: line)
       │
       ▼
 ┌─────────────┐
 │Speaker split│ ───(Speaker tags)───┐
 └──────┬──────┘                     │
        │                            ▼
 ┌──────▼──────┐               ┌─────────────┐
 │  Cleaning   │               │   Mention   │ ◄───(Proper names, vocatives)───┐
 └──────┬──────┘               │   finder    │                                 │
        │                      └──────┬──────┘                                 │
 ┌──────▼──────┐                      │                                        │
 │    Lexer    │ ◄────────────────────┼─────────────► ┌──────────────┐         │
 └──────┬──────┘                      ▼               │ Symbol table │─────────┘
        │                      ┌─────────────┐        └──────────────┘
 ┌──────▼──────┐               │Alias merging│
 │ Classifier  │               └──────┬──────┘
 └──────┬──────┘                      │
        │                      ┌──────▼──────┐
 ┌──────▼──────┐               │ Name tally  │
 │  Sentence   │               └──────┬──────┘
 │   result    │                      │
 └──────┬──────┘               ┌──────▼──────┐
        │                      │   Ranking   │
        │                      └──────┬──────┘
        │                             │
        └──────────────┬──────────────┘
                       ▼
              ┌─────────────────┐
              │Statistics report│
              └─────────────────┘
```

---

## Implemented Features (40–50% Milestone)

1. **Speaker Split & Text Sanitization** (`src/cleaner.py`):
   - Extracts character speakers from dialogue prefixes (`SPEAKER: line`).
   - Normalizes whitespace, repairs broken hyphenated line-breaks.
   
2. **Comic Lexical Analyzer** (`src/lexer.py`):
   - Token classes: `WORD`, `NUMBER`, `CONTRACTION`, `PUNCT`, `TERMINATOR`, `ELLIPSIS` (`...`), `INTERROBANG` (`?!`, `!?`), `SOUND_FX` (`BOOM`, `AAARGH`, repeated letter shouts), `UNKNOWN`.
   - Logs stray OCR noise (`~`, `#`, stray symbols) as lexical errors with character coordinate offsets.

3. **Symbol Table Manager** (`src/symbol_table.py`):
   - Maintains token frequencies, lexical classes, proper name flags, and line references.

4. **Rule-Based Sentence Classifier & Tone Cue Detector** (`src/classifier.py`):
   - Categorizes sentences into `statement`, `question`, `exclamation`, and `command`.
   - Flags tone markers: shouting, hesitation, surprise/incredulity, and sound effects/pain.

5. **Mention Finder & Vocative Rules** (`src/mention_finder.py`):
   - Replaces the CFG parser's vocative rule with pattern matching: `comma + name + terminator` and leading vocatives.
   - Discovers in-sentence third-person mentions of characters.

6. **Character Popularity Engine** (`src/character_popularity.py`):
   - **Alias Merging**: Maps variants (`BRUCE`, `THE DARK KNIGHT`) to canonical identities (`BATMAN`).
   - **Multi-Metric Tallying**: Spoken lines ($S$), Addressed vocatives ($A$), Mentions ($M$), Tone bonus ($T$).
   - **Weighted Composite Score**:
     $$\text{Popularity}(C) = 1.0 \cdot S + 1.5 \cdot A + 0.8 \cdot M + 0.2 \cdot T$$
   - **Leaderboard Generator**: Formats a ranked prominence table.

7. **Batch Reporter & CLI** (`src/reporter.py`, `main.py`):
   - Processes batch dialogue files or single sentences with full console summaries.

---

## Usage

### 1. Run Batch Analysis on Comic Dataset
```bash
python main.py --file data/sample_comic_dialogue.txt
```

### 2. Run Single Sentence Analysis
```bash
python main.py --sentence "WHERE COULD HE BE, NATASHA?"
python main.py --sentence "HAVE A PEANUT."
python main.py --sentence "GREEN ARROW: I JUST STOPPED THE ENTIRE WORLD FROM BEING EATEN, DINAH."
```

### 3. Run Test Suite
```bash
python -m unittest discover -s tests
```
