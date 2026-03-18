import asyncio
import json
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from src.gateway.core import SebastianGateway, settings

app = FastAPI()
logger = logging.getLogger("SEBASTIAN-WebSocket")
gateway = SebastianGateway()

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
