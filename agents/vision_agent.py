"""
Vision Agent — Camera & Image Analysis
========================================
Captures images from the webcam and analyzes them
using the DeepInfra vision API.
"""

import json
from agents.agent_base import BaseAgent, AgentResponse, AgentType


class VisionAgent(BaseAgent):
    name = "Vision Analysis"
    agent_type = AgentType.VISION
    description = "Captures images from the webcam camera and analyzes them using AI vision models."
    capabilities = [
        "capture image from camera", "analyze what camera sees",
        "identify objects", "read text from images",
        "what is this", "look at this", "tell me about this",
        "describe what you see"
    ]

    def __init__(self):
        super().__init__()
        self._loaded = False

    def _ensure_loaded(self):
        if self._loaded:
            return
        try:
            from Vision.PC_Cam import capture_image_and_save, encode_image_to_base64, Vbrain
            self._capture = capture_image_and_save
            self._encode = encode_image_to_base64
            self._vbrain = Vbrain
        except ImportError as e:
            print(f"[VisionAgent] Failed to load vision modules: {e}")
            self._capture = None
            self._encode = None
            self._vbrain = None
        self._loaded = True

    async def execute(self, query: str, context: dict | None = None) -> AgentResponse:
        """Capture an image and analyze it."""
        self._ensure_loaded()

        if not self._capture or not self._vbrain:
            return AgentResponse(
                agent=AgentType.VISION,
                text="Vision modules aren't available right now. Camera might not be connected.",
                success=False,
                error="Vision modules not loaded"
            )

        try:
            image_path = "user_data/captured_image.png"

            # Capture image
            success = await self._run_sync(self._capture, image_path)
            if not success:
                return AgentResponse(
                    agent=AgentType.VISION,
                    text="I couldn't capture an image. Please check if your camera is connected.",
                    success=False,
                    error="Camera capture failed"
                )

            # Encode and analyze
            encoded = await self._run_sync(self._encode, image_path)
            analysis = await self._run_sync(self._vbrain, encoded)

            if analysis:
                return AgentResponse(
                    agent=AgentType.VISION,
                    text=analysis,
                    success=True,
                    action_taken="captured and analyzed image",
                    data={"image_path": image_path}
                )
            else:
                return AgentResponse(
                    agent=AgentType.VISION,
                    text="I captured the image but couldn't analyze it. The vision API might be unavailable.",
                    success=False,
                    error="Vision API returned None"
                )

        except Exception as e:
            return AgentResponse(
                agent=AgentType.VISION,
                text=f"Something went wrong with the vision system: {str(e)}",
                success=False,
                error=str(e)
            )

    async def stream_execute(self, query: str, context: dict | None = None):
        """Vision is capture + analyze — show status updates."""
        yield json.dumps({"type": "status", "agent": "vision", "text": "📷 Activating camera..."})
        yield json.dumps({"type": "status", "agent": "vision", "text": "🔍 Analyzing image..."})
        response = await self.execute(query, context)
        yield json.dumps({
            "type": "done",
            "agent": "vision",
            "text": response.text,
            "action_taken": response.action_taken
        })
