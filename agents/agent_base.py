"""
Base Agent Framework — Ultra Edition
=====================================
Defines the contract all agents must follow, plus shared response types,
retry logic, metrics tracking, and the context pipeline that makes
inter-agent communication seamless.
"""

import enum
import time
import uuid
import asyncio
from dataclasses import dataclass, field
from typing import AsyncGenerator, Optional, Any


# ═══════════════════════════════════════════════════════════════
# Enums
# ═══════════════════════════════════════════════════════════════

class AgentType(str, enum.Enum):
    """Identifiers for each specialized agent."""
    CHAT = "chat"
    AUTOMATION = "automation"
    VISION = "vision"
    SYSTEM = "system"
    SCHEDULER = "scheduler"
    CONTENT = "content"
    ORCHESTRATOR = "orchestrator"


class AgentStatus(str, enum.Enum):
    """Lifecycle status of an agent."""
    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"
    RECOVERING = "recovering"
    DISABLED = "disabled"


# ═══════════════════════════════════════════════════════════════
# Data Classes
# ═══════════════════════════════════════════════════════════════

@dataclass
class AgentContext:
    """
    Full context passed between agents during execution.
    This is the 'bloodstream' of inter-agent communication —
    it carries everything the next agent needs to know.
    """
    session_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    query: str = ""
    previous_results: list[dict] = field(default_factory=list)
    user_mood: str = "neutral"
    user_profile: dict = field(default_factory=dict)
    recent_memory: list[dict] = field(default_factory=list)
    chain_depth: int = 0                # how many agents deep we are
    max_chain_depth: int = 5            # prevent infinite loops
    metadata: dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def add_result(self, agent: str, result: dict):
        """Append an agent's result to the chain."""
        self.previous_results.append({
            "agent": agent,
            "result": result,
            "timestamp": time.time()
        })
        self.chain_depth += 1

    def get_last_result(self) -> dict | None:
        """Get the most recent agent result."""
        return self.previous_results[-1] if self.previous_results else None

    def can_chain(self) -> bool:
        """Check if we can add another agent to the chain."""
        return self.chain_depth < self.max_chain_depth

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "query": self.query,
            "previous_results": self.previous_results,
            "user_mood": self.user_mood,
            "chain_depth": self.chain_depth,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }


@dataclass
class AgentResponse:
    """
    Standardized response from any agent.
    Now includes confidence scoring, timing, and chain metadata.
    """
    agent: AgentType
    text: str
    success: bool = True
    confidence: float = 1.0               # 0.0 - 1.0, how sure the agent is
    action_taken: Optional[str] = None    # e.g. "opened Chrome"
    data: Optional[dict] = None           # structured data payload
    audio_file: Optional[str] = None      # path to TTS audio
    error: Optional[str] = None
    processing_time: float = 0.0          # seconds taken
    agent_chain: list[str] = field(default_factory=list)  # agents involved
    metadata: dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "agent": self.agent.value,
            "text": self.text,
            "success": self.success,
            "confidence": self.confidence,
            "action_taken": self.action_taken,
            "data": self.data,
            "audio_file": self.audio_file,
            "error": self.error,
            "processing_time": round(self.processing_time, 3),
            "agent_chain": self.agent_chain,
            "metadata": self.metadata,
            "timestamp": self.timestamp,
        }


@dataclass
class AgentMetrics:
    """Tracks performance metrics for an agent."""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    total_latency: float = 0.0
    last_called: float = 0.0
    error_history: list[str] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        if self.total_calls == 0:
            return 0.0
        return self.successful_calls / self.total_calls

    @property
    def avg_latency(self) -> float:
        if self.total_calls == 0:
            return 0.0
        return self.total_latency / self.total_calls

    def record_call(self, success: bool, latency: float, error: str | None = None):
        self.total_calls += 1
        self.total_latency += latency
        self.last_called = time.time()
        if success:
            self.successful_calls += 1
        else:
            self.failed_calls += 1
            if error:
                self.error_history.append(error)
                # Keep only last 20 errors
                if len(self.error_history) > 20:
                    self.error_history = self.error_history[-20:]

    def to_dict(self) -> dict:
        return {
            "total_calls": self.total_calls,
            "success_rate": round(self.success_rate, 3),
            "avg_latency_ms": round(self.avg_latency * 1000, 1),
            "last_called": self.last_called,
            "recent_errors": self.error_history[-5:],
        }


