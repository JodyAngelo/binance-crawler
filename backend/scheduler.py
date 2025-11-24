import asyncio
from crawler import crawl
from storage import save_cache
from websockets_server.utils import broadcast

async def start_scheduler(interval_minutes: int, cache: dict):
    print(f"Running Scheduler in {interval_minutes} minutes")
    old_data = cache
    while True:
        await asyncio.sleep(interval_minutes * 60)
        print(f"Start Checking new Binance Data...")

        new_data = await asyncio.to_thread(crawl) 

        if old_data != new_data: # Compare old data with new data
            print(f"New Data Arrived!")
            save_cache(new_data)

            await broadcast(new_data)
            old_data = new_data
        else:
            print(f" No new data.")

