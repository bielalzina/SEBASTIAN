import os
import subprocess
import json
import sys

def run_shell(command, timeout=30):
    try:
        # En Windows s'aconsella usar powershell
        result = subprocess.run(
            ["powershell", "-Command", command],
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding='utf-8'
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"error": f"Comanda ha superat el temps límit de {timeout}s"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = " ".join(sys.argv[1:])
        print(json.dumps(run_shell(cmd)))
    else:
        print(json.dumps({"error": "No s'ha passat cap comanda"}))
