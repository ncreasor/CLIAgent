"""
Simple Agent - keyword routing, no prompts bullshit
Model only for chat, Python handles all tool calls
"""

import json
import logging
import re
from typing import List, Dict, Any, Optional
import ollama

from tools.bash_tool import BashTool
from tools.file_tool import FileTool
from tools.self_modify_tool import SelfModifyTool
from tools.git_tool import GitTool


class SimpleAgent:
    """AI Agent with keyword-based tool routing"""

    def __init__(self, config: dict):
        """Initialize the agent"""
        self.config = config
        self.logger = logging.getLogger('SimpleAgent')

        # Initialize Ollama client
        self.client = ollama.Client(host=config.get('ollama_host', 'http://localhost:11434'))
        self.model = config.get('model', 'qwen3:8b')

        # Conversation history
        self.conversation_history: List[Dict] = []

        # Initialize tools
        self.tools = {
            'bash': BashTool(),
            'file': FileTool(),
            'self_modify': SelfModifyTool(),
            'git': GitTool()
        }

        # Statistics
        self.stats = {
            'requests': 0,
            'errors': 0,
            'self_improvements': 0,
            'tools_used': {}
        }

        self.logger.info(f"SimpleAgent initialized with model: {self.model}")

    def process(self, user_message: str) -> str:
        """Process user message - keyword routing to tools or chat"""
        self.stats['requests'] += 1
        self.logger.info(f"Processing: {user_message[:50]}...")

        msg_lower = user_message.lower().strip()

        # Keyword routing - detect intent and call tool directly
        if self._needs_file_list(msg_lower):
            return self._handle_file_list()

        elif self._needs_bash(msg_lower):
            command = self._extract_command(user_message)
            return self._handle_bash(command)

        elif self._needs_git(msg_lower):
            command = self._extract_git_command(user_message)
            return self._handle_git(command)

        elif self._needs_file_read(msg_lower):
            file_path = self._extract_file_path(user_message)
            return self._handle_file_read(file_path)

        else:
            # Simple chat - let model respond
            return self._chat(user_message)

    def _needs_file_list(self, msg: str) -> bool:
        """Check if user wants file list"""
        keywords = ['файлы', 'файлов', 'список файлов', 'что тут', 'покажи файл',
                   'files', 'list files', 'show files', 'what files']
        return any(kw in msg for kw in keywords)

    def _needs_bash(self, msg: str) -> bool:
        """Check if user wants to run command"""
        keywords = ['запусти', 'выполни', 'run', 'execute', 'команду']
        return any(kw in msg for kw in keywords)

    def _needs_git(self, msg: str) -> bool:
        """Check if user wants git operation"""
        return 'git' in msg

    def _needs_file_read(self, msg: str) -> bool:
        """Check if user wants to read file"""
        keywords = ['прочитай', 'покажи содержимое', 'read', 'show content', 'cat']
        return any(kw in msg for kw in keywords)

    def _extract_command(self, msg: str) -> str:
        """Extract command from message"""
        # Try to find command after keywords
        patterns = [
            r'запусти\s+(.+)',
            r'выполни\s+(.+)',
            r'run\s+(.+)',
            r'execute\s+(.+)'
        ]
        for pattern in patterns:
            match = re.search(pattern, msg, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        # Default - maybe entire message is command?
        return msg.strip()

    def _extract_git_command(self, msg: str) -> str:
        """Extract git subcommand"""
        # Remove "git" and get the rest
        match = re.search(r'git\s+(.+)', msg, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        return "status"  # default

    def _extract_file_path(self, msg: str) -> str:
        """Extract file path from message"""
        # Look for paths
        match = re.search(r'[\'"]?([a-zA-Z0-9_./-]+\.[a-zA-Z]+)[\'"]?', msg)
        if match:
            return match.group(1)
        return "README.md"  # default

    def _handle_file_list(self) -> str:
        """List files in current directory"""
        print("\n[file list] ", end="", flush=True)
        try:
            result = self.tools['file'].execute({"action": "list", "directory": "."})
            self.stats['tools_used']['file'] = self.stats['tools_used'].get('file', 0) + 1
            print("✓\n")

            # Show result to model for summary
            summary = self._chat_with_context(
                f"Пользователь спросил про файлы. Вот список файлов:\n{result}\n\nОпиши коротко структуру (3-5 пунктов, без эмодзи)"
            )
            return summary
        except Exception as e:
            print(f"✗\n")
            return f"Ошибка: {e}"

    def _handle_bash(self, command: str) -> str:
        """Execute bash command"""
        print(f"\n[bash: {command}] ", end="", flush=True)
        try:
            result = self.tools['bash'].execute({"command": command})
            self.stats['tools_used']['bash'] = self.stats['tools_used'].get('bash', 0) + 1
            print("✓\n")
            print(f"{result}\n")
            return ""
        except Exception as e:
            print(f"✗\n")
            return f"Ошибка: {e}"

    def _handle_git(self, git_command: str) -> str:
        """Execute git command"""
        print(f"\n[git {git_command}] ", end="", flush=True)
        try:
            result = self.tools['git'].execute({"command": git_command})
            self.stats['tools_used']['git'] = self.stats['tools_used'].get('git', 0) + 1
            print("✓\n")
            print(f"{result}\n")
            return ""
        except Exception as e:
            print(f"✗\n")
            return f"Ошибка: {e}"

    def _handle_file_read(self, file_path: str) -> str:
        """Read file contents"""
        print(f"\n[read {file_path}] ", end="", flush=True)
        try:
            result = self.tools['file'].execute({"action": "read", "file_path": file_path})
            self.stats['tools_used']['file'] = self.stats['tools_used'].get('file', 0) + 1
            print("✓\n")

            # Truncate if too long
            if len(result) > 500:
                print(f"{result[:500]}...\n(truncated)\n")
            else:
                print(f"{result}\n")
            return ""
        except Exception as e:
            print(f"✗\n")
            return f"Ошибка: {e}"

    def _chat(self, message: str) -> str:
        """Simple chat without tools"""
        self.conversation_history.append({
            "role": "user",
            "content": message
        })

        print("Думаю... ", end="", flush=True)

        response_text = self._call_model_streaming()

        self.conversation_history.append({
            "role": "assistant",
            "content": response_text
        })

        return ""

    def _chat_with_context(self, message: str) -> str:
        """Chat with specific context (no history)"""
        messages = [
            {"role": "system", "content": "Ты AutoCLI - AI агент для кода. Отвечай кратко, без эмодзи."},
            {"role": "user", "content": message}
        ]

        try:
            response = self.client.chat(
                model=self.model,
                messages=messages,
                stream=False,
                options={"temperature": 0.7, "num_predict": 256}
            )
            return response['message']['content'].strip()
        except Exception as e:
            self.logger.error(f"Chat error: {e}")
            return ""

    def _call_model_streaming(self) -> str:
        """Call model with streaming"""
        messages = [
            {"role": "system", "content": "Ты AutoCLI - AI агент для кода. Отвечай кратко, без эмодзи."}
        ] + self.conversation_history

        try:
            stream = self.client.chat(
                model=self.model,
                messages=messages,
                stream=True,
                options={"temperature": 0.7, "num_predict": 256}
            )

            full_text = ""
            first = True

            for chunk in stream:
                if 'message' in chunk and 'content' in chunk['message']:
                    piece = chunk['message']['content']
                    if piece:
                        if first:
                            print("\r" + " " * 50 + "\r", end="", flush=True)
                            first = False
                        print(piece, end="", flush=True)
                        full_text += piece

            print("\n")
            return full_text

        except Exception as e:
            self.logger.error(f"Streaming error: {e}")
            return f"Ошибка: {e}"

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        self.logger.info("History cleared")

    def print_status(self):
        """Print agent status"""
        print("\n=== Agent Status ===")
        print(f"Model: {self.model}")
        print(f"Requests: {self.stats['requests']}")
        print(f"Errors: {self.stats['errors']}")
        print(f"\nTools used:")
        for tool, count in self.stats['tools_used'].items():
            print(f"  {tool}: {count}")
        print(f"\nHistory length: {len(self.conversation_history)} messages")

    def self_improve(self):
        """Trigger self-improvement"""
        self.logger.info("Self-improvement triggered")
        prompt = "Проанализируй свой код и предложи улучшения."
        self.stats['self_improvements'] += 1
        return self._chat(prompt)

    def self_improve_on_error(self, error_message: str):
        """Self-improve based on error"""
        self.logger.info(f"Self-improving on error: {error_message}")
        prompt = f"Произошла ошибка: {error_message}\nПроанализируй и предложи исправление."
        self.stats['self_improvements'] += 1
        return self._chat(prompt)
