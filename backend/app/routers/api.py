"""FastAPI routers for all API endpoints with JSON file persistence cache."""
import json
import os
from pathlib import Path
from fastapi import APIRouter, HTTPException, Response
from app.models.schemas import (
    AnalyzeRequest, AnalysisResult, CompareRequest,
    ChatRequest, ChatResponse, GeocodeResult
)
from app.utils.geocoder import geocode_address, reverse_geocode
from app.services.mcda_engine import run_full_analysis
from app.services.llm_service import generate_chat_response
from app.services.report_generator import generate_pdf_report
from app.services.osm_geometry import fetch_building_footprints, fetch_road_buffer

router = APIRouter()

CACHE_FILE = Path(__file__).parent.parent.parent / "data_cache.json"
_cache: dict[str, AnalysisResult] = {}


def _load_cache():
    global _cache
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                for item_id, item_dict in raw_data.items():
                    _cache[item_id] = AnalysisResult.model_validate(item_dict)
        except Exception:
            _cache = {}


def _save_cache():
    try:
        raw_data = {k: v.model_dump(mode="json") for k, v in _cache.items()}
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(raw_data, f, indent=2)
    except Exception:
        pass


# Load cache on module import
_load_cache()


@router.get("/health")
async def health():
    return {"status": "ok", "service": "GeoSafe AI Backend", "cached_items": len(_cache)}


@router.get("/geocode")
async def geocode(address: str) -> GeocodeResult:
    try:
        return await geocode_address(address)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/analyze")
async def analyze_property(req: AnalyzeRequest) -> AnalysisResult:
    try:
        if req.lat and req.lon:
            geo = await reverse_geocode(req.lat, req.lon)
            lat, lon = req.lat, req.lon
            import re
            is_coord = bool(re.match(r"^-?\d+\.?\d*,\s*-?\d+\.?\d*$", req.address.strip())) if req.address else False
            address = geo.address if (not req.address or is_coord) else req.address
            city, state = geo.city, geo.state
        else:
            geo = await geocode_address(req.address)
            lat, lon = geo.lat, geo.lon
            address, city, state = geo.address, geo.city, geo.state

        result = await run_full_analysis(lat, lon, address, city, state)
        _cache[result.id] = result
        _save_cache()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/analyze/{analysis_id}")
async def get_analysis(analysis_id: str) -> AnalysisResult:
    if analysis_id not in _cache:
        _load_cache()  # Reload in case saved by another process
    if analysis_id not in _cache:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return _cache[analysis_id]


@router.post("/compare")
async def compare_properties(req: CompareRequest) -> list[AnalysisResult]:
    import asyncio
    tasks = [
        analyze_property(AnalyzeRequest(
            address=p.address, lat=p.lat, lon=p.lon
        ))
        for p in req.properties
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    valid = [r for r in results if isinstance(r, AnalysisResult)]
    if not valid:
        raise HTTPException(status_code=400, detail="All property analyses failed")
    return valid


@router.post("/chat")
async def chat(req: ChatRequest) -> ChatResponse:
    ctx = req.analysis_context or {}
    if req.analysis_id and req.analysis_id in _cache:
        cached = _cache[req.analysis_id]
        ctx = {
            "address": cached.address,
            "city": cached.city,
            "state": cached.state,
            "safety_score": cached.safety_score,
            "decision": cached.decision.value,
            "hazards": {
                "flood": {"score": cached.flood_risk.score, "level": cached.flood_risk.level.value},
                "earthquake": {"score": cached.earthquake_risk.score, "level": cached.earthquake_risk.level.value},
                "cyclone": {"score": cached.cyclone_risk.score, "level": cached.cyclone_risk.level.value},
                "air_quality": {"score": cached.air_quality.score, "level": cached.air_quality.level.value},
                "climate": {"score": cached.climate_future.score, "level": cached.climate_future.level.value},
            },
            "flood_detail": cached.flood_risk.details,
            "earthquake_detail": cached.earthquake_risk.details,
            "air_detail": cached.air_quality.details,
            "climate_detail": cached.climate_future.details,
        }
    reply = await generate_chat_response(req.message, ctx)
    return ChatResponse(reply=reply)


@router.post("/report/generate/{analysis_id}")
async def generate_report(analysis_id: str):
    if analysis_id not in _cache:
        _load_cache()
    if analysis_id not in _cache:
        raise HTTPException(status_code=404, detail="Analysis not found. Run /analyze first.")
    result = _cache[analysis_id]
    pdf_bytes = await generate_pdf_report(result)

    content_type = "application/pdf"
    filename = f"geosafe_report_{analysis_id[:8]}.pdf"
    if not pdf_bytes[:4] == b"%PDF":
        content_type = "text/html"
        filename = filename.replace(".pdf", ".html")

    return Response(
        content=pdf_bytes,
        media_type=content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/map-features")
async def get_map_features(lat: float, lon: float, radius: int = 450, safety_score: float = 65, address: str = None):
    """Fetch real OSM building footprints & road geometries with per-feature micro-scores."""
    try:
        query_type = "area"
        if address:
            addr_lower = address.lower().strip()
            parts = [p.strip() for p in addr_lower.split(",")]
            if len(parts) <= 2:
                query_type = "city"
            else:
                street_keywords = {
                    "road", "street", "st", "rd", "lane", "ln", "avenue", "ave", "cross", 
                    "main", "highway", "building", "house", "plot", "flat", "door", "no.", 
                    "no:", "shop", "floor", "block", "sector", "layout"
                }
                words = addr_lower.replace(",", " ").replace(".", " ").split()
                has_digits = any(any(c.isdigit() for c in w) for w in words)
                has_street_kw = any(w in street_keywords for w in words)
                if has_digits or has_street_kw:
                    query_type = "plot_or_street"

        import asyncio
        buildings, roads = await asyncio.gather(
            fetch_building_footprints(lat, lon, radius_m=radius, base_score=safety_score, query_type=query_type, address=address or ""),
            fetch_road_buffer(lat, lon, base_score=safety_score, query_type=query_type, address=address or ""),
            return_exceptions=True
        )
        b_features = buildings.get("features", []) if isinstance(buildings, dict) else []
        r_features = roads.get("features", []) if isinstance(roads, dict) else []
        combined_features = b_features + r_features
        return {"type": "FeatureCollection", "features": combined_features}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch map features: {str(e)}")
