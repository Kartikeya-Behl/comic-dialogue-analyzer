"""
Character Popularity Engine.
Handles alias merging, multi-metric name tallying, weighted score ranking,
and conversational interaction networks.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Union
import os
from .config import DEFAULT_ALIASES, DEFAULT_WEIGHTS
from .alias_loader import load_aliases_from_json, DEFAULT_ALIASES_PATH


@dataclass
class CharacterStats:
    canonical_name: str
    spoken_count: int = 0
    addressed_count: int = 0
    mentioned_count: int = 0
    tone_count: int = 0
    popularity_score: float = 0.0
    aliases_encountered: Set[str] = field(default_factory=set)
    lines_active: List[int] = field(default_factory=list)
    addressed_others: Dict[str, int] = field(default_factory=dict)

    def compute_score(self, weights: Dict[str, float]) -> float:
        """
        Computes composite popularity score based on weighted metrics.
        """
        w_s = weights.get("spoken", 1.0)
        w_a = weights.get("addressed", 1.5)
        w_m = weights.get("mentioned", 0.8)
        w_t = weights.get("tone_bonus", 0.2)

        self.popularity_score = (
            w_s * self.spoken_count +
            w_a * self.addressed_count +
            w_m * self.mentioned_count +
            w_t * self.tone_count
        )
        return self.popularity_score


class CharacterPopularityEngine:
    def __init__(
        self,
        aliases: Optional[Dict[str, str]] = None,
        weights: Optional[Dict[str, float]] = None
    ):
        if aliases is not None:
            self.aliases = {k.upper(): v.upper() for k, v in aliases.items()}
        elif os.path.exists(DEFAULT_ALIASES_PATH):
            try:
                self.aliases = load_aliases_from_json(DEFAULT_ALIASES_PATH, fallback_aliases=DEFAULT_ALIASES)
            except Exception:
                self.aliases = {k.upper(): v.upper() for k, v in DEFAULT_ALIASES.items()}
        else:
            self.aliases = {k.upper(): v.upper() for k, v in DEFAULT_ALIASES.items()}

        self.weights: Dict[str, float] = weights or DEFAULT_WEIGHTS
        self.registry: Dict[str, CharacterStats] = {}

    def set_aliases(self, aliases: Dict[str, str]) -> None:
        """Replaces current aliases with a new normalized dictionary."""
        self.aliases = {k.upper(): v.upper() for k, v in aliases.items()}

    def load_aliases_from_file(self, filepath_or_source: Union[str, bytes, dict], merge: bool = False) -> None:
        """Loads aliases from a JSON file path, JSON string, or dict."""
        loaded = load_aliases_from_json(filepath_or_source)
        if merge:
            self.aliases.update(loaded)
        else:
            self.aliases = loaded

    def resolve_alias(self, name: str) -> str:
        """
        Maps any alias or variation to its canonical character name.
        Example: 'BRUCE' -> 'BATMAN', 'THE DARK KNIGHT' -> 'BATMAN'
        """
        clean_name = name.strip().upper()
        return self.aliases.get(clean_name, clean_name)

    def get_or_create(self, name: str) -> CharacterStats:
        canonical = self.resolve_alias(name)
        if canonical not in self.registry:
            self.registry[canonical] = CharacterStats(canonical_name=canonical)
        return self.registry[canonical]

    def record_activity(
        self,
        speaker: Optional[str] = None,
        addressed: Optional[str] = None,
        mentions: Optional[List[str]] = None,
        has_high_tone: bool = False,
        line_num: int = 1
    ) -> None:
        """
        Records a single dialogue interaction:
        - updates spoken count for speaker
        - updates addressed count for vocative recipient
        - updates mentions for referenced characters
        - tracks speaker -> addressed interaction edge
        """
        canonical_speaker = None
        if speaker:
            canonical_speaker = self.resolve_alias(speaker)
            spk_stats = self.get_or_create(speaker)
            spk_stats.spoken_count += 1
            spk_stats.aliases_encountered.add(speaker.strip().upper())
            if line_num not in spk_stats.lines_active:
                spk_stats.lines_active.append(line_num)
            if has_high_tone:
                spk_stats.tone_count += 1

        if addressed:
            canonical_addr = self.resolve_alias(addressed)
            addr_stats = self.get_or_create(addressed)
            addr_stats.addressed_count += 1
            addr_stats.aliases_encountered.add(addressed.strip().upper())
            if line_num not in addr_stats.lines_active:
                addr_stats.lines_active.append(line_num)

            # Record directed interaction if speaker is known
            if canonical_speaker and canonical_speaker != canonical_addr:
                spk_stats = self.get_or_create(canonical_speaker)
                spk_stats.addressed_others[canonical_addr] = (
                    spk_stats.addressed_others.get(canonical_addr, 0) + 1
                )

        if mentions:
            for m in mentions:
                canonical_m = self.resolve_alias(m)
                # Avoid self-mention inflating speaker or addressed counts
                if canonical_speaker and canonical_m == canonical_speaker:
                    continue
                if addressed and canonical_m == self.resolve_alias(addressed):
                    continue

                m_stats = self.get_or_create(m)
                m_stats.mentioned_count += 1
                m_stats.aliases_encountered.add(m.strip().upper())
                if line_num not in m_stats.lines_active:
                    m_stats.lines_active.append(line_num)

    def compute_rankings(self) -> List[CharacterStats]:
        """
        Calculates the popularity score for all registered characters
        and returns them ranked in descending order.
        """
        for stats in self.registry.values():
            stats.compute_score(self.weights)

        ranked = sorted(self.registry.values(), key=lambda s: s.popularity_score, reverse=True)
        return ranked

    def get_known_character_names(self) -> Set[str]:
        """
        Returns all known aliases and canonical character names.
        """
        names = set(self.aliases.keys()) | set(self.aliases.values()) | set(self.registry.keys())
        return names

    def generate_popularity_report(self) -> str:
        """
        Generates a formatted text table showing rankings, metrics, and scores.
        """
        rankings = self.compute_rankings()
        if not rankings:
            return "No character activity recorded."

        lines = []
        lines.append("=" * 82)
        lines.append(f"{'RANK':<5}{'CHARACTER':<20}{'SPOKEN':<9}{'ADDRESSED':<11}{'MENTIONED':<11}{'TONE':<8}{'SCORE':<8}")
        lines.append("-" * 82)

        for i, c in enumerate(rankings, 1):
            lines.append(
                f"{i:<5}{c.canonical_name:<20}{c.spoken_count:<9}{c.addressed_count:<11}{c.mentioned_count:<11}{c.tone_count:<8}{c.popularity_score:<8.1f}"
            )
        lines.append("=" * 82)
        return "\n".join(lines)
