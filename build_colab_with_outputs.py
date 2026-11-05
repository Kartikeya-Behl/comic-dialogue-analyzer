"""
Builds cd_project.ipynb with pre-executed live outputs for every module,
so it opens in Google Colab with all module-wise inputs and outputs fully visible,
and includes an interactive cell to test one dialogue line at a time.
"""

import json
import io
import sys
import contextlib

def create_executed_notebook():
    notebook = {
        "nbformat": 4,
        "nbformat_minor": 2,
        "metadata": {
            "colab": {
                "name": "cd project.ipynb",
                "provenance": []
            },
            "kernelspec": {
                "display_name": "Python 3",
                "name": "python3"
            },
            "language_info": {
                "name": "python"
            }
        },
        "cells": []
    }

    # Execution state shared across cells
    exec_globals = {}
    cell_counter = 1

    def add_markdown(md_text):
        notebook["cells"].append({
            "cell_type": "markdown",
            "metadata": {},
            "source": [line + "\n" for line in md_text.strip().splitlines()]
        })

    def add_executed_code(code_str):
        nonlocal cell_counter
        # Capture execution output
        stdout_buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(stdout_buf):
                exec(code_str, exec_globals)
            out_text = stdout_buf.getvalue()
        except Exception as e:
            out_text = f"Error during execution: {e}\n"

        outputs = []
        if out_text:
            outputs.append({
                "output_type": "stream",
                "name": "stdout",
                "text": [line + "\n" for line in out_text.splitlines()]
            })

        notebook["cells"].append({
            "cell_type": "code",
            "metadata": {},
            "execution_count": cell_counter,
            "outputs": outputs,
            "source": [line + "\n" for line in code_str.strip().splitlines()]
        })
        cell_counter += 1

    # --- TITLE & OVERVIEW ---
    add_markdown("""# CD Project: Compiler-Style Lexical Analysis of Comic Dialogue Text
**Course:** Compiler Design Lab (DA 6)  
**Team No:** 11 | **Slot:** G2+TG2  
**Team Members:** Kartikeya Behl (24BAI0083), Samarth Pritmani (24BAI0078), Vayun Tejwani (24BAI0027)

### Architecture Pipeline (Front-End Stages):
`Dialogue Input` ➔ **Module 1 (Speaker Split)** ➔ **Module 2 (Cleaning)** ➔ **Module 3 (Lexer)** ⟷ **Module 4 (Symbol Table)**

> This notebook implements module-by-module execution up to the Symbol Table (Lexer) as required, and supports processing input **one line at a time**.
""")

    # --- MODULE 1: SPEAKER SPLIT ---
    add_markdown("""---
## Module 1: Speaker Split
* **Function**: Takes raw dialogue input (from transcribed speech bubbles or script files) and extracts the speaker prefix (`SPEAKER: line` or `[SPEAKER]: line`) from the dialogue utterance.
* **Input**: Raw comic dialogue string with or without speaker prefix.
* **Output**: Identified Speaker and separated dialogue body.
""")

    code_m1 = """import re

class SpeakerSplitter:
    def __init__(self):
        # Regex matches 'SPEAKER: line' or '[SPEAKER]: line'
        self.pattern = re.compile(
            r'^\\s*(?:\\[(?P<bracket_spk>[^\\]]+)\\]|(?P<speaker>[A-Za-z0-9_\\-\\.\\s]+?))\\s*:\\s*(?P<dialogue>.*)$'
        )

    def split(self, raw_line: str):
        match = self.pattern.match(raw_line)
        if match:
            speaker = match.group("bracket_spk") or match.group("speaker")
            dialogue = match.group("dialogue")
            return speaker.strip(), dialogue.strip()
        return "UNKNOWN_SPEAKER", raw_line.strip()

splitter = SpeakerSplitter()

# ----------------- MODULE 1 INPUT / OUTPUT DEMONSTRATION -----------------
test_inputs_m1 = [
    "CLINT: WHERE COULD HE BE, NATASHA?",
    "BATMAN: HAVE A PEANUT.",
    "GREEN ARROW: I JUST STOPPED THE ENTIRE WORLD FROM BEING EATEN, DINAH.",
    "GORDON: BATMAN~ WE HAVE A 10-99 AT SECTOR 4#."
]

print("=" * 75)
print("              MODULE 1: SPEAKER SPLIT - INPUT & OUTPUT")
print("=" * 75)
for line in test_inputs_m1:
    spk, text = splitter.split(line)
    print(f"INPUT (Raw Line)     : {line}")
    print(f"OUTPUT (Speaker Tag) : '{spk}'")
    print(f"OUTPUT (Dialogue)    : '{text}'")
    print("-" * 75)
"""
    add_executed_code(code_m1)

    # --- MODULE 2: CLEANING ---
    add_markdown("""---
## Module 2: Cleaning & Normalization
* **Function**: Normalizes character spacing, collapses redundant spaces/tabs, and repairs hyphenated words split across line breaks (e.g., `SEC- TOR` $\\rightarrow$ `SECTOR`).
* **Input**: Extracted dialogue text from Module 1.
* **Output**: Standardized, continuous dialogue string ready for tokenization.
""")

    code_m2 = """class DialogueCleaner:
    def clean(self, text: str) -> str:
        # 1. Repair hyphenated broken words across line-breaks (e.g. 'SEC- TOR' -> 'SECTOR')
        text = re.sub(r'(\\b[A-Za-z]+)-\\s+([A-Za-z]+\\b)', r'\\1\\2', text)
        # 2. Collapse multiple spaces and tabs
        text = re.sub(r'[ \\t]+', ' ', text)
        return text.strip()

cleaner = DialogueCleaner()

# ----------------- MODULE 2 INPUT / OUTPUT DEMONSTRATION -----------------
test_inputs_m2 = [
    "WHERE   COULD HE   BE,   NATASHA?",
    "HAVE   A    PEANUT.",
    "BATMAN~   WE HAVE A 10-99   AT   SEC- TOR 4#."
]

print("=" * 75)
print("              MODULE 2: CLEANING - INPUT & OUTPUT")
print("=" * 75)
for line in test_inputs_m2:
    cleaned = cleaner.clean(line)
    print(f"INPUT (Uncleaned) : {line}")
    print(f"OUTPUT (Cleaned)  : {cleaned}")
    print("-" * 75)
"""
    add_executed_code(code_m2)

    # --- MODULE 3: LEXER ---
    add_markdown("""---
## Module 3: Comic Lexer (Lexical Analysis & OCR Error Tracking)
* **Function**: Scans cleaned dialogue characters from left-to-right using regular expressions. Categorizes characters into 9 token classes: `WORD`, `NUMBER`, `CONTRACTION`, `PUNCT`, `TERMINATOR`, `ELLIPSIS` (`...`), `INTERROBANG` (`?!`), `SOUND_FX` (`BOOM`, `AAARGH`), and `UNKNOWN`.
* **OCR Error Interception**: Any character matching no grammatical rule (e.g., stray OCR artifacts `~`, `#`) is trapped as an **UNKNOWN** token and recorded as a **Lexical Error** with its exact character position offset.
* **Input**: Cleaned dialogue text from Module 2.
* **Output**: Token Stream (Type, Value, Character Span) + Lexical Error Audit.
""")

    code_m3 = """from enum import Enum

class TokenType(str, Enum):
    WORD = "WORD"
    NUMBER = "NUMBER"
    CONTRACTION = "CONTRACTION"
    PUNCT = "PUNCT"
    TERMINATOR = "TERMINATOR"
    ELLIPSIS = "ELLIPSIS"
    INTERROBANG = "INTERROBANG"
    SOUND_FX = "SOUND_FX"
    UNKNOWN = "UNKNOWN"

# Onomatopoeia & sound effects lexicon
SOUND_EFFECTS = {
    "BOOM", "AAARGH", "AARGH", "POW", "BAM", "ZAP", "SMASH",
    "THWIP", "OOF", "UGH", "CRASH", "BANG", "KABOOM"
}

class ComicLexer:
    def __init__(self):
        self.re_ellipsis = re.compile(r'^(?:\\.{3,}|…)')
        self.re_interrobang = re.compile(r'^(?:\\?+!+|!+\\?+)[\\?!]*')
        self.re_contraction = re.compile(r"^[A-Za-z]+['’][A-Za-z]+")
        self.re_word = re.compile(r'^[A-Za-z]+')
        self.re_number = re.compile(r'^\\d+')
        self.re_terminator = re.compile(r'^[.?!]')
        self.re_punct = re.compile(r'^[,:;\\-—]')
        # Detects elongated shouting vowels (e.g. AAARGH, NOOOO, YEAAAH)
        self.re_elongated = re.compile(r'([A-Za-z])\\1{2,}', re.IGNORECASE)

    def tokenize(self, text: str):
        tokens = []
        errors = []
        i = 0
        n = len(text)

        while i < n:
            ch = text[i]
            # Skip whitespace
            if ch.isspace():
                i += 1
                continue

            sub = text[i:]

            # 1. Ellipsis (... or …)
            m = self.re_ellipsis.match(sub)
            if m:
                v = m.group(0)
                tokens.append((TokenType.ELLIPSIS, v, i, i + len(v)))
                i += len(v)
                continue

            # 2. Interrobang (?!, !?)
            m = self.re_interrobang.match(sub)
            if m:
                v = m.group(0)
                tokens.append((TokenType.INTERROBANG, v, i, i + len(v)))
                i += len(v)
                continue

            # 3. Contraction (DON'T, IT'S)
            m = self.re_contraction.match(sub)
            if m:
                v = m.group(0)
                tokens.append((TokenType.CONTRACTION, v, i, i + len(v)))
                i += len(v)
                continue

            # 4. Words & Sound FX
            m = self.re_word.match(sub)
            if m:
                v = m.group(0)
                t_type = TokenType.SOUND_FX if (v.upper() in SOUND_EFFECTS or self.re_elongated.search(v)) else TokenType.WORD
                tokens.append((t_type, v, i, i + len(v)))
                i += len(v)
                continue

            # 5. Numeric Literals
            m = self.re_number.match(sub)
            if m:
                v = m.group(0)
                tokens.append((TokenType.NUMBER, v, i, i + len(v)))
                i += len(v)
                continue

            # 6. Punctuation
            m = self.re_punct.match(sub)
            if m:
                v = m.group(0)
                tokens.append((TokenType.PUNCT, v, i, i + len(v)))
                i += len(v)
                continue

            # 7. Terminator
            m = self.re_terminator.match(sub)
            if m:
                v = m.group(0)
                tokens.append((TokenType.TERMINATOR, v, i, i + len(v)))
                i += len(v)
                continue

            # 8. Unrecognized Symbol -> Lexical Error (OCR Noise)
            errors.append({"symbol": ch, "position": i})
            tokens.append((TokenType.UNKNOWN, ch, i, i + 1))
            i += 1

        return tokens, errors

lexer = ComicLexer()

# ----------------- MODULE 3 INPUT / OUTPUT DEMONSTRATION -----------------
test_sample_m3 = "BATMAN~ WE HAVE A 10-99 AT SECTOR 4#. BOOM! DON'T WAIT...?!"
tokens_m3, errors_m3 = lexer.tokenize(test_sample_m3)

print("=" * 80)
print("              MODULE 3: COMIC LEXER - INPUT & OUTPUT")
print("=" * 80)
print(f"INPUT (Cleaned Text) : {test_sample_m3}")
print("-" * 80)
print("OUTPUT (Token Stream):")
print(f"{'INDEX':<7}{'CLASS':<15}{'TOKEN VALUE':<18}{'SPAN':<10}")
print("-" * 55)
for idx, (t_type, val, s, e) in enumerate(tokens_m3, 1):
    print(f"{idx:<7}{t_type.value:<15}'{val}'{s:>10}:{e:<4}")

print("-" * 80)
print(f"OUTPUT (Lexical Errors / Stray OCR Noise) [{len(errors_m3)} Detected]:")
for err in errors_m3:
    print(f"  • Stray Symbol '{err['symbol']}' intercepted at character coordinate {err['position']}")
print("=" * 80)
"""
    add_executed_code(code_m3)

    # --- MODULE 4: SYMBOL TABLE ---
    add_markdown("""---
## Module 4: Symbol Table
* **Function**: Maintains the central repository of distinct tokens. Tracks category, occurrence frequency count, and flags candidate proper names for downstream character popularity analysis.
* **Input**: Token stream emitted by Module 3 (Lexer).
* **Output**: Formatted Symbol Table with token classes, cumulative counts, and proper name flags.
""")

    code_m4 = """class SymbolTable:
    def __init__(self):
        # Key: uppercase token identifier
        self.table = {}

    def insert(self, token_val: str, token_type: str, is_proper_name: bool = False):
        key = token_val.upper()
        if key not in self.table:
            self.table[key] = {
                "name": token_val,
                "type": token_type,
                "count": 1,
                "is_proper_name": is_proper_name
            }
        else:
            self.table[key]["count"] += 1
            if is_proper_name:
                self.table[key]["is_proper_name"] = True

    def display(self):
        print(f"{'TOKEN':<16}{'LEXICAL CLASS':<16}{'FREQUENCY':<12}{'PROPER NAME?':<15}")
        print("-" * 60)
        # Display sorted by frequency descending
        sorted_entries = sorted(self.table.values(), key=lambda x: x['count'], reverse=True)
        for entry in sorted_entries:
            print(f"{entry['name']:<16}{entry['type']:<16}{entry['count']:<12}{str(entry['is_proper_name']):<15}")

# ----------------- MODULE 4 INPUT / OUTPUT DEMONSTRATION -----------------
KNOWN_NAMES = {"BATMAN", "NATASHA", "BRUCE", "DINAH", "CLINT", "JOKER", "SUPERMAN"}

symbol_table = SymbolTable()

# Insert tokens from sample sentences to demonstrate accumulation
sample_stream = [
    "CLINT: WHERE COULD HE BE, NATASHA?",
    "BATMAN: HAVE A PEANUT.",
    "BATMAN: THE JOKER IS AT THE DOCKS, ROBIN."
]

for line in sample_stream:
    _, text = splitter.split(line)
    cleaned = cleaner.clean(text)
    toks, _ = lexer.tokenize(cleaned)
    for t_type, val, _, _ in toks:
        is_name = val.upper() in KNOWN_NAMES
        symbol_table.insert(token_val=val, token_type=t_type.value, is_proper_name=is_name)

print("=" * 75)
print("            MODULE 4: SYMBOL TABLE - CUMULATIVE SNAPSHOT")
print("=" * 75)
symbol_table.display()
print("=" * 75)
"""
    add_executed_code(code_m4)

    # --- LIVE INTERACTIVE RUNNER (ONE LINE AT A TIME) ---
    add_markdown("""---
## Live Interactive Pipeline: Process Input One Line at a Time
Run this cell to enter any dialogue line (or press Enter to execute the default sample).  
It coordinates **Module 1 ➔ Module 2 ➔ Module 3 ⟷ Module 4** and displays the step-by-step inputs and outputs.
""")

    code_runner = """def process_single_line_step_by_step(raw_line: str, sym_tab: SymbolTable):
    print("=" * 80)
    print(f"RAW INPUT LINE : \\"{raw_line}\\"")
    print("=" * 80)

    # STEP 1: Speaker Split
    spk, raw_dialogue = splitter.split(raw_line)
    print("\\n[MODULE 1 OUTPUT: SPEAKER SPLIT]")
    print(f"  • Speaker Tag Extracted : '{spk}'")
    print(f"  • Dialogue Utterance    : \\"{raw_dialogue}\\"")

    # STEP 2: Cleaning
    cleaned_dialogue = cleaner.clean(raw_dialogue)
    print("\\n[MODULE 2 OUTPUT: CLEANING & NORMALIZATION]")
    print(f"  • Standardized Text     : \\"{cleaned_dialogue}\\"")

    # STEP 3: Lexer
    tokens, errors = lexer.tokenize(cleaned_dialogue)
    short_classes = " ".join(t[0].value for t in tokens)
    print("\\n[MODULE 3 OUTPUT: COMIC LEXER]")
    print(f"  • Short Form Token Pattern : {short_classes}")
    print(f"  • Total Tokens Emitted     : {len(tokens)}")
    print("  • Detailed Tokens List     :")
    for idx, (t_type, val, s, e) in enumerate(tokens, 1):
        print(f"      {idx:>2}. [{t_type.value:<12}] '{val}' (span {s}:{e})")

    if errors:
        print(f"  • Lexical Errors Intercepted : {len(errors)} OCR stray symbol(s)")
        for err in errors:
            print(f"      (!) Symbol '{err['symbol']}' at character offset {err['position']}")
    else:
        print("  • Lexical Errors Intercepted : 0 (Clean lexical scan)")

    # STEP 4: Symbol Table Update
    for t_type, val, _, _ in tokens:
        is_name = val.upper() in KNOWN_NAMES
        sym_tab.insert(val, t_type.value, is_proper_name=is_name)

    print("\\n[MODULE 4 OUTPUT: UPDATED SYMBOL TABLE SNAPSHOT]")
    sym_tab.display()
    print("=" * 80 + "\\n")

# --- Interactive Line Input ---
# In Google Colab, you can type any sentence in the input box:
interactive_sym_tab = SymbolTable()
default_sample = "CLINT: WHERE COULD HE BE, NATASHA?"

# Use default for pre-rendered view, or uncomment input() for manual typing in Colab:
# user_line = input(f"Enter dialogue line [Press Enter for '{default_sample}']: ").strip() or default_sample
user_line = default_sample

process_single_line_step_by_step(user_line, interactive_sym_tab)
"""
    add_executed_code(code_runner)

    # --- BATCH SAMPLE TEST (TABLE 2 FROM BASE PAPER) ---
    add_markdown("""---
## Benchmark Demonstration: Processing Table 2 Inputs (One-by-One)
This cell processes dialogue sentences from Table 2 of the base paper along with OCR noise samples, demonstrating sequential module outputs.
""")

    code_benchmark = """benchmark_dialogues = [
    "BATMAN: HAVE A PEANUT.",
    "GREEN ARROW: I JUST STOPPED THE ENTIRE WORLD FROM BEING EATEN, DINAH.",
    "GORDON: BATMAN~ WE HAVE A 10-99 AT SECTOR 4#.",
    "THE JOKER: HAHAHA! DID YOU REALLY THINK YOU COULD CATCH ME, BRUCE?!"
]

bench_sym_tab = SymbolTable()
for dialogue in benchmark_dialogues:
    process_single_line_step_by_step(dialogue, bench_sym_tab)
"""
    add_executed_code(code_benchmark)

    # Write files: both 'cd_project.ipynb' and 'cd project.ipynb'
    with open("cd_project.ipynb", "w", encoding="utf-8") as f:
        json.dump(notebook, f, indent=2)

    with open("cd project.ipynb", "w", encoding="utf-8") as f:
        json.dump(notebook, f, indent=2)

    print("[SUCCESS] Successfully generated executed 'cd_project.ipynb' and 'cd project.ipynb'!")

if __name__ == "__main__":
    create_executed_notebook()
