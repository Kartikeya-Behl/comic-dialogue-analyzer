"""
Lexical Analyzer for Comic Dialogue Text.
Groups text into comic-specific tokens and detects lexical errors with character positions.
"""

import re
from dataclasses import dataclass
from typing import List, Tuple, Set, Optional
from .config import TokenType, DEFAULT_SOUND_EFFECTS


@dataclass
class Token:
    value: str
    type: TokenType
    start_pos: int
    end_pos: int
    line_num: int = 1

    def __repr__(self) -> str:
        return f"Token({self.type.value}, '{self.value}', pos={self.start_pos}:{self.end_pos})"


@dataclass
class LexicalError:
    symbol: str
    position: int
    line_num: int = 1
    description: str = "Stray OCR noise or unsupported symbol"

    def __repr__(self) -> str:
        return f"LexicalError('{self.symbol}', at pos {self.position})"


class ComicLexer:
    def __init__(self, sound_effects: Optional[Set[str]] = None):
        self.sound_effects = sound_effects if sound_effects is not None else DEFAULT_SOUND_EFFECTS
        
        # Regex patterns ordered by precedence
        self.re_ellipsis = re.compile(r'^(?:\.{3,}|…)')
        self.re_interrobang = re.compile(r'^(?:\?+!+|!+\?+)[\?!]*')
        self.re_contraction = re.compile(r"^[A-Za-z]+['’][A-Za-z]+")
        self.re_word = re.compile(r'^[A-Za-z]+')
        self.re_number = re.compile(r'^\d+')
        self.re_terminator = re.compile(r'^[.?!]')
        self.re_punct = re.compile(r'^[,:;\-—]')
        # Pattern for elongated words with 3+ repeated identical letters (e.g. AAARGH, NOOOO)
        self.re_elongated = re.compile(r'([A-Za-z])\1{2,}', re.IGNORECASE)

    def is_sound_fx(self, word: str) -> bool:
        """
        Determines if a word is an onomatopoeia or sound effect.
        Checks explicit lexicon or repeated elongated letters.
        """
        upper = word.upper()
        if upper in self.sound_effects:
            return True
        if self.re_elongated.search(word):
            return True
        return False

    def tokenize(self, text: str, line_num: int = 1) -> Tuple[List[Token], List[LexicalError]]:
        """
        Scans cleaned text left-to-right, returning a token stream
        and a list of lexical errors with character offsets.
        """
        tokens: List[Token] = []
        errors: List[LexicalError] = []
        
        i = 0
        n = len(text)
        
        while i < n:
            ch = text[i]
            
            # Skip whitespace
            if ch.isspace():
                i += 1
                continue
            
            substr = text[i:]
            
            # 1. Ellipsis (... or …)
            m = self.re_ellipsis.match(substr)
            if m:
                val = m.group(0)
                tokens.append(Token(val, TokenType.ELLIPSIS, i, i + len(val), line_num))
                i += len(val)
                continue
            
            # 2. Interrobang (?!, !?, ??!, etc.)
            m = self.re_interrobang.match(substr)
            if m:
                val = m.group(0)
                tokens.append(Token(val, TokenType.INTERROBANG, i, i + len(val), line_num))
                i += len(val)
                continue
            
            # 3. Contraction (DON'T, IT'S, I'M)
            m = self.re_contraction.match(substr)
            if m:
                val = m.group(0)
                tokens.append(Token(val, TokenType.CONTRACTION, i, i + len(val), line_num))
                i += len(val)
                continue
            
            # 4. Sound FX & Words
            m = self.re_word.match(substr)
            if m:
                val = m.group(0)
                if self.is_sound_fx(val):
                    tokens.append(Token(val, TokenType.SOUND_FX, i, i + len(val), line_num))
                else:
                    tokens.append(Token(val, TokenType.WORD, i, i + len(val), line_num))
                i += len(val)
                continue
            
            # 5. Number
            m = self.re_number.match(substr)
            if m:
                val = m.group(0)
                tokens.append(Token(val, TokenType.NUMBER, i, i + len(val), line_num))
                i += len(val)
                continue
            
            # 6. Punctuation
            m = self.re_punct.match(substr)
            if m:
                val = m.group(0)
                tokens.append(Token(val, TokenType.PUNCT, i, i + len(val), line_num))
                i += len(val)
                continue
            
            # 7. Terminator
            m = self.re_terminator.match(substr)
            if m:
                val = m.group(0)
                tokens.append(Token(val, TokenType.TERMINATOR, i, i + len(val), line_num))
                i += len(val)
                continue
            
            # 8. Unrecognized character (Lexical Error)
            err = LexicalError(symbol=ch, position=i, line_num=line_num)
            errors.append(err)
            tokens.append(Token(ch, TokenType.UNKNOWN, i, i + 1, line_num))
            i += 1
            
        return tokens, errors
