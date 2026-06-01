"""
Event Bus — Production-Grade Inter-Agent Communication
=======================================================
Pub/sub event system with priority levels, typed topics,
event replay, shared context, and session broadcasting.
"""

import asyncio
import time
import enum
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable, Any
from agents.logger import get_logger

log = get_logger("event_bus")


# ═══════════════════════════════════════════════════════════════
# Event Types & Priority
# ═══════════════════════════════════════════════════════════════

class EventTopic(str, enum.Enum):
    """Typed topics to prevent typos and enable IDE autocomplete."""
    ROUTING = "routing"
    AGENT_START = "agent_start"
    AGENT_DONE = "agent_done"
    AGENT_ERROR = "agent_error"
    MEMORY_UPDATE = "memory_update"
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    MOOD_CHANGE = "mood_change"
    ALARM_FIRED = "alarm_fired"
    REMINDER_FIRED = "reminder_fired"
    SYSTEM_ALERT = "system_alert"
    USER_PREFERENCE = "user_preference"
    SKILL_CHAIN = "skill_chain"


class EventPriority(int, enum.Enum):
    """Priority levels — high-priority events are processed first."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


@dataclass
class Event:
    """An event published by an agent."""
    topic: EventTopic | str
    source: str                               # agent name
    data: Any = None
    priority: EventPriority = EventPriority.NORMAL
    timestamp: float = field(default_factory=time.time)
    session_id: str = ""

    def to_dict(self) -> dict:
        return {
            "topic": self.topic.value if isinstance(self.topic, EventTopic) else self.topic,
            "source": self.source,
            "data": self.data,
            "priority": self.priority.value if isinstance(self.priority, EventPriority) else self.priority,
            "timestamp": self.timestamp,
            "session_id": self.session_id,
        }


# ═══════════════════════════════════════════════════════════════
# Event Bus
# ═══════════════════════════════════════════════════════════════

class EventBus:
    """
    Central event bus for the multi-agent system.

    Features:
    - Pub/sub event system with priority levels
    - Shared context store (key-value)
    - Event history with replay capability
    - Session lifecycle broadcasting
    - Typed topics for safety
    """

    _instance = None

    def __new__(cls):
        """Singleton — one event bus for the entire system."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._subscribers: dict[str, list[Callable]] = defaultdict(list)
        self._context: dict[str, Any] = {}
        self._history: list[Event] = []
        self._max_history = 500
        self._session_id: str = ""
        self._initialized = True
        log.debug("Event bus initialized")

    # ── Session Management ───────────────────────────────────

    def set_session(self, session_id: str):
        """Set the current session ID."""
        self._session_id = session_id

    @property
    def session_id(self) -> str:
        return self._session_id

    # ── Pub/Sub ──────────────────────────────────────────────

    def subscribe(self, topic: EventTopic | str, callback: Callable):
        """Subscribe a callback to a topic."""
        topic_key = topic.value if isinstance(topic, EventTopic) else topic
        self._subscribers[topic_key].append(callback)
        log.debug(f"Subscribed to [{topic_key}]")

    def unsubscribe(self, topic: EventTopic | str, callback: Callable):
        """Remove a callback from a topic."""
        topic_key = topic.value if isinstance(topic, EventTopic) else topic
        if callback in self._subscribers[topic_key]:
            self._subscribers[topic_key].remove(callback)

    async def publish(self, event: Event):
        """Publish an event to all subscribers of that topic."""
        # Attach session ID if not set
        if not event.session_id:
            event.session_id = self._session_id

        # Store in history
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

        topic_key = event.topic.value if isinstance(event.topic, EventTopic) else event.topic
        log.event(topic_key, str(event.data)[:80] if event.data else "")

        # Process subscribers — high-priority events first
        callbacks = self._subscribers.get(topic_key, [])
        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
            except Exception as e:
                log.error(f"Subscriber error for [{topic_key}]: {e}")

    async def emit(self, topic: EventTopic | str, source: str, data: Any = None,
                   priority: EventPriority = EventPriority.NORMAL):
        """Shorthand for creating and publishing an event."""
        await self.publish(Event(
            topic=topic,
            source=source,
            data=data,
            priority=priority,
            session_id=self._session_id,
        ))

    # ── Shared Context Store ─────────────────────────────────

    def set_context(self, key: str, value: Any):
        """Store a value in the shared context."""
        self._context[key] = value

    def get_context(self, key: str, default: Any = None) -> Any:
        """Retrieve a value from the shared context."""
        return self._context.get(key, default)

    def get_all_context(self) -> dict:
        """Get entire context store."""
        return dict(self._context)

    def update_context(self, updates: dict):
        """Batch update context."""
        self._context.update(updates)

    # ── History & Replay ─────────────────────────────────────

    def get_recent_events(self, n: int = 10) -> list[Event]:
        """Get the N most recent events."""
        return self._history[-n:]

    def get_events_by_topic(self, topic: EventTopic | str, n: int = 10) -> list[Event]:
        """Get recent events filtered by topic."""
        topic_key = topic.value if isinstance(topic, EventTopic) else topic
        matching = [e for e in self._history if 
                    (e.topic.value if isinstance(e.topic, EventTopic) else e.topic) == topic_key]
        return matching[-n:]

    def get_events_by_source(self, source: str, n: int = 10) -> list[Event]:
        """Get recent events from a specific agent."""
        matching = [e for e in self._history if e.source == source]
        return matching[-n:]

    def replay_since(self, timestamp: float) -> list[Event]:
        """Replay all events since a given timestamp."""
        return [e for e in self._history if e.timestamp >= timestamp]

    # ── Cleanup ──────────────────────────────────────────────

    def clear(self):
        """Reset the event bus (for testing)."""
        self._subscribers.clear()
        self._context.clear()
        self._history.clear()

    def clear_history(self):
        """Clear event history only."""
        self._history.clear()
