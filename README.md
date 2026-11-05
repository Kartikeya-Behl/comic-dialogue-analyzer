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

7. **Multi-Sentence Speech Bubble Splitter** (`src/bubble_splitter.py`):
   - Pre-lexer boundary detector that splits multi-sentence speech balloons (e.g., `"LOOK OUT, BRUCE! WHERE DID HE GO? HE WAS JUST HERE..."`) into distinct clauses.
   - Evaluates tone cues, vocatives, and classifications for each clause independently while attributing speech turns and drama back to the speaker.

8. **Dynamic External Alias & Universe Configuration** (`src/alias_loader.py`):
   - JSON-driven alias mapping (`data/aliases.json`, `data/aliases_manga.json`).
   - Allows users to switch between DC, Marvel, Manga, or upload custom universes at runtime.

9. **Conversational Social Network Graph & Centrality Metrics** (`src/network_analyzer.py`):
   - Directed Network Graph of who addresses whom via vocative patterns ($A \rightarrow B$).
   - Computes Degree Centrality, In-Degree Centrality, Out-Degree Centrality, Betweenness Centrality, and PageRank.
   - Interactive Plotly network visualization with nodes sized by popularity score and colored by centrality metrics.

10. **Comprehensive Export & Download Suite** (`src/export_engine.py`):
    - One-click exports: Character Popularity Leaderboard (`.csv`), Multi-tab Analytics Workbook (`.xlsx`), Full token and sentence-level logs (`.json`), and Academic Paper Tables (`.tex` in standard `booktabs` format).

11. **Batch Reporter & CLI** (`src/reporter.py`, `main.py`):
    - Processes batch dialogue files or single sentences with full console summaries, network interaction metrics, and automated file exports.

---

## Usage

### 1. Run Batch Analysis with Multi-Sentence Splitting & Export
```bash
python main.py --file data/sample_comic_dialogue.txt --export exports/
```

### 2. Run Single Sentence / Multi-Sentence Bubble Analysis
```bash
python main.py --sentence "BATMAN: LOOK OUT, BRUCE! WHERE DID HE GO? HE WAS JUST HERE..."
python main.py --sentence "WHERE COULD HE BE, NATASHA?"
python main.py --sentence "GREEN ARROW: I JUST STOPPED THE ENTIRE WORLD FROM BEING EATEN, DINAH."
```

### 3. Load External Universe Aliases (e.g. Manga)
```bash
python main.py --file data/sample_comic_dialogue.txt --aliases data/aliases_manga.json
```

### 4. Launch Interactive Streamlit Dashboard
```bash
streamlit run app.py
```

### 5. Run Test Suite
```bash
python -m unittest discover -s tests
```
