"""
Symbol Table module for tracking token categories, frequencies, and proper names.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from .config import TokenType


@dataclass
class SymbolEntry:
    name: str
    token_type: TokenType
    count: int = 0
    is_proper_name: bool = False
    category: str = ""
    lines: List[int] = field(default_factory=list)


class SymbolTable:
    def __init__(self):
        # Key: uppercase token name
        self.table: Dict[str, SymbolEntry] = {}

    def insert(
        self,
        token_value: str,
        token_type: TokenType,
        line_num: int = 1,
        is_proper_name: bool = False,
        category: str = ""
    ) -> SymbolEntry:
        """
        Inserts or updates a token in the symbol table.
        """
        key = token_value.upper()
        if key not in self.table:
            self.table[key] = SymbolEntry(
                name=token_value,
                token_type=token_type,
                count=1,
                is_proper_name=is_proper_name,
                category=category,
                lines=[line_num]
            )
        else:
            entry = self.table[key]
            entry.count += 1
            if line_num not in entry.lines:
                entry.lines.append(line_num)
            if is_proper_name:
                entry.is_proper_name = True
            if category and not entry.category:
                entry.category = category
        return self.table[key]

    def lookup(self, token_value: str) -> Optional[SymbolEntry]:
        """
        Looks up a token by name.
        """
        return self.table.get(token_value.upper())

    def get_top_tokens(self, limit: int = 10, token_type: Optional[TokenType] = None) -> List[SymbolEntry]:
        """
        Returns the most frequent tokens, optionally filtered by token type.
        """
        items = list(self.table.values())
        if token_type is not None:
            items = [item for item in items if item.token_type == token_type]
        items.sort(key=lambda x: x.count, reverse=True)
        return items[:limit]

    def get_type_distribution(self) -> Dict[str, int]:
        """
        Returns the count of tokens per TokenType across all occurrences.
        """
        dist: Dict[str, int] = {}
        for entry in self.table.values():
            dist[entry.token_type.value] = dist.get(entry.token_type.value, 0) + entry.count
        return dist

    def get_proper_names(self) -> List[str]:
        """
        Returns all tokens flagged as proper names.
        """
        return [entry.name for entry in self.table.values() if entry.is_proper_name]
