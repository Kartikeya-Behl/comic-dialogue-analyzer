"""
Statistics and Reporting Engine.
Produces summary statistics over dataset batches:
- Sentence type distribution
- Token class breakdown & top tokens
- Lexical error audit with character coordinates
- Tone profile
- Character Popularity Rankings & Leaderboard
"""

import time
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from .pipeline import SentenceAnalysis, ComicDialoguePipeline
from .config import SentenceType, TokenType
from .network_analyzer import ConversationalNetworkAnalyzer


@dataclass
class DatasetReport:
    total_sentences: int
    total_tokens: int
    total_lexical_errors: int
    type_distribution: Dict[str, int]
    token_class_distribution: Dict[str, int]
    top_tokens: List[Dict[str, Any]]
    lexical_errors: List[Dict[str, Any]]
    tone_distribution: Dict[str, int]
    character_rankings: List[Dict[str, Any]]
    processing_time_ms: float
    network_summary: Optional[Dict[str, Any]] = None


class DialogueReporter:
    def __init__(self, pipeline: ComicDialoguePipeline):
        self.pipeline = pipeline

    def generate_report(self, analyses: List[SentenceAnalysis], elapsed_sec: float = 0.0) -> DatasetReport:
        """
        Aggregates batch results into a full statistical report.
        """
        total_sentences = len(analyses)
        total_tokens = sum(len(a.tokens) for a in analyses)
        
        # 1. Sentence type distribution
        type_dist = {st.value: 0 for st in SentenceType}
        for a in analyses:
            type_dist[a.sentence_type.value] = type_dist.get(a.sentence_type.value, 0) + 1

        # 2. Token class distribution from symbol table
        token_class_dist = self.pipeline.symbol_table.get_type_distribution()

        # 3. Top tokens
        top_symbols = self.pipeline.symbol_table.get_top_tokens(limit=10)
        top_tokens = [
            {"token": s.name, "type": s.token_type.value, "count": s.count}
            for s in top_symbols
        ]

        # 4. Lexical errors
        lexical_errors = []
        for a in analyses:
            for err in a.lexical_errors:
                lexical_errors.append({
                    "line": a.line_num,
                    "symbol": err.symbol,
                    "position": err.position,
                    "description": err.description,
                    "sentence_snippet": a.raw_text
                })

        # 5. Tone breakdown
        tone_dist = {
            "shouting": sum(1 for a in analyses if a.tone_cues.is_shouting),
            "hesitation": sum(1 for a in analyses if a.tone_cues.is_hesitant),
            "surprise_or_incredulity": sum(1 for a in analyses if a.tone_cues.is_surprise_or_incredulity),
            "pain_or_sound_fx": sum(1 for a in analyses if a.tone_cues.is_pain_or_action)
        }

        # 6. Character Popularity Leaderboard
        rankings = self.pipeline.popularity_engine.compute_rankings()
        char_rankings = [
            {
                "rank": i,
                "character": c.canonical_name,
                "spoken": c.spoken_count,
                "addressed": c.addressed_count,
                "mentioned": c.mentioned_count,
                "tone": c.tone_count,
                "score": round(c.popularity_score, 2),
                "aliases": list(c.aliases_encountered)
            }
            for i, c in enumerate(rankings, 1)
        ]

        # 7. Conversational Network Centrality Data
        net_analyzer = ConversationalNetworkAnalyzer(self.pipeline.popularity_engine)
        net_data = net_analyzer.build_network_data()

        return DatasetReport(
            total_sentences=total_sentences,
            total_tokens=total_tokens,
            total_lexical_errors=len(lexical_errors),
            type_distribution=type_dist,
            token_class_distribution=token_class_dist,
            top_tokens=top_tokens,
            lexical_errors=lexical_errors,
            tone_distribution=tone_dist,
            character_rankings=char_rankings,
            processing_time_ms=round(elapsed_sec * 1000, 2),
            network_summary=net_data
        )

    def print_text_summary(self, report: DatasetReport) -> str:
        """
        Renders a clean human-readable console summary of the analysis report.
        """
        lines = []
        lines.append("=" * 80)
        lines.append(" " * 22 + "COMIC DIALOGUE DATASET ANALYSIS")
        lines.append("=" * 80)
        lines.append(f"Sentences Processed : {report.total_sentences}")
        lines.append(f"Total Tokens        : {report.total_tokens}")
        lines.append(f"Lexical Errors      : {report.total_lexical_errors}")
        lines.append(f"Processing Time     : {report.processing_time_ms:.2f} ms")
        lines.append("-" * 80)

        # Sentence Type Breakdown
        lines.append("[1] SENTENCE CLASSIFICATION SPREAD:")
        for st_name, count in report.type_distribution.items():
            pct = (count / report.total_sentences * 100) if report.total_sentences else 0.0
            lines.append(f"    - {st_name.capitalize():<12}: {count:>4} ({pct:>5.1f}%)")
        lines.append("-" * 80)

        # Tone Cues Breakdown
        lines.append("[2] TONE CUES DETECTED:")
        for tone_name, count in report.tone_distribution.items():
            lines.append(f"    - {tone_name.replace('_', ' ').capitalize():<24}: {count:>4}")
        lines.append("-" * 80)

        # Token Class Distribution
        lines.append("[3] TOKEN CLASS SPREAD:")
        for t_type, count in sorted(report.token_class_distribution.items(), key=lambda x: x[1], reverse=True):
            pct = (count / report.total_tokens * 100) if report.total_tokens else 0.0
            lines.append(f"    - {t_type:<14}: {count:>5} ({pct:>5.1f}%)")
        lines.append("-" * 80)

        # Most Frequent Tokens
        lines.append("[4] TOP FREQUENT TOKENS:")
        lines.append(f"    {'TOKEN':<15}{'CLASS':<15}{'FREQUENCY':<10}")
        for t in report.top_tokens[:8]:
            lines.append(f"    {t['token']:<15}{t['type']:<15}{t['count']:<10}")
        lines.append("-" * 80)

        # Lexical Errors
        if report.lexical_errors:
            lines.append(f"[5] LEXICAL ERRORS (OCR JUNK) [{len(report.lexical_errors)} found]:")
            for err in report.lexical_errors[:5]:
                lines.append(f"    Line {err['line']}, Pos {err['position']}: '{err['symbol']}' in \"{err['sentence_snippet']}\"")
            if len(report.lexical_errors) > 5:
                lines.append(f"    ... and {len(report.lexical_errors) - 5} more.")
            lines.append("-" * 80)

        # Character Popularity Leaderboard (PRIORITY)
        lines.append("[*] CHARACTER POPULARITY LEADERBOARD (PRIORITY RANKING):")
        lines.append(f"    {'RANK':<5}{'CHARACTER':<20}{'SPOKEN':<9}{'ADDRESSED':<11}{'MENTIONS':<10}{'TONE':<8}{'SCORE':<8}")
        lines.append("    " + "-" * 71)
        for c in report.character_rankings[:15]:
            lines.append(
                f"    {c['rank']:<5}{c['character']:<20}{c['spoken']:<9}{c['addressed']:<11}{c['mentioned']:<10}{c['tone']:<8}{c['score']:<8.1f}"
            )
        lines.append("-" * 80)

        # Conversational Network Centrality
        if report.network_summary and report.network_summary.get("nodes"):
            net = report.network_summary
            lines.append("[*] CONVERSATIONAL INTERACTION NETWORK & CENTRALITY:")
            lines.append(f"    {'RANK':<5}{'CHARACTER':<18}{'IN-DEG':<8}{'OUT-DEG':<9}{'DEG-CENT':<11}{'BETWEENNESS':<13}")
            lines.append("    " + "-" * 64)
            for i, n in enumerate(net["nodes"][:10], 1):
                lines.append(
                    f"    {i:<5}{n['character']:<18}{n['in_degree']:<8}{n['out_degree']:<9}"
                    f"{n['degree_centrality']:<11.3f}{n['betweenness_centrality']:<13.4f}"
                )
            if net.get("edges"):
                lines.append("    Top Conversational Edges (Who Addresses Whom):")
                sorted_edges = sorted(net["edges"], key=lambda e: e["weight"], reverse=True)
                for e in sorted_edges[:6]:
                    lines.append(f"      * {e['source']:<14} --({e['weight']:>2}x)--> {e['target']}")
            lines.append("-" * 80)

        lines.append("=" * 80)

        output = "\n".join(lines)
        return output
