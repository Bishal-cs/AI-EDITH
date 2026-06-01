"""
Orchestrator Agent — The Brain of EDITH
========================================
Uses Groq LLM to classify user intent and route queries
to the appropriate specialized agent. Like JARVIS deciding
whether Tony needs combat analysis, diagnostics, or a joke.
"""

import json
from groq import Groq
from dotenv import dotenv_values
from agents.agent_base import BaseAgent, AgentResponse, AgentType
from agents.event_bus import EventBus


env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")


class OrchestratorAgent(BaseAgent):
    name = "Orchestrator"
    agent_type = AgentType.ORCHESTRATOR
    description = "Routes user queries to the best specialized agent."

    def __init__(self):
        super().__init__()
        self.client = Groq(api_key=GroqAPIKey)
        self.agents: dict[AgentType, BaseAgent] = {}
        self.event_bus = EventBus()

    def register_agent(self, agent: BaseAgent):
        """Register a specialized agent with the orchestrator."""
        self.agents[agent.agent_type] = agent
        print(f"  ✦ Registered agent: {agent.name} [{agent.agent_type.value}]")

    def get_agent(self, agent_type: AgentType) -> BaseAgent | None:
        """Get a registered agent by type."""
        return self.agents.get(agent_type)

    def _build_routing_prompt(self) -> str:
        """Build the system prompt that helps the LLM classify intent."""
        agent_descriptions = "\n".join(
            f"- **{a.agent_type.value}**: {a.description} | Capabilities: {', '.join(a.capabilities)}"
            for a in self.agents.values()
        )
        return f"""You are the Orchestrator of EDITH, an AI assistant system with multiple specialized agents.

Your ONLY job is to classify the user's intent and pick the BEST agent to handle it.

Available agents:
{agent_descriptions}

RULES:
1. Respond with ONLY valid JSON: {{"agent": "<agent_type>", "reasoning": "<brief reason>"}}
2. Pick exactly ONE agent.
3. For casual conversation, greetings, questions about yourself, emotional talk, or anything that doesn't match a specific capability → use "chat"
4. For opening/closing apps, playing music, searching, browser control, WhatsApp → use "automation"
5. For camera, image analysis, "what is this", "look at this" → use "vision"
6. For weather, battery, RAM, storage, volume, brightness, mic health, internet speed → use "system"
7. For alarms, reminders, schedules, timers → use "scheduler"
8. For writing letters, content, essays, creating files → use "content"
9. If the user says "exit" or "quit" or "goodbye" → use "chat"

Respond with ONLY the JSON object. No other text."""

    async def classify_intent(self, query: str) -> AgentType:
        """Use LLM to classify which agent should handle the query."""
        try:
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": self._build_routing_prompt()},
                    {"role": "user", "content": query}
                ],
                max_tokens=100,
                temperature=0.1,  # Low temp for consistent classification
                response_format={"type": "json_object"}
            )
            
            result = json.loads(completion.choices[0].message.content)
            agent_type_str = result.get("agent", "chat")
            reasoning = result.get("reasoning", "")

            # Publish routing event for debugging / UI display
            await self.event_bus.publish(
                __import__("agents.event_bus", fromlist=["Event"]).Event(
                    topic="routing",
                    source="orchestrator",
                    data={"query": query, "routed_to": agent_type_str, "reasoning": reasoning}
                )
            )

            try:
                return AgentType(agent_type_str)
            except ValueError:
                return AgentType.CHAT

        except Exception as e:
            print(f"[Orchestrator] Classification error: {e}")
            return AgentType.CHAT  # Fallback to chat

    async def execute(self, query: str, context: dict | None = None) -> AgentResponse:
        """Classify intent and delegate to the right agent."""
        # Step 1: Classify
        target_type = await self.classify_intent(query)
        
        # Step 2: Get the target agent
        target_agent = self.agents.get(target_type)
        if not target_agent:
            return AgentResponse(
                agent=AgentType.ORCHESTRATOR,
                text=f"I don't have a {target_type.value} agent available right now.",
                success=False,
                error=f"Agent {target_type.value} not registered"
            )

        # Step 3: Delegate
        try:
            response = await target_agent.execute(query, context)
            return response
        except Exception as e:
            return AgentResponse(
                agent=target_type,
                text=f"Something went wrong with the {target_type.value} agent: {str(e)}",
                success=False,
                error=str(e)
            )

    async def stream_execute(self, query: str, context: dict | None = None):
        """Classify and stream from the target agent."""
        target_type = await self.classify_intent(query)
        target_agent = self.agents.get(target_type)

        if not target_agent:
            yield json.dumps({
                "type": "error",
                "agent": "orchestrator",
                "text": f"No {target_type.value} agent available."
            })
            return

        # Yield routing info first
        yield json.dumps({
            "type": "routing",
            "agent": target_type.value,
            "text": f"Routing to {target_agent.name}..."
        })

        # Then stream the agent's response
        try:
            async for chunk in target_agent.stream_execute(query, context):
                yield chunk
        except Exception as e:
            yield json.dumps({
                "type": "error",
                "agent": target_type.value,
                "text": f"Error: {str(e)}"
            })

    def get_status(self) -> dict:
        """Return status of all registered agents."""
        return {
            "orchestrator": "active",
            "agents": {
                a_type.value: {
                    "name": agent.name,
                    "active": agent.is_active,
                    "capabilities": agent.capabilities
                }
                for a_type, agent in self.agents.items()
            }
        }
