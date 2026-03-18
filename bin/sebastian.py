import asyncio
import sys
import os
import argparse
import signal

def run_doctor():
    print("\n🔍 Dr. Sebastian Diagnostics")
    print("-" * 30)
    
    # Check .env
    if os.path.exists(".env"):
        print("✅ .env trobat")
    else:
        print("❌ .env NO trobat")

    # Check Workspace
    workspace_files = ['SOUL.md', 'AGENTS.md', 'IDENTITY.md', 'USER.md', 'TOOLS.md', 'MEMORY.md', 'HEARTBEAT.md']
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

def main():
    parser = argparse.ArgumentParser(description="SEBASTIAN CLI")
    parser.add_argument("command", choices=["start", "doctor", "pairing", "onboard"])
    parser.add_argument("subcommand", nargs="*", help="Subcomanda (ex: approve <channel> <code>)")

    args = parser.parse_args()

    if args.command == "doctor":
        run_doctor()
    elif args.command == "start":
        print("\n🚀 Iniciant SEBASTIAN Gateway (WebSocket + Telegram)...")
        # Aquí llançaríem els processos en paral·lel normalment
        # De moment simulat o llançant el de WebSocket
        import uvicorn
        from src.channels.websocket_server import app
        from src.gateway.core import settings
        uvicorn.run(app, host="0.0.0.0", port=settings.GATEWAY_PORT)
    else:
        print(f"Ordre {args.command} no implementada completament.")

if __name__ == "__main__":
    main()
