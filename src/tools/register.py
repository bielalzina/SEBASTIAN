import sys
import os
import json

def register_tool(name, schema, entry_point):
    """
    Registra una eina per ser utilitzada pel gateway.
    Crea un fitxer JSON de definició a tools/
    """
    tool_def = {
        "name": name,
        "parameters": schema,
        "entry_point": entry_point
    }
    with open(f"tools/{name}.json", "w") as f:
        json.dump(tool_def, f, indent=4)
    print(f"Tool {name} registrada correctament.")

if __name__ == "__main__":
    # Registrar les 3 eines inicials
    register_tool("shell", {
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "L'ordre a executar al PowerShell."}
        },
        "required": ["command"]
    }, "tools/shell.py")

    register_tool("file_ops", {
        "type": "object",
        "properties": {
            "operation": {"type": "string", "enum": ["read", "write", "append", "list"]},
            "source": {"type": "string", "description": "Camí del fitxer o directori."},
            "content": {"type": "string", "description": "Contingut si s'escriu o s'afegeix."},
            "destination": {"type": "string", "description": "Destí per a còpia o mogut."}
        },
        "required": ["operation", "source"]
    }, "tools/file_ops.py")

    register_tool("web_search", {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "La cerca a realitzar a DuckDuckGo."}
        },
        "required": ["query"]
    }, "tools/web_search.py")
