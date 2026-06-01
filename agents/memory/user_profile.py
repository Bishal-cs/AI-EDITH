"""
User Profile — Long-Term Preference Learning
==============================================
Tracks user preferences, habits, mood patterns,
and frequently used features so EDITH can personalize
responses and proactively suggest actions.
"""

import os
import json
import time
from datetime import datetime
from typing import Optional
from agents.logger import get_logger

log = get_logger("memory")


class UserProfile:
    """
    Persistent user profile that learns from interactions.
    
    Tracks:
    - Name, last seen, total sessions
    - Preferred apps and common searches
    - Mood history (rolling window)
    - Frequently used agents
    - Custom preferences
    """

    _instance = None
    STORAGE_PATH = os.path.join("user_data", "user_profile.json")

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._profile: dict = {}
        self._load()
        self._initialized = True

    def _default_profile(self) -> dict:
        """Default profile structure."""
        return {
            "name": "User",
            "location": "",
            "last_seen": time.time(),
            "first_seen": time.time(),
            "total_sessions": 0,
            "preferred_apps": {},         # {"chrome": 15, "spotify": 8, ...}
            "common_searches": [],        # last 20 search terms
            "mood_history": [],           # last 50 mood readings
            "agent_usage": {},            # {"chat": 45, "automation": 20, ...}
            "preferences": {
                "verbosity": "normal",    # "concise", "normal", "detailed"
                "humor_level": "moderate",
                "weather_location": "",
                "preferred_music_platform": "youtube",
            },
            "conversation_topics": [],    # last 30 topics discussed
        }

    def _load(self):
        """Load profile from disk."""
        try:
            if os.path.exists(self.STORAGE_PATH):
                with open(self.STORAGE_PATH, "r", encoding="utf-8") as f:
                    self._profile = json.load(f)
                log.debug("User profile loaded")
            else:
                self._profile = self._default_profile()
                self._save()
                log.info("Created new user profile")
        except (json.JSONDecodeError, Exception) as e:
            log.warning(f"Failed to load user profile: {e}")
            self._profile = self._default_profile()

    def _save(self):
        """Persist profile to disk."""
        try:
            os.makedirs(os.path.dirname(self.STORAGE_PATH), exist_ok=True)
            with open(self.STORAGE_PATH, "w", encoding="utf-8") as f:
                json.dump(self._profile, f, indent=2)
        except Exception as e:
            log.error(f"Failed to save user profile: {e}")

    # ── Getters ──────────────────────────────────────────────

    def get_profile(self) -> dict:
        """Get the full profile dict."""
        return dict(self._profile)

    def get(self, key: str, default=None):
        """Get a top-level profile value."""
        return self._profile.get(key, default)

    def get_preference(self, key: str, default=None):
        """Get a preference value."""
        return self._profile.get("preferences", {}).get(key, default)

    def get_name(self) -> str:
        return self._profile.get("name", "User")

    def get_location(self) -> str:
        return self._profile.get("location", "") or self._profile.get("preferences", {}).get("weather_location", "")

    # ── Setters ──────────────────────────────────────────────

    def set(self, key: str, value):
        """Set a top-level profile value."""
        self._profile[key] = value
        self._save()

    def set_preference(self, key: str, value):
        """Set a preference value."""
        if "preferences" not in self._profile:
            self._profile["preferences"] = {}
        self._profile["preferences"][key] = value
        self._save()

    def set_name(self, name: str):
        self._profile["name"] = name
        self._save()

    def set_location(self, location: str):
        self._profile["location"] = location
        self._profile.setdefault("preferences", {})["weather_location"] = location
        self._save()

    # ── Tracking Methods ─────────────────────────────────────

    def record_session_start(self):
        """Record that a new session has started."""
        self._profile["last_seen"] = time.time()
        self._profile["total_sessions"] = self._profile.get("total_sessions", 0) + 1
        self._save()

    def record_agent_use(self, agent_name: str):
        """Track which agents are used most."""
        usage = self._profile.setdefault("agent_usage", {})
        usage[agent_name] = usage.get(agent_name, 0) + 1
        self._save()

    def record_app_use(self, app_name: str):
        """Track which apps are opened most."""
        apps = self._profile.setdefault("preferred_apps", {})
        apps[app_name] = apps.get(app_name, 0) + 1
        self._save()

    def record_search(self, query: str):
        """Track search terms."""
        searches = self._profile.setdefault("common_searches", [])
        searches.append(query)
        if len(searches) > 20:
            self._profile["common_searches"] = searches[-20:]
        self._save()

    def record_mood(self, mood: str):
        """Record a mood reading."""
        moods = self._profile.setdefault("mood_history", [])
        moods.append({
            "mood": mood,
            "timestamp": time.time()
        })
        if len(moods) > 50:
            self._profile["mood_history"] = moods[-50:]
        self._save()

    def record_topic(self, topic: str):
        """Track conversation topics."""
        topics = self._profile.setdefault("conversation_topics", [])
        topics.append(topic)
        if len(topics) > 30:
            self._profile["conversation_topics"] = topics[-30:]
        self._save()

    # ── Analysis ─────────────────────────────────────────────

    def infer_mood(self, recent_turns: list[dict] | None = None) -> str:
        """
        Infer user's current mood from recent conversation turns.
        Uses simple keyword analysis. For deeper analysis, the chat
        agent uses LLM-based mood detection.
        """
        if not recent_turns:
            # Fall back to last recorded mood
            moods = self._profile.get("mood_history", [])
            if moods:
                return moods[-1].get("mood", "neutral")
            return "neutral"

        # Simple keyword-based mood detection
        positive_words = {"great", "awesome", "happy", "love", "thanks", "good", 
                         "amazing", "wonderful", "excellent", "perfect", "nice", "cool",
                         "haha", "hehe", "lol", "yay", "excited"}
        negative_words = {"bad", "sad", "angry", "frustrated", "hate", "terrible",
                         "awful", "annoying", "stressed", "tired", "ugh", "damn",
                         "horrible", "worst", "sucks"}
        
        text = " ".join(
            t.get("content", "").lower() 
            for t in recent_turns 
            if t.get("role") == "user"
        )
        words = set(text.split())

        pos_count = len(words & positive_words)
        neg_count = len(words & negative_words)

        if pos_count > neg_count + 1:
            return "positive"
        elif neg_count > pos_count + 1:
            return "negative"
        elif neg_count > 0 and pos_count == 0:
            return "stressed"
        return "neutral"

    def get_top_apps(self, n: int = 5) -> list[str]:
        """Get the user's most-used apps."""
        apps = self._profile.get("preferred_apps", {})
        sorted_apps = sorted(apps.items(), key=lambda x: x[1], reverse=True)
        return [app for app, _ in sorted_apps[:n]]

    def get_top_agents(self, n: int = 3) -> list[str]:
        """Get the most-used agent types."""
        usage = self._profile.get("agent_usage", {})
        sorted_agents = sorted(usage.items(), key=lambda x: x[1], reverse=True)
        return [agent for agent, _ in sorted_agents[:n]]

    def get_time_since_last_seen(self) -> str:
        """Human-readable time since last session."""
        last = self._profile.get("last_seen", 0)
        if last == 0:
            return "first time"
        diff = time.time() - last
        if diff < 60:
            return "just now"
        elif diff < 3600:
            return f"{int(diff/60)} minutes ago"
        elif diff < 86400:
            return f"{int(diff/3600)} hours ago"
        else:
            return f"{int(diff/86400)} days ago"

    def get_greeting_context(self) -> str:
        """Generate context string for personalized greetings."""
        name = self.get_name()
        last_seen = self.get_time_since_last_seen()
        sessions = self._profile.get("total_sessions", 0)
        top_agents = self.get_top_agents(2)

        parts = [f"User: {name}", f"Last seen: {last_seen}", f"Sessions: {sessions}"]
        if top_agents:
            parts.append(f"Most used: {', '.join(top_agents)}")

        recent_moods = self._profile.get("mood_history", [])[-3:]
        if recent_moods:
            mood_str = ", ".join(m.get("mood", "neutral") for m in recent_moods)
            parts.append(f"Recent moods: {mood_str}")

        return " | ".join(parts)
