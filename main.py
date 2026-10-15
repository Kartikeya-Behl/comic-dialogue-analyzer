"""
Main CLI entry point for Comic Dialogue Analyzer & Character Popularity Engine.
"""

import sys
import os
import argparse
import time
from typing import List

# Ensure src is in python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.pipeline import ComicDialoguePipeline, SentenceAnalysis
from src.reporter import DialogueReporter, DatasetReport


def print_sentence_detail(res: SentenceAnalysis) -> None:
    print("-" * 80)
    print(f"Line {res.line_num}: {res.speaker or 'ANONYMOUS'}: {res.raw_text}")
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


def run_batch_file(filepath: str, show_per_sentence: bool = True) -> None:
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' does not exist.")
        sys.exit(1)

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    pipeline = ComicDialoguePipeline()
    reporter = DialogueReporter(pipeline)

    print(f"\n[+] Analyzing Comic Dialogue file: {filepath}")
    print(f"[+] Loaded {len(lines)} raw lines (ignoring comments/empty)...\n")

    t_start = time.perf_counter()
    analyses: List[SentenceAnalysis] = pipeline.analyze_batch(lines)
    t_end = time.perf_counter()

    if show_per_sentence:
        print("=" * 80)
        print("                     INDIVIDUAL SENTENCE RESULTS")
        print("=" * 80)
        for a in analyses:
            print_sentence_detail(a)
        print()

    # Generate dataset summary
    report: DatasetReport = reporter.generate_report(analyses, elapsed_sec=t_end - t_start)
    print(reporter.print_text_summary(report))


def run_single_sentence(sentence_text: str) -> None:
    pipeline = ComicDialoguePipeline()
    res = pipeline.analyze_sentence(sentence_text)
    
    print("\n" + "=" * 80)
    print("                    SINGLE SENTENCE ANALYSIS RESULT")
    print("=" * 80)
    print_sentence_detail(res)
    
    print("\nDetailed Token Stream:")
    for tok in res.tokens:
        print(f"  - [{tok.type.value:<12}] '{tok.value}' (span {tok.start_pos}:{tok.end_pos})")
    
    print("\nSymbol Table Snapshot:")
    for key, entry in pipeline.symbol_table.table.items():
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
        help="Analyze a single input sentence string"
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Omit individual sentence details in batch mode, show summary only"
    )

    args = parser.parse_args()

    if args.sentence:
        run_single_sentence(args.sentence)
    else:
        run_batch_file(args.file, show_per_sentence=not args.compact)


if __name__ == "__main__":
    main()
