import asyncio
import json
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from src.gateway.core import SebastianGateway, settings

app = FastAPI()
logger = logging.getLogger("SEBASTIAN-WebSocket")
gateway = SebastianGateway()

@app.get("/", response_class=HTMLResponse)
async def get_home():
    return """
    <!DOCTYPE html>
    <html lang="ca">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SEBASTIAN | Neural Interface</title>
        <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
        <style>
            :root {
                --accent: #00f2ff;
                --bg: #0a0b10;
                --card: rgba(255, 255, 255, 0.05);
            }
            body {
                background: var(--bg);
                color: white;
                font-family: 'Inter', sans-serif;
                margin: 0;
                overflow: hidden;
                display: flex;
                height: 100vh;
            }
            .sidebar {
                width: 300px;
                background: rgba(0, 0, 0, 0.4);
                backdrop-filter: blur(20px);
                border-right: 1px solid rgba(255,255,255,0.1);
                display: flex;
                flex-direction: column;
                padding: 30px;
            }
            .main {
                flex: 1;
                display: flex;
                flex-direction: column;
                background: radial-gradient(circle at 50% 50%, #16213e 0%, #0a0b10 100%);
                position: relative;
            }
            h1 {
                font-family: 'Orbitron', sans-serif;
                color: var(--accent);
                font-size: 1.5rem;
                letter-spacing: 2px;
                margin: 0 0 20px 0;
            }
            #chat-container {
                flex: 1;
                overflow-y: auto;
                padding: 40px;
                display: flex;
                flex-direction: column;
                gap: 20px;
                scroll-behavior: smooth;
            }
            .message {
                max-width: 80%;
                padding: 15px 20px;
                border-radius: 15px;
                line-height: 1.5;
                animation: fadeIn 0.3s ease;
            }
            .user-msg {
                align-self: flex-end;
                background: var(--accent);
                color: black;
                font-weight: 600;
            }
            .bot-msg {
                align-self: flex-start;
                background: var(--card);
                border: 1px solid rgba(255,255,255,0.1);
                border-left: 4px solid var(--accent);
            }
            .input-area {
                padding: 30px;
                background: rgba(0,0,0,0.5);
                border-top: 1px solid rgba(255,255,255,0.1);
                display: flex;
                gap: 15px;
            }
            input {
                flex: 1;
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.2);
                padding: 15px;
                color: white;
                border-radius: 10px;
                outline: none;
                transition: 0.3s;
            }
            input:focus { border-color: var(--accent); }
            button {
                background: var(--accent);
                border: none;
                padding: 10px 25px;
                border-radius: 10px;
                font-weight: bold;
                cursor: pointer;
                transition: 0.3s;
            }
            button:hover { transform: scale(1.05); filter: brightness(1.2); }
            @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } }
            .status { font-size: 0.8rem; color: #888; margin-top: auto; }
            .dot { height: 8px; width: 8px; background: #55ff55; border-radius: 50%; display: inline-block; margin-right: 5px; }
        </style>
    </head>
    <body>
        <div class="sidebar">
            <h1>SEBASTIAN</h1>
            <p style="color:#aaa; font-size:0.9rem;">Neural Gateway Interface</p>
            <div class="status">
                <span class="dot"></span> Online via WebSocket<br>
                Port: 18789
            </div>
        </div>
        <div class="main">
            <div id="chat-container"></div>
            <div class="input-area">
                <input type="text" id="msgInput" placeholder="Envia un missatger a SEBASTIAN..." onkeypress="if(event.key=='Enter') send()">
                <button onclick="send()">ENVIAR</button>
            </div>
        </div>

        <script>
            const chat = document.getElementById('chat-container');
            const input = document.getElementById('msgInput');
            const ws = new WebSocket(`ws://${location.host}/ws`);

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                if(data.type === 'response') addMsg(data.text, 'bot');
            };

            function addMsg(text, type) {
                const div = document.createElement('div');
                div.className = `message ${type === 'bot' ? 'bot-msg' : 'user-msg'}`;
                div.innerText = text;
                chat.appendChild(div);
                chat.scrollTop = chat.scrollHeight;
            }

            function send() {
                const text = input.value.trim();
                if(!text) return;
                ws.send(JSON.stringify({type: 'message', text: text}));
                addMsg(text, 'user');
                input.value = '';
            }

            addMsg('Connectat al sistema. Esperant ordres...', 'bot');
        </script>
    </body>
    </html>
    """

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    session_id = f"ws-{websocket.client.host}"
    logger.info(f"Nova connexió WebSocket: {session_id}")
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "message":
                text = message.get("text")
                response = await gateway.process_message(session_id, text)
                await websocket.send_text(json.dumps({
                    "type": "response",
                    "text": response
                }))
    except WebSocketDisconnect:
        logger.info(f"S'ha tancat la sessió: {session_id}")
    except Exception as e:
        logger.error(f"Error WebSocket: {e}")
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.GATEWAY_PORT)
