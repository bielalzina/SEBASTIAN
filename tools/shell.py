import os
import subprocess
import json
import sys


def run_shell(command, timeout=30):
    try:
        # Detectar si som a Linux (Debian) o Windows
        if os.name == "posix":
            shell_cmd = ["/bin/bash", "-c", command]
        else:
            shell_cmd = ["powershell", "-Command", command]

        result = subprocess.run(
            shell_cmd, capture_output=True, text=True, timeout=timeout, encoding="utf-8"
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"error": f"Comanda ha superat el temps límit de {timeout}s"}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    input_data = sys.stdin.read()
    if input_data:
        try:
            data = json.loads(input_data)
            command = data.get("command")
            print(json.dumps(run_shell(command)))
        except Exception as e:
            print(json.dumps({"error": f"Error de parsing: {str(e)}"}))
    else:
        print(json.dumps({"error": "No hi ha dades al STDIN"}))
