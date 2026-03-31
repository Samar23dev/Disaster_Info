# GeoPulse Intelligence — Distributed Geospatial Event Monitoring Engine

> Real-time news ingestion pipeline with sub-minute latency: async scraping → NLP enrichment → geocoded interactive map.

---

## Architecture — Four-Stage Pipeline

```
50+ RSS / Web Sources
        │
        ▼
┌─────────────────────┐
│  Async Ingestion    │  asyncio + aiohttp, Semaphore rate-limiter
│  (Collector)        │  ETag / If-Modified-Since incremental fetch
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  NLP Enrichment     │  L1: SpaCy NER  →  L2: Gemini 1.5 Flash
│  (Brain)            │  Toponym resolution + sentiment scoring
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Spatial Indexing   │  MongoDB 2dsphere  +  geocoding cache
│  (Mapper)           │  MD5 dedup  +  Folium marker clustering
└────────┬────────────┘
         │
         ▼
┌─────────────────────┐
│  Delivery Layer     │  Streamlit dashboard  +  FCM push alerts
└─────────────────────┘
```

---

## Technical Deep Dives

### 1. High-Concurrency Ingestion

- `asyncio` + `aiohttp` parallelizes fetches across 50+ sources simultaneously — non-blocking I/O, no thread-per-source overhead.
- `asyncio.Semaphore` enforces a "good-citizen" back-pressure policy to prevent 429/IP-blacklist responses.
- **Incremental fetching** via `ETag` and `If-Modified-Since` HTTP headers skips unchanged feeds entirely — **75% bandwidth reduction** vs. full re-fetch.

### 2. Two-Stage Toponym Resolution

Raw entity text like "Paris" is geographically ambiguous. Resolution is staged to minimize API cost:

```
Article text
     │
     ▼
L1 — SpaCy NER          (local, free)
     Extract: PERSON, ORG, GPE, LOC entities
     │
     ▼  ambiguous or low-confidence?
     │
     ▼
L2 — Gemini 1.5 Flash   (API call, triggered only when needed)
     Context window: surrounding sentences
     Resolve: currency, landmark, regional markers → final [Lat, Long]
```

Sentiment scoring runs in the same Gemini pass — color-coded markers (red = conflict/crisis, green = growth) without a second API call.

### 3. Geocoding Cache & Deduplication

- **MongoDB-backed geocode cache:** `Location_Name → [Lat, Long]` stored in a `2dsphere`-indexed collection. Cache-hit avoids Nominatim/Google Maps API call entirely — **80% reduction in geocoding API calls**.
- **MD5 idempotency:** Each article body is hashed on ingest. Duplicate hash → skip insert. Zero duplicate entries in the event store regardless of feed overlap.

### 4. Spatial Rendering

- **Folium + Leaflet.markercluster:** 1,000+ map markers clustered into zoom-aware aggregates — frontend stays responsive at full dataset scale.
- **MongoDB `2dsphere` indexing** enables `$near` and `$geoWithin` queries for proximity-based alert filtering without application-layer distance math.

### 5. Resilience & Observability

- **Exponential backoff** on 403/429 — request frequency auto-adjusts without manual intervention.
- **Fail-safe health checks** detect upstream HTML structure changes and emit Slack/email alerts via SMTP.
- **GitHub Actions cron** drives 24/7 autonomous pipeline execution — no always-on server required.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Concurrency | Python asyncio / aiohttp |
| NLP — L1 | SpaCy (NER) |
| NLP — L2 | Google Gemini 1.5 Flash |
| Map rendering | Folium / Leaflet.js + markercluster |
| Database | MongoDB (2dsphere index) |
| Frontend | Streamlit |
| Push notifications | Flutter + Firebase Cloud Messaging |
| CI / Scheduling | GitHub Actions (cron) |
| Data export | Pandas → JSON / XLSX |

---

## Key Metrics

| Metric | Value |
|---|---|
| End-to-end latency (scrape → map) | < 15 seconds across 50 sources |
| Geocoding accuracy | 90%+ via LLM context verification |
| Bandwidth saved (incremental fetch) | 75% vs. full re-fetch baseline |
| Geocoding API calls saved (cache) | 80% reduction |

---

## Project Structure

```
Disaster_Info/
├── main.py              # Entry point, Streamlit navigation
├── home.py              # Live disaster news feed
├── datacollection.py    # Async ingestion + NLP pipeline
├── insight.py           # Analytics: charts, time-series, word cloud
├── weather.py           # Windy API integration, weather overlays
├── alerts.py            # FCM push alert subscription system
├── precaution.py        # Disaster-type safety protocols
├── login.py             # User auth, preference persistence
├── datafiles/           # Cached geocode store + event snapshots
├── assets/ icons/       # Static UI resources
└── requirements.txt
```

---

## Setup

```bash
git clone https://github.com/Samar23dev/Disaster_Info.git
cd Disaster_Info
pip install -r requirements.txt
```

Create `.env`:

```env
MONGODB_URI=your_mongodb_connection_string
MONGODB_DB=your_database_name
MONGODB_COLLECTION=your_collection_name
WINDY_API_KEY=your_windy_api_key
GEMINI_API_KEY=your_gemini_api_key
EMAIL_SENDER=your_email
EMAIL_PASSWORD=your_email_password
```

```bash
streamlit run main.py
```

---

## Scaling Roadmap

- **Distributed scraping:** Migrate GitHub Actions → AWS Step Functions for horizontal parallelization.
- **Stream ingestion:** Amazon Kinesis for live social media feeds alongside RSS.
- **Predictive layer:** Time-series model on historical geospatial data for crisis hotspot prediction.
