"""
Episodic Memory — Persistent Session Summaries
================================================
Stores condensed summaries of past sessions so EDITH
can recall: "Last time we talked about X" or "You've been
asking about Y a lot lately."

Each episode is a summary of a full conversation session,
stored in user_data/episodic_memory.json.
"""

import os
import json
import time
from dataclasses import dataclass, field
from typing import Optional
from agents.logger import get_logger

log = get_logger("memory")


@dataclass
class Episode:
    """A summarized memory of a past session."""
    timestamp: float
    summary: str
    agents_used: list[str]
    keywords: list[str]
    sentiment: str = "neutral"    # positive, negative, neutral
    query_count: int = 0
    session_id: str = ""

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "summary": self.summary,
            "agents_used": self.agents_used,
            "keywords": self.keywords,
            "sentiment": self.sentiment,
            "query_count": self.query_count,
            "session_id": self.session_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Episode":
        return cls(
            timestamp=data.get("timestamp", 0),
            summary=data.get("summary", ""),
            agents_used=data.get("agents_used", []),
            keywords=data.get("keywords", []),
            sentiment=data.get("sentiment", "neutral"),
            query_count=data.get("query_count", 0),
            session_id=data.get("session_id", ""),
        )


class EpisodicMemory:
    """
    Long-term memory of past conversation sessions.
    
    - Stores summarized episodes (not raw turns)
    - Searchable by keyword overlap
    - LLM-powered summarization at session end
    - Persisted to disk as JSON
    """

    _instance = None
    STORAGE_PATH = os.path.join("user_data", "episodic_memory.json")
    MAX_EPISODES = 200

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._episodes: list[Episode] = []
        self._load()
        self._initialized = True

    def _load(self):
        """Load episodes from disk."""
        try:
            if os.path.exists(self.STORAGE_PATH):
                with open(self.STORAGE_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._episodes = [Episode.from_dict(ep) for ep in data]
                log.debug(f"Loaded {len(self._episodes)} episodic memories")
        except (json.JSONDecodeError, Exception) as e:
            log.warning(f"Failed to load episodic memory: {e}")
            self._episodes = []

    def _save(self):
        """Persist episodes to disk."""
        try:
            os.makedirs(os.path.dirname(self.STORAGE_PATH), exist_ok=True)
            with open(self.STORAGE_PATH, "w", encoding="utf-8") as f:
                json.dump([ep.to_dict() for ep in self._episodes], f, indent=2)
        except Exception as e:
            log.error(f"Failed to save episodic memory: {e}")

    def record_episode(
        self,
        summary: str,
        agents_used: list[str],
        keywords: list[str],
        sentiment: str = "neutral",
        query_count: int = 0,
        session_id: str = ""
    ):
        """Record a new episode from a completed session."""
        episode = Episode(
            timestamp=time.time(),
            summary=summary,
            agents_used=agents_used,
            keywords=keywords,
            sentiment=sentiment,
            query_count=query_count,
            session_id=session_id,
        )
        self._episodes.append(episode)

        # Trim old episodes
        if len(self._episodes) > self.MAX_EPISODES:
            self._episodes = self._episodes[-self.MAX_EPISODES:]

        self._save()
        log.debug(f"Recorded episode: {summary[:60]}...")

    async def summarize_and_record(
        self,
        turns: list[dict],
        agents_used: list[str],
        session_id: str,
        groq_client=None
    ):
        """
        Use Groq LLM to summarize a session's turns into an episode.
        Falls back to a simple summary if LLM is unavailable.
        """
        if not turns:
            return

        # Try LLM summarization
        if groq_client:
            try:
                # Build a condensed transcript
                transcript = "\n".join(
                    f"{t.get('role', 'unknown')}: {t.get('content', '')[:150]}"
                    for t in turns[-20:]  # Last 20 turns max
                )

                completion = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": 
                         "Summarize this conversation in 1-2 sentences. "
                         "Also extract: keywords (comma-separated), sentiment (positive/negative/neutral). "
                         "Reply as JSON: {\"summary\": \"...\", \"keywords\": [\"...\"], \"sentiment\": \"...\"}"},
                        {"role": "user", "content": transcript}
                    ],
                    max_tokens=200,
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )

                result = json.loads(completion.choices[0].message.content)
                self.record_episode(
                    summary=result.get("summary", "Session occurred"),
                    agents_used=agents_used,
                    keywords=result.get("keywords", []),
                    sentiment=result.get("sentiment", "neutral"),
                    query_count=len([t for t in turns if t.get("role") == "user"]),
                    session_id=session_id,
                )
                return

            except Exception as e:
                log.warning(f"LLM summarization failed, using fallback: {e}")

        # Fallback: simple summary
        user_msgs = [t.get("content", "")[:50] for t in turns if t.get("role") == "user"]
        summary = f"Discussed: {', '.join(user_msgs[:5])}"
        keywords = []
        for t in turns:
            keywords.extend(t.get("content", "").lower().split()[:3])
        keywords = list(set(keywords))[:10]

        self.record_episode(
            summary=summary,
            agents_used=agents_used,
            keywords=keywords,
            query_count=len(user_msgs),
            session_id=session_id,
        )

    def recall(self, query: str, n: int = 5) -> list[Episode]:
        """
        Recall the N most relevant past episodes by keyword overlap.
        """
        query_words = set(query.lower().split())
        scored = []

        for episode in self._episodes:
            ep_words = set(word.lower() for word in episode.keywords)
            ep_words.update(episode.summary.lower().split())
            overlap = len(query_words & ep_words)
            if overlap > 0:
                scored.append((overlap, episode))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [ep for _, ep in scored[:n]]

    def get_recent(self, n: int = 5) -> list[Episode]:
        """Get the N most recent episodes."""
        return self._episodes[-n:]

    def get_recent_summaries(self, n: int = 3) -> str:
        """Get recent episode summaries as a string for context injection."""
        recent = self.get_recent(n)
        if not recent:
            return ""
        lines = []
        for ep in recent:
            from datetime import datetime
            dt = datetime.fromtimestamp(ep.timestamp)
            lines.append(f"[{dt.strftime('%b %d, %I:%M %p')}] {ep.summary}")
        return "\n".join(lines)

    @property
    def total_episodes(self) -> int:
        return len(self._episodes)
