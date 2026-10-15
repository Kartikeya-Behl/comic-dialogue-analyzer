"""
Streamlit Interactive Dashboard for Comic Dialogue Analyzer & Character Popularity Engine.
"""

import sys
import os
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Add workspace to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.pipeline import ComicDialoguePipeline, SentenceAnalysis
from src.reporter import DialogueReporter, DatasetReport
from src.config import TokenType, SentenceType


# Page configuration
st.set_page_config(
    page_title="Comic Dialogue & Popularity Analyzer",
    page_icon="💥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border-radius: 8px;
        padding: 16px;
        border: 1px solid #E2E8F0;
        text-align: center;
    }
    .token-chip {
        display: inline-block;
        padding: 3px 8px;
        margin: 3px;
        border-radius: 4px;
        font-size: 0.85rem;
        font-family: monospace;
        font-weight: 600;
    }
    .token-WORD { background-color: #E0F2FE; color: #0369A1; }
    .token-TERMINATOR { background-color: #FEE2E2; color: #B91C1C; }
    .token-PUNCT { background-color: #F1F5F9; color: #475569; }
    .token-CONTRACTION { background-color: #FEF3C7; color: #B45309; }
    .token-SOUND_FX { background-color: #FFEDD5; color: #C2410C; }
    .token-ELLIPSIS { background-color: #EDE9FE; color: #6D28D9; }
    .token-INTERROBANG { background-color: #FCE7F3; color: #BE185D; }
    .token-NUMBER { background-color: #DCFCE7; color: #15803D; }
    .token-UNKNOWN { background-color: #EF4444; color: #FFFFFF; }
</style>
""", unsafe_allow_html=True)


def get_token_html(tokens):
    chips = []
    for t in tokens:
        cls_name = f"token-{t.type.value}"
        chips.append(f'<span class="token-chip {cls_name}" title="{t.type.value} [span {t.start_pos}:{t.end_pos}]">{t.value}</span>')
    return " ".join(chips)


def create_network_graph(ranked_chars):
    """Creates a directed interaction network graph of who addressed whom."""
    nodes = [c["character"] for c in ranked_chars[:12]]
    node_set = set(nodes)
    
    edges = []
    # Gather edge pairs from registry
    for c in ranked_chars[:12]:
        spk = c["character"]
        # In a real run, addressed_others stores counts
        # We can map top interactions
    
    # Simple interactive chord or network using Plotly
    # If no complex graph, return None
    return None


def run_dashboard():
    st.markdown('<div class="main-title">💥 Comic Dialogue Analyzer & Character Popularity Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Compiler front-end analysis without syntactic parser: lexical categorization, OCR error tracking, tone modeling, and multi-factor character prominence.</div>', unsafe_allow_html=True)

    # Sidebar configuration
    st.sidebar.header("⚙️ Configuration & Controls")

    # Data Source Selection
    source_mode = st.sidebar.radio(
        "Select Dialogue Source:",
        ["Benchmark Datasets", "Live Single-Sentence Playground", "Upload Custom Script"],
        index=0
    )

    # Popularity Weight Controls
    with st.sidebar.expander("⚖️ Character Popularity Weights", expanded=False):
        w_spoken = st.slider("Weight: Lines Spoken (ws)", 0.0, 3.0, 1.0, 0.1)
        w_addressed = st.slider("Weight: Vocative Addressed (wa)", 0.0, 3.0, 1.5, 0.1)
        w_mentioned = st.slider("Weight: Dialogue Mentions (wm)", 0.0, 3.0, 0.8, 0.1)
        w_tone = st.slider("Weight: Tone Bonus (wt)", 0.0, 1.0, 0.2, 0.05)

    custom_weights = {
        "spoken": w_spoken,
        "addressed": w_addressed,
        "mentioned": w_mentioned,
        "tone_bonus": w_tone
    }

    # Pipeline Initialization
    pipeline = ComicDialoguePipeline()
    pipeline.popularity_engine.weights = custom_weights
    reporter = DialogueReporter(pipeline)

    # -------------------------------------------------------------
    # MODE 1: Single Sentence Live Playground
    # -------------------------------------------------------------
    if source_mode == "Live Single-Sentence Playground":
        st.subheader("🔍 Single Dialogue Sentence Inspector")
        st.write("Test individual comic dialogue lines against the lexer, symbol table, vocative rules, and classifier.")

        presets = [
            "CLINT: WHERE COULD HE BE, NATASHA?",
            "BATMAN: HAVE A PEANUT.",
            "GREEN ARROW: I JUST STOPPED THE ENTIRE WORLD FROM BEING EATEN, DINAH.",
            "THE JOKER: HAHAHA! DID YOU REALLY THINK YOU COULD CATCH ME, BRUCE?!",
            "GORDON: BATMAN~ WE HAVE A 10-99 AT SECTOR 4#.",
            "SPIDER-MAN: WHOA?! THWIP! I DIDN'T EXPECT YOU HERE, JOKER!",
            "BLACK WIDOW: I HEAR YOU, STARK... BUT SOMETHING IS WRONG."
        ]
        
        selected_preset = st.selectbox("Choose a Benchmark Sample from Paper:", presets)
        input_sentence = st.text_input("Or Enter Custom Dialogue Line (Speaker: Text):", value=selected_preset)

        if st.button("🚀 Analyze Sentence", type="primary"):
            t_start = time.perf_counter()
            analysis: SentenceAnalysis = pipeline.analyze_sentence(input_sentence)
            elapsed = (time.perf_counter() - t_start) * 1000

            st.success(f"Analysis completed in {elapsed:.2f} ms")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Identified Speaker", analysis.speaker or "None (Anonymous)")
            with col2:
                st.metric("Sentence Classification", analysis.sentence_type.value.upper())
            with col3:
                st.metric("Person Addressed (Vocative)", analysis.addressed or "None")
            with col4:
                st.metric("Lexical Errors", len(analysis.lexical_errors))

            st.markdown("#### 🧩 Tokenized Stream")
            st.markdown(get_token_html(analysis.tokens), unsafe_allow_html=True)
            st.caption("Hover over tokens to see exact character span and token class.")

            st.markdown("#### 📋 Detailed Analysis")
            col_a, col_b = st.columns(2)
            with col_a:
                st.write("**Sentence Classification Reason:**", analysis.classification_reason)
                tone_tags = ", ".join(analysis.tone_cues.tags) if analysis.tone_cues.tags else "Neutral"
                st.write("**Tone Markers Detected:**", tone_tags)
                if analysis.mentions:
                    st.write("**Third-Party Mentions Found:**", ", ".join(analysis.mentions))

            with col_b:
                if analysis.lexical_errors:
                    st.error(f"Found {len(analysis.lexical_errors)} Lexical OCR Errors:")
                    for err in analysis.lexical_errors:
                        st.write(f"- Character `{err.symbol}` at offset {err.position}: {err.description}")
                else:
                    st.info("No lexical errors detected. All characters mapped cleanly.")

            st.markdown("#### 🗄️ Symbol Table Snapshot")
            symbols_data = [
                {"Token": e.name, "Class": e.token_type.value, "Count": e.count, "Proper Name": e.is_proper_name}
                for e in pipeline.symbol_table.table.values()
            ]
            st.dataframe(pd.DataFrame(symbols_data), use_container_width=True)

        return

    # -------------------------------------------------------------
    # MODE 2: Dataset Batch Analysis
    # -------------------------------------------------------------
    dataset_file = ""
    if source_mode == "Benchmark Datasets":
        ds_choice = st.sidebar.selectbox(
            "Select Benchmark Dataset:",
            [
                "Cornell Superhero Dialogue (6,335 lines: Batman, Superman, Spider-Man, Avengers)",
                "Cornell Sample (1,000 lines)",
                "Sample Comic Dialogue (18 lines from Paper Table 2)"
            ]
        )
        if "Superhero" in ds_choice:
            dataset_file = "data/cornell_superhero_dialogue.txt"
        elif "1,000" in ds_choice:
            dataset_file = "data/cornell_sample_1000.txt"
        else:
            dataset_file = "data/sample_comic_dialogue.txt"
    else:
        uploaded_file = st.sidebar.file_uploader("Upload Dialogue Text File", type=["txt", "csv"])
        if uploaded_file is not None:
            dataset_file = os.path.join("data", "uploaded_temp.txt")
            with open(dataset_file, "wb") as f:
                f.write(uploaded_file.getbuffer())

    if not dataset_file or not os.path.exists(dataset_file):
        st.warning("Please select or upload a dataset file.")
        return

    with open(dataset_file, "r", encoding="utf-8", errors="ignore") as f:
        raw_lines = f.readlines()

    limit_lines = st.sidebar.slider("Max lines to process:", 100, min(10000, len(raw_lines)), min(6500, len(raw_lines)), 500)
    lines_to_process = raw_lines[:limit_lines]

    # Run Analysis
    with st.spinner(f"Processing {len(lines_to_process):,} lines through compiler pipeline..."):
        t0 = time.perf_counter()
        analyses = pipeline.analyze_batch(lines_to_process)
        t_elapsed = time.perf_counter() - t0
        report: DatasetReport = reporter.generate_report(analyses, elapsed_sec=t_elapsed)

    # Top KPI Metrics Cards
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    with kpi1:
        st.metric("Sentences Processed", f"{report.total_sentences:,}")
    with kpi2:
        st.metric("Total Tokens", f"{report.total_tokens:,}")
    with kpi3:
        st.metric("Lexical Errors (OCR)", f"{report.total_lexical_errors:,}")
    with kpi4:
        st.metric("Throughput Latency", f"{report.processing_time_ms:.1f} ms")
    with kpi5:
        top_char = report.character_rankings[0]["character"] if report.character_rankings else "N/A"
        top_score = report.character_rankings[0]["score"] if report.character_rankings else 0
        st.metric("👑 Top Character", f"{top_char}", f"{top_score} pts")

    st.markdown("---")

    # Tabs for structured viewing
    tab_pop, tab_compiler, tab_errors, tab_sentences = st.tabs([
        "⭐ Character Popularity (Priority)",
        "📊 Compiler Front-End Analytics",
        "⚠️ Lexical OCR Errors",
        "📜 Sentence Inspector"
    ])

    # -------------------------------------------------------------
    # TAB 1: Character Popularity
    # -------------------------------------------------------------
    with tab_pop:
        st.subheader("👑 Character Popularity Leaderboard & Prominence Breakdown")
        st.markdown(
            "Popularity is quantified through a weighted composite model of direct speech agency ($S$), "
            "interpersonal vocative address ($A$), narrative mentions ($M$), and high-emotion tone spikes ($T$)."
        )

        char_df = pd.DataFrame(report.character_rankings)

        if not char_df.empty:
            top_n = st.slider("Display Top Characters:", 5, min(30, len(char_df)), 12)
            sub_df = char_df.head(top_n).copy()

            # Stacked Bar Chart for Score Components
            fig_score = go.Figure()
            fig_score.add_trace(go.Bar(
                x=sub_df["character"],
                y=sub_df["spoken"] * custom_weights["spoken"],
                name="Lines Spoken (Agency)",
                marker_color="#3B82F6"
            ))
            fig_score.add_trace(go.Bar(
                x=sub_df["character"],
                y=sub_df["addressed"] * custom_weights["addressed"],
                name="Vocative Addressed (Focus)",
                marker_color="#8B5CF6"
            ))
            fig_score.add_trace(go.Bar(
                x=sub_df["character"],
                y=sub_df["mentioned"] * custom_weights["mentioned"],
                name="Mentions (Presence)",
                marker_color="#10B981"
            ))
            fig_score.add_trace(go.Bar(
                x=sub_df["character"],
                y=sub_df["tone"] * custom_weights["tone_bonus"],
                name="Tone Bonus (Emotion)",
                marker_color="#F59E0B"
            ))

            fig_score.update_layout(
                barmode='stack',
                title=f"Top {top_n} Character Popularity Scores (Component Breakdown)",
                xaxis_title="Character",
                yaxis_title="Weighted Score",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                height=450
            )
            st.plotly_chart(fig_score, use_container_width=True)

            # Interactive Leaderboard Table
            st.markdown("#### 🏆 Full Popularity Leaderboard")
            st.dataframe(
                char_df[["rank", "character", "spoken", "addressed", "mentioned", "tone", "score", "aliases"]],
                use_container_width=True,
                height=400
            )
        else:
            st.info("No characters detected in the current selection.")

    # -------------------------------------------------------------
    # TAB 2: Compiler Front-End Analytics
    # -------------------------------------------------------------
    with tab_compiler:
        st.subheader("📊 Compiler Front-End Analytics (Without Parser)")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("##### 📌 Sentence Classification Spread")
            type_df = pd.DataFrame(list(report.type_distribution.items()), columns=["Type", "Count"])
            fig_type = px.pie(
                type_df,
                values="Count",
                names="Type",
                hole=0.45,
                color="Type",
                color_discrete_map={
                    "statement": "#3B82F6",
                    "question": "#8B5CF6",
                    "exclamation": "#EF4444",
                    "command": "#F59E0B"
                }
            )
            fig_type.update_layout(height=350)
            st.plotly_chart(fig_type, use_container_width=True)

        with col2:
            st.markdown("##### 🎭 Tone Cues Distribution")
            tone_df = pd.DataFrame(list(report.tone_distribution.items()), columns=["Tone", "Count"])
            tone_df["Tone"] = tone_df["Tone"].str.replace("_", " ").str.capitalize()
            fig_tone = px.bar(
                tone_df,
                x="Tone",
                y="Count",
                color="Tone",
                color_discrete_sequence=["#EF4444", "#8B5CF6", "#EC4899", "#F59E0B"]
            )
            fig_tone.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig_tone, use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            st.markdown("##### 🏷️ Token Class Distribution")
            t_class_df = pd.DataFrame(list(report.token_class_distribution.items()), columns=["Token Class", "Occurrences"])
            t_class_df = t_class_df.sort_values(by="Occurrences", ascending=False)
            fig_tclass = px.bar(
                t_class_df,
                x="Token Class",
                y="Occurrences",
                color="Token Class",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_tclass.update_layout(height=380, showlegend=False)
            st.plotly_chart(fig_tclass, use_container_width=True)

        with col4:
            st.markdown("##### 🗂️ Top 10 Most Frequent Tokens")
            top_tok_df = pd.DataFrame(report.top_tokens)
            fig_tok = px.bar(
                top_tok_df,
                x="token",
                y="count",
                color="type",
                title="Top Tokens in Dataset"
            )
            fig_tok.update_layout(height=380)
            st.plotly_chart(fig_tok, use_container_width=True)

    # -------------------------------------------------------------
    # TAB 3: Lexical OCR Errors
    # -------------------------------------------------------------
    with tab_errors:
        st.subheader("⚠️ Lexical OCR Errors & Stray Junk Symbols")
        st.markdown(
            "Any character failing all lexical rules (such as OCR artifacts `~`, `#`, stray symbols) "
            "is intercepted as a lexical error with exact line and character coordinate positions."
        )

        if report.lexical_errors:
            err_df = pd.DataFrame(report.lexical_errors)
            st.dataframe(err_df[["line", "symbol", "position", "description", "sentence_snippet"]], use_container_width=True)
        else:
            st.success("🎉 No lexical errors found in this dataset sample!")

    # -------------------------------------------------------------
    # TAB 4: Sentence Inspector
    # -------------------------------------------------------------
    with tab_sentences:
        st.subheader("📜 Sentence-by-Sentence Results")
        sample_size = min(50, len(analyses))
        st.caption(f"Showing first {sample_size} sentences:")

        sentence_rows = []
        for a in analyses[:sample_size]:
            sentence_rows.append({
                "Line": a.line_num,
                "Speaker": a.speaker or "ANONYMOUS",
                "Dialogue": a.raw_text,
                "Type": a.sentence_type.value.upper(),
                "Addressed": a.addressed or "-",
                "Mentions": ", ".join(a.mentions) if a.mentions else "-",
                "Tone": ", ".join(a.tone_cues.tags) if a.tone_cues.tags else "Neutral",
                "Tokens (Short)": a.short_tokens_str()
            })

        st.dataframe(pd.DataFrame(sentence_rows), use_container_width=True, height=450)


if __name__ == "__main__":
    run_dashboard()
