"""
Main CLI entry point for Comic Dialogue Analyzer & Character Popularity Engine.
"""

import sys
import os
import argparse
import time
from typing import List, Optional, Dict

# Ensure src is in python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.pipeline import ComicDialoguePipeline, SentenceAnalysis
from src.reporter import DialogueReporter, DatasetReport
from src.alias_loader import load_aliases_from_json
from src.export_engine import ExportEngine


def print_sentence_detail(res: SentenceAnalysis) -> None:
    print("-" * 80)
    clause_tag = f" [Clause {res.clause_index}/{res.total_clauses}]" if res.total_clauses > 1 else ""
    print(f"Line {res.line_num}{clause_tag}: {res.speaker or 'ANONYMOUS'}: {res.raw_text}")
    print(f"  * Tokens (short)     : {res.short_tokens_str()}")
    print(f"  * Sentence Type      : {res.sentence_type.value.upper()} ({res.classification_reason})")
    
    tone_str = ", ".join(res.tone_cues.tags) if res.tone_cues.tags else "neutral"
    print(f"  * Tone Cues          : {tone_str}")
    
    if res.addressed:
        print(f"  * Who is Addressed   : {res.addressed} (from vocative pattern)")
    if res.mentions:
        print(f"  * Who is Mentioned   : {', '.join(res.mentions)}")
    if res.lexical_errors:
        err_str = "; ".join(f"'{e.symbol}' at char pos {e.position}" for e in res.lexical_errors)
        print(f"  * Lexical Errors     : {err_str}")


def run_batch_file(
    filepath: str,
    show_per_sentence: bool = True,
    split_bubbles: bool = True,
    alias_path: Optional[str] = None,
    export_dir: Optional[str] = None
) -> None:
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' does not exist.")
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    pipeline = ComicDialoguePipeline()

    if alias_path:
        if os.path.exists(alias_path):
            print(f"[+] Loading external aliases from: {alias_path}")
            aliases = load_aliases_from_json(alias_path)
            pipeline.set_aliases(aliases)
        else:
            print(f"[!] Warning: Alias file '{alias_path}' not found, using defaults.")

    reporter = DialogueReporter(pipeline)

    print(f"\n[+] Analyzing Comic Dialogue file: {filepath}")
    print(f"[+] Loaded {len(lines)} raw lines (split_bubbles={'ON' if split_bubbles else 'OFF'})...\n")

    t_start = time.perf_counter()
    analyses: List[SentenceAnalysis] = pipeline.analyze_batch(lines, split_bubbles=split_bubbles)
    t_end = time.perf_counter()

    if show_per_sentence:
        print("=" * 80)
        print("                     INDIVIDUAL SENTENCE RESULTS")
        print("=" * 80)
        for a in analyses[:50]:  # Cap display at 50 to avoid terminal flooding
            print_sentence_detail(a)
        if len(analyses) > 50:
            print(f"\n... and {len(analyses) - 50} more sentences evaluated.")
        print()

    # Generate dataset summary
    report: DatasetReport = reporter.generate_report(analyses, elapsed_sec=t_end - t_start)
    print(reporter.print_text_summary(report))

    # Export if requested
    if export_dir:
        print(f"\n[+] Exporting analysis artifacts to directory: {export_dir}")
        saved = ExportEngine.save_all_exports(
            output_dir=export_dir,
            report=report,
            analyses=analyses,
            network_data=report.network_summary
        )
        for key, fpath in saved.items():
            print(f"    - {key:<16}: {fpath}")
        print("[+] All export artifacts saved successfully!\n")


def run_single_sentence(
    sentence_text: str,
    split_bubbles: bool = True,
    alias_path: Optional[str] = None
) -> None:
    pipeline = ComicDialoguePipeline()
    if alias_path and os.path.exists(alias_path):
        aliases = load_aliases_from_json(alias_path)
        pipeline.set_aliases(aliases)

    if split_bubbles:
        analyses = pipeline.analyze_bubble(sentence_text)
    else:
        analyses = [pipeline.analyze_sentence(sentence_text)]

    print("\n" + "=" * 80)
    print("                    SENTENCE / BUBBLE ANALYSIS RESULT")
    print("=" * 80)
    for a in analyses:
        print_sentence_detail(a)
        print("  Tokens:")
        for tok in a.tokens:
            print(f"    - [{tok.type.value:<12}] '{tok.value}' (span {tok.start_pos}:{tok.end_pos})")

    print("\nSymbol Table Snapshot:")
    for key, entry in list(pipeline.symbol_table.table.items())[:15]:
        print(f"  - {entry.name:<15} Type: {entry.token_type.value:<12} Count: {entry.count} ProperName: {entry.is_proper_name}")

    print("=" * 80 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Compiler-Style Comic Dialogue Analyzer & Character Popularity Engine"
    )
    parser.add_argument(
        "--file", "-f",
        type=str,
        default="data/sample_comic_dialogue.txt",
        help="Path to comic dialogue text file"
    )
    parser.add_argument(
        "--sentence", "-s",
        type=str,
        help="Analyze a single input sentence or multi-clause bubble string"
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Omit individual sentence details in batch mode, show summary only"
    )
    parser.add_argument(
        "--no-split-bubbles",
        action="store_true",
        help="Disable multi-sentence speech bubble splitting"
    )
    parser.add_argument(
        "--aliases", "-a",
        type=str,
        help="Path to external JSON alias configuration file (e.g. data/aliases.json)"
    )
    parser.add_argument(
        "--export", "-e",
        type=str,
        help="Output directory to save CSV, Excel, JSON, and LaTeX paper tables"
    )

    args = parser.parse_args()

    if args.sentence:
        run_single_sentence(
            args.sentence,
            split_bubbles=not args.no_split_bubbles,
            alias_path=args.aliases
        )
    else:
        run_batch_file(
            args.file,
            show_per_sentence=not args.compact,
            split_bubbles=not args.no_split_bubbles,
            alias_path=args.aliases,
            export_dir=args.export
        )


if __name__ == "__main__":
    main()
