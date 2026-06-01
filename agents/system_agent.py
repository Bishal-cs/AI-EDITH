"""
System Agent — Device Info, Weather, & Hardware Control
========================================================
Handles system diagnostics, weather, volume, brightness,
battery, mic health, and internet speed.
"""

import json
from agents.agent_base import BaseAgent, AgentResponse, AgentType


class SystemAgent(BaseAgent):
    name = "System Diagnostics"
    agent_type = AgentType.SYSTEM
    description = "Provides system information, weather reports, and hardware controls (volume, brightness, battery, RAM, storage, mic health)."
    capabilities = [
        "check weather", "weather report",
        "check battery", "battery percentage",
        "check RAM", "device RAM", "device storage", "available space",
        "check volume", "set volume",
        "check brightness", "set brightness",
        "check microphone", "mic health",
        "internet speed", "check internet speed"
    ]

    def __init__(self):
        super().__init__()
        self._loaded = False

    def _ensure_loaded(self):
        if self._loaded:
            return

        try:
            from Weather_check.Check__weather import get_weather_by_address
            self._get_weather = get_weather_by_address
        except ImportError:
            self._get_weather = None

        try:
            from Automation.Battery import chekc_Percentage
            self._check_battery = chekc_Percentage
        except ImportError:
            self._check_battery = None

        try:
            from Features.control_volume import get_volume_window, set_volume
            self._get_volume = get_volume_window
            self._set_volume = set_volume
        except ImportError:
            self._get_volume = None
            self._set_volume = None

        try:
            from Features.Brightness_set import check_br_persentage, set_brightness_windows
            self._check_brightness = check_br_persentage
            self._set_brightness = set_brightness_windows
        except ImportError:
            self._check_brightness = None
            self._set_brightness = None

        try:
            from Features.Mic_health import mic_health
            self._mic_health = mic_health
        except ImportError:
            self._mic_health = None

        try:
            import psutil
            self._psutil = psutil
        except ImportError:
            self._psutil = None

        self._loaded = True

    async def execute(self, query: str, context: dict | None = None) -> AgentResponse:
        """Execute a system/hardware command."""
        self._ensure_loaded()
        q = query.lower().strip()

        try:
            # ── Weather ──
            if "weather" in q:
                if self._get_weather:
                    report = await self._run_sync(self._get_weather, "Westbengal Hooghly")
                    return AgentResponse(
                        agent=AgentType.SYSTEM,
                        text=f"Here's the current weather report:\n{report}",
                        success=True,
                        action_taken="weather_check"
                    )
                return AgentResponse(agent=AgentType.SYSTEM, text="Weather module is not available.", success=False)

            # ── Battery ──
            elif "battery" in q:
                if self._psutil:
                    battery = self._psutil.sensors_battery()
                    if battery:
                        percent = battery.percent
                        plugged = "charging" if battery.power_plugged else "on battery"
                        return AgentResponse(
                            agent=AgentType.SYSTEM,
                            text=f"Battery is at {percent}%, currently {plugged}.",
                            success=True,
                            action_taken="battery_check",
                            data={"percent": percent, "plugged": battery.power_plugged}
                        )
                return AgentResponse(agent=AgentType.SYSTEM, text="Couldn't read battery status.", success=False)

            # ── RAM ──
            elif "ram" in q:
                if self._psutil:
                    ram = self._psutil.virtual_memory()
                    total = ram.total / (1024 ** 3)
                    available = ram.available / (1024 ** 3)
                    used_pct = ram.percent
                    return AgentResponse(
                        agent=AgentType.SYSTEM,
                        text=f"RAM: {total:.1f} GB total, {available:.1f} GB available ({used_pct}% used).",
                        success=True,
                        action_taken="ram_check",
                        data={"total_gb": round(total, 1), "available_gb": round(available, 1), "percent": used_pct}
                    )
                return AgentResponse(agent=AgentType.SYSTEM, text="RAM info unavailable.", success=False)

            # ── Storage ──
            elif "storage" in q or "disk" in q or "space" in q:
                if self._psutil:
                    partitions = self._psutil.disk_partitions()
                    info_lines = []
                    data_parts = []
                    for p in partitions:
                        try:
                            usage = self._psutil.disk_usage(p.mountpoint)
                            total = usage.total / (1024 ** 3)
                            free = usage.free / (1024 ** 3)
                            info_lines.append(f"Drive {p.device}: {total:.1f} GB total, {free:.1f} GB free")
                            data_parts.append({"drive": p.device, "total_gb": round(total, 1), "free_gb": round(free, 1)})
                        except PermissionError:
                            continue
                    return AgentResponse(
                        agent=AgentType.SYSTEM,
                        text="Storage overview:\n" + "\n".join(info_lines),
                        success=True,
                        action_taken="storage_check",
                        data={"partitions": data_parts}
                    )
                return AgentResponse(agent=AgentType.SYSTEM, text="Storage info unavailable.", success=False)

            # ── Volume ──
            elif "volume" in q:
                if "set" in q:
                    # Extract number from query
                    nums = [int(s) for s in q.split() if s.isdigit()]
                    if nums and self._set_volume:
                        level = min(100, max(0, nums[0]))
                        await self._run_sync(self._set_volume, level)
                        return AgentResponse(
                            agent=AgentType.SYSTEM,
                            text=f"Volume set to {level}%.",
                            success=True,
                            action_taken=f"set_volume_{level}"
                        )
                elif self._get_volume:
                    vol = await self._run_sync(self._get_volume)
                    return AgentResponse(
                        agent=AgentType.SYSTEM,
                        text=f"Current volume: {vol}",
                        success=True,
                        action_taken="check_volume"
                    )
                return AgentResponse(agent=AgentType.SYSTEM, text="Volume control is not available.", success=False)

            # ── Brightness ──
            elif "brightness" in q:
                if "set" in q:
                    nums = [int(s) for s in q.split() if s.isdigit()]
                    if nums and self._set_brightness:
                        level = min(100, max(0, nums[0]))
                        await self._run_sync(self._set_brightness, level)
                        return AgentResponse(
                            agent=AgentType.SYSTEM,
                            text=f"Brightness set to {level}%.",
                            success=True,
                            action_taken=f"set_brightness_{level}"
                        )
                elif self._check_brightness:
                    await self._run_sync(self._check_brightness)
                    return AgentResponse(
                        agent=AgentType.SYSTEM,
                        text="Brightness info displayed.",
                        success=True,
                        action_taken="check_brightness"
                    )
                return AgentResponse(agent=AgentType.SYSTEM, text="Brightness control is not available.", success=False)

            # ── Mic Health ──
            elif "mic" in q or "microphone" in q:
                if self._mic_health:
                    await self._run_sync(self._mic_health)
                    return AgentResponse(
                        agent=AgentType.SYSTEM,
                        text="Microphone health check completed.",
                        success=True,
                        action_taken="mic_health_check"
                    )
                return AgentResponse(agent=AgentType.SYSTEM, text="Mic health module not available.", success=False)

            # ── Fallback ──
            return AgentResponse(
                agent=AgentType.SYSTEM,
                text="I can check weather, battery, RAM, storage, volume, brightness, or mic health. What would you like?",
                success=True
            )

        except Exception as e:
            return AgentResponse(
                agent=AgentType.SYSTEM,
                text=f"System check encountered an error: {str(e)}",
                success=False,
                error=str(e)
            )

    async def stream_execute(self, query: str, context: dict | None = None):
        yield json.dumps({"type": "status", "agent": "system", "text": "Running diagnostics..."})
        response = await self.execute(query, context)
        yield json.dumps({
            "type": "done",
            "agent": "system",
            "text": response.text,
            "data": response.data
        })
