"""
Scheduler Agent — Alarms & Reminders
======================================
Handles setting alarms, scheduling tasks,
and managing time-based reminders.
Wraps existing Time_operations/ modules.
"""

import json
from agents.agent_base import BaseAgent, AgentResponse, AgentType


# Number prefixes for time formatting (from original co_brain.py)
SINGLE_DIGIT_HOURS = ["1:", "2:", "3:", "4:", "5:", "6:", "7:", "8:", "9:"]
DOUBLE_DIGIT_HOURS = ["11:", "12:"]


class SchedulerAgent(BaseAgent):
    name = "Time Scheduler"
    agent_type = AgentType.SCHEDULER
    description = "Manages alarms, schedules, reminders, and time-based tasks."
    capabilities = [
        "set alarm", "set reminder", "schedule task",
        "tell me at (time)", "remind me", "wake me up",
        "check schedule", "check alarms"
    ]

    def __init__(self):
        super().__init__()
        self._loaded = False
        self.alarm_path = "user_data/Alarm_Data.txt"
        self.schedule_path = "user_data/schedule.txt"

    def _ensure_loaded(self):
        if self._loaded:
            return
        try:
            from Time_operations.Brain import input_manage, input_manage_Alam
            self._input_manage = input_manage
            self._input_manage_alarm = input_manage_Alam
        except ImportError as e:
            print(f"[SchedulerAgent] Failed to load time modules: {e}")
            self._input_manage = None
            self._input_manage_alarm = None
        self._loaded = True

    def _format_time_string(self, text: str) -> str:
        """Normalize time strings (add leading zeros, fix AM/PM)."""
        text = text.replace(" p.m.", "PM").replace(" a.m.", "AM")
        text = text.replace(" pm", "PM").replace(" am", "AM")

        # Check if it's a double-digit hour (11:, 12:) — no padding needed
        has_double = any(dh in text for dh in DOUBLE_DIGIT_HOURS)
        if not has_double:
            for sh in SINGLE_DIGIT_HOURS:
                if sh in text:
                    text = text.replace(sh, f"0{sh}")
                    break
        return text

    async def execute(self, query: str, context: dict | None = None) -> AgentResponse:
        """Process a scheduling/alarm command."""
        self._ensure_loaded()
        q = query.lower().strip()

        try:
            # ── Set Alarm ──
            if "alarm" in q or "wake" in q:
                if self._input_manage_alarm:
                    formatted = self._format_time_string(q)
                    await self._run_sync(self._input_manage_alarm, formatted)
                    return AgentResponse(
                        agent=AgentType.SCHEDULER,
                        text="Alarm has been set. I'll make sure you don't miss it.",
                        success=True,
                        action_taken="set_alarm"
                    )
                return AgentResponse(
                    agent=AgentType.SCHEDULER,
                    text="Alarm module is not available right now.",
                    success=False
                )

            # ── Schedule / Remind ──
            elif "schedule" in q or "remind" in q or "tell me" in q:
                if self._input_manage:
                    formatted = self._format_time_string(q)
                    await self._run_sync(self._input_manage, formatted)
                    return AgentResponse(
                        agent=AgentType.SCHEDULER,
                        text="Got it. I've scheduled that for you.",
                        success=True,
                        action_taken="set_schedule"
                    )
                return AgentResponse(
                    agent=AgentType.SCHEDULER,
                    text="Scheduling module is not available right now.",
                    success=False
                )

            # ── Check existing alarms/schedules ──
            elif "check" in q:
                info_parts = []
                try:
                    with open(self.alarm_path, "r") as f:
                        alarms = f.read().strip()
                        if alarms:
                            info_parts.append(f"Active alarms:\n{alarms}")
                        else:
                            info_parts.append("No active alarms.")
                except FileNotFoundError:
                    info_parts.append("No alarm file found.")

                try:
                    with open(self.schedule_path, "r") as f:
                        schedules = f.read().strip()
                        if schedules:
                            info_parts.append(f"Scheduled tasks:\n{schedules}")
                        else:
                            info_parts.append("No scheduled tasks.")
                except FileNotFoundError:
                    info_parts.append("No schedule file found.")

                return AgentResponse(
                    agent=AgentType.SCHEDULER,
                    text="\n".join(info_parts),
                    success=True,
                    action_taken="check_schedules"
                )

            return AgentResponse(
                agent=AgentType.SCHEDULER,
                text="I can set alarms, schedule reminders, or check your existing schedule. What would you like?",
                success=True
            )

        except Exception as e:
            return AgentResponse(
                agent=AgentType.SCHEDULER,
                text=f"Scheduling error: {str(e)}",
                success=False,
                error=str(e)
            )

    async def stream_execute(self, query: str, context: dict | None = None):
        yield json.dumps({"type": "status", "agent": "scheduler", "text": "Setting up schedule..."})
        response = await self.execute(query, context)
        yield json.dumps({
            "type": "done",
            "agent": "scheduler",
            "text": response.text
        })
