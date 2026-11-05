"""
Script to generate cd_project.ipynb for Google Colab.
"""

import json

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

def add_md(content):
    notebook["cells"].append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in content.strip().splitlines()]
    })

def add_code(content):
    notebook["cells"].append({
        "cell_type": "code",
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": [line + "\n" for line in content.strip().splitlines()]
    })

# Title and Overview
add_md("""# CD Project: Compiler-Style Lexical Analysis of Comic Dialogue Text
**Course:** Compiler Design Lab (DA 6)  
**Pipeline Phases Implemented:**
`Dialogue Input` ➔ `Speaker Split` ➔ `Cleaning` ➔ `Lexer` ⟷ `Symbol Table`

This Google Colab notebook processes dialogue **one line at a time** and displays the input and output for each module step by step.
""")

# Module 1
add_md("""## Module 1: Speaker Split
Separates speaker tags (e.g. `BATMAN:`) from the dialogue line using regular expressions.
""")

add_code("""import re

class SpeakerSplitter:
    def __init__(self):
        # Matches 'SPEAKER: line' or '[SPEAKER]: line'
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
print("Module 1 (Speaker Splitter) loaded successfully!")
""")

# Module 2
add_md("""## Module 2: Cleaning & Normalization
Collapses redundant spaces, repairs line-broken hyphenated words, and standardizes text.
""")

add_code("""class DialogueCleaner:
    def clean(self, text: str) -> str:
        # 1. Repair broken hyphenated words across line wraps (e.g., 'sec- tor' -> 'sector')
        text = re.sub(r'(\\b[A-Za-z]+)-\\s+([A-Za-z]+\\b)', r'\\1\\2', text)
        # 2. Collapse redundant spaces and tabs
        text = re.sub(r'[ \\t]+', ' ', text)
        return text.strip()

cleaner = DialogueCleaner()
print("Module 2 (Dialogue Cleaner) loaded successfully!")
""")

# Module 3
add_md("""## Module 3: Comic Lexer (Lexical Analysis & OCR Error Detection)
Tokenizes dialogue into comic-specific token classes (`WORD`, `NUMBER`, `CONTRACTION`, `PUNCT`, `TERMINATOR`, `ELLIPSIS`, `INTERROBANG`, `SOUND_FX`, `UNKNOWN`).  
Stray OCR noise symbols (like `~`, `#`) are captured as lexical errors with exact character positions.
""")

add_code("""from enum import Enum

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

SOUND_EFFECTS = {"BOOM", "AAARGH", "AARGH", "POW", "BAM", "ZAP", "SMASH", "THWIP", "OOF", "UGH", "CRASH"}

class ComicLexer:
    def __init__(self):
        self.re_ellipsis = re.compile(r'^(?:\\.{3,}|…)')
        self.re_interrobang = re.compile(r'^(?:\\?+!+|!+\\?+)[\\?!]*')
        self.re_contraction = re.compile(r"^[A-Za-z]+['’][A-Za-z]+")
        self.re_word = re.compile(r'^[A-Za-z]+')
        self.re_number = re.compile(r'^\\d+')
        self.re_terminator = re.compile(r'^[.?!]')
        self.re_punct = re.compile(r'^[,:;\\-—]')
        self.re_elongated = re.compile(r'([A-Za-z])\\1{2,}', re.IGNORECASE)

    def tokenize(self, text: str):
        tokens = []
        errors = []
        i = 0
        n = len(text)

        while i < n:
            ch = text[i]
            if ch.isspace():
                i += 1
                continue

            sub = text[i:]
            # Ellipsis (...)
            m = self.re_ellipsis.match(sub)
            if m:
                v = m.group(0)
                tokens.append((TokenType.ELLIPSIS, v, i, i + len(v)))
                i += len(v)
                continue

            # Interrobang (?!)
            m = self.re_interrobang.match(sub)
            if m:
                v = m.group(0)
                tokens.append((TokenType.INTERROBANG, v, i, i + len(v)))
                i += len(v)
                continue

            # Contraction (DON'T, IT'S)
            m = self.re_contraction.match(sub)
            if m:
                v = m.group(0)
                tokens.append((TokenType.CONTRACTION, v, i, i + len(v)))
                i += len(v)
                continue

            # Word / Sound FX (BOOM, AAARGH)
            m = self.re_word.match(sub)
            if m:
                v = m.group(0)
                t_type = TokenType.SOUND_FX if (v.upper() in SOUND_EFFECTS or self.re_elongated.search(v)) else TokenType.WORD
                tokens.append((t_type, v, i, i + len(v)))
                i += len(v)
                continue

            # Number
            m = self.re_number.match(sub)
            if m:
                v = m.group(0)
                tokens.append((TokenType.NUMBER, v, i, i + len(v)))
                i += len(v)
                continue

            # Punctuation (comma, hyphen, colon)
            m = self.re_punct.match(sub)
            if m:
                v = m.group(0)
                tokens.append((TokenType.PUNCT, v, i, i + len(v)))
                i += len(v)
                continue

            # Terminator (., ?, !)
            m = self.re_terminator.match(sub)
            if m:
                v = m.group(0)
                tokens.append((TokenType.TERMINATOR, v, i, i + len(v)))
                i += len(v)
                continue

            # Lexical Error (Stray OCR noise)
            errors.append({"symbol": ch, "position": i})
            tokens.append((TokenType.UNKNOWN, ch, i, i + 1))
            i += 1

        return tokens, errors

lexer = ComicLexer()
print("Module 3 (Comic Lexer) loaded successfully!")
""")