# ═══════════════════════════════════════════════════════════════
# Base Agent
# ═══════════════════════════════════════════════════════════════

class BaseAgent:
    """
    Abstract base class for all EDITH agents.

    Each agent declares its name, description, and capabilities.
    The Orchestrator uses these to decide routing. Now includes
    retry logic, metrics tracking, and lifecycle management.
    """

    name: str = "BaseAgent"
    agent_type: AgentType = AgentType.CHAT
    description: str = "A base agent with no capabilities."
    capabilities: list[str] = []

    def __init__(self):
        self._status = AgentStatus.IDLE
        self._metrics = AgentMetrics()

    @property
    def is_active(self) -> bool:
        return self._status not in (AgentStatus.DISABLED, AgentStatus.ERROR)

    @property
    def status(self) -> AgentStatus:
        return self._status

    @property
    def metrics(self) -> AgentMetrics:
        return self._metrics

    def get_capability_summary(self) -> str:
        """Returns a string summary for the orchestrator's routing prompt."""
        caps = ", ".join(self.capabilities)
        return f"{self.name} ({self.agent_type.value}): {self.description}. Can handle: {caps}"

    async def execute(self, query: str, context: AgentContext | None = None) -> AgentResponse:
        """
        Process a user query and return a response.
        Override in subclasses.
        """
        raise NotImplementedError(f"{self.name} must implement execute()")

    async def execute_with_retry(
        self,
        query: str,
        context: AgentContext | None = None,
        retries: int = 3,
        backoff: float = 0.5
    ) -> AgentResponse:
        """
        Execute with automatic retry and exponential backoff.
        Tracks metrics for every call.
        """
        last_error = None
        self._status = AgentStatus.RUNNING

        for attempt in range(retries):
            start = time.time()
            try:
                response = await self.execute(query, context)
                latency = time.time() - start
                response.processing_time = latency
                response.agent_chain = [self.agent_type.value]

                self._metrics.record_call(
                    success=response.success,
                    latency=latency,
                    error=response.error
                )
                self._status = AgentStatus.IDLE
                return response

            except Exception as e:
                latency = time.time() - start
                last_error = str(e)
                self._metrics.record_call(success=False, latency=latency, error=last_error)

                if attempt < retries - 1:
                    self._status = AgentStatus.RECOVERING
                    wait = backoff * (2 ** attempt)
                    await asyncio.sleep(wait)
                else:
                    self._status = AgentStatus.ERROR

        # All retries exhausted
        return AgentResponse(
            agent=self.agent_type,
            text=f"I tried {retries} times but couldn't complete that. Error: {last_error}",
            success=False,
            confidence=0.0,
            error=last_error,
            agent_chain=[self.agent_type.value]
        )

    async def stream_execute(self, query: str, context: AgentContext | None = None) -> AsyncGenerator[str, None]:
        """
        Stream response tokens one by one for real-time display.
        Default implementation wraps execute() as a single yield.
        Override in subclasses for true streaming.
        """
        response = await self.execute(query, context)
        yield response.text

    def _run_sync(self, func, *args, **kwargs) -> Any:
        """Helper to run synchronous functions in an async context."""
        loop = asyncio.get_event_loop()
        return loop.run_in_executor(None, lambda: func(*args, **kwargs))

    def reset(self):
        """Reset agent to idle state."""
        self._status = AgentStatus.IDLE
