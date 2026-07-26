"""
Cyclone & Tsunami Risk – India coastline analysis
Sources: IMD cyclone track database, IBTrACS, coastal distance estimation
"""
import math
from app.models.schemas import HazardScore, RiskLevel
from app.utils.india_data import COASTAL_STATES, CYCLONE_RISK_COASTAL


# Approximate India coastline reference points for coastal distance estimation
INDIA_COASTLINE_POINTS = [
    (8.07, 77.55), (9.9, 78.1), (10.8, 79.8), (11.9, 79.8),
    (13.1, 80.3), (14.8, 80.0), (16.5, 81.8), (17.7, 83.3),
    (19.3, 84.8), (20.3, 86.7), (21.5, 87.1), (21.9, 88.1),
    (22.5, 88.5), (8.5, 76.9), (9.5, 76.3), (10.9, 75.6),
    (12.9, 74.8), (14.8, 74.1), (15.4, 73.9), (16.9, 73.6),
    (18.9, 72.8), (20.0, 72.8), (21.6, 72.5), (22.8, 72.6),
    (23.6, 68.4), (22.2, 68.9), (20.9, 70.5),
]


def _min_coastal_distance_km(lat: float, lon: float) -> float:
    """Estimate minimum distance to India's coastline in km."""
    min_dist = float("inf")
    for clat, clon in INDIA_COASTLINE_POINTS:
        # Haversine distance
        dlat = math.radians(lat - clat)
        dlon = math.radians(lon - clon)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(clat)) * math.cos(math.radians(lat)) * math.sin(dlon/2)**2
        dist = 2 * 6371 * math.asin(math.sqrt(a))
        min_dist = min(min_dist, dist)
    return min_dist


async def calculate_cyclone_risk(lat: float, lon: float, state: str) -> HazardScore:
    state_lower = state.lower()
    coastal_dist = _min_coastal_distance_km(lat, lon)
    factors = []

    is_coastal = state_lower in COASTAL_STATES or coastal_dist < 150

    if not is_coastal and coastal_dist > 300:
        return HazardScore(
            score=8.0,
            level=RiskLevel.VERY_LOW,
            details="Property is inland (>300km from coast). Cyclone risk is negligible.",
            contributing_factors=[
                f"Distance from coast: ~{coastal_dist:.0f}km",
                f"State ({state}) is not in a coastal cyclone zone"
            ]
        )

    # Base cyclone risk from state history
    base_cyclone = CYCLONE_RISK_COASTAL.get(state_lower, 30)
    factors.append(f"Historical cyclone frequency for {state}: {base_cyclone}/100")

    # Coastal proximity scaling
    if coastal_dist < 10:
        prox_factor = 1.0
        factors.append(f"Property is very close to coast ({coastal_dist:.1f}km) – direct cyclone exposure")
    elif coastal_dist < 50:
        prox_factor = 0.85
        factors.append(f"Within 50km of coast – high cyclone exposure")
    elif coastal_dist < 100:
        prox_factor = 0.65
        factors.append(f"Within 100km of coast – moderate cyclone exposure")
    elif coastal_dist < 200:
        prox_factor = 0.4
        factors.append(f"Within 200km of coast – limited cyclone wind risk")
    else:
        prox_factor = 0.2
        factors.append(f"~{coastal_dist:.0f}km inland – residual cyclone wind risk")

    # Bay of Bengal is more active than Arabian Sea
    if lon > 80:  # Bay of Bengal coast
        base_cyclone = min(100, base_cyclone * 1.15)
        factors.append("Bay of Bengal coastline – historically more cyclone-active than Arabian Sea")

    score = round(base_cyclone * prox_factor, 1)
    score = min(100, max(0, score))

    if score >= 65:
        level = RiskLevel.VERY_HIGH
        detail = f"Very high cyclone risk. Coastal proximity ({coastal_dist:.0f}km) and historical storm frequency demand storm-resistant construction."
    elif score >= 45:
        level = RiskLevel.HIGH
        detail = f"High cyclone risk for this coastal location. Wind-resistant roofing and storm shutters are essential."
    elif score >= 25:
        level = RiskLevel.MODERATE
        detail = f"Moderate cyclone exposure. Property is {coastal_dist:.0f}km from coast. Standard wind-load design norms apply."
    elif score >= 15:
        level = RiskLevel.LOW
        detail = "Low cyclone risk. Inland location provides reasonable protection from cyclonic storms."
    else:
        level = RiskLevel.VERY_LOW
        detail = "Very low cyclone risk. Distance from coast makes direct cyclone impact very unlikely."

    return HazardScore(score=score, level=level, details=detail, contributing_factors=factors)


async def calculate_tsunami_risk(lat: float, lon: float, state: str) -> HazardScore:
    """Tsunami risk based on coastal proximity and Bay of Bengal / Indian Ocean exposure."""
    coastal_dist = _min_coastal_distance_km(lat, lon)
    state_lower = state.lower()

    # High tsunami risk states (Indian Ocean/Bay of Bengal facing)
    high_tsunami = {"andaman and nicobar islands", "tamil nadu", "andhra pradesh", "odisha", "kerala"}
    medium_tsunami = {"west bengal", "lakshadweep", "pondicherry"}

    if coastal_dist > 50:
        return HazardScore(
            score=5.0,
            level=RiskLevel.VERY_LOW,
            details=f"Property is ~{coastal_dist:.0f}km inland. Tsunami inundation risk is negligible.",
            contributing_factors=[f"Coastal distance: {coastal_dist:.0f}km (>50km threshold for negligible risk)"]
        )

    if state_lower in high_tsunami:
        base = 60
        factor_str = f"{state} faces Indian Ocean / Bay of Bengal – historical tsunami exposure (2004 event)"
    elif state_lower in medium_tsunami:
        base = 35
        factor_str = f"{state} has moderate tsunami exposure history"
    else:
        base = 20
        factor_str = f"{state} coastal zone – limited historical tsunami record"

    # Elevation correction: coastal elevation matters
    prox_penalty = max(0, (50 - coastal_dist) / 50)
    score = round(base * (0.6 + 0.4 * prox_penalty), 1)

    if score >= 50:
        level = RiskLevel.HIGH
        detail = f"High tsunami risk. Coastal location in {state} with Indian Ocean exposure requires elevated construction."
    elif score >= 30:
        level = RiskLevel.MODERATE
        detail = f"Moderate tsunami risk. {coastal_dist:.0f}km from coast in historically exposed region."
    else:
        level = RiskLevel.LOW
        detail = f"Low tsunami risk. Limited historical tsunami events in this coastal segment."

    return HazardScore(
        score=score, level=level, details=detail,
        contributing_factors=[factor_str, f"Coastal distance: {coastal_dist:.1f}km"]
    )
