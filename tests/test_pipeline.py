"""
Unit tests for Comic Dialogue Analyzer & Character Popularity Engine.
"""

import unittest
from src.cleaner import DialogueCleaner
from src.lexer import ComicLexer, TokenType
from src.classifier import SentenceClassifier, SentenceType
from src.mention_finder import MentionFinder
from src.character_popularity import CharacterPopularityEngine
from src.pipeline import ComicDialoguePipeline


class TestComicDialoguePipeline(unittest.TestCase):
    def setUp(self):
        self.cleaner = DialogueCleaner()
        self.lexer = ComicLexer()
        self.classifier = SentenceClassifier()
        self.popularity = CharacterPopularityEngine()
        self.pipeline = ComicDialoguePipeline()

    def test_speaker_split(self):
        speaker, text = self.cleaner.split_speaker("BATMAN: WHERE COULD HE BE, NATASHA?")
        self.assertEqual(speaker, "BATMAN")
        self.assertEqual(text, "WHERE COULD HE BE, NATASHA?")

        speaker2, text2 = self.cleaner.split_speaker("HAVE A PEANUT.")
        self.assertIsNone(speaker2)
        self.assertEqual(text2, "HAVE A PEANUT.")

    def test_lexer_comic_tokens(self):
        text = "WHERE COULD HE BE, NATASHA? DON'T WAIT... BOOM! WHAT?!"
        tokens, errors = self.lexer.tokenize(text)
        token_types = [t.type for t in tokens]
        
        self.assertIn(TokenType.WORD, token_types)
        self.assertIn(TokenType.CONTRACTION, token_types)
        self.assertIn(TokenType.ELLIPSIS, token_types)
        self.assertIn(TokenType.SOUND_FX, token_types)
        self.assertIn(TokenType.INTERROBANG, token_types)
        self.assertEqual(len(errors), 0)

    def test_lexical_errors_ocr_junk(self):
        text = "BATMAN~ WE HAVE A PROBLEM #4."
        tokens, errors = self.lexer.tokenize(text)
        self.assertEqual(len(errors), 2)
        self.assertEqual(errors[0].symbol, "~")
        self.assertEqual(errors[0].position, 6)
        self.assertEqual(errors[1].symbol, "#")
        self.assertEqual(errors[1].position, 26)

    def test_sentence_classification_table_2(self):
        # Case 1: Question
        t1, _ = self.lexer.tokenize("WHERE COULD HE BE, NATASHA?")
        res1 = self.classifier.classify(t1)
        self.assertEqual(res1.sentence_type, SentenceType.QUESTION)

        # Case 2: Command
        t2, _ = self.lexer.tokenize("HAVE A PEANUT.")
        res2 = self.classifier.classify(t2)
        self.assertEqual(res2.sentence_type, SentenceType.COMMAND)

        # Case 3: Statement
        t3, _ = self.lexer.tokenize("I JUST STOPPED THE ENTIRE WORLD FROM BEING EATEN, DINAH.")
        res3 = self.classifier.classify(t3)
        self.assertEqual(res3.sentence_type, SentenceType.STATEMENT)

        # Case 4: Exclamation & Tone
        t4, _ = self.lexer.tokenize("AAARGH! LOOK OUT!")
        res4 = self.classifier.classify(t4)
        self.assertEqual(res4.sentence_type, SentenceType.EXCLAMATION)
        self.assertTrue(res4.tone.is_shouting)
        self.assertTrue(res4.tone.is_pain_or_action)

    def test_vocative_and_mentions(self):
        known = {"NATASHA", "DINAH", "BATMAN", "SUPERMAN", "CLARK"}
        finder = MentionFinder(known_names=known)

        # Trailing vocative: comma + name + terminator
        tokens, _ = self.lexer.tokenize("WHERE COULD HE BE, NATASHA?")
        res = finder.extract(tokens)
        self.assertEqual(res.addressed_name, "NATASHA")

        # Third-party mention
        tokens_mention, _ = self.lexer.tokenize("I HEARD THAT SUPERMAN IS IN METROPOLIS, BATMAN.")
        res_mention = finder.extract(tokens_mention, speaker="ROBIN")
        self.assertEqual(res_mention.addressed_name, "BATMAN")
        self.assertIn("SUPERMAN", res_mention.mentioned_names)

    def test_alias_merging_and_popularity_ranking(self):
        engine = CharacterPopularityEngine()
        
        # Bruce Wayne / Batman speaking and being addressed
        engine.record_activity(speaker="BRUCE", addressed="NATASHA")
        engine.record_activity(speaker="BATMAN", addressed="ROBIN")
        engine.record_activity(speaker="ROBIN", addressed="BATMAN")
        engine.record_activity(speaker="JOKER", mentions=["THE DARK KNIGHT"])
        
        rankings = engine.compute_rankings()
        top_character = rankings[0]
        
        # Canonical name should be merged to BATMAN
        self.assertEqual(top_character.canonical_name, "BATMAN")
        self.assertEqual(top_character.spoken_count, 2)     # "BRUCE" + "BATMAN"
        self.assertEqual(top_character.addressed_count, 1)  # addressed by ROBIN
        self.assertEqual(top_character.mentioned_count, 1)  # mentioned as THE DARK KNIGHT
        self.assertGreater(top_character.popularity_score, 0)


if __name__ == "__main__":
    unittest.main()