# Module 4
add_md("""## Module 4: Symbol Table
Stores unique tokens, accumulates occurrences, records lexical categories, and flags candidate character names.
""")

add_code("""class SymbolTable:
    def __init__(self):
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
        print(f"{'TOKEN':<15}{'CLASS':<15}{'COUNT':<10}{'PROPER NAME?':<15}")
        print("-" * 55)
        for key, entry in self.table.items():
            print(f"{entry['name']:<15}{entry['type']:<15}{entry['count']:<10}{str(entry['is_proper_name']):<15}")

symbol_table = SymbolTable()
KNOWN_PROPER_NAMES = {"BATMAN", "NATASHA", "BRUCE", "DINAH", "CLINT", "JOKER", "ROBIN", "SUPERMAN"}
print("Module 4 (Symbol Table) loaded successfully!")
""")

# Step by Step Live Pipeline Runner
add_md("""## 🚀 Live Interactive Pipeline (One Line at a Time)
Run this cell to input a dialogue line.  
It will show the **Input and Output** of each module sequentially:
1. **Module 1 (Speaker Split)**
2. **Module 2 (Cleaning)**
3. **Module 3 (Lexer - Token Stream & Lexical Errors)**
4. **Module 4 (Symbol Table Snapshot)**
""")

add_code("""def process_single_line(raw_line: str, sym_tab: SymbolTable):
    print("=" * 80)
    print(f"INPUT SENTENCE: \\"{raw_line}\\"")
    print("=" * 80)

    # 1. Speaker Split
    speaker, dialogue_text = splitter.split(raw_line)
    print("\\n[1] MODULE 1: SPEAKER SPLIT")
    print(f"    • Speaker Identified : {speaker}")
    print(f"    • Extracted Dialogue : \\"{dialogue_text}\\"")

    # 2. Cleaning
    cleaned_dialogue = cleaner.clean(dialogue_text)
    print("\\n[2] MODULE 2: CLEANING & NORMALIZATION")
    print(f"    • Cleaned Text       : \\"{cleaned_dialogue}\\"")

    # 3. Lexical Analysis
    tokens, errors = lexer.tokenize(cleaned_dialogue)
    short_tokens = " ".join(t[0].value for t in tokens)
    print("\\n[3] MODULE 3: LEXER (TOKEN STREAM)")
    print(f"    • Short Form Tokens  : {short_tokens}")
    print("    • Detailed Tokens Stream:")
    for t_type, val, start_pos, end_pos in tokens:
        print(f"        [{t_type.value:<12}] '{val}' (character span {start_pos}:{end_pos})")

    if errors:
        print("    • Lexical Errors (OCR Stray Noise):")
        for err in errors:
            print(f"        (!) Symbol '{err['symbol']}' at character offset {err['position']}")
    else:
        print("    • Lexical Errors     : None (Valid syntax tokens)")

    # 4. Symbol Table Update
    for t_type, val, _, _ in tokens:
        is_name = val.upper() in KNOWN_PROPER_NAMES
        sym_tab.insert(val, t_type.value, is_proper_name=is_name)

    print("\\n[4] MODULE 4: SYMBOL TABLE SNAPSHOT (CUMULATIVE)")
    sym_tab.display()
    print("=" * 80)

# --- Interactive Prompt: Enter any line here ---
default_line = "CLINT: WHERE COULD HE BE, NATASHA?"
user_input = input(f"Enter dialogue line [Press Enter to test '{default_line}']: ").strip()
if not user_input:
    user_input = default_line

process_single_line(user_input, symbol_table)
""")

# Sample Batch verification cell
add_md("""### Quick Benchmark Test (Table 2 Inputs from Base Paper)
Run this cell to see how sample sentences from the paper process one after another:
""")

add_code("""benchmark_sentences = [
    "BATMAN: HAVE A PEANUT.",
    "GREEN ARROW: I JUST STOPPED THE ENTIRE WORLD FROM BEING EATEN, DINAH.",
    "GORDON: BATMAN~ WE HAVE A 10-99 AT SECTOR 4#.",
    "THE JOKER: HAHAHA! DID YOU REALLY THINK YOU COULD CATCH ME, BRUCE?!"
]

benchmark_table = SymbolTable()
for line in benchmark_sentences:
    process_single_line(line, benchmark_table)
    print("\\n" + "-" * 80 + "\\n")
""")

with open("cd_project.ipynb", "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=2)

print("[SUCCESS] Created cd_project.ipynb successfully!")
