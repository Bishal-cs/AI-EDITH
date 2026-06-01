"""
Content Agent — Writing & File Creation
=========================================
Generates content (letters, essays, articles) using LLM
and creates files with proper extensions.
"""

import os
import json
import subprocess
from groq import Groq
from dotenv import dotenv_values
from agents.agent_base import BaseAgent, AgentResponse, AgentType

env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")
Username = env_vars.get("Username", "User")


class ContentAgent(BaseAgent):
    name = "Content Creator"
    agent_type = AgentType.CONTENT
    description = "Writes content (letters, essays, articles, code) using AI and creates files with proper extensions."
    capabilities = [
        "write content", "write a letter", "write an essay",
        "write an article", "write code",
        "create file", "create python file", "create text file",
        "create html file", "create java file", "create json file"
    ]

    # File extension mapping
    EXTENSION_MAP = {
        "python": ".py", "java": ".java", "text": ".txt",
        "html": ".html", "css": ".css", "javascript": ".js",
        "json": ".json", "xml": ".xml", "csv": ".csv",
        "markdown": ".md", "yaml": ".yaml", "image": ".jpg",
        "video": ".mp4", "audio": ".mp3", "pdf": ".pdf",
        "word": ".docx", "excel": ".xlsx", "powerpoint": ".pptx",
        "zip": ".zip", "tar": ".tar",
    }

    def __init__(self):
        super().__init__()
        self.client = Groq(api_key=GroqAPIKey)
        self.system_prompt = [{
            "role": "system",
            "content": f"You are a professional content writer assisting {Username}. "
                       f"Write clear, well-structured content as requested. "
                       f"For letters, use proper formatting. For code, use proper syntax."
        }]

    def _get_extension(self, text: str) -> str:
        """Determine file extension from the query text."""
        text_lower = text.lower()
        for keyword, ext in self.EXTENSION_MAP.items():
            if f"{keyword} file" in text_lower:
                return ext
        return ".txt"

    def _extract_filename(self, text: str) -> str:
        """Extract filename from query or generate a default."""
        text_lower = text.lower()
        # Remove known keywords
        for keyword in ["create", "file", "named", "with name"] + list(self.EXTENSION_MAP.keys()):
            text_lower = text_lower.replace(keyword, "")
        name = text_lower.strip().replace(" ", "_")
        return name if name else "output"

    async def _generate_content(self, topic: str) -> str:
        """Use Groq LLM to generate content."""
        try:
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=self.system_prompt + [
                    {"role": "user", "content": topic}
                ],
                max_tokens=2048,
                temperature=0.7,
                stream=True,
            )

            answer = ""
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    answer += chunk.choices[0].delta.content

            return answer.replace("</s>", "")
        except Exception as e:
            return f"Error generating content: {str(e)}"

    async def execute(self, query: str, context: dict | None = None) -> AgentResponse:
        """Handle content writing or file creation."""
        q = query.lower().strip()

        try:
            # ── Content Writing ──
            if "write" in q:
                topic = q.replace("write a content", "").replace("write content", "")
                topic = topic.replace("write a ", "").replace("write ", "").strip()

                if not topic:
                    return AgentResponse(
                        agent=AgentType.CONTENT,
                        text="What would you like me to write about?",
                        success=True
                    )

                content = await self._generate_content(topic)
                
                # Save to file
                safe_name = topic.lower().replace(" ", "_")[:30]
                file_path = os.path.join("user_data", f"{safe_name}.txt")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                # Open in notepad
                try:
                    subprocess.Popen(["notepad.exe", file_path])
                except Exception:
                    pass

                return AgentResponse(
                    agent=AgentType.CONTENT,
                    text=f"I've written the content about '{topic}' and opened it for you. Here's a preview:\n\n{content[:300]}...",
                    success=True,
                    action_taken=f"wrote content about '{topic}'",
                    data={"file_path": file_path, "preview": content[:500]}
                )

            # ── File Creation ──
            elif "create" in q:
                ext = self._get_extension(q)
                name = self._extract_filename(q)
                filename = f"{name}{ext}"
                
                with open(filename, "w") as f:
                    pass  # Create empty file

                return AgentResponse(
                    agent=AgentType.CONTENT,
                    text=f"File '{filename}' has been created.",
                    success=True,
                    action_taken=f"created file '{filename}'"
                )

            return AgentResponse(
                agent=AgentType.CONTENT,
                text="I can write content (letters, essays, articles) or create files. What do you need?",
                success=True
            )

        except Exception as e:
            return AgentResponse(
                agent=AgentType.CONTENT,
                text=f"Content creation error: {str(e)}",
                success=False,
                error=str(e)
            )

    async def stream_execute(self, query: str, context: dict | None = None):
        """Stream content generation with progress updates."""
        q = query.lower().strip()

        if "write" in q:
            topic = q.replace("write a content", "").replace("write content", "")
            topic = topic.replace("write a ", "").replace("write ", "").strip()

            yield json.dumps({"type": "status", "agent": "content", "text": f"Composing content about '{topic}'..."})

            # Generate with streaming
            try:
                completion = self.client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=self.system_prompt + [
                        {"role": "user", "content": topic if topic else query}
                    ],
                    max_tokens=2048,
                    temperature=0.7,
                    stream=True,
                )

                full_content = ""
                for chunk in completion:
                    token = chunk.choices[0].delta.content
                    if token:
                        full_content += token
                        yield json.dumps({
                            "type": "token",
                            "agent": "content",
                            "text": token
                        })

                # Save file
                safe_name = (topic or "content").lower().replace(" ", "_")[:30]
                file_path = os.path.join("user_data", f"{safe_name}.txt")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(full_content)

                try:
                    subprocess.Popen(["notepad.exe", file_path])
                except Exception:
                    pass

                yield json.dumps({
                    "type": "done",
                    "agent": "content",
                    "text": full_content,
                    "action_taken": f"wrote and saved to {file_path}"
                })

            except Exception as e:
                yield json.dumps({
                    "type": "error",
                    "agent": "content",
                    "text": f"Error: {str(e)}"
                })
        else:
            response = await self.execute(query, context)
            yield json.dumps({
                "type": "done",
                "agent": "content",
                "text": response.text
            })
