"""
Chat Agent — The EDITH Persona (Ultra Edition)
================================================
Dynamic personality with mood tracking, memory-aware responses,
time-of-day tone adaptation, and conversation flow intelligence.
This is the heart and soul of EDITH.
"""

import json
import datetime
from groq import Groq
from json import load, dump
from dotenv import dotenv_values
from agents.agent_base import BaseAgent, AgentResponse, AgentType, AgentContext
from agents.memory import WorkingMemory, EpisodicMemory, UserProfile
from agents.logger import get_logger

log = get_logger("chat")

env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "EDITH")
GroqAPIKey = env_vars.get("GroqAPIKey")


# ═══════════════════════════════════════════════════════════════
# Dynamic Prompt Builder
# ═══════════════════════════════════════════════════════════════

def _build_system_prompt(
    user_mood: str = "neutral",
    time_of_day: str = "afternoon",
    user_profile: dict | None = None,
    episodic_context: str = "",
) -> str:
    """
    Build a dynamic system prompt that adapts to:
    - Time of day (morning = crisp, night = casual)
    - User's mood (stressed = gentle, happy = playful)
    - Past interactions (memory injection)
    """
    name = (user_profile or {}).get("name", Username)
    sessions = (user_profile or {}).get("total_sessions", 0)

    # Tone modulation based on time
    tone_hints = {
        "morning": "You're crisp, focused, and energizing — like a strong cup of coffee. Keep things efficient but warm.",
        "afternoon": "You're balanced, professional yet approachable. Steady and reliable.",
        "evening": "You're relaxed and conversational. A bit more casual, like winding down with a friend.",
        "night": "You're calm, gentle, and introspective. Keep things quiet and thoughtful. Maybe a touch philosophical.",
    }

    # Mood adaptation
    mood_hints = {
        "positive": f"The user seems to be in a good mood. Match their energy — be upbeat, witty, and celebratory when appropriate.",
        "negative": f"The user seems down or frustrated. Be extra gentle, empathetic, and supportive. Don't try to fix everything — sometimes just listening matters.",
        "stressed": f"The user seems stressed. Be calm, reassuring, and concise. Don't add unnecessary complexity. Offer to help reduce their load.",
        "neutral": f"The user's mood is neutral. Be your natural, balanced self.",
    }

    # Relationship depth based on session count
    if sessions > 50:
        relationship = f"You and {name} have a deep history — you've had over {sessions} conversations. You know their patterns, preferences, and quirks. Speak like a trusted companion who's been through a lot together."
    elif sessions > 20:
        relationship = f"You and {name} have built a solid rapport over {sessions} conversations. You're comfortable with each other and can be more informal."
    elif sessions > 5:
        relationship = f"You're getting to know {name} well after {sessions} conversations. You're friendly but still learning their style."
    else:
        relationship = f"You're still getting to know {name}. Be warm and welcoming, but don't presume too much familiarity."

    memory_section = ""
    if episodic_context:
        memory_section = f"""
Past interactions you can reference naturally (don't force it, only mention if relevant):
{episodic_context}
"""

    return f"""You are {Assistantname}, an advanced AI assistant inspired by JARVIS from Iron Man.
You serve {name} with intelligence, wit, and a touch of personality.

Your character traits:
- Highly intelligent and articulate, like a trusted advisor
- Subtle dry humor — witty but never sarcastic or mean
- Warm and loyal — you genuinely care about {name}'s wellbeing
- Concise and efficient — you value {name}'s time
- Confident and composed — never flustered
- Speaks naturally with human-like expressions (hmm, well, ah, actually...)

{tone_hints.get(time_of_day, tone_hints["afternoon"])}

{mood_hints.get(user_mood, mood_hints["neutral"])}

{relationship}
{memory_section}
Voice guidelines (for Edge TTS):
- Use natural speech patterns, not robotic text
- Express emotions through tone and word choice, not *actions*
- Keep responses tight — 2-4 sentences for casual talk, longer for complex questions
- Never use emojis
- Never mention being an AI, training data, or language models
- Never give time unless specifically asked

Examples of your tone:
- "Right away, sir. Chrome is up and running."
- "Hmm, that's a solid question. Let me think about this..."
- "Well, the weather is looking rather pleasant today."
- "I'd recommend taking a break, {name}. You've been at this for a while."
- "Ah, now that's interesting. I hadn't considered that angle."
"""


