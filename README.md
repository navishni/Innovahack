# GeoSafe AI

> **Autonomous Property Safety & Legal Verification Platform for Indian Real Estate**

GeoSafe AI is the first fully autonomous platform that takes an Indian property address and returns a comprehensive risk verdict — combining **11 environmental hazard assessments**, **autonomous legal due diligence**, and **AI-powered analysis** — without any manual intervention.

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [Solution Overview](#solution-overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [API Integrations](#api-integrations)
- [MCDA Scoring Engine](#mcda-scoring-engine)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [Environment Variables](#environment-variables)
- [API Endpoints](#api-endpoints)
- [How It Works](#how-it-works)
- [Geocoding System](#geocoding-system)
- [Hazard Modules](#hazard-modules)
- [Legal Verification](#legal-verification)
- [Contributing](#contributing)
- [License](#license)
- [Disclaimer](#disclaimer)

---

## Problem Statement

India's real estate market is worth **$300 billion+** and is the second-largest employer after agriculture. Yet it operates with almost zero data-driven safety verification for buyers.

### The Core Problem Has Three Layers

**1. Fragmented, Inaccessible Safety Data**

Hazard information — flood zones, seismic risk, CRZ violations, industrial pollution, heat exposure, landslide susceptibility — is scattered across dozens of government databases (IMD, CPCB, GSI, FSI, SPCB, OSM) that are either offline, paywalled, or require expert navigation. No single platform synthesizes this for a specific street-level address.

**2. Zero Legal Due Diligence Automation**

Verifying a property's legal standing — title chain, encumbrances, builder blacklist status, RERA registration, active court litigation — requires physical visits to Sub-Registrar offices, District Court websites, and state RERA portals. This process takes weeks, costs thousands, and most buyers skip it entirely, leading to India's Rs 5 lakh crore+ litigation backlog in property disputes.

**3. No Integrated Risk Assessment**

Even when buyers get some data (e.g., a flood map), no platform combines environmental, structural, and legal risks into a single actionable verdict. Buyers make decisions based on broker promises, not data.

### Who Is Affected

| Stakeholder | Pain Point |
|---|---|
| Individual home buyers | Cannot assess flood, earthquake, cyclone, pollution risk for a specific address |
| First-time buyers | Lack domain knowledge to interpret government data |
| NRI buyers | Cannot physically visit courts, SRO offices, or site locations |
| Real estate agents | Have no tool to provide verified safety data to clients |
| Banks/lenders | Property valuation does not include risk scoring |
| Insurance companies | No standardized risk score for underwriting |

---

## Solution Overview

GeoSafe AI takes a property address as input and returns a **comprehensive, data-driven risk verdict** — without any manual intervention.

### Core Workflow

```
User enters address
        ↓
    Geocoding (5-strategy fallback)
        ↓
    Parallel API Calls (12+ free APIs)
        ↓
    11 Hazard Assessments
        ↓
    MCDA Scoring Engine (13 weighted factors)
        ↓
    5 Hard-Override Risk Flags
        ↓
    Verdict: SAFE / CAUTION / HIGH_RISK / CRITICAL_RISK
        ↓
    Interactive Map + AI Summary + PDF Report
```

### What Makes It Different

| Feature | Existing Solutions | GeoSafe AI |
|---|---|---|
| Flood risk | Static NDMA PDF maps | Real-time Open-Meteo rainfall + OSM waterbody proximity scoring |
| Earthquake risk | GSI seismic zone maps | IS 1893:2016 PGA calculation with nearest fault distance |
| Air quality | CPCB city-level AQI | Street-level AQI from Open-Meteo (PM2.5, PM10, NO2, O3) |
| Industrial pollution | Manual site visits | OSM Overpass API with CPCB safe distance norms |
| Legal verification | Physical SRO/court visits | Indian Kanoon API + Bhuvan WMS CRZ overlay |
| Risk scoring | None exists | 13-factor MCDA engine with weighted hazard scores |
| Verdict | None exists | Autonomous SAFE/CAUTION/HIGH_RISK/CRITICAL_RISK determination |

---

## Key Features

### Property Analysis
- **13-Factor Hazard Assessment** — Flood, earthquake, cyclone, landslide, tsunami, air quality, heat, groundwater, soil, industrial pollution, climate projections
- **Real-Time API Data** — All hazard scores from live API calls, zero hardcoded values
- **Safety Score (0-100)** — Weighted MCDA scoring with color-coded verdict
- **5 Hard-Override Risk Flags** — Demolition order, CRZ violation, active litigation, builder blacklist, title defect

### Geocoding
- **5-Strategy Fallback** — India Nominatim → Global Nominatim → Photon → Google (optional) → City center
- **Locality Extraction** — Strips building/flat names, searches for actual locality + city
- **Known Locality Validation** — Cross-references 100+ Indian cities/suburbs for precision

### Visualization
- **Interactive Leaflet Map** — Polygon visualization with color-coded risk zones
- **Nearby Emergency Services** — Real OSM Overpass data for hospitals, police, fire stations
- **Safety Gauge** — Color-coded score visualization (green/amber/red)
- **Hazard Cards** — Individual risk cards with consequence statements

### Legal Verification (Fully Autonomous)
- **Indian Kanoon API** — Automated court case search for property litigation
- **Bhuvan WMS** — CRZ overlay and satellite imagery from ISRO
- **Document Upload + OCR** — Parse EC/deed documents when no public API exists
- **RERA Registration Check** — Verify builder RERA compliance
- **Builder Blacklist Check** — Cross-reference against known blacklisted builders
- **Title Chain Analysis** — Automated title verification

### Comparison & Reporting
- **Side-by-Side Comparison** — Compare 2 properties with radar charts
- **PDF Report Generation** — Downloadable analysis reports
- **AI Summaries** — Gemini-powered property recommendations
- **Analysis History** — Save and retrieve past analyses

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js 16)                        │
│                                                                     │
│   React 19 │ Tailwind CSS 4 │ Framer Motion │ Zustand │ Leaflet    │
│                                                                     │
│   Pages: / │ /search │ /analysis/[id] │ /compare │ /legal-check    │
├─────────────────────────────────────────────────────────────────────┤
│                        API Layer (FastAPI)                          │
│                                                                     │
│   POST /api/analyze    GET /api/geocode    POST /api/compare        │
│   GET  /api/health     POST /api/chat      POST /api/report         │
├─────────────────────────────────────────────────────────────────────┤
│                        SERVICE LAYER                                │
│                                                                     │
│   ┌─────────────┐  ┌──────────────┐  ┌─────────────┐               │
│   │   Geocoder   │  │  Discovery   │  │   MCDA      │               │
│   │   Engine     │  │   Engine     │  │   Engine    │               │
│   │ (5-strategy) │  │ (11 hazards) │  │ (13 factors)│               │
│   └─────────────┘  └──────────────┘  └─────────────┘               │
│                                                                     │
│   ┌─────────────┐  ┌──────────────┐  ┌─────────────┐               │
│   │   Legal      │  │    LLM       │  │   Report    │               │
│   │   Service    │  │   Service    │  │  Generator  │               │
│   │ (6 checks)   │  │  (Gemini)    │  │  (PDF)      │               │
│   └─────────────┘  └──────────────┘  └─────────────┘               │
├─────────────────────────────────────────────────────────────────────┤
│                     EXTERNAL APIs (12+ Free)                        │
│                                                                     │
│   Open-Meteo (5) │ OSM Overpass (3 mirrors) │ ISRIC SoilGrids       │
│   Indian Kanoon  │ Bhuvan WMS (ISRO)        │ GSI Faults            │
│   Photon Geocoder│ Google Gemini            │ Google Maps (optional)│
└─────────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| Python 3.12+ | Core language |
| FastAPI | REST API framework |
| Pydantic | Data validation |
| httpx | Async HTTP client |
| WeasyPrint | PDF generation |
| uvicorn | ASGI server |

### Frontend
| Technology | Purpose |
|---|---|
| Next.js 16 | React framework (Turbopack) |
| React 19 | UI library |
| TypeScript | Type safety |
| Tailwind CSS 4 | Styling |
| Framer Motion | Animations |
| Zustand | State management |
| Recharts | Data visualization |
| Leaflet / react-leaflet | Interactive maps |

### APIs & Data Sources
| API | Purpose |
|---|---|
| Open-Meteo (5 APIs) | Weather, AQI, Climate, Marine, Elevation |
| ISRIC SoilGrids | Soil properties |
| OSM Overpass (3 mirrors) | Flood, industrial, noise, biodiversity |
| Indian Kanoon | Court case search |
| Bhuvan WMS (ISRO) | CRZ overlay, satellite imagery |
| GSI Named Faults | Earthquake fault lines |
| Photon / Nominatim | Address geocoding |
| Google Gemini | AI summaries |
| Google Maps (optional) | High-precision geocoding |

---

## API Integrations

### Free APIs (No Key Required)

| # | API | Endpoint | Purpose |
|---|---|---|---|
| 1 | Open-Meteo Weather | `api.open-meteo.com/v1/forecast` | Temperature, rainfall, wind, heatwave |
| 2 | Open-Meteo Air Quality | `air-quality-api.open-meteo.com/v1/air-quality` | AQI, PM2.5, PM10, NO2, O3 |
| 3 | Open-Meteo Climate | `climate-api.open-meteo.com/v1/climate` | CMIP6 future projections |
| 4 | Open-Meteo Marine | `marine-api.open-meteo.com/v1/marine` | Wave height for coastal risk |
| 5 | Open-Meteo Elevation | `api.open-meteo.com/v1/elevation` | SRTM DEM elevation data |
| 6 | ISRIC SoilGrids | `rest.isric.org/soilgrids/v2.0/properties/query` | Soil clay%, sand%, SOC, pH |
| 7 | OSM Overpass | `overpass-api.de/api/interpreter` (+ 2 mirrors) | Flood, industrial, noise, biodiversity |
| 8 | Nominatim | `nominatim.openstreetmap.org/search` | Address geocoding |
| 9 | Nominatim Reverse | `nominatim.openstreetmap.org/reverse` | Coordinates to address |
| 10 | Photon Geocoder | `photon.komoot.io/api/` | Geocoding fallback |
| 11 | Indian Kanoon | `api.indiankanoon.org/` | Court case search |
| 12 | Bhuvan WMS | `bhuvan.nrsc.gov.in/globe/service/wms` | CRZ overlay, satellite |

### Optional APIs (Key Required)

| # | API | Purpose | Cost |
|---|---|---|---|
| 13 | Google Maps Geocoding | High-precision address geocoding | $5/1K requests |
| 14 | Google Gemini | AI-generated summaries | Free tier available |

---

## MCDA Scoring Engine

### Multi-Criteria Decision Analysis

The MCDA engine combines 13 independent hazard factors using weighted scoring:

```python
weights = {
    "flood": 0.18,           # Highest weight — most common disaster in India
    "earthquake": 0.16,      # Second highest — affects entire zones
    "cyclone": 0.10,         # Coastal regions
    "landslide": 0.09,       # Hill states
    "tsunami": 0.06,         # Coastal but rare
    "air_quality": 0.09,     # Urban health risk
    "heat": 0.07,            # Climate change factor
    "groundwater": 0.08,     # Long-term sustainability
    "soil": 0.07,            # Construction suitability
    "pollution": 0.05,       # Industrial proximity
    "climate": 0.05,         # Future risk projection
}
```

### Score Calculation

```python
safety_score = 100 - (sum of weighted_risk_scores)
```

### Decision Thresholds

| Score | Verdict | Meaning |
|---|---|---|
| >= 75 | SAFE | Low risk, suitable for investment |
| >= 50 | CAUTION | Moderate risk, verify specific concerns |
| >= 25 | HIGH_RISK | Significant risk, not recommended |
| < 25 | CRITICAL_RISK | Extreme risk, avoid investment |

### 5 Hard-Override Risk Flags

Before any scoring, these critical risks override everything:

1. **Active demolition/eviction order** → CRITICAL_RISK
2. **CRZ violation zone** → CRITICAL_RISK
3. **Active court litigation on property** → CRITICAL_RISK
4. **Builder/company blacklist** → CRITICAL_RISK
5. **Title defect detected** → CRITICAL_RISK

### 4-Factor Flood Scoring

```python
flood_score = (
    waterbody_proximity_factor *    # Distance to nearest river/lake/canal
    annual_rainfall_factor *        # State-level expected rainfall
    state_flood_risk_factor *       # Historical flood-prone state data
    elevation_factor                # Low elevation = higher flood risk
)
```

---

## Project Structure

```
INNOVAHACK/
├── README.md                          # This file
├── LICENSE                            # MIT License
│
├── backend/                           # Python FastAPI backend
│   ├── main.py                        # Application entry point
│   ├── requirements.txt               # Python dependencies
│   ├── data_cache.json                # Analysis cache storage
│   │
│   └── app/
│       ├── __init__.py
│       ├── config.py                  # Settings management
│       │
│       ├── models/
│       │   └── schemas.py             # Pydantic data models
│       │
│       ├── routers/
│       │   └── api.py                 # API route definitions
│       │
│       ├── services/
│       │   ├── discovery_engine.py    # 11 hazard assessment functions
│       │   ├── mcda_engine.py         # MCDA scoring engine
│       │   ├── llm_service.py         # Gemini AI integration
│       │   ├── legal_service.py       # Legal verification service
│       │   ├── report_generator.py    # PDF report generation
│       │   ├── osm_geometry.py        # Map polygon scoring
│       │   └── nearby_services.py     # Emergency services lookup
│       │
│       └── utils/
│           ├── geocoder.py            # 5-strategy geocoding engine
│           └── india_data.py          # Disaster history, faults, rivers
│
└── frontend/                          # Next.js 16 frontend
    ├── package.json                   # Node.js dependencies
    ├── next.config.ts                 # Next.js configuration
    ├── tailwind.config.ts             # Tailwind CSS configuration
    ├── tsconfig.json                  # TypeScript configuration
    │
    └── src/
        ├── app/
        │   ├── layout.tsx             # Root layout with Navbar
        │   ├── page.tsx               # Homepage
        │   │
        │   ├── search/
        │   │   └── page.tsx           # Property search page
        │   │
        │   ├── analysis/
        │   │   └── [id]/
        │   │       └── page.tsx       # Analysis dashboard
        │   │
        │   ├── compare/
        │   │   └── page.tsx           # Side-by-side comparison
        │   │
        │   ├── legal-check/
        │   │   └── page.tsx           # Legal verification page
        │   │
        │   └── reports/
        │       └── page.tsx           # Report history page
        │
        ├── components/
        │   ├── Navbar.tsx             # Shared navigation bar
        │   ├── HazardCard.tsx         # Individual hazard risk card
        │   ├── PropertyMap.tsx        # Interactive Leaflet map
        │   ├── SafetyGauge.tsx        # Score visualization gauge
        │   ├── CompareChart.tsx       # Radar chart for comparison
        │   └── AIChat.tsx             # AI chat interface
        │
        └── lib/
            ├── api.ts                 # Backend API client
            ├── store.ts               # Zustand state management
            └── geoUtils.ts            # Map utility functions
```

---

## Setup Instructions

### Prerequisites

- Python 3.12+
- Node.js 18+
- npm or yarn

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/GeoSafe-AI.git
cd GeoSafe-AI
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload --port 8000
```

Backend runs at: `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs at: `http://localhost:3000`

### 4. Verify Installation

```bash
# Test backend health
curl http://localhost:8000/api/health

# Test geocoding
curl "http://localhost:8000/api/geocode?address=pallavaram+chennai"
```

---

## Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Required: Gemini API key for AI summaries
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Google Maps API key for enhanced geocoding
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
```

### API Key Details

| Key | Required | Purpose | How to Get |
|---|---|---|---|
| `GEMINI_API_KEY` | Yes | AI-generated property summaries | [Google AI Studio](https://aistudio.google.com/apikey) |
| `GOOGLE_MAPS_API_KEY` | No | High-precision geocoding | [Google Cloud Console](https://console.cloud.google.com/) |

### Without API Keys

The application works without any API keys:
- All 11 hazard modules use free APIs (Open-Meteo, OSM Overpass, ISRIC SoilGrids)
- Geocoding uses Nominatim and Photon (free, no key)
- Legal verification uses Indian Kanoon (free tier)
- Only AI summaries require the Gemini key

---

## API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Health check and cache status |
| `GET` | `/api/geocode?address=` | Geocode address to coordinates |
| `POST` | `/api/analyze` | Full property analysis |
| `GET` | `/api/analyze/{id}` | Retrieve saved analysis |
| `POST` | `/api/compare` | Compare 2 properties |
| `POST` | `/api/chat` | AI chat about a property |
| `POST` | `/api/report/generate/{id}` | Generate PDF report |
| `GET` | `/api/map-features?lat=&lon=&radius=` | Map polygon data |
| `GET` | `/api/nearby-services?lat=&lon=` | Emergency services lookup |

### Request/Response Examples

**Geocode:**
```bash
GET /api/geocode?address=mk+flats+pallava+garden+pallavaram+chennai
```

```json
{
  "address": "Pallavaram, Siva Shankaran Street, Tirusulam, Alandur, Chennai, Tamil Nadu, 600043, India",
  "lat": 12.97,
  "lon": 80.15,
  "city": "Alandur",
  "state": "Tamil Nadu",
  "country": "India"
}
```

**Analyze:**
```bash
POST /api/analyze
{
  "address": "Koramangala, Bangalore"
}
```

```json
{
  "id": "analysis_abc123",
  "address": "Koramangala, Bangalore",
  "lat": 12.94,
  "lon": 77.62,
  "safety_score": 68.5,
  "decision": "CAUTION",
  "hazards": { ... },
  "summary": "..."
}
```

---

## How It Works

### Step 1: Address Input
User enters a property address (e.g., "MK Flats Pallava Garden Pallavaram Chennai")

### Step 2: Geocoding
The 5-strategy geocoder converts the address to precise coordinates:
1. Extracts locality variants (strips building names)
2. Searches India Nominatim → Global Nominatim → Photon → Google → City center
3. Validates against 100+ known Indian localities
4. Returns coordinates (e.g., 12.97, 80.15 for Pallavaram)

### Step 3: Parallel API Calls
11 hazard functions call free APIs simultaneously:
- Open-Meteo Weather → Temperature, rainfall, wind
- Open-Meteo Air Quality → AQI, PM2.5, PM10
- Open-Meteo Climate → CMIP6 future projections
- Open-Meteo Marine → Wave height (coastal)
- Open-Meteo Elevation → SRTM DEM elevation
- ISRIC SoilGrids → Soil properties
- OSM Overpass → Waterbodies, industrial, noise, biodiversity
- GSI Fault Lines → Nearest fault distance

### Step 4: Hazard Scoring
Each hazard function returns a risk score (0-100) with:
- Multi-factor scoring formula
- Actual data values (not hardcoded)
- Specific neighborhood evidence
- Graduated consequence statements

### Step 5: MCDA Weighted Scoring
The MCDA engine combines 13 factors using weighted scoring:
```python
safety_score = 100 - sum(weight_i * risk_i for i in 13 factors)
```

### Step 6: Hard-Override Check
5 critical risks override the score to CRITICAL_RISK:
- Demolition order, CRZ violation, active litigation, builder blacklist, title defect

### Step 7: Verdict Generation
Final verdict based on score thresholds:
- SAFE (>=75) / CAUTION (>=50) / HIGH_RISK (>=25) / CRITICAL_RISK (<25)

### Step 8: Response
Returns comprehensive result with:
- Safety score and verdict
- 11 hazard cards with scores and consequences
- Interactive map with risk polygons
- AI-generated summary
- Nearby emergency services

---

## Geocoding System

### 5-Strategy Fallback

```
Strategy 1: India Nominatim (specific Indian addresses)
    ↓ (no result)
Strategy 2: Global Nominatim (broader search)
    ↓ (no result)
Strategy 3: Photon Geocoder (OpenStreetMap-based)
    ↓ (no result)
Strategy 4: Google Maps API (if key available)
    ↓ (no result)
Strategy 5: City Center Fallback (with warning)
```

### Locality Extraction

The geocoder strips building/flat names and searches for actual localities:

**Input:** "MK Flats Pallava Garden Pallavaram Chennai"

**Variants Generated:**
1. "mk flats pallava garden pallavaram chennai" (original)
2. "pallava garden pallavaram chennai" (stripped building names)
3. "garden pallavaram chennai" (stripped more)
4. "pallavaram chennai" (locality + city)
5. "pallavaram" (locality only)
6. "pallavaram india" (locality + country)

**Result:** Pallavaram, Chennai (12.97, 80.15)

### Known Locality Validation

Cross-references 100+ Indian cities and suburbs:
- Chennai: Pallavaram, Chrompet, Tambaram, Velachery, Adyar, T Nagar, Anna Nagar
- Bangalore: Koramangala, Whitefield, Electronic City, HSR Layout, Indiranagar
- Mumbai: Andheri, Bandra, Powai, Juhu, Worli, Colaba
- And 70+ more localities

---

## Hazard Modules

### 1. Flood Risk (Weight: 0.18)
- **Data:** Open-Meteo rainfall, OSM waterbodies, SRTM elevation
- **Factors:** Waterbody proximity, annual rainfall, state flood risk, elevation
- **Evidence:** 16 disaster regions with historical flood data

### 2. Earthquake Risk (Weight: 0.16)
- **Data:** GSI named faults, IS 1893:2016 seismic zones
- **Factors:** Nearest fault distance, PGA calculation, state seismic zone
- **Evidence:** 25+ Indian fault lines with coordinates

### 3. Cyclone Risk (Weight: 0.10)
- **Data:** Open-Meteo marine, coastline points
- **Factors:** Coastal distance, wave height, state cyclone history
- **Evidence:** 8 cyclone-prone states with historical data

### 4. Landslide Risk (Weight: 0.09)
- **Data:** SRTM elevation, slope calculation, state susceptibility
- **Factors:** Slope angle, elevation, rainfall, hill state risk
- **Evidence:** Himachal, Uttarakhand, Northeast India data

### 5. Tsunami Risk (Weight: 0.06)
- **Data:** Open-Meteo marine, coastline points
- **Factors:** Coastal distance, wave height, historical tsunami data
- **Evidence:** 50+ coastal boundary points

### 6. Air Quality (Weight: 0.09)
- **Data:** Open-Meteo Air Quality API
- **Factors:** PM2.5, PM10, NO2, O3, European AQI conversion
- **Evidence:** Real-time street-level AQI data

### 7. Heat Stress (Weight: 0.07)
- **Data:** Open-Meteo Weather API
- **Factors:** Temperature, humidity, UV index, heatwave days
- **Evidence:** Actual weather data, not city averages

### 8. Groundwater (Weight: 0.08)
- **Data:** CGWB state-level data
- **Factors:** State groundwater availability, extraction rate
- **Evidence:** Central Ground Water Board data

### 9. Soil Quality (Weight: 0.07)
- **Data:** ISRIC SoilGrids API
- **Factors:** Clay%, sand%, organic carbon, pH
- **Evidence:** Real soil properties at depth layers

### 10. Industrial Pollution (Weight: 0.05)
- **Data:** OSM Overpass API, CPCB norms
- **Factors:** Industry distance, category (Red/Orange/Green)
- **Evidence:** CPCB mandated safe distances (500m/300m/200m)

### 11. Climate Projections (Weight: 0.05)
- **Data:** Open-Meteo Climate API (CMIP6)
- **Factors:** Temperature change, precipitation change by 2050
- **Evidence:** EC_Earth3P_HR model projections

---

## Legal Verification

### Autonomous Legal Checks (6 Types)

1. **Court Case Search** — Indian Kanoon API searches for active litigation on the property
2. **CRZ Verification** — Bhuvan WMS checks if property falls in CRZ zone
3. **RERA Registration** — Verifies builder RERA compliance
4. **Builder Blacklist Check** — Cross-references against known blacklisted builders
5. **Title Chain Analysis** — Automated title verification
6. **Encumbrance Check** — Checks for existing mortgages/encumbrances

### Document Upload + OCR

When no public API exists for a specific check:
- User uploads EC, deed, or title document
- OCR extracts text from document
- AI parses and verifies document authenticity
- Returns verification result

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Follow ESLint rules for TypeScript/React code
- Write meaningful commit messages
- Add comments for complex logic
- Update documentation for new features

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## Disclaimer

GeoSafe AI is for informational purposes only. It does not constitute professional advice, legal opinion, or investment recommendation. Always consult certified professionals (lawyers, structural engineers, environmental consultants) before making property investment decisions.

The platform uses publicly available data sources and AI analysis. While we strive for accuracy, data may be incomplete, outdated, or inaccurate. The developers assume no liability for decisions made based on this platform's output.

---

## Acknowledgments

- **Open-Meteo** — Free weather, air quality, climate, marine, and elevation APIs
- **OpenStreetMap** — Community-driven geographic data
- **ISRIC** — World Soil Information database
- **Indian Kanoon** — Indian court records database
- **ISRO Bhuvan** — Indian satellite imagery and CRZ data
- **Geological Survey of India** — Fault line data
- **NDMA** — National Disaster Management Authority data
- **CPCB** — Central Pollution Control Board norms

---

<p align="center">Built with care for Indian home buyers</p>
