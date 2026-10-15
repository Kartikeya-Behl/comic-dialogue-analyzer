"""
Cleaner and Speaker Split module.
Extracts speaker prefixes, cleans OCR noise, handles hyphen repair,
and normalizes spacing.
"""

import re
from dataclasses import dataclass
from typing import Optional, Tuple, List


@dataclass
class PreprocessedSentence:
    speaker: Optional[str]
    raw_text: str
    cleaned_text: str
    original_line: str


class DialogueCleaner:
    def __init__(self):
        # Regex to match "SPEAKER: text" or "SPEAKER (O.S.): text" or "[SPEAKER]: text"
        self.speaker_pattern = re.compile(
            r'^\s*(?:\[(?P<bracket_speaker>[^\]]+)\]|(?P<speaker>[A-Za-z0-9_\-\.\s]+?))\s*:\s*(?P<dialogue>.*)$'
        )

    def split_speaker(self, line: str) -> Tuple[Optional[str], str]:
        """
        Splits dialogue line into speaker and dialogue body.
        Example: 'BATMAN: WHERE COULD HE BE, NATASHA?' -> ('BATMAN', 'WHERE COULD HE BE, NATASHA?')
        """
        match = self.speaker_pattern.match(line)
        if match:
            speaker = match.group("bracket_speaker") or match.group("speaker")
            dialogue = match.group("dialogue")
            return speaker.strip(), dialogue.strip()
        return None, line.strip()

    def clean_text(self, text: str) -> str:
        """
        Cleans dialogue text by collapsing extra whitespace,
        repairing hyphenated broken line wraps (e.g. 'com- \nputer' -> 'computer'),
        and ensuring consistent formatting.
        """
        # Repair broken hyphenated words at ends of lines or before spaces
        text = re.sub(r'(\b[A-Za-z]+)-\s+([A-Za-z]+\b)', r'\1\2', text)
        
        # Collapse multiple spaces and tabs
        text = re.sub(r'[ \t]+', ' ', text)
        return text.strip()

    def preprocess(self, raw_line: str) -> PreprocessedSentence:
        """
        Runs the full speaker split and text cleaning step.
        """
        speaker, dialogue = self.split_speaker(raw_line)
        cleaned = self.clean_text(dialogue)
        return PreprocessedSentence(
            speaker=speaker,
            raw_text=dialogue,
            cleaned_text=cleaned,
            original_line=raw_line
        )
