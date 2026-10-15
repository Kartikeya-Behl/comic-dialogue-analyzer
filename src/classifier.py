"""
Rule-Based Sentence Classifier and Tone Cue Analyzer.
Classifies dialogue into statement, question, exclamation, or command,
and extracts tonal signals (shouting, hesitation, surprise, pain).
"""

from dataclasses import dataclass, field
from typing import List, Set
from .config import TokenType, SentenceType, QUESTION_STARTERS, IMPERATIVE_VERBS
from .lexer import Token


@dataclass
class ToneCues:
    is_shouting: bool = False
    is_hesitant: bool = False
    is_surprise_or_incredulity: bool = False
    is_pain_or_action: bool = False
    tags: List[str] = field(default_factory=list)


@dataclass
class ClassificationResult:
    sentence_type: SentenceType
    tone: ToneCues
    primary_reason: str


class SentenceClassifier:
    def __init__(
        self,
        question_starters: Set[str] = QUESTION_STARTERS,
        imperative_verbs: Set[str] = IMPERATIVE_VERBS
    ):
        self.question_starters = question_starters
        self.imperative_verbs = imperative_verbs

    def extract_tone(self, tokens: List[Token]) -> ToneCues:
        """
        Analyzes tokens to identify tone markers such as shouting,
        hesitation, surprise/incredulity, and sound effects.
        """
        cues = ToneCues()
        
        for tok in tokens:
            # Hesitation: ellipsis
            if tok.type == TokenType.ELLIPSIS:
                cues.is_hesitant = True
                if "hesitation" not in cues.tags:
                    cues.tags.append("hesitation")
            
            # Surprise / Incredulity: interrobang
            elif tok.type == TokenType.INTERROBANG:
                cues.is_surprise_or_incredulity = True
                cues.is_shouting = True
                if "surprise/incredulity" not in cues.tags:
                    cues.tags.append("surprise/incredulity")
            
            # Shouting: exclamation marks
            elif tok.type == TokenType.TERMINATOR and "!" in tok.value:
                cues.is_shouting = True
                if "shouting" not in cues.tags:
                    cues.tags.append("shouting")
            
            # Action / Pain / Sound FX
            elif tok.type == TokenType.SOUND_FX:
                cues.is_pain_or_action = True
                if "pain/sound_fx" not in cues.tags:
                    cues.tags.append("pain/sound_fx")
        
        return cues

    def classify(self, tokens: List[Token]) -> ClassificationResult:
        """
        Classifies the sentence into statement, question, exclamation, or command
        using opening words, closing punctuation, and token classes.
        """
        tone = self.extract_tone(tokens)
        
        if not tokens:
            return ClassificationResult(
                sentence_type=SentenceType.STATEMENT,
                tone=tone,
                primary_reason="Empty token sequence"
            )

        # Extract meaningful first non-punctuation word
        word_tokens = [t for t in tokens if t.type in (TokenType.WORD, TokenType.SOUND_FX, TokenType.CONTRACTION)]
        first_word = word_tokens[0].value.upper() if word_tokens else ""
        
        # Extract closing terminator/punctuation
        last_tok = tokens[-1]
        last_symbol = last_tok.value if last_tok.type in (TokenType.TERMINATOR, TokenType.INTERROBANG, TokenType.ELLIPSIS) else ""

        # Case 1: Pure sound effect sequence
        if word_tokens and all(t.type == TokenType.SOUND_FX for t in word_tokens):
            return ClassificationResult(
                sentence_type=SentenceType.EXCLAMATION,
                tone=tone,
                primary_reason="Exclusively composed of sound effects / onomatopoeia"
            )

        # Case 2: Interrobang closing
        if last_tok.type == TokenType.INTERROBANG:
            if first_word in self.question_starters:
                return ClassificationResult(
                    sentence_type=SentenceType.QUESTION,
                    tone=tone,
                    primary_reason=f"Opening question word '{first_word}' with interrobang terminator"
                )
            return ClassificationResult(
                sentence_type=SentenceType.EXCLAMATION,
                tone=tone,
                primary_reason="Closing interrobang expressing exclamation"
            )

        # Case 3: Question mark closing
        if "?" in last_symbol:
            return ClassificationResult(
                sentence_type=SentenceType.QUESTION,
                tone=tone,
                primary_reason=f"Terminating question mark (opening: '{first_word}')"
            )

        # Case 4: Opening with Question starter
        if first_word in self.question_starters and "?" in last_symbol:
            return ClassificationResult(
                sentence_type=SentenceType.QUESTION,
                tone=tone,
                primary_reason=f"Begins with '{first_word}' and closes with question mark"
            )

        # Case 5: Command / Imperative check
        # Starts directly with an imperative verb
        if first_word in self.imperative_verbs:
            return ClassificationResult(
                sentence_type=SentenceType.COMMAND,
                tone=tone,
                primary_reason=f"Starts with imperative verb '{first_word}'"
            )

        # Case 6: Exclamation mark closing
        if "!" in last_symbol:
            return ClassificationResult(
                sentence_type=SentenceType.EXCLAMATION,
                tone=tone,
                primary_reason="Closes with exclamation mark"
            )

        # Case 7: Default Statement
        return ClassificationResult(
            sentence_type=SentenceType.STATEMENT,
            tone=tone,
            primary_reason="Standard declarative construction"
        )
