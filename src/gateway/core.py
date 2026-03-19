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
    MAX_ITERATIONS: int = 10
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


# (El ReActLoop, ContextAssembler, LLMClient y SebastianGateway siguen igual que en tu archivo original)
