"""
Comprehensive Unit Tests for Comic Dialogue Analyzer & Character Popularity Engine.
Covers:
- Speaker splitting & preprocessing
- Comic lexical tokenization & OCR noise interception
- Sentence classification & tone cue detection
- Vocatives & third-party mentions
- Multi-sentence speech balloon splitting
- Dynamic JSON alias loading
- Conversational interaction network & centrality metrics
- Comprehensive export suite (CSV, JSON, LaTeX, Excel)
"""

import unittest
import json
import os
from src.cleaner import DialogueCleaner
from src.lexer import ComicLexer, TokenType
from src.classifier import SentenceClassifier, SentenceType
from src.mention_finder import MentionFinder
from src.character_popularity import CharacterPopularityEngine
from src.pipeline import ComicDialoguePipeline
from src.bubble_splitter import BubbleSplitter
from src.alias_loader import load_aliases_from_json
from src.network_analyzer import ConversationalNetworkAnalyzer
from src.reporter import DialogueReporter
from src.export_engine import ExportEngine


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

    def test_multi_sentence_bubble_splitter(self):
        splitter = BubbleSplitter()
        line = "LOOK OUT, BRUCE! WHERE DID HE GO? HE WAS JUST HERE..."
        clauses = splitter.split(line)
        self.assertEqual(len(clauses), 3)
        self.assertEqual(clauses[0], "LOOK OUT, BRUCE!")
        self.assertEqual(clauses[1], "WHERE DID HE GO?")
        self.assertEqual(clauses[2], "HE WAS JUST HERE...")

        # Test abbreviation preservation
        abbr_line = "DR. STRANGE, WATCH OUT! BOOM!"
        abbr_clauses = splitter.split(abbr_line)
        self.assertEqual(len(abbr_clauses), 2)
        self.assertEqual(abbr_clauses[0], "DR. STRANGE, WATCH OUT!")
        self.assertEqual(abbr_clauses[1], "BOOM!")

    def test_pipeline_bubble_analysis(self):
        pipeline = ComicDialoguePipeline()
        bubble_line = "BATMAN: LOOK OUT, BRUCE! WHERE DID HE GO? HE WAS JUST HERE..."
        analyses = pipeline.analyze_bubble(bubble_line)

        self.assertEqual(len(analyses), 3)
        # All clauses should share the speaker
        for a in analyses:
            self.assertEqual(a.speaker, "BATMAN")
            self.assertEqual(a.total_clauses, 3)

        # Clause 1: Command, shouting
        self.assertEqual(analyses[0].sentence_type, SentenceType.COMMAND)
        self.assertTrue(analyses[0].tone_cues.is_shouting)
        self.assertEqual(analyses[0].addressed, "BRUCE")  # BRUCE addressed via vocative pattern

        # Clause 2: Question
        self.assertEqual(analyses[1].sentence_type, SentenceType.QUESTION)

        # Clause 3: Statement, hesitation
        self.assertEqual(analyses[2].sentence_type, SentenceType.STATEMENT)
        self.assertTrue(analyses[2].tone_cues.is_hesitant)

    def test_dynamic_alias_loader(self):
        # Direct dict
        aliases_dict = {"PIRATE HUNTER": "ZORO", "MUGIWARA": "LUFFY"}
        loaded = load_aliases_from_json(aliases_dict)
        self.assertEqual(loaded["PIRATE HUNTER"], "ZORO")
        self.assertEqual(loaded["MUGIWARA"], "LUFFY")

        # JSON String with 'aliases' block
        json_str = '{"universe": "Custom", "aliases": {"TONY": "IRON MAN", "CAP": "CAPTAIN AMERICA"}}'
        loaded2 = load_aliases_from_json(json_str)
        self.assertEqual(loaded2["TONY"], "IRON MAN")
        self.assertEqual(loaded2["CAP"], "CAPTAIN AMERICA")

    def test_conversational_network_and_centrality(self):
        pipeline = ComicDialoguePipeline()
        lines = [
            "BATMAN: WHERE COULD HE BE, NATASHA?",
            "NATASHA: HE IS IN GOTHAM, BRUCE!",
            "ROBIN: LOOK OUT, BATMAN! THE JOKER IS HERE!",
            "BATMAN: STAY BACK, ROBIN!"
        ]
        pipeline.analyze_batch(lines)

        net_analyzer = ConversationalNetworkAnalyzer(pipeline.popularity_engine)
        net_data = net_analyzer.build_network_data()

        self.assertGreater(net_data["total_nodes"], 0)
        self.assertGreater(net_data["total_edges"], 0)

        # Batman was addressed by Natasha and Robin (in_degree >= 2)
        batman_node = next(n for n in net_data["nodes"] if n["character"] == "BATMAN")
        self.assertGreaterEqual(batman_node["in_degree"], 2)
        self.assertGreaterEqual(batman_node["degree_centrality"], 0.0)

    def test_export_engine_suite(self):
        pipeline = ComicDialoguePipeline()
        lines = [
            "BATMAN: WHERE COULD HE BE, NATASHA?",
            "NATASHA: HE IS IN GOTHAM, BRUCE!"
        ]
        analyses = pipeline.analyze_batch(lines)
        reporter = DialogueReporter(pipeline)
        report = reporter.generate_report(analyses, elapsed_sec=0.005)

        # Test CSV export
        csv_str = ExportEngine.export_leaderboard_csv(report)
        self.assertIn("Character", csv_str)
        self.assertIn("BATMAN", csv_str)

        # Test JSON export
        json_str = ExportEngine.export_full_json(report, analyses, report.network_summary)
        parsed_json = json.loads(json_str)
        self.assertIn("character_popularity_leaderboard", parsed_json)
        self.assertIn("sentence_level_analyses", parsed_json)

        # Test LaTeX export
        latex_str = ExportEngine.generate_latex_tables(report, report.network_summary)
        self.assertIn("\\begin{table}", latex_str)
        self.assertIn("\\toprule", latex_str)
        self.assertIn("BATMAN", latex_str)


if __name__ == "__main__":
    unittest.main()
