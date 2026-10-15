"""
Mention Finder and Vocative Extractor.
Extracts directly addressed characters via lexical vocative patterns
and finds third-party character mentions in dialogue tokens.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Set, Tuple
from .config import TokenType
from .lexer import Token


@dataclass
class MentionResult:
    addressed_name: Optional[str] = None
    mentioned_names: List[str] = field(default_factory=list)


class MentionFinder:
    def __init__(self, known_names: Optional[Set[str]] = None):
        """
        known_names: Set of uppercase name strings/aliases used to identify characters.
        """
        self.known_names = set(known_names) if known_names else set()

    def add_known_name(self, name: str) -> None:
        self.known_names.add(name.upper())

    def add_known_names(self, names: Set[str]) -> None:
        for n in names:
            self.known_names.add(n.upper())

    def find_vocative(self, tokens: List[Token]) -> Optional[Tuple[str, int]]:
        """
        Detects vocative (person addressed) using lexical patterns:
        1. Trailing vocative: COMMA + NAME + TERMINATOR/INTERROBANG/ELLIPSIS
           Example: 'WHERE COULD HE BE, NATASHA?' -> 'NATASHA'
           Example: '... BEING EATEN, DINAH.' -> 'DINAH'
        2. Leading vocative: NAME + COMMA at start of sentence
           Example: 'NATASHA, LOOK OUT!' -> 'NATASHA'
        3. Medial vocative: COMMA + NAME + COMMA
           Example: 'I TOLD YOU, BRUCE, TO WAIT.' -> 'BRUCE'
        
        Returns tuple of (name, token_index) or None.
        """
        n = len(tokens)
        if n < 3:
            return None

        # Pattern 1: Leading vocative (<NAME>, <COMMA>, ...)
        first_tok = tokens[0]
        second_tok = tokens[1]
        if (first_tok.type == TokenType.WORD and
            second_tok.type == TokenType.PUNCT and second_tok.value == ","):
            candidate = first_tok.value.upper()
            if not self.known_names or candidate in self.known_names:
                return candidate, 0

        # Pattern 2: Comma + Name + Terminator/Ellipsis/Interrobang/Comma (at end or mid-clause)
        # e.g. "..., NATASHA?", "..., BRUCE... WE HAVE BACKUP.", "LISTEN TO ME, DICK. WE TRUST HIM."
        for i in range(1, n - 1):
            prev_tok = tokens[i - 1]
            curr_tok = tokens[i]
            next_tok = tokens[i + 1]

            if (prev_tok.type == TokenType.PUNCT and prev_tok.value == "," and
                curr_tok.type == TokenType.WORD and
                (next_tok.type in (TokenType.TERMINATOR, TokenType.INTERROBANG, TokenType.ELLIPSIS) or
                 (next_tok.type == TokenType.PUNCT and next_tok.value == ","))):
                candidate = curr_tok.value.upper()
                if not self.known_names or candidate in self.known_names:
                    return candidate, i

        return None

    def find_mentions(
        self,
        tokens: List[Token],
        speaker: Optional[str] = None,
        vocative_idx: Optional[int] = None
    ) -> List[str]:
        """
        Identifies third-party character names mentioned inside the sentence.
        Excludes the speaker and the addressed vocative target.
        """
        mentions: List[str] = []
        speaker_upper = speaker.upper() if speaker else ""
        
        # Check single-word and multi-word candidate matches from tokens
        # First gather word tokens with their indices
        word_indices = [
            (i, tokens[i].value.upper())
            for i in range(len(tokens))
            if tokens[i].type == TokenType.WORD and i != vocative_idx
        ]

        # Multi-word checks first (e.g. "IRON MAN", "BLACK WIDOW", "GREEN LANTERN")
        matched_indices = set()
        for length in (3, 2):
            for j in range(len(word_indices) - length + 1):
                window_indices = [word_indices[j + k][0] for k in range(length)]
                if any(idx in matched_indices for idx in window_indices):
                    continue
                window_phrase = " ".join(word_indices[j + k][1] for k in range(length))
                if window_phrase in self.known_names:
                    if window_phrase != speaker_upper:
                        mentions.append(window_phrase)
                        for idx in window_indices:
                            matched_indices.add(idx)

        # Single-word checks
        for idx, word_upper in word_indices:
            if idx in matched_indices:
                continue
            if word_upper in self.known_names:
                if word_upper != speaker_upper:
                    mentions.append(word_upper)

        return mentions

    def extract(self, tokens: List[Token], speaker: Optional[str] = None) -> MentionResult:
        """
        Runs both vocative (addressed) extraction and mentions discovery.
        """
        voc_res = self.find_vocative(tokens)
        addressed_name = voc_res[0] if voc_res else None
        voc_idx = voc_res[1] if voc_res else None
        
        mentions = self.find_mentions(tokens, speaker=speaker, vocative_idx=voc_idx)
        return MentionResult(addressed_name=addressed_name, mentioned_names=mentions)
