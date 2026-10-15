"""
Configuration and lexicon definitions for the Comic Dialogue Analyzer.
"""

from enum import Enum
from typing import Dict, Set, List


class TokenType(str, Enum):
    WORD = "WORD"
    NUMBER = "NUMBER"
    CONTRACTION = "CONTRACTION"
    PUNCT = "PUNCT"
    TERMINATOR = "TERMINATOR"
    ELLIPSIS = "ELLIPSIS"
    INTERROBANG = "INTERROBANG"
    SOUND_FX = "SOUND_FX"
    UNKNOWN = "UNKNOWN"


class SentenceType(str, Enum):
    STATEMENT = "statement"
    QUESTION = "question"
    EXCLAMATION = "exclamation"
    COMMAND = "command"


# Onomatopoeia and common comic sound effects
DEFAULT_SOUND_EFFECTS: Set[str] = {
    "BOOM", "AAARGH", "AARGH", "ARGH", "POW", "BAM", "KABOOM", "WHAM", "ZAP",
    "CRASH", "BANG", "SMASH", "OOF", "UGH", "THWIP", "SNIKT", "KAPOW", "GULP",
    "GASP", "WHOOSH", "CLANG", "THUD", "ROAR", "SCREECH", "BEEP", "PING",
    "SWOOSH", "CRACK", "SPLAT", "BUZZ", "HISS", "YIKES", "OUCH"
}

# Wh-words and auxiliary verbs for identifying questions
QUESTION_STARTERS: Set[str] = {
    "WHO", "WHAT", "WHERE", "WHEN", "WHY", "HOW", "WHICH", "WHOSE", "WHOM",
    "COULD", "CAN", "IS", "ARE", "AM", "WAS", "WERE", "DO", "DOES", "DID",
    "WILL", "WOULD", "SHALL", "SHOULD", "MAY", "MIGHT", "MUST"
}

# Common imperative starting verbs for command classification
IMPERATIVE_VERBS: Set[str] = {
    "HAVE", "STOP", "GO", "LOOK", "LISTEN", "GIVE", "TAKE", "TELL", "WAIT",
    "HELP", "GET", "COME", "RUN", "STAY", "DROP", "PUT", "HOLD", "BRING",
    "MOVE", "STAND", "SHUT", "WATCH", "OPEN", "CLOSE", "LEAVE", "FOLLOW",
    "SHOOT", "ATTACK", "DUCK", "JUMP", "FIRE", "SURRENDER", "FREEZE"
}

# Default alias mapping: variant -> canonical name
DEFAULT_ALIASES: Dict[str, str] = {
    "BRUCE": "BATMAN",
    "BRUCE WAYNE": "BATMAN",
    "THE DARK KNIGHT": "BATMAN",
    "DARK KNIGHT": "BATMAN",
    "THE BAT": "BATMAN",
    "BATMAN": "BATMAN",

    "TONY": "IRON MAN",
    "TONY STARK": "IRON MAN",
    "STARK": "IRON MAN",
    "IRON MAN": "IRON MAN",

    "NATASHA": "BLACK WIDOW",
    "NAT": "BLACK WIDOW",
    "NATASHA ROMANOFF": "BLACK WIDOW",
    "ROMANOFF": "BLACK WIDOW",
    "BLACK WIDOW": "BLACK WIDOW",

    "DINAH": "BLACK CANARY",
    "DINAH LANCE": "BLACK CANARY",
    "BLACK CANARY": "BLACK CANARY",

    "CLARK": "SUPERMAN",
    "CLARK KENT": "SUPERMAN",
    "KAL-EL": "SUPERMAN",
    "MAN OF STEEL": "SUPERMAN",
    "SUPERMAN": "SUPERMAN",

    "STEVE": "CAPTAIN AMERICA",
    "STEVE ROGERS": "CAPTAIN AMERICA",
    "CAP": "CAPTAIN AMERICA",
    "CAPTAIN AMERICA": "CAPTAIN AMERICA",

    "PETER": "SPIDER-MAN",
    "PETER PARKER": "SPIDER-MAN",
    "SPIDEY": "SPIDER-MAN",
    "WEB-SLINGER": "SPIDER-MAN",
    "SPIDER-MAN": "SPIDER-MAN",

    "JOKER": "THE JOKER",
    "THE JOKER": "THE JOKER",
    "CLOWN PRINCE": "THE JOKER",

    "ROBIN": "ROBIN",
    "DICK": "ROBIN",
    "DICK GRAYSON": "ROBIN",

    "THOR": "THOR",
    "ODINSON": "THOR",
    "GOD OF THUNDER": "THOR",

    "LOKI": "LOKI",
    "GOD OF MISCHIEF": "LOKI",

    "HAL": "GREEN LANTERN",
    "HAL JORDAN": "GREEN LANTERN",
    "GREEN LANTERN": "GREEN LANTERN"
}

# Default scoring weights for Character Popularity ranking
DEFAULT_WEIGHTS: Dict[str, float] = {
    "spoken": 1.0,      # Line spoken directly (Direct agency)
    "addressed": 1.5,   # Direct vocative address (Conversational focal point)
    "mentioned": 0.8,   # Third-party mention in text (Narrative footprint)
    "tone_bonus": 0.2   # Emotional/high-energy bonus (shout, scream, sound fx)
}
