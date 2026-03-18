import os
import json
import sys

def file_op(operation, source, content=None, destination=None):
    try:
        source = os.path.abspath(source)
        if operation == "read":
            with open(source, 'r', encoding='utf-8') as f:
                return {"content": f.read()}
        elif operation == "write":
            with open(source, 'w', encoding='utf-8') as f:
                f.write(content)
                return {"status": "success"}
        elif operation == "append":
            with open(source, 'a', encoding='utf-8') as f:
                f.write(content)
                return {"status": "success"}
        elif operation == "list":
             return {"files": os.listdir(source)}
        else:
            return {"error": f"Operació {operation} no reconeguda"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        args = json.loads(sys.argv[1])
        print(json.dumps(file_op(**args)))
    else:
        print(json.dumps({"error": "No s'han passat arguments JSON"}))
