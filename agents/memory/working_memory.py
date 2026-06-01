"""
Working Memory — Short-Term Agent Memory
==========================================
In-RAM store of the last N turns with timestamps,
agent attribution, and fast keyword search.
Think of this as EDITH's "what just happened" buffer.
"""

import time
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MemoryEntry:
    """A single turn in working memory."""
    role: str                     # "user", "assistant", "system", "agent"
    content: str
    agent: str = "unknown"        # which agent produced/consumed this
    timestamp: float = field(default_factory=time.time)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "role": self.role,
            "content": self.content,
            "agent": self.agent,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MemoryEntry":
        return cls(
            role=data.get("role", "unknown"),
            content=data.get("content", ""),
            agent=data.get("agent", "unknown"),
            timestamp=data.get("timestamp", time.time()),
            metadata=data.get("metadata", {}),
        )


class WorkingMemory:
    """
    Short-term memory buffer.
    
    - Holds last `max_entries` turns in RAM
    - Searchable by keyword
    - Each entry tagged with agent + timestamp
    - Automatically evicts oldest entries when full
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """Singleton — one working memory for the system."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, max_entries: int = 30):
        if self._initialized:
            return
        self._entries: list[MemoryEntry] = []
        self._max_entries = max_entries
        self._initialized = True

    def push(
        self,
        role: str,
        content: str,
        agent: str = "unknown",
        metadata: dict | None = None
    ):
        """Add a new entry to working memory."""
        entry = MemoryEntry(
            role=role,
            content=content,
            agent=agent,
            metadata=metadata or {}
        )
        self._entries.append(entry)
        # Evict oldest if over limit
        if len(self._entries) > self._max_entries:
            self._entries = self._entries[-self._max_entries:]

    def get_recent(self, n: int = 10) -> list[MemoryEntry]:
        """Get the N most recent entries."""
        return self._entries[-n:]

    def get_recent_as_messages(self, n: int = 10) -> list[dict]:
        """Get recent entries formatted as LLM messages."""
        return [
            {"role": e.role if e.role in ("user", "assistant", "system") else "system",
             "content": e.content}
            for e in self._entries[-n:]
        ]

    def search(self, query: str, max_results: int = 5) -> list[MemoryEntry]:
        """Search memory by keyword overlap (case-insensitive)."""
        query_words = set(query.lower().split())
        scored = []
        for entry in self._entries:
            content_words = set(entry.content.lower().split())
            overlap = len(query_words & content_words)
            if overlap > 0:
                scored.append((overlap, entry))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in scored[:max_results]]

    def get_by_agent(self, agent: str, n: int = 10) -> list[MemoryEntry]:
        """Get entries from a specific agent."""
        return [e for e in self._entries if e.agent == agent][-n:]

    def get_conversation_summary(self) -> str:
        """Generate a brief summary of recent conversation for context injection."""
        recent = self.get_recent(5)
        if not recent:
            return "No recent conversation."
        
        lines = []
        for entry in recent:
            role_label = "User" if entry.role == "user" else f"{entry.agent.title()}"
            preview = entry.content[:100] + ("..." if len(entry.content) > 100 else "")
            lines.append(f"{role_label}: {preview}")
        return "\n".join(lines)

    def clear(self):
        """Clear all working memory."""
        self._entries.clear()

    @property
    def size(self) -> int:
        return len(self._entries)

    def to_list(self) -> list[dict]:
        return [e.to_dict() for e in self._entries]
