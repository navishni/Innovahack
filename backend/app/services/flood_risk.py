"""
Flood Risk Assessment Module
Sources: SRTM elevation (OpenTopoData), OpenWeatherMap, India state flood data
Method: Multi-criteria analysis on elevation, rainfall, river proximity, state risk
"""
import httpx
import math
from app.models.schemas import HazardScore, RiskLevel
from app.utils.india_data import FLOOD_PRONE_STATES, STATE_ANNUAL_RAINFALL, MAJOR_RIVERS


async def fetch_elevation(lat: float, lon: float) -> float:
    """Get elevation in metres from OpenTopoData (SRTM30m)."""
    try:
        url = f"https://api.opentopodata.org/v1/srtm30m?locations={lat},{lon}"
        async with httpx.AsyncClient(timeout=8) as c:
            r = await c.get(url)
            data = r.json()
            return float(data["results"][0]["elevation"] or 50)
    except Exception:
        # Fallback: estimate from lat (coastal areas tend to be lower)
        return _estimate_elevation_fallback(lat, lon)


def _estimate_elevation_fallback(lat: float, lon: float) -> float:
    """Heuristic elevation estimate based on geography."""
    # Mountain regions
    if lat > 30 and lon < 80:
        return 2000 + (lat - 30) * 200
    # Northeast hills
    if lat > 24 and lon > 90:
        return 500 + (lat - 24) * 100
    # Coastal regions
    if lon < 73 or lon > 87 or lat < 12:
        return 15
    # Deccan plateau
    if 15 < lat < 22 and 73 < lon < 82:
        return 400
    # Indo-Gangetic plain
    if 24 < lat < 30 and 75 < lon < 88:
        return 100
    return 150


def _river_proximity_risk(lat: float, lon: float) -> float:
    """Returns 0-1 based on proximity to major rivers."""
    min_dist = float("inf")
    for river in MAJOR_RIVERS:
        lat_mid = sum(river["lat_range"]) / 2
        lon_mid = sum(river["lon_range"]) / 2
        if (river["lat_range"][0] <= lat <= river["lat_range"][1] and
                river["lon_range"][0] <= lon <= river["lon_range"][1]):
            # Within river corridor
            dist = math.sqrt((lat - lat_mid)**2 + (lon - lon_mid)**2)
            min_dist = min(min_dist, dist)

    if min_dist == float("inf"):
        return 0.1
    if min_dist < 0.5:
        return 0.9
    if min_dist < 1.5:
        return 0.6
    if min_dist < 3:
        return 0.4
    return 0.2


async def calculate_flood_risk(lat: float, lon: float, state: str, city: str) -> HazardScore:
    elevation = await fetch_elevation(lat, lon)
    state_lower = state.lower()
    
    # 1. Elevation factor (0-40 pts risk)
    if elevation < 5:
        elev_risk = 95
        elev_factor = "Extremely low elevation (< 5m) – severe flood exposure"
    elif elevation < 15:
        elev_risk = 75
        elev_factor = "Very low elevation (< 15m) – high flood vulnerability"
    elif elevation < 30:
        elev_risk = 55
        elev_factor = "Low elevation – moderate flood risk"
    elif elevation < 100:
        elev_risk = 30
        elev_factor = f"Moderate elevation ({elevation:.0f}m) – limited flood risk"
    elif elevation < 500:
        elev_risk = 15
        elev_factor = f"Good elevation ({elevation:.0f}m) – low flood risk"
    else:
        elev_risk = 5
        elev_factor = f"High elevation ({elevation:.0f}m) – very low flood risk"

    # 2. State flood proneness (0-30 pts)
    state_risk = 70 if state_lower in FLOOD_PRONE_STATES else 20
    state_factor = f"State ({state}) is {'flood-prone' if state_lower in FLOOD_PRONE_STATES else 'not a major flood zone'}"

    # 3. Annual rainfall (0-20 pts)
    rainfall = STATE_ANNUAL_RAINFALL.get(state_lower, 1000)
    if rainfall > 3000:
        rain_risk = 90
        rain_factor = f"Very high annual rainfall ({rainfall}mm) – drainage stress risk"
    elif rainfall > 1500:
        rain_risk = 60
        rain_factor = f"High annual rainfall ({rainfall}mm)"
    elif rainfall > 800:
        rain_risk = 35
        rain_factor = f"Moderate annual rainfall ({rainfall}mm)"
    else:
        rain_risk = 15
        rain_factor = f"Low annual rainfall ({rainfall}mm) – low rainfall-driven flood risk"

    # 4. River proximity (0-10 pts)
    river_risk_val = _river_proximity_risk(lat, lon)
    river_factor = f"River proximity index: {river_risk_val:.2f}"

    # Weighted score
    score = (
        elev_risk * 0.40 +
        state_risk * 0.25 +
        rain_risk * 0.25 +
        river_risk_val * 100 * 0.10
    )
    score = min(100, max(0, score))

    factors = [elev_factor, state_factor, rain_factor, river_factor]

    if score >= 70:
        level = RiskLevel.VERY_HIGH
        detail = f"Flood risk is very high. Elevation: {elevation:.0f}m, Rainfall: {rainfall}mm/yr. Property is in a flood-vulnerable zone."
    elif score >= 50:
        level = RiskLevel.HIGH
        detail = f"Significant flood risk. Low elevation ({elevation:.0f}m) and high rainfall ({rainfall}mm/yr) increase vulnerability."
    elif score >= 35:
        level = RiskLevel.MODERATE
        detail = f"Moderate flood risk. Elevation {elevation:.0f}m provides some protection but seasonal flooding possible."
    elif score >= 20:
        level = RiskLevel.LOW
        detail = f"Low flood risk. Elevation {elevation:.0f}m and moderate rainfall ({rainfall}mm/yr) indicate manageable risk."
    else:
        level = RiskLevel.VERY_LOW
        detail = f"Very low flood risk. High elevation ({elevation:.0f}m) and low rainfall ensure excellent flood safety."

    return HazardScore(score=round(score, 1), level=level, details=detail, contributing_factors=factors)
