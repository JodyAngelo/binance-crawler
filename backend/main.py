from crawler import crawl
from storage import load_cache, save_cache
from scheduler import start_scheduler
from websockets_server.utils import handler, broadcast
import asyncio
import websockets

async def start_websocket_server():
    print("WebSocket server running on ws://localhost:8001")
    await websockets.serve(handler, "localhost", 8001)

async def crawl_initial_cache():
    print("Cache empty - crawling now...")
    data = await asyncio.to_thread(crawl)
    save_cache(data)
    await broadcast(data)
    return data

async def run_services():
    await start_websocket_server()

    cache = load_cache() or await crawl_initial_cache()

    # Run scheduler 
    asyncio.create_task(start_scheduler(interval_minutes=30, cache=cache))

    # Do nothing forever, to keep this run_service function alive
    await asyncio.Future()  


if __name__ == "__main__":
    asyncio.run(run_services())
