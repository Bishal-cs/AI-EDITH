"""
Automation Agent — App/Web/Media Control
==========================================
Handles opening/closing apps, browser control, music playback,
Google search, WhatsApp, and scroll/playback controls.
Wraps all existing Automation/ and Features/ modules.
"""

import json
import threading
import asyncio
from agents.agent_base import BaseAgent, AgentResponse, AgentType


class AutomationAgent(BaseAgent):
    name = "Automation Control"
    agent_type = AgentType.AUTOMATION
    description = "Controls applications, browser, music playback, Google search, WhatsApp messaging, and system actions like sleep."
    capabilities = [
        "open application", "close application",
        "play music on youtube", "play music on spotify",
        "search google", "search in browser",
        "browser tab control", "scroll up/down",
        "video playback control (pause/play/next/previous)",
        "send whatsapp message",
        "stop/resume media", "sleep/shutdown device"
    ]

    def __init__(self):
        super().__init__()
        # Lazy-load heavy modules to avoid import-time side effects
        self._loaded = False

    def _ensure_loaded(self):
        """Lazy-load automation modules on first use."""
        if self._loaded:
            return
        try:
            from Automation.open_app import open_app, close_app
            self._open_app = open_app
            self._close_app = close_app
        except ImportError:
            self._open_app = None
            self._close_app = None

        try:
            from Automation.play_music_yt import play_music_youtube
            self._play_yt = play_music_youtube
        except ImportError:
            self._play_yt = None

        try:
            from Automation.play_music_soprtify import play_music_on_spotify
            self._play_spotify = play_music_on_spotify
        except ImportError:
            self._play_spotify = None

        try:
            from Automation.tab_automation import perform_browser_action
            self._browser_action = perform_browser_action
        except ImportError:
            self._browser_action = None

        try:
            from Automation.youtube_playback import perform_video_control
            self._video_control = perform_video_control
        except ImportError:
            self._video_control = None

        try:
            from Automation.scroll_system import perform_scroll_action
            self._scroll_action = perform_scroll_action
        except ImportError:
            self._scroll_action = None

        try:
            from Automation.web_open import open_website
            self._open_website = open_website
        except ImportError:
            self._open_website = None

        try:
            from Whatsapp_automation.wa import send_msg_wa
            self._send_wa = send_msg_wa
        except ImportError:
            self._send_wa = None

        self._loaded = True

    async def execute(self, query: str, context: dict | None = None) -> AgentResponse:
        """Execute an automation command."""
        self._ensure_loaded()
        query_lower = query.lower().strip()

        try:
            # ── Open App ──
            if query_lower.startswith("open"):
                app_name = query_lower.replace("open", "").strip()
                if self._open_app:
                    await self._run_sync(self._open_app, app_name)
                    return AgentResponse(
                        agent=AgentType.AUTOMATION,
                        text=f"Right away. Launching {app_name} for you.",
                        action_taken=f"opened {app_name}",
                        success=True
                    )

            # ── Close App ──
            elif query_lower.startswith("close"):
                app_name = query_lower.replace("close", "").strip()
                if self._close_app:
                    await self._run_sync(self._close_app, app_name)
                    return AgentResponse(
                        agent=AgentType.AUTOMATION,
                        text=f"Done. {app_name.title()} has been closed.",
                        action_taken=f"closed {app_name}",
                        success=True
                    )

            # ── Play Music YouTube ──
            elif "play" in query_lower and ("youtube" in query_lower or "music" in query_lower):
                if "spotify" in query_lower and self._play_spotify:
                    song = query_lower.replace("play", "").replace("on spotify", "").replace("music", "").strip()
                    await self._run_sync(self._play_spotify, song if song else query_lower)
                    return AgentResponse(
                        agent=AgentType.AUTOMATION,
                        text=f"Playing on Spotify. Enjoy the music.",
                        action_taken="play_spotify",
                        success=True
                    )
                elif self._play_yt:
                    song = query_lower.replace("play", "").replace("on youtube", "").replace("music", "").strip()
                    await self._run_sync(self._play_yt, song if song else query_lower)
                    return AgentResponse(
                        agent=AgentType.AUTOMATION,
                        text=f"Playing on YouTube. Sit back and enjoy.",
                        action_taken="play_youtube",
                        success=True
                    )

            # ── Google Search ──
            elif "search" in query_lower:
                import pywhatkit
                search_term = query_lower.replace("search in google", "").replace("search", "").strip()
                if search_term:
                    await self._run_sync(pywhatkit.search, search_term)
                    return AgentResponse(
                        agent=AgentType.AUTOMATION,
                        text=f"Here's what I found on '{search_term}'.",
                        action_taken=f"searched '{search_term}'",
                        success=True
                    )

            # ── WhatsApp ──
            elif "whatsapp" in query_lower and self._send_wa:
                await self._run_sync(self._send_wa)
                return AgentResponse(
                    agent=AgentType.AUTOMATION,
                    text="WhatsApp message has been sent.",
                    action_taken="sent whatsapp message",
                    success=True
                )

            # ── Stop/Resume Media ──
            elif "stop" in query_lower or "resume" in query_lower or "pause" in query_lower:
                import pyautogui
                await self._run_sync(pyautogui.press, "space")
                return AgentResponse(
                    agent=AgentType.AUTOMATION,
                    text="Toggled playback.",
                    action_taken="toggle_playback",
                    success=True
                )

            # ── Sleep Mode ──
            elif "sleep" in query_lower:
                import pyautogui, time
                await self._run_sync(pyautogui.hotkey, 'win', 'x')
                await asyncio.sleep(0.3)
                await self._run_sync(pyautogui.press, 'u')
                await asyncio.sleep(1)
                await self._run_sync(pyautogui.press, 's')
                return AgentResponse(
                    agent=AgentType.AUTOMATION,
                    text="Putting the system to sleep. Goodnight.",
                    action_taken="sleep_mode",
                    success=True
                )

            # ── Browser / Video / Scroll fallback ──
            else:
                actions_taken = []
                if self._browser_action:
                    await self._run_sync(self._browser_action, query_lower)
                    actions_taken.append("browser")
                if self._video_control:
                    await self._run_sync(self._video_control, query_lower)
                    actions_taken.append("video")
                if self._scroll_action:
                    await self._run_sync(self._scroll_action, query_lower)
                    actions_taken.append("scroll")

                if actions_taken:
                    return AgentResponse(
                        agent=AgentType.AUTOMATION,
                        text="Done. Action executed.",
                        action_taken=", ".join(actions_taken),
                        success=True
                    )

            return AgentResponse(
                agent=AgentType.AUTOMATION,
                text="I understood you want an automation action, but I couldn't match the specific command. Could you rephrase?",
                success=False
            )

        except Exception as e:
            return AgentResponse(
                agent=AgentType.AUTOMATION,
                text=f"I ran into an issue executing that: {str(e)}",
                success=False,
                error=str(e)
            )

    async def stream_execute(self, query: str, context: dict | None = None):
        """Automation actions are instant — wrap execute()."""
        yield json.dumps({"type": "status", "agent": "automation", "text": "Executing action..."})
        response = await self.execute(query, context)
        yield json.dumps({
            "type": "done",
            "agent": "automation",
            "text": response.text,
            "action_taken": response.action_taken
        })
