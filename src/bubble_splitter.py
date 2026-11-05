"""
Multi-Sentence Speech Bubble Splitter.
Splits multi-sentence comic dialogue balloons into individual syntactic/pragmatic clauses,
preserving comic punctuation, abbreviations, and emotional markers.
"""

import re
from typing import List


# Common abbreviations that end with a period and must not trigger a sentence split
PROTECTED_ABBREVIATIONS = {
    "MR", "MRS", "MS", "DR", "PROF", "CAPT", "COL", "GEN", "LT", "SGT",
    "O.S", "V.O", "VS", "ETC", "I.E", "E.G", "ST", "JR", "SR", "NO", "VOL"
}


class BubbleSplitter:
    """
    Splits multi-sentence speech bubbles into distinct clauses.
    Example:
      'LOOK OUT, BRUCE! WHERE DID HE GO? HE WAS JUST HERE...'
      -> ['LOOK OUT, BRUCE!', 'WHERE DID HE GO?', 'HE WAS JUST HERE...']
    """

    def __init__(self):
        # Pattern matching terminal punctuation sequences:
        # 1. Ellipsis: '...' or '…'
        # 2. Interrobang: '?!', '!?', '?!!', '!??'
        # 3. Repeated or single exclamation: '!+'
        # 4. Repeated or single question mark: '?+'
        # 5. Period: '.'
        self.split_pattern = re.compile(
            r'(\.{3,}|…|(?:\?+!+|!+\?+)[\?!]*|!+|\?+|\.)(?=\s+[A-Z0-9"\'‘“\(\[\-]|\s*$)',
            re.IGNORECASE
        )

    def is_protected_abbreviation(self, text: str, match_end_pos: int) -> bool:
        """
        Checks if a matched period is part of a known title or abbreviation (e.g. 'DR.', 'CAPT.').
        """
        # Look behind from match position to get the preceding word
        prefix = text[:match_end_pos - 1].rstrip()
        word_match = re.search(r'\b([A-Za-z]+)$', prefix)
        if word_match:
            candidate = word_match.group(1).upper()
            if candidate in PROTECTED_ABBREVIATIONS:
                return True
        return False

    def split(self, text: str) -> List[str]:
        """
        Splits dialogue text into individual sentence clauses.
        Returns a list of non-empty clauses with their respective boundary punctuation attached.
        """
        raw = text.strip()
        if not raw:
            return []

        clauses: List[str] = []
        last_idx = 0

        for match in self.split_pattern.finditer(raw):
            terminator = match.group(1)
            end_pos = match.end()

            # If it's a single period, check if it's an abbreviation
            if terminator == "." and self.is_protected_abbreviation(raw, end_pos):
                continue

            clause = raw[last_idx:end_pos].strip()
            if clause:
                clauses.append(clause)
            last_idx = end_pos

        # Remaining trailing text without standard terminator (if any)
        trailing = raw[last_idx:].strip()
        if trailing:
            # If we already have clauses, append trailing fragment
            clauses.append(trailing)
        elif not clauses:
            # No terminator was matched at all; return whole raw text
            clauses.append(raw)

        return clauses
