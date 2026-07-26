"""
Earthquake Risk Assessment – India Seismic Zone based (IS 1893:2016)
Data: NCS India seismic zone map, USGS earthquake catalog
"""
import httpx
from app.models.schemas import HazardScore, RiskLevel
from app.utils.india_data import STATE_SEISMIC_ZONE


async def fetch_recent_earthquakes(lat: float, lon: float) -> list[dict]:
    """Fetch recent earthquakes within 200km from USGS API."""
    try:
        url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
        params = {
            "format": "geojson",
            "latitude": lat,
            "longitude": lon,
            "maxradiuskm": 200,
            "minmagnitude": 3.5,
            "limit": 10,
            "orderby": "time",
        }
        async with httpx.AsyncClient(timeout=8) as c:
            r = await c.get(url, params=params)
            data = r.json()
            return data.get("features", [])
    except Exception:
        return []


async def calculate_earthquake_risk(lat: float, lon: float, state: str) -> HazardScore:
    state_lower = state.lower()
    zone = STATE_SEISMIC_ZONE.get(state_lower, 3)

    # Zone-based base risk
    zone_risk = {2: 15, 3: 40, 4: 65, 5: 85}
    base_score = zone_risk.get(zone, 40)
    zone_names = {2: "Low", 3: "Moderate", 4: "High", 5: "Very High"}
    zone_name = zone_names.get(zone, "Moderate")

    factors = [f"IS 1893 Seismic Zone {zone} ({zone_name} hazard) for {state}"]

    # Adjust for Himalayan proximity (high seismicity)
    if lat > 28 and (lon < 78 or (lon > 93 and lon < 98)):
        base_score = min(100, base_score + 15)
        factors.append("Proximity to Himalayan seismic belt increases risk")

    # Check recent earthquake activity
    recent = await fetch_recent_earthquakes(lat, lon)
    if recent:
        magnitudes = [f["properties"]["mag"] for f in recent if f["properties"].get("mag")]
        max_mag = max(magnitudes) if magnitudes else 0
        if max_mag >= 5.5:
            base_score = min(100, base_score + 12)
            factors.append(f"Recent significant earthquake (M{max_mag:.1f}) within 200km")
        elif max_mag >= 4.5:
            base_score = min(100, base_score + 6)
            factors.append(f"Recent moderate earthquake (M{max_mag:.1f}) within 200km")
        elif magnitudes:
            factors.append(f"Minor seismic activity recorded (M{max_mag:.1f}) nearby")
    else:
        factors.append("No significant recent earthquakes (>M3.5) within 200km")

    # Liquefaction potential for flat plains
    if 24 < lat < 30 and 75 < lon < 88:
        base_score = min(100, base_score + 5)
        factors.append("Indo-Gangetic alluvial plain – moderate liquefaction potential")

    score = round(base_score, 1)

    if score >= 70:
        level = RiskLevel.VERY_HIGH
        detail = f"Very high seismic risk. Zone {zone} ({zone_name}) per IS 1893. Earthquake-resistant construction is mandatory."
    elif score >= 50:
        level = RiskLevel.HIGH
        detail = f"High seismic risk in Zone {zone} ({zone_name}). Reinforced structures required per BIS codes."
    elif score >= 35:
        level = RiskLevel.MODERATE
        detail = f"Moderate seismic zone (Zone {zone}). Standard earthquake-resistant construction recommended."
    elif score >= 20:
        level = RiskLevel.LOW
        detail = f"Low seismic risk (Zone {zone}). Basic BIS earthquake design norms apply."
    else:
        level = RiskLevel.VERY_LOW
        detail = f"Very low seismic risk (Zone {zone}). Minimal earthquake hazard in this region."

    return HazardScore(score=score, level=level, details=detail, contributing_factors=factors)
