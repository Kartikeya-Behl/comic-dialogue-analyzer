"""
Streamlit Interactive Dashboard for Comic Dialogue Analyzer & Character Popularity Engine.
Redesigned with a premium, human-crafted modern digital product aesthetic:
- Flawless Dark/Light Theme Contrast (100% sidebar and headline visibility)
- Clean, aligned System Telemetry block with no text wrapping collisions
- Proportional bento containers (38/62 split, 70/30 split)
- Crisp 1px structural micro-borders and zero blurry drop-shadows
- Monospaced metadata badges and rapid micro-interactions
- Directed conversational social interaction networks (NetworkX + Plotly)
- Multi-sentence speech bubble splitting
- Dynamic external universe & alias configurations
- Comprehensive academic export suite (CSV, Excel .xlsx, JSON, LaTeX tables)
"""

import sys
import os
import time
import io
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Add workspace to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.pipeline import ComicDialoguePipeline, SentenceAnalysis
from src.reporter import DialogueReporter, DatasetReport
from src.config import TokenType, SentenceType, DEFAULT_WEIGHTS
from src.alias_loader import load_aliases_from_json, get_available_alias_presets
from src.network_analyzer import ConversationalNetworkAnalyzer
from src.export_engine import ExportEngine


# Page configuration
st.set_page_config(
    page_title="Comic Dialogue & Popularity Analyzer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------
# DYNAMIC HIGH-END DUAL-THEME STYLING SYSTEM (DARK & LIGHT)
# -------------------------------------------------------------
def get_custom_css(is_dark: bool) -> str:
    if is_dark:
        vars_css = """
        --bg-main: #080D1A;
        --bg-sidebar: #0A0F1E;
        --bg-card: #0E1525;
        --bg-card-hero: #0B1120;
        --bg-card-hover: #111A2D;
        --bg-panel: #0E1525;
        --bg-subtle: rgba(14, 21, 37, 0.85);
        --bg-code: rgba(8, 13, 26, 0.9);
        
        --border-subtle: rgba(255, 255, 255, 0.08);
        --border-hover: rgba(56, 189, 248, 0.35);
        --border-accent: #38BDF8;
        
        --text-primary: #F1F5F9;
        --text-secondary: #CBD5E1;
        --text-muted: #64748B;
        --text-accent: #38BDF8;
        --text-accent-purple: #A78BFA;
        
        --stat-divider: rgba(255, 255, 255, 0.1);
        --glow-color: rgba(56, 189, 248, 0.08);
        --gradient-title: linear-gradient(135deg, #38BDF8 0%, #818CF8 55%, #F472B6 100%);
        
        --tab-inactive: #64748B;
        --tab-hover: #CBD5E1;
        --tab-active: #38BDF8;
        --tab-active-border: #38BDF8;

        --sidebar-text: #CBD5E1;
        --sidebar-text-active: #F8FAFC;
        --sidebar-header: #38BDF8;
        --sidebar-caption: #64748B;
        --sidebar-border: rgba(255, 255, 255, 0.07);

        --pill-blue-bg: rgba(37, 99, 235, 0.2);
        --pill-blue-color: #93C5FD;
        --pill-blue-border: rgba(59, 130, 246, 0.35);

        --pill-purple-bg: rgba(124, 58, 237, 0.2);
        --pill-purple-color: #C4B5FD;
        --pill-purple-border: rgba(139, 92, 246, 0.35);

        --pill-green-bg: rgba(16, 185, 129, 0.2);
        --pill-green-color: #6EE7B7;
        --pill-green-border: rgba(16, 185, 129, 0.35);

        --pill-amber-bg: rgba(245, 158, 11, 0.2);
        --pill-amber-color: #FCD34D;
        --pill-amber-border: rgba(245, 158, 11, 0.35);

        --token-word-bg: rgba(2, 132, 199, 0.15);
        --token-word-color: #7DD3FC;
        --token-word-border: rgba(56, 189, 248, 0.3);

        --token-term-bg: rgba(220, 38, 38, 0.15);
        --token-term-color: #FCA5A5;
        --token-term-border: rgba(239, 68, 68, 0.3);

        --token-punct-bg: rgba(100, 116, 139, 0.15);
        --token-punct-color: #CBD5E1;
        --token-punct-border: rgba(148, 163, 184, 0.25);

        --token-contr-bg: rgba(217, 119, 6, 0.15);
        --token-contr-color: #FCD34D;
        --token-contr-border: rgba(245, 158, 11, 0.3);

        --token-sound-bg: rgba(234, 88, 12, 0.15);
        --token-sound-color: #FDBA74;
        --token-sound-border: rgba(249, 115, 22, 0.3);

        --token-elli-bg: rgba(124, 58, 237, 0.15);
        --token-elli-color: #C4B5FD;
        --token-elli-border: rgba(139, 92, 246, 0.3);

        --token-interr-bg: rgba(219, 39, 119, 0.15);
        --token-interr-color: #F9A8D4;
        --token-interr-border: rgba(236, 72, 153, 0.3);

        --token-num-bg: rgba(22, 163, 74, 0.15);
        --token-num-color: #86EFAC;
        --token-num-border: rgba(34, 197, 94, 0.3);

        --token-unk-bg: rgba(239, 68, 68, 0.25);
        --token-unk-color: #FEE2E2;
        --token-unk-border: #EF4444;

        --input-bg: #0F172A;
        --input-color: #F1F5F9;
        --input-border: rgba(255, 255, 255, 0.1);
        """
    else:
        vars_css = """
        --bg-main: #F8FAFC;
        --bg-sidebar: #FFFFFF;
        --bg-card: #FFFFFF;
        --bg-card-hero: #FFFFFF;
        --bg-card-hover: #F8FAFC;
        --bg-panel: #FFFFFF;
        --bg-subtle: #F1F5F9;
        --bg-code: #F1F5F9;
        
        --border-subtle: #E2E8F0;
        --border-hover: rgba(2, 132, 199, 0.45);
        --border-accent: #0284C7;
        
        --text-primary: #0F172A;
        --text-secondary: #334155;
        --text-muted: #64748B;
        --text-accent: #0284C7;
        --text-accent-purple: #7C3AED;
        
        --stat-divider: #CBD5E1;
        --glow-color: rgba(2, 132, 199, 0.06);
        --gradient-title: linear-gradient(135deg, #0284C7 0%, #6366F1 55%, #DB2777 100%);
        
        --tab-inactive: #64748B;
        --tab-hover: #0F172A;
        --tab-active: #0284C7;
        --tab-active-border: #0284C7;

        --sidebar-text: #334155;
        --sidebar-text-active: #0F172A;
        --sidebar-header: #0284C7;
        --sidebar-caption: #64748B;
        --sidebar-border: #E2E8F0;

        --pill-blue-bg: #EFF6FF;
        --pill-blue-color: #1D4ED8;
        --pill-blue-border: #BFDBFE;

        --pill-purple-bg: #F5F3FF;
        --pill-purple-color: #6D28D9;
        --pill-purple-border: #DDD6FE;

        --pill-green-bg: #ECFDF5;
        --pill-green-color: #047857;
        --pill-green-border: #A7F3D0;

        --pill-amber-bg: #FFFBEB;
        --pill-amber-color: #B45309;
        --pill-amber-border: #FDE68A;

        --token-word-bg: #E0F2FE;
        --token-word-color: #0284C7;
        --token-word-border: #BAE6FD;

        --token-term-bg: #FEE2E2;
        --token-term-color: #DC2626;
        --token-term-border: #FECACA;

        --token-punct-bg: #F1F5F9;
        --token-punct-color: #475569;
        --token-punct-border: #CBD5E1;

        --token-contr-bg: #FEF3C7;
        --token-contr-color: #D97706;
        --token-contr-border: #FDE68A;

        --token-sound-bg: #FFEDD5;
        --token-sound-color: #EA580C;
        --token-sound-border: #FED7AA;

        --token-elli-bg: #EDE9FE;
        --token-elli-color: #7C3AED;
        --token-elli-border: #DDD6FE;

        --token-interr-bg: #FCE7F3;
        --token-interr-color: #DB2777;
        --token-interr-border: #FBCFE8;

        --token-num-bg: #DCFCE7;
        --token-num-color: #16A34A;
        --token-num-border: #BBF7D0;

        --token-unk-bg: #FEE2E2;
        --token-unk-color: #B91C1C;
        --token-unk-border: #EF4444;

        --input-bg: #FFFFFF;
        --input-color: #0F172A;
        --input-border: #CBD5E1;
        """

    return f"""
    <style>
        :root {{
            {vars_css}
        }}

        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

        html, body, [class*="css"], [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
            background-color: var(--bg-main) !important;
            color: var(--text-primary) !important;
        }}

        [data-testid="stAppViewContainer"] > .main {{
            background: var(--bg-main) !important;
            color: var(--text-primary) !important;
        }}

        .main .block-container {{
            padding-top: 1.8rem !important;
            padding-bottom: 3rem !important;
            max-width: 1200px !important;
        }}

        /* Headings & Text */
        h1, h2, h3, h4, h5, h6 {{
            color: var(--text-primary) !important;
        }}
        p, span, label {{
            color: inherit;
        }}

        /* Sidebar Styling */
        [data-testid="stSidebar"] {{
            min-width: 300px !important;
            max-width: 320px !important;
            background: var(--bg-sidebar) !important;
            border-right: 1px solid var(--sidebar-border) !important;
        }}
        section[data-testid="stSidebar"] > div {{
            width: 100% !important;
            padding-top: 1.2rem !important;
            padding-bottom: 2rem !important;
        }}
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] div,
        [data-testid="stSidebar"] .stRadio label,
        [data-testid="stSidebar"] .stSelectbox label,
        [data-testid="stSidebar"] .stSlider label,
        [data-testid="stSidebar"] .stCheckbox label {{
            color: var(--sidebar-text) !important;
            font-size: 0.88rem !important;
            font-weight: 500 !important;
        }}
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {{
            font-size: 0.72rem !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.12em !important;
            color: var(--sidebar-header) !important;
            margin-top: 1.2rem !important;
            margin-bottom: 0.4rem !important;
        }}
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label span {{
            color: var(--sidebar-text-active) !important;
            font-size: 0.88rem !important;
        }}
        [data-testid="stSidebar"] .stCaption,
        [data-testid="stSidebar"] small {{
            color: var(--sidebar-caption) !important;
        }}

        /* Modern Segmented appearance for Theme Toggle */
        [data-testid="stSidebar"] div[role="radiogroup"] {{
            background: var(--bg-card);
            padding: 4px;
            border-radius: 8px;
            border: 1px solid var(--border-subtle);
        }}

        /* Input Controls */
        .stTextInput input, .stTextArea textarea {{
            background-color: var(--input-bg) !important;
            color: var(--input-color) !important;
            border: 1px solid var(--input-border) !important;
            border-radius: 8px !important;
        }}
        .stSelectbox div[data-baseweb="select"] {{
            background-color: var(--input-bg) !important;
            border: 1px solid var(--input-border) !important;
            border-radius: 8px !important;
        }}
        .stSelectbox div[data-baseweb="select"] span {{
            color: var(--input-color) !important;
        }}

        /* Dataframe Container */
        [data-testid="stDataFrame"] {{
            border: 1px solid var(--border-subtle) !important;
            border-radius: 10px !important;
            background-color: var(--bg-card) !important;
        }}

        /* Expander */
        [data-testid="stExpander"] {{
            background: var(--bg-card) !important;
            border: 1px solid var(--border-subtle) !important;
            border-radius: 10px !important;
        }}
        [data-testid="stExpander"] details summary p, 
        [data-testid="stExpander"] details summary span {{
            color: var(--text-primary) !important;
            font-weight: 600 !important;
        }}

        /* Hero Section */
        .hero-wrap {{
            position: relative;
            padding: 2.4rem 0 2rem 0;
            margin-bottom: 0.5rem;
            overflow: hidden;
        }}
        .hero-wrap::before {{
            content: "";
            position: absolute;
            top: -60px; left: -80px;
            width: 500px; height: 400px;
            background: radial-gradient(ellipse at center, var(--glow-color) 0%, transparent 70%);
            pointer-events: none;
        }}
        .hero-eyebrow {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            color: var(--text-accent);
            margin-bottom: 0.9rem;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .hero-eyebrow::before {{
            content: "";
            display: inline-block;
            width: 20px; height: 1.5px;
            background: var(--text-accent);
        }}
        .hero-title {{
            font-size: 3.8rem !important;
            font-weight: 900 !important;
            letter-spacing: -0.05em !important;
            line-height: 1.05 !important;
            color: var(--text-primary) !important;
            margin: 0 0 0.5rem 0 !important;
        }}
        .hero-title span {{
            background: var(--gradient-title);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .hero-subtitle {{
            font-size: 1.02rem !important;
            font-weight: 400 !important;
            color: var(--text-muted) !important;
            line-height: 1.65 !important;
            max-width: 560px;
            margin: 0 0 2rem 0 !important;
        }}
        .hero-stats-row {{
            display: flex;
            gap: 1.6rem;
            flex-wrap: wrap;
            align-items: center;
        }}
        .hero-stat {{
            display: flex;
            flex-direction: column;
            gap: 2px;
        }}
        .hero-stat-num {{
            font-size: 1.5rem;
            font-weight: 800;
            letter-spacing: -0.03em;
            color: var(--text-primary);
            line-height: 1;
        }}
        .hero-stat-label {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.65rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: var(--text-muted);
        }}
        .hero-stat-divider {{
            width: 1px;
            height: 32px;
            background: var(--stat-divider);
            align-self: center;
        }}

        /* Bento Cards */
        .bento-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: 14px;
            padding: 1.4rem 1.5rem;
            position: relative;
            overflow: hidden;
            transition: border-color 0.15s ease, background 0.15s ease, box-shadow 0.15s ease;
        }}
        .bento-card:hover {{
            border-color: var(--border-hover);
            background: var(--bg-card-hover);
        }}
        .bento-card-hero {{
            background: var(--bg-card-hero);
            border-left: 3px solid var(--border-accent);
        }}
        .bento-label {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.64rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            color: var(--text-muted);
            margin-bottom: 0.6rem;
        }}
        .bento-value-hero {{
            font-size: 2.2rem;
            font-weight: 800;
            letter-spacing: -0.04em;
            color: var(--text-primary);
            line-height: 1.1;
            margin-bottom: 0.3rem;
        }}
        .bento-score-hero {{
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--text-accent);
            margin: 0.3rem 0 0.7rem;
        }}
        .bento-unit {{
            font-size: 0.8rem;
            font-weight: 400;
            color: var(--text-muted);
        }}
        .bento-value-sm {{
            font-size: 1.7rem;
            font-weight: 700;
            letter-spacing: -0.03em;
            color: var(--text-primary);
            line-height: 1.1;
            margin-bottom: 0.25rem;
        }}
        .bento-sub {{
            font-size: 0.8rem;
            color: var(--text-muted);
            line-height: 1.4;
            margin-top: 0.4rem;
        }}

        /* Pills */
        .bento-pill {{
            display: inline-block;
            padding: 3px 9px;
            border-radius: 5px;
            font-size: 0.74rem;
            font-family: 'JetBrains Mono', monospace;
            font-weight: 600;
            margin: 2px 2px 0 0;
        }}
        .pill-blue   {{ background: var(--pill-blue-bg);   color: var(--pill-blue-color);   border: 1px solid var(--pill-blue-border); }}
        .pill-purple {{ background: var(--pill-purple-bg); color: var(--pill-purple-color); border: 1px solid var(--pill-purple-border); }}
        .pill-green  {{ background: var(--pill-green-bg);  color: var(--pill-green-color);  border: 1px solid var(--pill-green-border); }}
        .pill-amber  {{ background: var(--pill-amber-bg);  color: var(--pill-amber-color);  border: 1px solid var(--pill-amber-border); }}

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 6px !important;
            border-bottom: 1px solid var(--border-subtle) !important;
            padding-bottom: 0 !important;
            margin-bottom: 1.8rem !important;
            background: transparent !important;
        }}
        .stTabs [data-baseweb="tab"] {{
            padding: 10px 18px !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 600 !important;
            font-size: 0.88rem !important;
            border-radius: 8px 8px 0 0 !important;
            background: transparent !important;
            border: none !important;
            border-bottom: 2px solid transparent !important;
            color: var(--tab-inactive) !important;
            transition: all 0.12s ease !important;
        }}
        .stTabs [data-baseweb="tab"]:hover {{
            color: var(--tab-hover) !important;
            background: var(--bg-subtle) !important;
        }}
        .stTabs [aria-selected="true"] {{
            color: var(--tab-active) !important;
            border-bottom: 2px solid var(--tab-active-border) !important;
        }}

        /* Panels & Code/Math Boxes */
        .panel-card {{
            background: var(--bg-panel);
            border: 1px solid var(--border-subtle);
            border-radius: 14px;
            padding: 1.5rem 1.75rem;
            margin-bottom: 1rem;
            transition: border-color 0.15s ease;
        }}
        .panel-card:hover {{
            border-color: var(--border-hover);
        }}
        .panel-label {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.64rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            color: var(--text-muted);
            margin-bottom: 0.7rem;
        }}
        .panel-desc {{
            font-size: 0.82rem;
            color: var(--text-muted);
            line-height: 1.6;
            margin: 0;
        }}
        .panel-desc b {{
            color: var(--text-primary);
        }}
        .math-box {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.82rem;
            color: var(--text-accent);
            margin-bottom: 0.8rem;
            padding: 10px;
            background: var(--bg-code);
            border: 1px solid var(--border-subtle);
            border-radius: 8px;
            line-height: 1.7;
        }}

        /* Clause card */
        .clause-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: 12px;
            padding: 1.1rem 1.3rem;
            margin-bottom: 0.75rem;
            transition: border-color 0.15s ease;
        }}
        .clause-card:hover {{
            border-color: var(--border-hover);
        }}

        /* Export tiles */
        .export-tile {{
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: 12px;
            padding: 1.2rem 1.3rem;
            margin-bottom: 10px;
            transition: border-color 0.15s ease, background 0.15s ease;
        }}
        .export-tile:hover {{
            border-color: var(--border-hover);
            background: var(--bg-card-hover);
        }}
        .export-title {{
            font-weight: 700;
            font-size: 0.92rem;
            color: var(--text-primary);
            margin-bottom: 0.25rem;
        }}
        .export-desc {{
            font-size: 0.8rem;
            color: var(--text-muted);
            line-height: 1.45;
            margin-bottom: 0.7rem;
        }}

        /* Dyad row */
        .dyad-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 12px;
            background: var(--bg-subtle);
            border: 1px solid var(--border-subtle);
            border-radius: 8px;
            margin-bottom: 6px;
            font-size: 0.85rem;
            color: var(--text-primary);
            transition: border-color 0.12s ease;
        }}
        .dyad-row:hover {{
            border-color: var(--border-hover);
        }}
        .dyad-names {{
            color: var(--text-primary);
        }}

        /* Token chips */
        .token-chip {{
            display: inline-block;
            padding: 4px 10px;
            margin: 3px;
            border-radius: 5px;
            font-size: 0.88rem;
            font-family: 'JetBrains Mono', monospace;
            font-weight: 600;
            letter-spacing: -0.01em;
            transition: transform 0.1s ease, opacity 0.1s ease;
        }}
        .token-chip:hover {{ transform: scale(1.06); opacity: 0.9; }}
        .token-WORD        {{ background: var(--token-word-bg);   color: var(--token-word-color);   border: 1px solid var(--token-word-border); }}
        .token-TERMINATOR  {{ background: var(--token-term-bg);   color: var(--token-term-color);   border: 1px solid var(--token-term-border); }}
        .token-PUNCT       {{ background: var(--token-punct-bg);  color: var(--token-punct-color);  border: 1px solid var(--token-punct-border); }}
        .token-CONTRACTION {{ background: var(--token-contr-bg);  color: var(--token-contr-color);  border: 1px solid var(--token-contr-border); }}
        .token-SOUND_FX    {{ background: var(--token-sound-bg);  color: var(--token-sound-color);  border: 1px solid var(--token-sound-border); }}
        .token-ELLIPSIS    {{ background: var(--token-elli-bg);   color: var(--token-elli-color);   border: 1px solid var(--token-elli-border); }}
        .token-INTERROBANG {{ background: var(--token-interr-bg); color: var(--token-interr-color); border: 1px solid var(--token-interr-border); }}
        .token-NUMBER      {{ background: var(--token-num-bg);    color: var(--token-num-color);    border: 1px solid var(--token-num-border); }}
        .token-UNKNOWN     {{ background: var(--token-unk-bg);    color: var(--token-unk-color);    border: 1px solid var(--token-unk-border); }}
    </style>
    """



def get_token_html(tokens):
    chips = []
    for t in tokens:
        cls_name = f"token-{t.type.value}"
        chips.append(f'<span class="token-chip {cls_name}" title="{t.type.value} [span {t.start_pos}:{t.end_pos}]">{t.value}</span>')
    return " ".join(chips)


def run_dashboard():
    # -------------------------------------------------------------
    # THEME TOGGLE & STATE MANAGEMENT (DARK & LIGHT)
    # -------------------------------------------------------------
    if "theme" not in st.session_state:
        st.session_state["theme"] = "dark"

    st.sidebar.markdown("### 🎨 Theme Mode")
    theme_choice = st.sidebar.radio(
        "Theme Mode",
        ["🌙 Dark Mode", "☀️ Light Mode"],
        index=0 if st.session_state["theme"] == "dark" else 1,
        horizontal=True,
        label_visibility="collapsed"
    )
    is_dark = "Dark" in theme_choice
    st.session_state["theme"] = "dark" if is_dark else "light"

    # Inject dynamic CSS based on active theme
    st.markdown(get_custom_css(is_dark), unsafe_allow_html=True)

    # Chart palette variables for theme harmony
    chart_font_color = "#E2E8F0" if is_dark else "#0F172A"
    chart_grid_color = "rgba(255, 255, 255, 0.08)" if is_dark else "rgba(0, 0, 0, 0.08)"
    chart_sub_color = "#94A3B8" if is_dark else "#475569"

    # ================================================================
    # HERO — FULL-WIDTH, BORDERLESS, PREMIUM
    # ================================================================
    st.markdown("""
    <div class="hero-wrap">
        <div class="hero-eyebrow">Comic Dialogue Analyzer</div>
        <h1 class="hero-title">Who's speaking?<br/><span>Let's find out.</span></h1>
        <p class="hero-subtitle">
            Upload a comic script and we'll show you which characters speak the most,
            who gets called out by name, and what the emotional tone looks like — all automatically.
        </p>
        <div class="hero-stats-row">
            <div class="hero-stat">
                <span class="hero-stat-num">~10k</span>
                <span class="hero-stat-label">lines per second</span>
            </div>
            <div class="hero-stat-divider"></div>
            <div class="hero-stat">
                <span class="hero-stat-num">0</span>
                <span class="hero-stat-label">lines rejected</span>
            </div>
            <div class="hero-stat-divider"></div>
            <div class="hero-stat">
                <span class="hero-stat-num">4</span>
                <span class="hero-stat-label">export formats</span>
            </div>
            <div class="hero-stat-divider"></div>
            <div class="hero-stat">
                <span class="hero-stat-num">9</span>
                <span class="hero-stat-label">token types detected</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------------------------------------------
    # SIDEBAR CONTROLS & DYNAMIC PRESETS (WITH FULL VISIBILITY)
    # -------------------------------------------------------------
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎛️ Controls")

    # Data Source Selection
    source_mode = st.sidebar.radio(
        "What do you want to analyze?",
        ["Benchmark Datasets", "Live Speech Bubble Playground", "Upload Custom Script"],
        index=0
    )

    # 1. Bubble Splitting Setting
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ✂️ Speech Bubble Options")
    split_bubbles = st.sidebar.checkbox(
        "Split multi-sentence bubbles",
        value=True,
        help="In comics, one speech balloon often contains several sentences (e.g. 'LOOK OUT, BRUCE! WHERE DID HE GO?'). Turn this on to analyze each sentence separately for more accurate results."
    )

    # 2. Dynamic External Alias & Universe Configuration
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🦸 Character Universe")
    presets = get_available_alias_presets()
    preset_names = list(presets.keys())
    
    alias_source_mode = st.sidebar.radio(
        "Character aliases:",
        ["Preset Universe", "Upload Custom JSON"],
        index=0
    )

    active_aliases = None
    if alias_source_mode == "Preset Universe":
        selected_preset_name = st.sidebar.selectbox("Active Universe:", preset_names if preset_names else ["Default"])
        if preset_names:
            preset_path = presets[selected_preset_name]
            try:
                active_aliases = load_aliases_from_json(preset_path)
                st.sidebar.caption(f"✓ Bound {len(active_aliases)} character identities from `{os.path.basename(preset_path)}`")
            except Exception as e:
                st.sidebar.error(f"Error loading preset: {e}")
    else:
        uploaded_alias_file = st.sidebar.file_uploader("Upload Universe JSON:", type=["json"])
        if uploaded_alias_file is not None:
            try:
                alias_content = uploaded_alias_file.read().decode("utf-8")
                active_aliases = load_aliases_from_json(alias_content)
                st.sidebar.success(f"Loaded {len(active_aliases)} mappings from uploaded configuration.")
            except Exception as e:
                st.sidebar.error(f"Invalid JSON format: {e}")

    # 3. Popularity Weight Controls
    st.sidebar.markdown("---")
    with st.sidebar.expander("⚖️ Adjust How We Score Characters", expanded=False):
        w_spoken = st.slider("Score for lines spoken", 0.0, 3.0, 1.0, 0.1)
        w_addressed = st.slider("Score for being directly addressed", 0.0, 3.0, 1.5, 0.1)
        w_mentioned = st.slider("Score for being mentioned by others", 0.0, 3.0, 0.8, 0.1)
        w_tone = st.slider("Bonus for dramatic/intense lines", 0.0, 1.0, 0.2, 0.05)

    custom_weights = {
        "spoken": w_spoken,
        "addressed": w_addressed,
        "mentioned": w_mentioned,
        "tone_bonus": w_tone
    }

    # Pipeline Initialization
    pipeline = ComicDialoguePipeline()
    pipeline.popularity_engine.weights = custom_weights
    if active_aliases:
        pipeline.set_aliases(active_aliases)

    reporter = DialogueReporter(pipeline)

    # -------------------------------------------------------------
    # MODE 1: Single Sentence Live Playground (Asymmetrical IDE layout)
    # -------------------------------------------------------------
    if source_mode == "Live Speech Bubble Playground":
        st.markdown("### 🔍 Interactive Speech Balloon Inspector")
        st.caption("Deconstruct individual comic lines into clauses, lexical tokens, proper name vocatives, and emotional tone markers.")

        pg_col1, pg_col2 = st.columns([6, 4])

        with pg_col1:
            playground_presets = [
                "BATMAN: LOOK OUT, BRUCE! WHERE DID HE GO? HE WAS JUST HERE...",
                "CLINT: WHERE COULD HE BE, NATASHA?",
                "BATMAN: HAVE A PEANUT.",
                "GREEN ARROW: I JUST STOPPED THE ENTIRE WORLD FROM BEING EATEN, DINAH.",
                "THE JOKER: HAHAHA! DID YOU REALLY THINK YOU COULD CATCH ME, BRUCE?!",
                "GORDON: BATMAN~ WE HAVE A 10-99 AT SECTOR 4#.",
                "SPIDER-MAN: WHOA?! THWIP! I DIDN'T EXPECT YOU HERE, JOKER!",
                "TONY STARK: JARVIS, FULL POWER TO THRUSTERS! NOW!",
                "BLACK WIDOW: I HEAR YOU, STARK... BUT SOMETHING IS WRONG."
            ]
            
            selected_preset = st.selectbox("Load Benchmark Utterance:", playground_presets)
            input_sentence = st.text_input("Or Enter Custom Dialogue Line (Speaker: Text):", value=selected_preset)
            run_btn = st.button("🚀 Analyze This Line", type="primary", use_container_width=True)

        with pg_col2:
            st.markdown("""
            <div class="panel-card">
                <div class="panel-label">HOW IT WORKS</div>
                <p style="font-size:0.82rem; color:#64748B; margin-bottom:0; line-height:1.6;">
                    <b style="color:#94A3B8;">Sentence splitting:</b> Each speech balloon is broken into individual sentences so tone and addressing are tracked separately.<br/>
                    <b style="color:#94A3B8;">Vocative detection:</b> Finds who is being spoken <i>to</i> (e.g. "Look out, Bruce!" means Bruce is being addressed).<br/>
                    <b style="color:#94A3B8;">Noise handling:</b> Stray characters from scanning errors are flagged automatically.
                </p>
            </div>
            """, unsafe_allow_html=True)

        if run_btn:
            t_start = time.perf_counter()
            if split_bubbles:
                analyses: list[SentenceAnalysis] = pipeline.analyze_bubble(input_sentence)
            else:
                analyses = [pipeline.analyze_sentence(input_sentence)]
            elapsed = (time.perf_counter() - t_start) * 1000

            st.markdown("<br>", unsafe_allow_html=True)

            # Telemetry Cards
            spk = analyses[0].speaker or "Anonymous (Unprefixed)"
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.markdown(f"""
                <div class="bento-card">
                    <div class="bento-label">WHO IS SPEAKING</div>
                    <div class="bento-value-sm" style="color:var(--text-accent);">{spk}</div>
                </div>
                """, unsafe_allow_html=True)
            with m2:
                st.markdown(f"""
                <div class="bento-card">
                    <div class="bento-label">SENTENCES FOUND</div>
                    <div class="bento-value-sm">{len(analyses)}</div>
                </div>
                """, unsafe_allow_html=True)
            with m3:
                all_addressed = [a.addressed for a in analyses if a.addressed]
                addr_str = ", ".join(all_addressed) if all_addressed else "Nobody specific"
                st.markdown(f"""
                <div class="bento-card">
                    <div class="bento-label">SPOKEN TO</div>
                    <div class="bento-value-sm" style="color:var(--text-accent-purple);">{addr_str}</div>
                </div>
                """, unsafe_allow_html=True)
            with m4:
                total_errors = sum(len(a.lexical_errors) for a in analyses)
                err_color = "#EF4444" if total_errors > 0 else "#10B981"
                err_label = f"{total_errors} found" if total_errors > 0 else "None found"
                st.markdown(f"""
                <div class="bento-card">
                    <div class="bento-label">SCAN ERRORS</div>
                    <div class="bento-value-sm" style="color:{err_color};">{err_label}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### 🧩 Sentence-by-Sentence Breakdown")

            for idx, a in enumerate(analyses, 1):
                st.markdown(f"""
                <div class="clause-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
                        <span style="font-weight:700; font-size:1.05rem; color:var(--text-primary);">Clause {idx} of {len(analyses)}: <i>"{a.raw_text}"</i></span>
                        <span class="bento-pill pill-blue">{a.sentence_type.value.upper()}</span>
                    </div>
                    <div style="display:flex; gap:16px; margin-bottom:0.6rem; font-size:0.88rem; color:var(--text-muted);">
                        <span><b style="color:var(--text-primary);">Reason:</b> {a.classification_reason}</span>
                        <span><b style="color:var(--text-primary);">Tone:</b> {", ".join(a.tone_cues.tags) if a.tone_cues.tags else "Neutral"}</span>
                        <span><b style="color:var(--text-primary);">Addressed:</b> {a.addressed or "-"}</span>
                        <span><b style="color:var(--text-primary);">Mentions:</b> {", ".join(a.mentions) if a.mentions else "-"}</span>
                    </div>
                    <div>{get_token_html(a.tokens)}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
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
            "Select Benchmark Corpus:",
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
        uploaded_file = st.sidebar.file_uploader("Upload Dialogue Script (.txt / .csv):", type=["txt", "csv"])
        if uploaded_file is not None:
            dataset_file = os.path.join("data", "uploaded_temp.txt")
            with open(dataset_file, "wb") as f:
                f.write(uploaded_file.getbuffer())

    if not dataset_file or not os.path.exists(dataset_file):
        st.warning("Please select or upload a dataset file.")
        return

    with open(dataset_file, "r", encoding="utf-8", errors="ignore") as f:
        raw_lines = f.readlines()

    total_raw = len(raw_lines)
    if total_raw > 100:
        limit_lines = st.sidebar.slider(
            "Corpus Processing Depth:",
            min_value=100,
            max_value=min(10000, total_raw),
            value=min(6500, total_raw),
            step=100 if total_raw < 2000 else 500
        )
        lines_to_process = raw_lines[:limit_lines]
    else:
        lines_to_process = raw_lines

    # Run Analysis
    with st.spinner(f"Analyzing {len(lines_to_process):,} dialogue lines..."):
        t0 = time.perf_counter()
        analyses = pipeline.analyze_batch(lines_to_process, split_bubbles=split_bubbles)
        t_elapsed = time.perf_counter() - t0
        report: DatasetReport = reporter.generate_report(analyses, elapsed_sec=t_elapsed)

    # ================================================================
    # POST-ANALYSIS METRICS — 4-CARD PREMIUM GRID
    # ================================================================
    top_char  = report.character_rankings[0]["character"] if report.character_rankings else "N/A"
    top_score = report.character_rankings[0]["score"]     if report.character_rankings else 0.0
    top_spoken= report.character_rankings[0]["spoken"]    if report.character_rankings else 0
    top_addr  = report.character_rankings[0]["addressed"] if report.character_rankings else 0
    top_ment  = report.character_rankings[0]["mentioned"] if report.character_rankings else 0

    ocr_label = f"{report.total_lexical_errors} found"  if report.total_lexical_errors > 0 else "None"
    ocr_color = "#EF4444"                               if report.total_lexical_errors > 0 else "#10B981"

    # 4 cards: hero-wide left, then 3 equal right
    mc1, mc2, mc3, mc4 = st.columns([2.2, 1, 1, 1])

    with mc1:
        st.markdown(f"""
        <div class="bento-card bento-card-hero">
            <div class="bento-label">👑 Top Character — Rank #1</div>
            <div class="bento-value-hero">{top_char}</div>
            <div class="bento-score-hero">
                {top_score:.1f} <span class="bento-unit">points</span>
            </div>
            <div style="display:flex; gap:5px; flex-wrap:wrap;">
                <span class="bento-pill pill-blue">{top_spoken} spoken</span>
                <span class="bento-pill pill-purple">{top_addr} addressed</span>
                <span class="bento-pill pill-green">{top_ment} mentioned</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with mc2:
        st.markdown(f"""
        <div class="bento-card">
            <div class="bento-label">Processing Speed</div>
            <div class="bento-value-sm" style="color:#10B981;">{report.processing_time_ms:.0f}<span style="font-size:1rem; font-weight:500;"> ms</span></div>
            <div class="bento-sub">Time to analyze the entire script</div>
        </div>
        """, unsafe_allow_html=True)

    with mc3:
        st.markdown(f"""
        <div class="bento-card">
            <div class="bento-label">Scan Errors</div>
            <div class="bento-value-sm" style="color:{ocr_color};">{ocr_label}</div>
            <div class="bento-sub">Broken or unreadable characters flagged during analysis</div>
        </div>
        """, unsafe_allow_html=True)

    with mc4:
        st.markdown(f"""
        <div class="bento-card">
            <div class="bento-label">Lines Analyzed</div>
            <div class="bento-value-sm">{report.total_sentences:,}</div>
            <div class="bento-sub">{report.total_tokens:,} words &amp; symbols across <b style="color:var(--text-primary);">{len(report.character_rankings)}</b> characters</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # -------------------------------------------------------------
    # MODERN SEGMENTED TABS
    # -------------------------------------------------------------
    tab_pop, tab_network, tab_compiler, tab_errors, tab_sentences, tab_export = st.tabs([
        "⭐ Character Popularity",
        "🕸️ Conversational Network (Who Talks to Whom)",
        "📊 Compiler Analytics",
        "⚠️ Lexical OCR Errors",
        "📜 Speech Bubble Inspector",
        "📥 Academic Export Suite"
    ])

    # -------------------------------------------------------------
    # TAB 1: Character Popularity (65 / 35 Asymmetric Split)
    # -------------------------------------------------------------
    with tab_pop:
        char_df = pd.DataFrame(report.character_rankings)

        if not char_df.empty:
            pop_col_left, pop_col_right = st.columns([6.5, 3.5])

            with pop_col_left:
                st.caption("Each bar shows how a character's total score is built up — from their own speaking lines, being called by name, and being mentioned by others.")
                num_chars = len(char_df)
                top_n = st.slider("Characters to show:", min_value=3, max_value=min(30, num_chars), value=min(12, num_chars), key="slider_pop")
                sub_df = char_df.head(top_n).copy()

                # Modern Stacked Bar Chart with clean theme
                fig_score = go.Figure()
                fig_score.add_trace(go.Bar(
                    x=sub_df["character"],
                    y=sub_df["spoken"] * custom_weights["spoken"],
                    name="Lines Spoken",
                    marker=dict(color="#38BDF8")
                ))
                fig_score.add_trace(go.Bar(
                    x=sub_df["character"],
                    y=sub_df["addressed"] * custom_weights["addressed"],
                    name="Directly Addressed by Others",
                    marker=dict(color="#818CF8")
                ))
                fig_score.add_trace(go.Bar(
                    x=sub_df["character"],
                    y=sub_df["mentioned"] * custom_weights["mentioned"],
                    name="Mentioned by Others",
                    marker=dict(color="#34D399")
                ))
                fig_score.add_trace(go.Bar(
                    x=sub_df["character"],
                    y=sub_df["tone"] * custom_weights["tone_bonus"],
                    name="Dramatic/Intense Lines",
                    marker=dict(color="#FBBF24")
                ))

                fig_score.update_layout(
                    barmode='stack',
                    margin=dict(l=10, r=10, t=30, b=10),
                    xaxis=dict(showgrid=False, tickfont=dict(size=12, color=chart_font_color, family="Plus Jakarta Sans")),
                    yaxis=dict(showgrid=True, gridcolor=chart_grid_color, tickfont=dict(size=11, color=chart_sub_color)),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=11, color=chart_font_color)),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    height=420
                )
                st.plotly_chart(fig_score, use_container_width=True)

            with pop_col_right:
                st.markdown("""
                <div class="panel-card">
                    <div class="panel-label">HOW SCORES ARE CALCULATED</div>
                    <div class="math-box">
                        Score =<br/>
                        &nbsp;&nbsp;1.0 × lines spoken +<br/>
                        &nbsp;&nbsp;1.5 × times addressed +<br/>
                        &nbsp;&nbsp;0.8 × times mentioned +<br/>
                        &nbsp;&nbsp;0.2 × dramatic tone
                    </div>
                    <p class="panel-desc">
                        <b>Lines spoken:</b> How many times they say something.<br/>
                        <b>Addressed (×1.5):</b> Others calling them by name — weighted higher because it highlights narrative importance.<br/>
                        <b>Mentioned (×0.8):</b> Being talked about by others.<br/>
                        <b>Dramatic tone:</b> Small bonus for intense or action lines.
                    </p>
                </div>
                """, unsafe_allow_html=True)

            # Full Leaderboard Table with micro-borders
            st.markdown("#### 🏆 Full Character Rankings")
            st.caption("Spoken = lines said. Addressed = times called by name by someone else. Mentioned = talked about by others. Score = weighted total.")
            st.dataframe(
                char_df[["rank", "character", "spoken", "addressed", "mentioned", "tone", "score", "aliases"]],
                use_container_width=True,
                height=380
            )
        else:
            st.info("No characters detected in the current selection.")

    # -------------------------------------------------------------
    # TAB 2: Conversational Social Network (70 / 30 Asymmetric Split)
    # -------------------------------------------------------------
    with tab_network:
        net_analyzer = ConversationalNetworkAnalyzer(pipeline.popularity_engine)
        net_data = report.network_summary or net_analyzer.build_network_data()

        if net_data and net_data.get("nodes"):
            net_nodes_df = pd.DataFrame(net_data["nodes"])

            st.caption("Each node is a character. An arrow from A to B means A called out to B by name. Bigger nodes = higher popularity score. Hover a node for full details.")

            net_col_left, net_col_right = st.columns([7, 3])

            with net_col_left:
                ctrl1, ctrl2 = st.columns([1, 1])
                with ctrl1:
                    net_top_n = st.slider(
                        "Characters to show:",
                        min_value=3,
                        max_value=min(25, len(net_nodes_df)),
                        value=min(12, len(net_nodes_df)),
                        key="slider_net"
                    )
                with ctrl2:
                    color_metric = st.selectbox(
                        "Color nodes by:",
                        [
                            ("in_degree_centrality", "Who gets addressed the most"),
                            ("betweenness_centrality", "Who acts as a bridge between others"),
                            ("degree_centrality", "Total connections"),
                            ("score", "Popularity score")
                        ],
                        format_func=lambda x: x[1]
                    )[0]

                # Render Network Graph
                fig_network = net_analyzer.generate_plotly_figure(
                    top_n=net_top_n,
                    color_by=color_metric,
                    is_dark=is_dark
                )

                if fig_network:
                    fig_network.update_layout(
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)' if is_dark else 'rgba(241, 245, 249, 0.6)',
                        font=dict(color=chart_font_color),
                        title=dict(font=dict(color=chart_font_color, size=16))
                    )
                    st.plotly_chart(fig_network, use_container_width=True, config={'displayModeBar': False})
                else:
                    st.warning("Could not render network graph.")

            with net_col_right:
                st.markdown("""
                <div class="panel-card">
                    <div class="panel-label">HOW TO READ THE GRAPH</div>
                    <p class="panel-desc">
                        <b>Arrows</b> point from the speaker to the person they address by name.<br/><br/>
                        <b>Node size</b> reflects overall prominence score — bigger = more central character.<br/><br/>
                        <b>Node color</b> is set by the metric you pick above.
                    </p>
                </div>
                """, unsafe_allow_html=True)

                if net_data.get("edges"):
                    st.markdown("##### 🤝 Who Talks to Whom (Most)")
                    edges_df = pd.DataFrame(net_data["edges"]).sort_values(by="weight", ascending=False)
                    for _, row in edges_df.head(6).iterrows():
                        st.markdown(f"""
                        <div class="dyad-row">
                            <span class="dyad-names"><b>{row['source']}</b> &rarr; {row['target']}</span>
                            <span class="bento-pill pill-blue">{row['weight']}×</span>
                        </div>
                        """, unsafe_allow_html=True)

            # Centrality Metrics Table
            st.markdown("#### 📊 Character Connection Stats")
            st.caption("In-degree = how often addressed by others. Out-degree = how often they address others. Betweenness = how often they act as a bridge between characters.")
            st.dataframe(
                net_nodes_df.head(net_top_n)[[
                    "character", "in_degree", "out_degree", "degree_centrality",
                    "betweenness_centrality", "pagerank", "score"
                ]],
                use_container_width=True
            )
        else:
            st.info("No conversational vocative interactions detected in this subset.")

    # -------------------------------------------------------------
    # TAB 3: Compiler Front-End Analytics (Bento Layout)
    # -------------------------------------------------------------
    with tab_compiler:
        st.markdown("### 📊 Language & Token Breakdown")
        st.caption("A closer look at how dialogue is distributed across sentence types, emotional tone, and word categories.")

        col1, col2 = st.columns([5.2, 4.8])
        with col1:
            st.markdown("##### What kinds of sentences appear most?")
            st.caption("Statement = saying something. Question = asking. Exclamation = intense/emphatic. Command = ordering someone to act.")
            type_df = pd.DataFrame(list(report.type_distribution.items()), columns=["Type", "Count"])
            fig_type = px.pie(
                type_df,
                values="Count",
                names="Type",
                hole=0.55,
                color="Type",
                color_discrete_map={
                    "statement": "#38BDF8",
                    "question": "#818CF8",
                    "exclamation": "#F87171",
                    "command": "#FBBF24"
                }
            )
            fig_type.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=chart_font_color),
                height=320
            )
            st.plotly_chart(fig_type, use_container_width=True)

        with col2:
            st.markdown("##### What emotional tone do lines carry?")
            st.caption("Shouting = lines with lots of exclamation marks. Hesitation = lines with '...' trailing off. Surprise = '?!' disbelief. Combat = sound effects like BOOM or AAARGH.")
            tone_df = pd.DataFrame(list(report.tone_distribution.items()), columns=["Tone", "Count"])
            tone_df["Tone"] = tone_df["Tone"].str.replace("_", " ").str.capitalize()
            fig_tone = px.bar(
                tone_df,
                x="Tone",
                y="Count",
                color="Tone",
                color_discrete_sequence=["#F87171", "#818CF8", "#F472B6", "#FBBF24"]
            )
            fig_tone.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=chart_font_color),
                xaxis=dict(gridcolor=chart_grid_color, tickfont=dict(color=chart_sub_color)),
                yaxis=dict(gridcolor=chart_grid_color, tickfont=dict(color=chart_sub_color)),
                showlegend=False,
                height=320
            )
            st.plotly_chart(fig_tone, use_container_width=True)

        col3, col4 = st.columns([4.8, 5.2])
        with col3:
            st.markdown("##### What types of words appear most?")
            st.caption("WORD = regular word. SOUND_FX = action sounds like BOOM. CONTRACTION = words like don't, I'm. UNKNOWN = garbled/unreadable characters.")
            t_class_df = pd.DataFrame(list(report.token_class_distribution.items()), columns=["Token Class", "Occurrences"])
            t_class_df = t_class_df.sort_values(by="Occurrences", ascending=False)
            fig_tclass = px.bar(
                t_class_df,
                x="Token Class",
                y="Occurrences",
                color="Token Class",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_tclass.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=chart_font_color),
                xaxis=dict(gridcolor=chart_grid_color, tickfont=dict(color=chart_sub_color)),
                yaxis=dict(gridcolor=chart_grid_color, tickfont=dict(color=chart_sub_color)),
                showlegend=False,
                height=340
            )
            st.plotly_chart(fig_tclass, use_container_width=True)

        with col4:
            st.markdown("##### Most common words across the script")
            top_tok_df = pd.DataFrame(report.top_tokens)
            fig_tok = px.bar(
                top_tok_df,
                x="token",
                y="count",
                color="type",
                color_discrete_sequence=["#38BDF8", "#818CF8", "#34D399"]
            )
            fig_tok.update_layout(
                margin=dict(l=10, r=10, t=10, b=10),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=chart_font_color),
                xaxis=dict(gridcolor=chart_grid_color, tickfont=dict(color=chart_sub_color)),
                yaxis=dict(gridcolor=chart_grid_color, tickfont=dict(color=chart_sub_color)),
                height=340
            )
            st.plotly_chart(fig_tok, use_container_width=True)

    # -------------------------------------------------------------
    # TAB 4: Lexical OCR Errors (Telemetry & Diagnostic Log)
    # -------------------------------------------------------------
    with tab_errors:
        st.markdown("### ⚠️ Scan Error Log")
        st.caption("When scanning or converting a comic script, some characters may come out garbled (like '~', '#', or '|'). These are flagged here with their exact position so they can be reviewed.")

        if report.lexical_errors:
            err_df = pd.DataFrame(report.lexical_errors)
            st.dataframe(err_df[["line", "symbol", "position", "description", "sentence_snippet"]], use_container_width=True)
        else:
            st.success("🎉 No lexical OCR noise artifacts detected in this sample.")

    # -------------------------------------------------------------
    # TAB 5: Speech Bubble Inspector
    # -------------------------------------------------------------
    with tab_sentences:
        st.markdown("### 📜 Line-by-Line Breakdown")
        st.caption("Each row is one sentence from the script. 'Addressed' = who is being spoken to. 'Mentions' = who is being talked about. 'Tone' = emotional quality of the line.")
        sample_size = min(60, len(analyses))
        st.caption(f"Showing first {sample_size} processed sentences / decomposed clauses:")

        sentence_rows = []
        for a in analyses[:sample_size]:
            clause_str = f"{a.clause_index}/{a.total_clauses}" if a.total_clauses > 1 else "1/1"
            sentence_rows.append({
                "Line": a.line_num,
                "Clause": clause_str,
                "Speaker": a.speaker or "ANONYMOUS",
                "Dialogue": a.raw_text,
                "Type": a.sentence_type.value.upper(),
                "Addressed": a.addressed or "-",
                "Mentions": ", ".join(a.mentions) if a.mentions else "-",
                "Tone": ", ".join(a.tone_cues.tags) if a.tone_cues.tags else "Neutral",
                "Tokens (Short)": a.short_tokens_str()
            })

        st.dataframe(pd.DataFrame(sentence_rows), use_container_width=True, height=450)

    # -------------------------------------------------------------
    # TAB 6: Academic Export Suite (40 / 60 Asymmetric Split)
    # -------------------------------------------------------------
    with tab_export:
        st.markdown("### 📥 Download Your Results")
        st.caption("Export the analysis in several formats — use the CSV or Excel for spreadsheets, JSON for developers, or LaTeX if you're including this in an academic paper.")

        csv_leaderboard = ExportEngine.export_leaderboard_csv(report)
        json_report = ExportEngine.export_full_json(report, analyses, network_data=report.network_summary)
        latex_tables_code = ExportEngine.generate_latex_tables(report, network_data=report.network_summary)
        excel_bytes = ExportEngine.export_leaderboard_excel(report, network_data=report.network_summary)

        exp_col_left, exp_col_right = st.columns([4, 6])

        with exp_col_left:
            st.markdown("""
            <div class="export-tile" style="margin-bottom:12px;">
                <div class="export-title">📊 Character Rankings (CSV)</div>
                <div class="export-desc">A spreadsheet with every character's score, lines spoken, and how often they were addressed or mentioned. Opens in Excel or Google Sheets.</div>
            </div>
            """, unsafe_allow_html=True)
            st.download_button(
                label="Download Rankings (.csv)",
                data=csv_leaderboard,
                file_name="character_popularity_leaderboard.csv",
                mime="text/csv",
                use_container_width=True
            )

            st.markdown("""
            <div class="export-tile" style="margin-top:14px; margin-bottom:12px;">
                <div class="export-title">📗 Full Analytics Workbook (Excel)</div>
                <div class="export-desc">Multiple sheets in one file: character rankings, network connections, and scan error log.</div>
            </div>
            """, unsafe_allow_html=True)
            if excel_bytes:
                st.download_button(
                    label="Download Workbook (.xlsx)",
                    data=excel_bytes,
                    file_name="comic_dialogue_analytics.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            else:
                st.button("Excel Export Unavailable", disabled=True, use_container_width=True)

            st.markdown("""
            <div class="export-tile" style="margin-top:14px; margin-bottom:12px;">
                <div class="export-title">📦 Full Data Log (JSON)</div>
                <div class="export-desc">Complete machine-readable output with every token, score, and error position — useful for developers or further processing.</div>
            </div>
            """, unsafe_allow_html=True)
            st.download_button(
                label="Download Full Log (.json)",
                data=json_report,
                file_name="comic_dialogue_full_report.json",
                mime="application/json",
                use_container_width=True
            )

            st.markdown("""
            <div class="export-tile" style="margin-top:14px; margin-bottom:12px;">
                <div class="export-title">📄 Academic Paper Tables (LaTeX)</div>
                <div class="export-desc">Ready-to-paste LaTeX code for IEEE, ACM, or Overleaf papers. Paste directly into your results section.</div>
            </div>
            """, unsafe_allow_html=True)
            st.download_button(
                label="Download LaTeX Code (.tex)",
                data=latex_tables_code,
                file_name="academic_paper_tables.tex",
                mime="text/x-tex",
                type="primary",
                use_container_width=True
            )

        with exp_col_right:
            st.markdown("##### 📝 LaTeX Code Preview")
            st.caption("Copy this into any LaTeX editor (like Overleaf) to include formatted tables in your paper:")
            st.code(latex_tables_code, language="latex")


if __name__ == "__main__":
    run_dashboard()
