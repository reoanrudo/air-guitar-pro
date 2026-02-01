#!/usr/bin/env python3
"""
Simple WebSocket Server for Air Guitar
Mobile app → Python server
"""

import asyncio
import json
import logging
from aiohttp import web, WSMsgType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Store connections by room ID
connections = {}

async def handle_websocket(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    room_id = None

    try:
        async for msg in ws:
            if msg.type == WSMsgType.TEXT:
                data = json.loads(msg.data)
                action = data.get("action")
                logger.info(f"Received: {action}")

                if action == "register":
                    room_id = data.get("roomId")
                    logger.info(f"✅ Room registered: {room_id}")
                    connections[room_id] = ws

                    # 接続完了を通知
                    await ws.send_json({"action": "connected", "roomId": room_id})

                elif action == "data":
                    # データを受信
                    payload = data.get("payload")
                    room_id = data.get("roomId")

                    logger.info(f"📱 Data from mobile (Room: {room_id}): {payload}")

                    # TODO: ここで音を変える処理を実装
                    # 例：pygameで音を鳴らす、MIDIメッセージを送信など

                    # エコーしたことを確認
                    await ws.send_json({"action": "received", "status": "ok"})

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if room_id and room_id in connections:
            del connections[room_id]
            logger.info(f"Room {room_id} disconnected")

    return ws

async def index(request):
    return web.Response(text="Air Guitar Python Server Running\nMobile → PC communication ready")

async def health(request):
    return web.json_response({
        "status": "ok",
        "connections": len(connections)
    })

app = web.Application()
app.router.add_get("/", index)
app.router.add_get("/health", health)
app.router.add_get("/ws", handle_websocket)

if __name__ == "__main__":
    logger.info("🎸 Air Guitar Server Starting on 0.0.0.0:8000")
    logger.info("Ready for mobile connections...")
    web.run_app(app, host="0.0.0.0", port=8000)
