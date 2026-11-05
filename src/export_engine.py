"""
Comprehensive Export and Download Suite for Comic Dialogue Analysis.
Generates:
- Character Popularity Leaderboard as CSV and Excel (.xlsx)
- Full sentence-level token, classification, and error logs as structured JSON
- Professional LaTeX academic paper tables (booktabs format)
- Network centrality metrics exports
"""

import io
import json
from datetime import datetime
import os
from typing import List, Dict, Any, Optional

from .reporter import DatasetReport
from .pipeline import SentenceAnalysis


class ExportEngine:
    """
    Handles file generation and serialization for CSV, Excel, JSON, and LaTeX tables.
    """

    @staticmethod
    def export_leaderboard_csv(report: DatasetReport) -> str:
        """
        Renders the Character Popularity Leaderboard as standard RFC 4180 CSV text.
        """
        output = io.StringIO()
        headers = ["Rank", "Character", "Lines Spoken", "Vocative Addressed", "Mentions", "Tone Bonus", "Popularity Score", "Aliases Encountered"]
        output.write(",".join(f'"{h}"' for h in headers) + "\n")

        for c in report.character_rankings:
            aliases_str = "; ".join(c.get("aliases", []))
            row = [
                str(c.get("rank", 0)),
                f'"{c.get("character", "")}"',
                str(c.get("spoken", 0)),
                str(c.get("addressed", 0)),
                str(c.get("mentioned", 0)),
                str(c.get("tone", 0)),
                f'{c.get("score", 0.0):.2f}',
                f'"{aliases_str}"'
            ]
            output.write(",".join(row) + "\n")

        return output.getvalue()

    @staticmethod
    def export_network_csv(network_data: Dict[str, Any]) -> str:
        """
        Renders network centrality metrics as CSV text.
        """
        output = io.StringIO()
        headers = ["Rank", "Character", "In-Degree", "Out-Degree", "Total Degree", "Degree Centrality", "Betweenness Centrality", "PageRank", "Score"]
        output.write(",".join(f'"{h}"' for h in headers) + "\n")

        nodes = network_data.get("nodes", [])
        for i, n in enumerate(nodes, 1):
            row = [
                str(i),
                f'"{n.get("character", "")}"',
                str(n.get("in_degree", 0)),
                str(n.get("out_degree", 0)),
                str(n.get("total_degree", 0)),
                f'{n.get("degree_centrality", 0.0):.4f}',
                f'{n.get("betweenness_centrality", 0.0):.4f}',
                f'{n.get("pagerank", 0.0):.4f}',
                f'{n.get("score", 0.0):.2f}'
            ]
            output.write(",".join(row) + "\n")

        return output.getvalue()

    @staticmethod
    def export_leaderboard_excel(report: DatasetReport, network_data: Optional[Dict[str, Any]] = None) -> Optional[bytes]:
        """
        Exports the leaderboard and network metrics into a multi-tab Excel (.xlsx) workbook.
        Returns bytes, or None if pandas/openpyxl is unavailable.
        """
        try:
            import pandas as pd
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Sheet 1: Character Popularity
                char_records = []
                for c in report.character_rankings:
                    char_records.append({
                        "Rank": c.get("rank"),
                        "Character": c.get("character"),
                        "Lines Spoken (S)": c.get("spoken"),
                        "Vocative Addressed (A)": c.get("addressed"),
                        "Mentions (M)": c.get("mentioned"),
                        "Dramatic Tone (T)": c.get("tone"),
                        "Popularity Score": c.get("score"),
                        "Aliases": ", ".join(c.get("aliases", []))
                    })
                df_chars = pd.DataFrame(char_records)
                df_chars.to_excel(writer, sheet_name="Popularity Leaderboard", index=False)

                # Sheet 2: Network Centrality (if present)
                if network_data and network_data.get("nodes"):
                    df_net = pd.DataFrame(network_data["nodes"])
                    df_net.to_excel(writer, sheet_name="Network Centrality", index=False)

                # Sheet 3: Sentence Types & Tone
                type_records = [{"Category": "Sentence Type", "Class": k, "Count": v} for k, v in report.type_distribution.items()]
                tone_records = [{"Category": "Tone Cue", "Class": k, "Count": v} for k, v in report.tone_distribution.items()]
                df_dist = pd.DataFrame(type_records + tone_records)
                df_dist.to_excel(writer, sheet_name="Distributions", index=False)

                # Sheet 4: Lexical Errors (if any)
                if report.lexical_errors:
                    df_err = pd.DataFrame(report.lexical_errors)
                    df_err.to_excel(writer, sheet_name="Lexical OCR Errors", index=False)

            return output.getvalue()
        except Exception:
            return None

    @staticmethod
    def export_full_json(
        report: DatasetReport,
        analyses: List[SentenceAnalysis],
        network_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Exports full sentence-level token logs, classifications, lexical errors,
        and character popularity rankings as a structured JSON string.
        """
        sentences_payload = []
        for a in analyses:
            sentences_payload.append({
                "line_num": a.line_num,
                "clause_index": a.clause_index,
                "total_clauses": a.total_clauses,
                "speaker": a.speaker,
                "raw_text": a.raw_text,
                "cleaned_text": a.cleaned_text,
                "sentence_type": a.sentence_type.value,
                "classification_reason": a.classification_reason,
                "tone_cues": {
                    "is_shouting": a.tone_cues.is_shouting,
                    "is_hesitant": a.tone_cues.is_hesitant,
                    "is_surprise": a.tone_cues.is_surprise_or_incredulity,
                    "is_pain_or_sound_fx": a.tone_cues.is_pain_or_action,
                    "tags": a.tone_cues.tags
                },
                "addressed": a.addressed,
                "mentions": a.mentions,
                "tokens": [
                    {
                        "type": t.type.value,
                        "value": t.value,
                        "start_pos": t.start_pos,
                        "end_pos": t.end_pos
                    }
                    for t in a.tokens
                ],
                "lexical_errors": [
                    {
                        "symbol": err.symbol,
                        "position": err.position,
                        "description": err.description
                    }
                    for err in a.lexical_errors
                ]
            })

        payload = {
            "metadata": {
                "system": "Comic Dialogue Analyzer & Character Popularity Engine",
                "version": "2.0",
                "export_timestamp": datetime.now().isoformat(),
                "total_sentences_processed": report.total_sentences,
                "total_tokens": report.total_tokens,
                "total_lexical_errors": report.total_lexical_errors,
                "processing_time_ms": report.processing_time_ms
            },
            "summary_distributions": {
                "sentence_types": report.type_distribution,
                "tone_cues": report.tone_distribution,
                "token_classes": report.token_class_distribution,
                "top_tokens": report.top_tokens
            },
            "character_popularity_leaderboard": report.character_rankings,
            "conversational_network": network_data or {},
            "lexical_ocr_errors": report.lexical_errors,
            "sentence_level_analyses": sentences_payload
        }

        return json.dumps(payload, indent=2, ensure_ascii=False)

    @staticmethod
    def generate_latex_tables(
        report: DatasetReport,
        network_data: Optional[Dict[str, Any]] = None,
        top_chars_n: int = 10
    ) -> str:
        """
        Generates production-ready LaTeX table snippets adhering to IEEE/ACM formatting (booktabs).
        """
        lines = []
        lines.append("% ==========================================================================")
        lines.append("% LaTeX Tables Generated by Comic Dialogue Analyzer & Character Popularity Engine")
        lines.append("% Required packages in your LaTeX preamble:")
        lines.append("%   \\usepackage{booktabs}  % For professional horizontal rules")
        lines.append("%   \\usepackage{tabularx}  % For flexible column widths (optional)")
        lines.append("% ==========================================================================\n")

        # Table 1: Character Popularity Leaderboard
        lines.append("% Table I: Character Popularity Leaderboard")
        lines.append("\\begin{table}[htbp]")
        lines.append("  \\centering")
        lines.append("  \\caption{Character Popularity Leaderboard and Multi-Factor Prominence Metrics}")
        lines.append("  \\label{tab:character_popularity}")
        lines.append("  \\begin{tabular}{ccccccc}")
        lines.append("    \\toprule")
        lines.append("    \\textbf{Rank} & \\textbf{Character} & \\textbf{Spoken ($S$)} & \\textbf{Addressed ($A$)} & \\textbf{Mentions ($M$)} & \\textbf{Tone ($T$)} & \\textbf{Score} \\\\")
        lines.append("    \\midrule")

        chars = report.character_rankings[:top_chars_n]
        if chars:
            for c in chars:
                char_escaped = c.get("character", "").replace("_", "\\_").replace("&", "\\&")
                lines.append(
                    f"    {c.get('rank', 0)} & {char_escaped} & {c.get('spoken', 0)} & "
                    f"{c.get('addressed', 0)} & {c.get('mentioned', 0)} & {c.get('tone', 0)} & "
                    f"{c.get('score', 0.0):.1f} \\\\"
                )
        else:
            lines.append("    \\multicolumn{7}{c}{No character interactions recorded} \\\\")

        lines.append("    \\bottomrule")
        lines.append("  \\end{tabular}")
        lines.append("\\end{table}\n")

        # Table 2: Sentence Type and Tone Cues
        lines.append("% Table II: Sentence Classification and Dialogue Tone Spread")
        lines.append("\\begin{table}[htbp]")
        lines.append("  \\centering")
        lines.append("  \\caption{Dialogue Sentence Classification and Emotional Tone Distribution}")
        lines.append("  \\label{tab:sentence_tone_dist}")
        lines.append("  \\begin{tabular}{llrr}")
        lines.append("    \\toprule")
        lines.append("    \\textbf{Category} & \\textbf{Classification / Cue} & \\textbf{Occurrences} & \\textbf{Percentage (\\%)} \\\\")
        lines.append("    \\midrule")

        total_s = max(1, report.total_sentences)
        for st_name, count in report.type_distribution.items():
            pct = (count / total_s) * 100
            lines.append(f"    Sentence Type & {st_name.capitalize()} & {count} & {pct:.1f}\\% \\\\")

        lines.append("    \\midrule")
        for tone_name, count in report.tone_distribution.items():
            friendly_tone = tone_name.replace("_", " ").title()
            pct = (count / total_s) * 100
            lines.append(f"    Tone Cue & {friendly_tone} & {count} & {pct:.1f}\\% \\\\")

        lines.append("    \\bottomrule")
        lines.append("  \\end{tabular}")
        lines.append("\\end{table}\n")

        # Table 3: Conversational Network Centrality (if present)
        if network_data and network_data.get("nodes"):
            lines.append("% Table III: Conversational Interaction Network Centrality")
            lines.append("\\begin{table}[htbp]")
            lines.append("  \\centering")
            lines.append("  \\caption{Directed Conversational Network Centrality Metrics}")
            lines.append("  \\label{tab:network_centrality}")
            lines.append("  \\begin{tabular}{cccccc}")
            lines.append("    \\toprule")
            lines.append("    \\textbf{Character} & \\textbf{In-Degree} & \\textbf{Out-Degree} & \\textbf{Degree Centrality} & \\textbf{Betweenness} & \\textbf{PageRank} \\\\")
            lines.append("    \\midrule")

            net_nodes = network_data["nodes"][:top_chars_n]
            for n in net_nodes:
                char_escaped = n.get("character", "").replace("_", "\\_").replace("&", "\\&")
                lines.append(
                    f"    {char_escaped} & {n.get('in_degree', 0)} & {n.get('out_degree', 0)} & "
                    f"{n.get('degree_centrality', 0.0):.3f} & {n.get('betweenness_centrality', 0.0):.4f} & "
                    f"{n.get('pagerank', 0.0):.4f} \\\\"
                )

            lines.append("    \\bottomrule")
            lines.append("  \\end{tabular}")
            lines.append("\\end{table}\n")

        # Table 4: Token Class Distribution
        lines.append("% Table IV: Comic Lexical Token Class Spread")
        lines.append("\\begin{table}[htbp]")
        lines.append("  \\centering")
        lines.append("  \\caption{Lexical Token Class Distribution across Processed Dialogue}")
        lines.append("  \\label{tab:token_distribution}")
        lines.append("  \\begin{tabular}{lrr}")
        lines.append("    \\toprule")
        lines.append("    \\textbf{Token Class} & \\textbf{Frequency Count} & \\textbf{Relative Spread (\\%)} \\\\")
        lines.append("    \\midrule")

        total_tok = max(1, report.total_tokens)
        sorted_tokens = sorted(report.token_class_distribution.items(), key=lambda x: x[1], reverse=True)
        for t_cls, count in sorted_tokens:
            pct = (count / total_tok) * 100
            lines.append(f"    {t_cls} & {count} & {pct:.1f}\\% \\\\")

        lines.append("    \\bottomrule")
        lines.append("  \\end{tabular}")
        lines.append("\\end{table}")

        return "\n".join(lines)

    @staticmethod
    def save_all_exports(
        output_dir: str,
        report: DatasetReport,
        analyses: List[SentenceAnalysis],
        network_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        Saves all export artifacts to the designated directory and returns written file paths.
        """
        os.makedirs(output_dir, exist_ok=True)
        saved_files: Dict[str, str] = {}

        # 1. CSV Leaderboard
        csv_path = os.path.join(output_dir, "character_popularity_leaderboard.csv")
        with open(csv_path, "w", encoding="utf-8") as f:
            f.write(ExportEngine.export_leaderboard_csv(report))
        saved_files["csv_leaderboard"] = csv_path

        # 2. Network CSV (if network data)
        if network_data and network_data.get("nodes"):
            net_csv_path = os.path.join(output_dir, "network_centrality_metrics.csv")
            with open(net_csv_path, "w", encoding="utf-8") as f:
                f.write(ExportEngine.export_network_csv(network_data))
            saved_files["csv_network"] = net_csv_path

        # 3. Excel Workbook
        excel_bytes = ExportEngine.export_leaderboard_excel(report, network_data=network_data)
        if excel_bytes:
            excel_path = os.path.join(output_dir, "comic_dialogue_analytics.xlsx")
            with open(excel_path, "wb") as f:
                f.write(excel_bytes)
            saved_files["excel_workbook"] = excel_path

        # 4. Full JSON
        json_path = os.path.join(output_dir, "comic_dialogue_full_report.json")
        with open(json_path, "w", encoding="utf-8") as f:
            f.write(ExportEngine.export_full_json(report, analyses, network_data=network_data))
        saved_files["json_full"] = json_path

        # 5. LaTeX Tables (.tex)
        latex_path = os.path.join(output_dir, "academic_paper_tables.tex")
        with open(latex_path, "w", encoding="utf-8") as f:
            f.write(ExportEngine.generate_latex_tables(report, network_data=network_data))
        saved_files["latex_tables"] = latex_path

        return saved_files
