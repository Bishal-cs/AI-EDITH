"""
EDITH Logger — Structured, Color-Coded Logging
================================================
Rich-powered logging with per-agent color coding,
session file output, and clean formatting.
Replaces all print() calls across the system.
"""

import os
import sys
import time
import logging
from datetime import datetime
from typing import Optional

try:
    from rich.console import Console
    from rich.logging import RichHandler
    from rich.theme import Theme
    HAS_RICH = True
except ImportError:
    HAS_RICH = False


# ═══════════════════════════════════════════════════════════════
# Agent Colors
# ═══════════════════════════════════════════════════════════════

AGENT_COLORS = {
    "orchestrator": "bold cyan",
    "chat":         "bold green",
    "automation":   "bold yellow",
    "vision":       "bold magenta",
    "system":       "bold blue",
    "scheduler":    "bold red",
    "content":      "bold white",
    "memory":       "dim cyan",
    "event_bus":    "dim yellow",
    "edith":        "bold bright_white",
}

AGENT_ICONS = {
    "orchestrator": "🧠",
    "chat":         "💬",
    "automation":   "⚡",
    "vision":       "👁️",
    "system":       "🖥️",
    "scheduler":    "⏰",
    "content":      "✍️",
    "memory":       "🧬",
    "event_bus":    "📡",
    "edith":        "✦",
}

LOG_LEVEL_ICONS = {
    "DEBUG":   "🔍",
    "INFO":    "ℹ️",
    "SUCCESS": "✅",
    "WARNING": "⚠️",
    "ERROR":   "❌",
}


# ═══════════════════════════════════════════════════════════════
# Custom SUCCESS level
# ═══════════════════════════════════════════════════════════════

SUCCESS_LEVEL = 25
logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")


# ═══════════════════════════════════════════════════════════════
# Logger Class
# ═══════════════════════════════════════════════════════════════

class EdithLogger:
    """
    Centralized logger for the EDITH system.
    
    Features:
    - Per-agent color-coded console output
    - Session log files in user_data/logs/
    - Custom SUCCESS level
    - Rich formatting (if available)
    """

    _instances: dict[str, 'EdithLogger'] = {}
    _session_id: str = datetime.now().strftime("%Y%m%d_%H%M%S")
    _log_dir: str = os.path.join("user_data", "logs")
    _console: Optional[object] = None

    @classmethod
    def _ensure_log_dir(cls):
        os.makedirs(cls._log_dir, exist_ok=True)

    @classmethod
    def _get_console(cls):
        if cls._console is None and HAS_RICH:
            theme = Theme({name: color for name, color in AGENT_COLORS.items()})
            cls._console = Console(theme=theme, stderr=True)
        return cls._console

    def __init__(self, agent_name: str):
        self.agent_name = agent_name.lower()
        self.icon = AGENT_ICONS.get(self.agent_name, "●")
        self.color = AGENT_COLORS.get(self.agent_name, "white")
        self._logger = logging.getLogger(f"edith.{self.agent_name}")
        self._logger.setLevel(logging.DEBUG)
        self._logger.propagate = False

        # Only add handlers once
        if not self._logger.handlers:
            self._setup_handlers()

    def _setup_handlers(self):
        """Configure console and file handlers."""
        self._ensure_log_dir()

        # ── File Handler (always plain text) ──
        log_file = os.path.join(self._log_dir, f"session_{self._session_id}.log")
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_fmt = logging.Formatter(
            f"%(asctime)s | {self.agent_name.upper():>12} | %(levelname)-8s | %(message)s",
            datefmt="%H:%M:%S"
        )
        file_handler.setFormatter(file_fmt)
        self._logger.addHandler(file_handler)

        # ── Console Handler ──
        if HAS_RICH:
            console = self._get_console()
            rich_handler = RichHandler(
                console=console,
                show_path=False,
                show_time=True,
                rich_tracebacks=True,
                markup=True,
                log_time_format="%H:%M:%S"
            )
            rich_handler.setLevel(logging.INFO)
            self._logger.addHandler(rich_handler)
        else:
            console_handler = logging.StreamHandler(sys.stderr)
            console_handler.setLevel(logging.INFO)
            console_fmt = logging.Formatter(
                f"%(asctime)s {self.icon} [{self.agent_name.upper()}] %(message)s",
                datefmt="%H:%M:%S"
            )
            console_handler.setFormatter(console_fmt)
            self._logger.addHandler(console_handler)

    # ── Logging Methods ──────────────────────────────────────

    def debug(self, msg: str, **kwargs):
        self._logger.debug(f"{self.icon} [{self.agent_name}] {msg}", **kwargs)

    def info(self, msg: str, **kwargs):
        self._logger.info(f"{self.icon} [{self.agent_name}] {msg}", **kwargs)

    def success(self, msg: str, **kwargs):
        self._logger.log(SUCCESS_LEVEL, f"{self.icon} [{self.agent_name}] ✅ {msg}", **kwargs)

    def warning(self, msg: str, **kwargs):
        self._logger.warning(f"{self.icon} [{self.agent_name}] ⚠️  {msg}", **kwargs)

    def error(self, msg: str, **kwargs):
        self._logger.error(f"{self.icon} [{self.agent_name}] ❌ {msg}", **kwargs)

    def exception(self, msg: str, **kwargs):
        self._logger.exception(f"{self.icon} [{self.agent_name}] 💥 {msg}", **kwargs)

    # ── Special Logging ──────────────────────────────────────

    def agent_start(self, query: str):
        """Log when an agent starts processing."""
        self.info(f"Processing: \"{query[:80]}{'...' if len(query) > 80 else ''}\"")

    def agent_done(self, latency: float, success: bool = True):
        """Log when an agent finishes processing."""
        status = "SUCCESS" if success else "FAILED"
        self.info(f"Done ({status}) in {latency*1000:.0f}ms")

    def routing(self, query: str, target: str, confidence: float, reasoning: str = ""):
        """Log a routing decision."""
        self.info(
            f"Routing → [{target}] (confidence: {confidence:.0%}) "
            f"| {reasoning[:60]}"
        )

    def event(self, topic: str, data: str = ""):
        """Log an event bus event."""
        self.debug(f"Event [{topic}]: {data[:100]}")


# ═══════════════════════════════════════════════════════════════
# Factory
# ═══════════════════════════════════════════════════════════════

def get_logger(agent_name: str) -> EdithLogger:
    """Get or create a logger for the given agent."""
    key = agent_name.lower()
    if key not in EdithLogger._instances:
        EdithLogger._instances[key] = EdithLogger(agent_name)
    return EdithLogger._instances[key]
