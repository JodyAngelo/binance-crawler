import json
import asyncio
from storage import load_cache

connected_clients = set()

async def handler(websocket):
    connected_clients.add(websocket)
    print("New client connected")
    print(connected_clients)

    initial_data = load_cache()

    if initial_data: 
        await websocket.send(json.dumps(initial_data))
        print("Cached data sent!")

    try:
        # Keep the connection open
        async for _ in websocket:
            pass
    except:
        pass
    finally:
        connected_clients.remove(websocket)
        print("Client disconnected")
        print(connected_clients)

async def broadcast(data: dict):
    if not connected_clients:
        return
    
    print(data)
    data = json.dumps(data)

    # Send to all clients at once
    await asyncio.gather(*[client.send(data) for client in connected_clients])
    print("Cached data sent!")


