import requests
import re
import time
from typing import List
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL ="https://data.binance.vision/?prefix=data/futures/um/"

session = requests.Session()
session.headers.update({
    "User-Agent": "BinanceDataChecker",
    "Connection": "keep-alive"
})

def fetch_text(url: str) -> str:
    time.sleep(0.1)
    response = session.get(url, timeout=15)
    return response.text

def extract_base_prefix(url: str) -> str:
    return url[url.index("?"):]  

def extract_bucket_url(html: str) -> str:
    BUCKET_URL = re.search(r"BUCKET_URL\s*=\s*'([^']+)'", html)
    return BUCKET_URL.group(1)
        
def build_base_s3_url() -> str:
    html = fetch_text(BASE_URL)
    BASE_PREFIX = extract_base_prefix(BASE_URL)
    BUCKET_URL = extract_bucket_url(html)

    return BUCKET_URL + BASE_PREFIX 

def apply_limit(items: List[str], limit: int | None):
    if limit is None:
        return items
    return items[:limit]

def chunk_list(items, batch_size):
    chunks = []
    for i in range(0, len(items), batch_size):
        chunk = items[i:i + batch_size]
        chunks.append(chunk)
    return chunks

def get_frequencies(base_s3_url: str) -> List[str]:
    s3_endpoint = f"{base_s3_url}&delimiter=/"  # Add Amazon S3 parameter
    xml = fetch_text(s3_endpoint)
    
    prefixes = re.findall(r"<Prefix>(.*?)</Prefix>", xml)
    frequencies = []

    for prefix in prefixes:
        frequency = re.search(r"um/([^/]+)/", prefix)
        if frequency:
            frequencies.append(frequency.group(1))
            
    return frequencies

def get_categories(base_s3_url: str, frequency: str) -> List[str]:
    categories = []
    
    s3_endpoint = f"{base_s3_url}{frequency}/&delimiter=/"  # Add Amazon S3 parameter
    xml = fetch_text(s3_endpoint)
    prefixes = re.findall(r"<Prefix>(.*?)</Prefix>", xml)
    
    for prefix in prefixes:
        category = re.search(rf"{frequency}/([^/]+)/", prefix)
        if category:
            categories.append(category.group(1))
            
    return categories

def get_instruments(base_s3_url: str, frequency: str, category: str, limit: int | None = None) -> List[str]:
    instruments = []
    s3_endpoint = f"{base_s3_url}{frequency}/{category}/&delimiter=/"  # Add Amazon S3 parameter
    xml = fetch_text(s3_endpoint)
    prefixes = re.findall(r"<Prefix>(.*?)</Prefix>", xml)

    for prefix in prefixes:
        instrument = re.search(rf"{frequency}/{category}/([^/]+)/", prefix)
        if instrument:
            instruments.append(instrument.group(1))

        if limit is not None and len(instruments) >= limit:
            break
            
    return apply_limit(instruments, limit)

def get_timeframes(base_s3_url: str, frequency: str, category: str, instrument: str, limit: int | None = None) -> List[str]:
    timeframes = []
    s3_endpoint = f"{base_s3_url}{frequency}/{category}/{instrument}/&delimiter=/"  # Add Amazon S3 parameter
    xml = fetch_text(s3_endpoint)
    prefixes = re.findall(r"<Prefix>(.*?)</Prefix>", xml)
   
    for prefix in prefixes:
        timeframe = re.search(rf"{frequency}/{category}/{instrument}/([^/]+)/", prefix)
        if timeframe:
            timeframes.append(timeframe.group(1))
            
    return apply_limit(timeframes, limit)

def get_date_range(base_s3_url: str, frequency: str, category: str, instrument: str, timeframe: str | None = None):
    if timeframe:
        s3_endpoint = f"{base_s3_url}{frequency}/{category}/{instrument}/{timeframe}/&delimiter=/"
    else:
        s3_endpoint = f"{base_s3_url}{frequency}/{category}/{instrument}/&delimiter=/"

    xml = fetch_text(s3_endpoint)
    keys = re.findall(r"<Key>(.*?)</Key>", xml)
    dates = []

    for key in keys:
        if frequency == "daily":
            date = re.search(r"\d{4}-\d{2}-\d{2}", key)
        else:
            date = re.search(r"\d{4}-\d{2}", key)

        if date:
            dates.append(date.group(0))

    return {
        "from": min(dates),
        "to": max(dates)
    }

def crawl_root(executor, base_s3_url: str):
    result = {}
    frequencies = get_frequencies(base_s3_url)
    threads = [executor.submit(crawl_frequency, executor, base_s3_url, frequency) for frequency in frequencies]

    for thread in as_completed(threads):
        frequency, data = thread.result()
        result[frequency] = data

    return result
    
def crawl_frequency(executor, base_s3_url: str, frequency):
    result = {}
    categories = get_categories(base_s3_url, frequency)
    threads = [executor.submit(crawl_category, base_s3_url, frequency, category) for category in categories]

    for thread in as_completed(threads):
        category, data = thread.result()
        result[category] = data
    
    return frequency, result

def crawl_category(base_s3_url: str, frequency: str, category: str):
    result = {}
    instruments = get_instruments(base_s3_url, frequency, category, 10)
    instruments_batches = chunk_list(instruments, 2) 
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        for instrument_batch in instruments_batches:
            # print(frequency, category, instrument_batch)
            threads = [executor.submit(crawl_instrument, base_s3_url, frequency, category, instrument) for instrument in instrument_batch]

            for thread in as_completed(threads):
                instrument, data = thread.result()
                result[instrument] = data
        print(result)
    return category, result
 
def crawl_instrument(base_s3_url: str, frequency: str, category: str, instrument: str):
    result = {}
    timeframes = get_timeframes(base_s3_url, frequency, category, instrument)
    if timeframes:
        for timeframe in timeframes:
            result[timeframe] = get_date_range(base_s3_url, frequency, category, instrument, timeframe)
        return instrument, result
    
    return instrument, get_date_range(base_s3_url, frequency, category, instrument, timeframe=None)

def crawl():
    base_s3_url  = build_base_s3_url()

    executor = ThreadPoolExecutor(max_workers=10)
    tree_dict = crawl_root(executor, base_s3_url)
    executor.shutdown(wait=True)

    print(tree_dict)
    return tree_dict

 


  



