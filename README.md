# Binance Data Crawler 

Binance data crawler built using pure Python (`requests`) without any HTML scrapers.  
Designed for large-scale S3-style directory traversal and data extraction
---

## Features

### 1. Full Binance Folder Crawler
- Crawls `https://data.binance.vision/?prefix=data/futures/um/`
- Fetches:
  - All frequencies (e.g., `daily`, `monthly`)
  - All categories under each frequency
  - All instruments under each category
- Implemented using **pure requests + XML parsing**.


### 2. Multi-Threaded High-Speed Crawling
- Uses `concurrent.futures.ThreadPoolExecutor`
- Batched requests to avoid rate limits

### 3. Recurring Scheduler (Daily / X Minutes)
- Automatically checks when Binance uploads new files

### 4. WebSocket Backend → React Frontend
- Python backend pushes live metadata updates to a React UI
- React UI displays:
- Frequencies
- Categories
- Instruments
- Time frames
- Date ranges

### 5. Smart Cache System
- Caches previous results to avoid full re-crawls

---

## Tech Stack

### Backend
- Python 3
- `requests`
- `concurrent.futures`
- JSON data caching
- WebSocket server

### Frontend
- React + TypeScript  
- WebSocket client  



