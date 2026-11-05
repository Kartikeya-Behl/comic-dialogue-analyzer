"""
Pipeline Coordinator for Comic Dialogue Analysis.
Integrates speaker extraction, cleaning, lexing, symbol table tracking,
sentence & tone classification, and character popularity tallying.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from .cleaner import DialogueCleaner, PreprocessedSentence
from .lexer import ComicLexer, Token, LexicalError
from .symbol_table import SymbolTable
from .classifier import SentenceClassifier, ClassificationResult, ToneCues
from .mention_finder import MentionFinder, MentionResult
from .character_popularity import CharacterPopularityEngine, CharacterStats
from .config import SentenceType, TokenType


@dataclass
class SentenceAnalysis:
    line_num: int
    speaker: Optional[str]
    raw_text: str
    cleaned_text: str
    tokens: List[Token]
    lexical_errors: List[LexicalError]
    sentence_type: SentenceType
    tone_cues: ToneCues
    addressed: Optional[str]
    mentions: List[str]
    classification_reason: str
    clause_index: int = 1
    total_clauses: int = 1
    bubble_raw_text: Optional[str] = None

    def short_tokens_str(self) -> str:
        """
        Formats tokens in short form as presented in the paper (e.g. 'WORD WORD PUNCT WORD TERMINATOR').
        """
        return " ".join(t.type.value for t in self.tokens)


class ComicDialoguePipeline:
    def __init__(
        self,
        cleaner: Optional[DialogueCleaner] = None,
        lexer: Optional[ComicLexer] = None,
        symbol_table: Optional[SymbolTable] = None,
        classifier: Optional[SentenceClassifier] = None,
        popularity_engine: Optional[CharacterPopularityEngine] = None
    ):
        self.cleaner = cleaner or DialogueCleaner()
        self.lexer = lexer or ComicLexer()
        self.symbol_table = symbol_table or SymbolTable()
        self.classifier = classifier or SentenceClassifier()
        self.popularity_engine = popularity_engine or CharacterPopularityEngine()
        
        # Link mention finder with known names from popularity engine & aliases
        known_names = self.popularity_engine.get_known_character_names()
        self.mention_finder = MentionFinder(known_names=known_names)

    def set_aliases(self, aliases: dict) -> None:
        """
        Updates the character aliases dynamically and refreshes the mention finder lexicon.
        """
        self.popularity_engine.set_aliases(aliases)
        known_names = self.popularity_engine.get_known_character_names()
        self.mention_finder = MentionFinder(known_names=known_names)

    def analyze_sentence(self, line: str, line_num: int = 1) -> SentenceAnalysis:
        """
        Runs complete analysis for a single dialogue sentence without bubble splitting.
        """
        # 1. Speaker Split & Preprocessing
        prep: PreprocessedSentence = self.cleaner.preprocess(line)

        # 2. Lexical Analysis
        tokens, errors = self.lexer.tokenize(prep.cleaned_text, line_num=line_num)

        # 3. Update Symbol Table
        known_names = self.popularity_engine.get_known_character_names()
        for tok in tokens:
            is_name = tok.value.upper() in known_names
            self.symbol_table.insert(
                token_value=tok.value,
                token_type=tok.type,
                line_num=line_num,
                is_proper_name=is_name
            )

        # 4. Sentence Classification & Tone Analysis
        class_res: ClassificationResult = self.classifier.classify(tokens)

        # 5. Vocative & Mention Detection
        mention_res: MentionResult = self.mention_finder.extract(tokens, speaker=prep.speaker)

        # 6. Character Popularity Tallying
        has_high_tone = class_res.tone.is_shouting or class_res.tone.is_pain_or_action
        self.popularity_engine.record_activity(
            speaker=prep.speaker,
            addressed=mention_res.addressed_name,
            mentions=mention_res.mentioned_names,
            has_high_tone=has_high_tone,
            line_num=line_num
        )

        return SentenceAnalysis(
            line_num=line_num,
            speaker=prep.speaker,
            raw_text=prep.raw_text,
            cleaned_text=prep.cleaned_text,
            tokens=tokens,
            lexical_errors=errors,
            sentence_type=class_res.sentence_type,
            tone_cues=class_res.tone,
            addressed=mention_res.addressed_name,
            mentions=mention_res.mentioned_names,
            classification_reason=class_res.primary_reason,
            clause_index=1,
            total_clauses=1,
            bubble_raw_text=line
        )

    def analyze_bubble(
        self,
        line: str,
        line_num: int = 1,
        tally_speaker_once: bool = True
    ) -> List[SentenceAnalysis]:
        """
        Splits a multi-sentence speech bubble into individual clauses,
        evaluates tone and vocatives separately for each clause,
        and aggregates results back to the original speaker.
        """
        prep_clauses: List[PreprocessedSentence] = self.cleaner.preprocess_bubble(line)
        if not prep_clauses:
            return [self.analyze_sentence(line, line_num=line_num)]

        analyses: List[SentenceAnalysis] = []
        known_names = self.popularity_engine.get_known_character_names()
        speaker = prep_clauses[0].speaker
        bubble_has_high_tone = False

        # First pass: classify and collect information for all clauses
        clause_items = []
        for prep in prep_clauses:
            tokens, errors = self.lexer.tokenize(prep.cleaned_text, line_num=line_num)
            for tok in tokens:
                is_name = tok.value.upper() in known_names
                self.symbol_table.insert(
                    token_value=tok.value,
                    token_type=tok.type,
                    line_num=line_num,
                    is_proper_name=is_name
                )
            class_res = self.classifier.classify(tokens)
            mention_res = self.mention_finder.extract(tokens, speaker=speaker)
            high_tone = class_res.tone.is_shouting or class_res.tone.is_pain_or_action
            if high_tone:
                bubble_has_high_tone = True

            clause_items.append((prep, tokens, errors, class_res, mention_res, high_tone))

        # Second pass: record activity
        for idx, (prep, tokens, errors, class_res, mention_res, high_tone) in enumerate(clause_items):
            # If tally_speaker_once is True, credit the speaker turn once on the first clause
            spk_to_record = speaker if (not tally_speaker_once or idx == 0) else None
            high_tone_to_record = bubble_has_high_tone if idx == 0 else high_tone

            self.popularity_engine.record_activity(
                speaker=spk_to_record,
                addressed=mention_res.addressed_name,
                mentions=mention_res.mentioned_names,
                has_high_tone=high_tone_to_record if spk_to_record else False,
                line_num=line_num
            )

            analyses.append(
                SentenceAnalysis(
                    line_num=line_num,
                    speaker=speaker,
                    raw_text=prep.raw_text,
                    cleaned_text=prep.cleaned_text,
                    tokens=tokens,
                    lexical_errors=errors,
                    sentence_type=class_res.sentence_type,
                    tone_cues=class_res.tone,
                    addressed=mention_res.addressed_name,
                    mentions=mention_res.mentioned_names,
                    classification_reason=class_res.primary_reason,
                    clause_index=prep.clause_index,
                    total_clauses=prep.total_clauses,
                    bubble_raw_text=line
                )
            )

        return analyses

    def analyze_batch(
        self,
        lines: List[str],
        split_bubbles: bool = True
    ) -> List[SentenceAnalysis]:
        """
        Processes a list of dialogue lines. If split_bubbles is True,
        multi-sentence bubbles are split into individual clauses.
        """
        results: List[SentenceAnalysis] = []
        for i, line in enumerate(lines, 1):
            if not line.strip() or line.strip().startswith("#"):
                continue
            if split_bubbles:
                bubble_results = self.analyze_bubble(line, line_num=i)
                results.extend(bubble_results)
            else:
                res = self.analyze_sentence(line, line_num=i)
                results.append(res)
        return results
