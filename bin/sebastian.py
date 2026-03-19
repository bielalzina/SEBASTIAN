import asyncio
import sys
import os
import argparse
import signal
from multiprocessing import Process

# 1. AFERIR PROJECT_ROOT PER TROBAR EL PAQUET 'src'
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


# 2. FUNCIÓ DOCTOR (MANTINGUDA)
def run_doctor():
    print("\n🔍 Dr. Sebastian Diagnostics")
    print("-" * 30)

    # Check .env
    if os.path.exists(".env"):
        print("✅ .env trobat")
    else:
        print("❌ .env NO trobat")

    # Check Workspace
    workspace_files = [
        "SOUL.md",
        "AGENTS.md",
        "IDENTITY.md",
        "USER.md",
        "TOOLS.md",
        "MEMORY.md",
        "HEARTBEAT.md",
    ]
    for file in workspace_files:
        path = os.path.join("workspace", file)
        if os.path.exists(path):
            print(f"✅ Workspace: {file} trobat")
        else:
            print(f"❌ Workspace: {file} NO trobat")

    # Check Tools
    tools_dir = "tools"
    if os.path.exists(tools_dir):
        json_tools = [f for f in os.listdir(tools_dir) if f.endswith(".json")]
        print(f"✅ Eines: {len(json_tools)} eines registrades")

    print("-" * 30)
    print("Diagnostics completats.\n")


# 3. FUNCIONS DE LLANÇAMENT
def start_websocket():
    import uvicorn
    from src.channels.websocket_server import app
    from src.gateway.core import settings

    print(f"📡 WebSocket Server iniciat al port {settings.GATEWAY_PORT}...")
    uvicorn.run(app, host="0.0.0.0", port=settings.GATEWAY_PORT, log_level="error")


def start_telegram():
    from src.channels.telegram_bot import TelegramAdapter
    from src.gateway.core import SebastianGateway, settings

    if settings.TELEGRAM_BOT_TOKEN == "PENDING" or not settings.TELEGRAM_BOT_TOKEN:
        print("⚠️ Telegram Bot NO iniciat (TOKEN pendent o incorrecte).")
        return

    print("🤖 Telegram Bot iniciat...")
    gateway = SebastianGateway()
    adapter = TelegramAdapter(gateway)
    adapter.run()


# 4. ENTRY POINT
def main():
    parser = argparse.ArgumentParser(description="SEBASTIAN CLI")
    parser.add_argument("command", choices=["start", "doctor", "pairing", "onboard"])
    parser.add_argument(
        "subcommand", nargs="*", help="Subcomanda (ex: approve <channel> <code>)"
    )

    args = parser.parse_args()

    if args.command == "doctor":
        run_doctor()
    elif args.command == "start":
        print("\n🚀 Iniciant SEBASTIAN (Multiprocess: WebSocket + Telegram)...")

        # Llançar WebSocket i Telegram en paral·lel
        p1 = Process(target=start_websocket)
        p2 = Process(target=start_telegram)

        p1.start()
        p2.start()

        # Esperar que els processos acabin (normalment estaran actius fins que els mates)
        try:
            p1.join()
            p2.join()
        except KeyboardInterrupt:
            p1.terminate()
            p2.terminate()
    else:
        print(f"Ordre {args.command} encara no integrada al multiprocés.")


if __name__ == "__main__":
    main()
