import sys
import os
import json
import asyncio
import logging
import httpx
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

# Configuració de logs
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("SEBASTIAN-Gateway")


class Settings(BaseSettings):
    OPENROUTER_API_KEY: str
    TELEGRAM_BOT_TOKEN: str = "PENDING"
    TELEGRAM_ALLOWED_USERS: str = "[]"
    SANDBOX_MODE: str = "off"
    GATEWAY_PORT: int = 18789
    WORKSPACE_PATH: str = "./workspace"
    MAX_ITERATIONS: int = 30
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


try:
    settings = Settings()
except Exception as e:
    logger.error(f"Error carregant configuració: {e}")
    sys.exit(1)


class ToolExecutor:
    def __init__(self):
        self.tools_path = "tools"

    def get_available_tools(self) -> List[Dict[str, Any]]:
        tools = []
        for file in os.listdir(self.tools_path):
            if file.endswith(".json"):
                with open(
                    os.path.join(self.tools_path, file), "r", encoding="utf-8"
                ) as f:
                    tools.append(json.load(f))
        return tools

    async def execute(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        tool_json_path = os.path.join(self.tools_path, f"{tool_name}.json")
        if not os.path.exists(tool_json_path):
            return f"Error: Eina {tool_name} no trobada."

        with open(tool_json_path, "r", encoding="utf-8") as f:
            tool_def = json.load(f)

        entry_point = tool_def["entry_point"]
        args_str = json.dumps(arguments)

        # Obrim el procés i configurem stdin per enviar les dades sense corrupció de caràcters
        process = await asyncio.create_subprocess_exec(
            "python3",
            entry_point,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate(input=args_str.encode())

        if stderr:
            logger.error(f"Error executant {tool_name}: {stderr.decode()}")

        return stdout.decode().strip()


class ReActLoop:
    def __init__(self, llm_client, executor):
        self.llm_client = llm_client
        self.executor = executor
        self.max_iterations = settings.MAX_ITERATIONS

    async def run(self, messages: List[Dict[str, str]], model: str) -> Dict[str, Any]:
        tools = self.executor.get_available_tools()
        tools_desc = "\nEines disponibles:\n" + json.dumps(tools, indent=2)

        messages[0]["content"] += tools_desc
        messages[0][
            "content"
        ] += '\nSi vols usar una eina, respon amb: TOOL_CALL: {"name": "nom", "arguments": {...}}'

        for i in range(self.max_iterations):
            logger.info(f"Iteració ReAct {i+1}/{self.max_iterations}...")
            response = await self.llm_client.get_completion(messages, model)
            content = response.get("content", "")
            
            if "TOOL_CALL:" in content:
                try:
                    import re
                    # Busquem el primer JSON dins del text des de TOOL_CALL:
                    json_match = re.search(r"TOOL_CALL:\s*(\{.*\})", content, re.DOTALL)
                    if not json_match:
                        raise ValueError("No s'ha trobat un format JSON vàlid després de TOOL_CALL:")
                    
                    json_str = json_match.group(1).strip()
                    tool_call = json.loads(json_str)
                    
                    logger.info(f"Executant eina: {tool_call['name']}")
                    result = await self.executor.execute(tool_call["name"], tool_call["arguments"])
                    
                    messages.append(response)
                    messages.append({"role": "user", "content": f"RESULTAT DE L'EINA: {result}"})
                except Exception as e:
                    logger.error(f"Error parsejant o executant eina: {e}")
                    messages.append(response)
                    messages.append({"role": "user", "content": f"ERROR: {str(e)} (Assegura't de tancar el JSON correctament)"})
            else:
                return response

        return {
            "role": "assistant",
            "content": "He superat el límit d'iteracions de ReAct.",
        }


class ContextAssembler:
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
        self.system_files = [
            "SOUL.md",
            "AGENTS.md",
            "IDENTITY.md",
            "USER.md",
            "TOOLS.md",
            "MEMORY.md",
        ]

    async def assemble(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        system_prompt = ""
        for file_name in self.system_files:
            file_path = os.path.join(self.workspace_path, file_name)
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    system_prompt += f"--- {file_name} ---\n{f.read()}\n\n"
        return [{"role": "system", "content": system_prompt}] + messages


class LLMClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"

    async def get_completion(
        self, messages: List[Dict[str, str]], model: str
    ) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/bielalzina/SEBASTIAN",
            "X-Title": "SEBASTIAN Agent",
            "Content-Type": "application/json",
        }
        payload = {"model": model, "messages": messages, "max_tokens": 4000}
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]


class SebastianGateway:
    def __init__(self):
        self.sessions = {}
        self.context_assembler = ContextAssembler(settings.WORKSPACE_PATH)
        self.llm_client = LLMClient(settings.OPENROUTER_API_KEY)
        self.executor = ToolExecutor()
        self.react_loop = ReActLoop(self.llm_client, self.executor)
        self.default_model = "google/gemini-2.0-flash-001"

    async def process_message(self, session_id: str, text: str):
        if session_id not in self.sessions:
            self.sessions[session_id] = []

        self.sessions[session_id].append({"role": "user", "content": text})
        full_messages = await self.context_assembler.assemble(self.sessions[session_id])

        try:
            response_msg = await self.react_loop.run(full_messages, self.default_model)
            self.sessions[session_id].append(response_msg)
            return response_msg.get("content", "No he pogut generar cap resposta.")
        except Exception as e:
            logger.error(f"Error: {e}")
            return f"Error: {e}"


if __name__ == "__main__":

    async def test():
        gateway = SebastianGateway()
        res = await gateway.process_message("test", "Hola Sebastian")
        print(res)

    asyncio.run(test())
