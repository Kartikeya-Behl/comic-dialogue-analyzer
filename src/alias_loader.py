"""
Dynamic External Alias and Lexicon Loader.
Loads JSON-based character alias maps across different comic and fiction universes.
"""

import json
import os
from typing import Dict, Any, Optional, Union


DEFAULT_ALIASES_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "aliases.json"
)


def load_aliases_from_json(
    source: Union[str, bytes, dict],
    fallback_aliases: Optional[Dict[str, str]] = None
) -> Dict[str, str]:
    """
    Parses an external JSON alias configuration.
    Accepts:
      - a file path string
      - raw JSON string/bytes
      - an existing parsed dict

    The JSON can either be a direct mapping:
      {"BRUCE": "BATMAN", "TONY": "IRON MAN"}
    or a structured container:
      {"universe": "DC", "aliases": {"BRUCE": "BATMAN", ...}}

    Returns a normalized {UPPERCASE_ALIAS: UPPERCASE_CANONICAL} dictionary.
    """
    data = None

    if isinstance(source, dict):
        data = source
    elif isinstance(source, (str, bytes)):
        # Check if it's an existing file path
        if isinstance(source, str) and os.path.isfile(source):
            try:
                with open(source, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                if fallback_aliases is not None:
                    return fallback_aliases
                raise ValueError(f"Could not load alias file '{source}': {e}")
        else:
            # Try parsing as JSON string or bytes
            try:
                data = json.loads(source)
            except Exception as e:
                if fallback_aliases is not None:
                    return fallback_aliases
                raise ValueError(f"Invalid JSON string passed to load_aliases_from_json: {e}")

    if not isinstance(data, dict):
        if fallback_aliases is not None:
            return fallback_aliases
        raise ValueError("Alias JSON must evaluate to a dictionary.")

    raw_map = data.get("aliases", data)
    if not isinstance(raw_map, dict):
        if fallback_aliases is not None:
            return fallback_aliases
        raise ValueError("Key 'aliases' must contain a key-value dictionary.")

    normalized: Dict[str, str] = {}
    for alias, canonical in raw_map.items():
        if isinstance(alias, str) and isinstance(canonical, str):
            clean_alias = alias.strip().upper()
            clean_canonical = canonical.strip().upper()
            if clean_alias and clean_canonical:
                normalized[clean_alias] = clean_canonical

    return normalized


def get_available_alias_presets(data_dir: Optional[str] = None) -> Dict[str, str]:
    """
    Discovers all available alias configuration files (*alias*.json) in the data directory.
    Returns mapping of friendly name -> file path.
    """
    if data_dir is None:
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

    presets: Dict[str, str] = {}
    if not os.path.isdir(data_dir):
        return presets

    for fname in sorted(os.listdir(data_dir)):
        if fname.endswith(".json") and "alias" in fname.lower():
            full_path = os.path.join(data_dir, fname)
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    content = json.load(f)
                    universe = content.get("universe", fname.replace(".json", "").replace("_", " ").title())
                    presets[universe] = full_path
            except Exception:
                presets[fname] = full_path

    return presets
