#!/usr/bin/env python3
"""WebSocket test client"""

import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://10.239.209.208:8000/ws"

    try:
        print(f"Connecting to {uri}...")
        async with websockets.connect(uri) as websocket:
            print("✅ Connected!")

            # Register as mobile client
            await websocket.send(json.dumps({
                "action": "register",
                "peerId": "TEST-MOBILE-CLIENT"
            }))

            # Wait for server response
            response = await websocket.recv()
            print(f"Server says: {response}")

            # Send test data
            await websocket.send(json.dumps({
                "action": "data",
                "payload": {
                    "type": "CHORD_CHANGE",
                    "payload": {"chord": "C"}
                }
            }))
            print("✅ Sent test data!")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