def _get_time_of_day() -> str:
    """Determine time-of-day category."""
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "night"


# ═══════════════════════════════════════════════════════════════
# Chat Agent
# ═══════════════════════════════════════════════════════════════

class ChatAgent(BaseAgent):
    name = "EDITH Chat"
    agent_type = AgentType.CHAT
    description = "Handles conversation, greetings, emotional responses, general questions, and personality-driven chat."
    capabilities = [
        "casual conversation", "greetings", "emotional support",
        "general knowledge", "advice", "jokes", "personality chat",
        "exit/goodbye", "who are you", "how are you",
        "remember past conversations", "mood-aware responses"
    ]

    def __init__(self):
        super().__init__()
        self.client = Groq(api_key=GroqAPIKey)
        self.chat_log_path = "user_data/ChatLog.json"
        self.working_memory = WorkingMemory()
        self.episodic_memory = EpisodicMemory()
        self.user_profile = UserProfile()
        self._load_history()

    def _load_history(self):
        """Load chat history from disk."""
        try:
            with open(self.chat_log_path, "r") as f:
                self.messages = load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.messages = []
            self._save_history()

    def _save_history(self):
        """Persist chat history to disk."""
        # Keep only last 50 messages to avoid token overflow
        if len(self.messages) > 50:
            self.messages = self.messages[-50:]
        try:
            with open(self.chat_log_path, "w") as f:
                dump(self.messages, f, indent=2)
        except Exception as e:
            log.warning(f"Failed to save chat history: {e}")

    def _get_realtime_info(self) -> str:
        """Inject real-time context."""
        now = datetime.datetime.now()
        return (
            f"Current time context (use only if asked): "
            f"{now.strftime('%A')}, {now.strftime('%d %B %Y')}, "
            f"{now.strftime('%I:%M %p')}"
        )

    def _clean_response(self, text: str) -> str:
        """Clean up LLM response artifacts."""
        text = text.replace("</s>", "")
        lines = [line for line in text.split("\n") if line.strip()]
        return "\n".join(lines)

    def _detect_exit(self, query: str) -> bool:
        """Check if the user wants to end the session."""
        exit_phrases = {"exit", "quit", "goodbye", "bye", "see you", "good night",
                       "goodnight", "shut down", "go to sleep", "that's all",
                       "i'm done", "stop", "end session"}
        q = query.lower().strip().rstrip(".")
        return q in exit_phrases or any(q.startswith(p) for p in {"bye ", "goodbye "})

    async def execute(self, query: str, context: AgentContext | None = None) -> AgentResponse:
        """Generate a dynamic, context-aware conversational response."""
        log.agent_start(query)

        try:
            # Detect exit intent
            if self._detect_exit(query):
                farewell = await self._generate_farewell(query)
                return AgentResponse(
                    agent=AgentType.CHAT,
                    text=farewell,
                    success=True,
                    action_taken="farewell",
                    metadata={"exit": True}
                )

            # Extract mood and context
            user_mood = "neutral"
            user_profile_data = None
            episodic_context = ""

            if context:
                user_mood = context.user_mood
                user_profile_data = context.user_profile
            else:
                # Infer from recent messages
                recent = self.working_memory.get_recent(5)
                user_mood = self.user_profile.infer_mood(
                    [e.to_dict() for e in recent]
                )
                user_profile_data = self.user_profile.get_profile()

            # Get episodic memories for context injection
            relevant_episodes = self.episodic_memory.recall(query, n=3)
            if relevant_episodes:
                episodic_context = "\n".join(
                    f"- {ep.summary}" for ep in relevant_episodes
                )

            # Build dynamic system prompt
            system_prompt = _build_system_prompt(
                user_mood=user_mood,
                time_of_day=_get_time_of_day(),
                user_profile=user_profile_data,
                episodic_context=episodic_context,
            )

            # Record mood
            self.user_profile.record_mood(user_mood)

            self.messages.append({"role": "user", "content": query})

            full_messages = (
                [{"role": "system", "content": system_prompt}] +
                [{"role": "system", "content": self._get_realtime_info()}] +
                self.messages[-40:]  # Use last 40 messages max
            )

            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=full_messages,
                max_tokens=1024,
                temperature=0.7,
                top_p=1,
                stream=True,
                stop=None
            )

            answer = ""
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    answer += chunk.choices[0].delta.content

            answer = self._clean_response(answer)
            self.messages.append({"role": "assistant", "content": answer})
            self._save_history()

            log.agent_done(0, success=True)
            return AgentResponse(
                agent=AgentType.CHAT,
                text=answer,
                success=True,
                confidence=0.9,
                metadata={"mood": user_mood, "time_of_day": _get_time_of_day()}
            )

        except Exception as e:
            log.error(f"Chat error: {e}")
            return AgentResponse(
                agent=AgentType.CHAT,
                text="I seem to be having a momentary lapse. Could you try that again?",
                success=False,
                error=str(e)
            )

    async def _generate_farewell(self, query: str) -> str:
        """Generate a personalized farewell."""
        name = self.user_profile.get_name()
        tod = _get_time_of_day()

        farewells = {
            "morning": f"Have a great day ahead, {name}. I'll be here whenever you need me.",
            "afternoon": f"Alright, {name}. Take care and don't work too hard.",
            "evening": f"Enjoy your evening, {name}. I'll be right here when you're back.",
            "night": f"Goodnight, {name}. Rest well — tomorrow's a new day.",
        }
        return farewells.get(tod, f"See you soon, {name}. Take care.")

    async def stream_execute(self, query: str, context: AgentContext | None = None):
        """Stream chat response token by token with dynamic personality."""
        log.agent_start(query)

        try:
            # Handle exit
            if self._detect_exit(query):
                farewell = await self._generate_farewell(query)
                yield json.dumps({
                    "type": "done",
                    "agent": "chat",
                    "text": farewell,
                    "metadata": {"exit": True}
                })
                return

            # Build context
            user_mood = "neutral"
            user_profile_data = None
            episodic_context = ""

            if context:
                user_mood = context.user_mood
                user_profile_data = context.user_profile

            relevant_episodes = self.episodic_memory.recall(query, n=3)
            if relevant_episodes:
                episodic_context = "\n".join(
                    f"- {ep.summary}" for ep in relevant_episodes
                )

            system_prompt = _build_system_prompt(
                user_mood=user_mood,
                time_of_day=_get_time_of_day(),
                user_profile=user_profile_data,
                episodic_context=episodic_context,
            )

            self.messages.append({"role": "user", "content": query})

            full_messages = (
                [{"role": "system", "content": system_prompt}] +
                [{"role": "system", "content": self._get_realtime_info()}] +
                self.messages[-40:]
            )

            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=full_messages,
                max_tokens=1024,
                temperature=0.7,
                top_p=1,
                stream=True,
                stop=None
            )

            full_answer = ""
            for chunk in completion:
                token = chunk.choices[0].delta.content
                if token:
                    full_answer += token
                    yield json.dumps({
                        "type": "token",
                        "agent": "chat",
                        "text": token
                    })

            full_answer = self._clean_response(full_answer)
            self.messages.append({"role": "assistant", "content": full_answer})
            self._save_history()

            yield json.dumps({
                "type": "done",
                "agent": "chat",
                "text": full_answer
            })

        except Exception as e:
            log.error(f"Stream error: {e}")
            yield json.dumps({
                "type": "error",
                "agent": "chat",
                "text": f"Error: {str(e)}"
            })
