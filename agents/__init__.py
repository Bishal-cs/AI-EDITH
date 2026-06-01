"""
AI-EDITH Multi-Agent System
============================
A JARVIS-inspired multi-agent architecture where specialized agents
handle different capabilities, orchestrated by an intelligent router.
"""

from agents.agent_base import BaseAgent, AgentResponse, AgentType
from agents.orchestrator import OrchestratorAgent
from agents.event_bus import EventBus

__all__ = [
    "BaseAgent",
    "AgentResponse", 
    "AgentType",
    "OrchestratorAgent",
    "EventBus",
]
