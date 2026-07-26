"""
Precision geocoding for Indian addresses.
Returns exact building/street/locality coordinates, NOT city center.
Multi-strategy: address normalization, locality extraction, viewbox constraints.
"""
import re
import math
import httpx
from app.config import get_settings
from app.models.schemas import GeocodeResult

HEADERS = {
    "User-Agent": "GeoSafeAI/1.0 (India property safety platform; github.com/geosafe-ai)",
    "Accept": "application/json",
}

NOMINATIM_SEARCH = "https://nominatim.openstreetmap.org/search"
PHOTON_SEARCH = "https://photon.komoot.io/api/"

# Indian state abbreviations
_STATE_MAP = {
    "TN": "Tamil Nadu", "MH": "Maharashtra", "KA": "Karnataka",
    "DL": "Delhi", "GJ": "Gujarat", "AP": "Andhra Pradesh",
    "TS": "Telangana", "UP": "Uttar Pradesh", "RJ": "Rajasthan",
    "WB": "West Bengal", "KL": "Kerala", "MP": "Madhya Pradesh",
    "PB": "Punjab", "HR": "Haryana", "OR": "Odisha", "GA": "Goa",
    "HP": "Himachal Pradesh", "UK": "Uttarakhand", "SK": "Sikkim",
    "AS": "Assam", "ML": "Meghalaya", "MZ": "Mizoram",
    "MN": "Manipur", "NL": "Nagaland", "TR": "Tripura",
    "AR": "Arunachal Pradesh", "CG": "Chhattisgarh", "JH": "Jharkhand",
}

# Building/flat name patterns to strip
_BUILDING_PATTERNS = re.compile(
    r'\b(mk\s+flats?|flat\s*\d*|apt\s*\d*|apartment\s*\d*|'
    r'house\s*\d*|h\s*\d*|no\.?\s*\d+|door\s*\d*|'
    r'residency|enclave|complex|tower|block\s*[a-z]?\s*|'
    r'wing\s*[a-z]?\s*|floor\s*\d*|suite\s*\d*|'
    r'near|opp?\.?|behind|beside|next\s+to|adjacent\s+to|'
    r'in\s+front\s+of|opposite|behind)\b',
    re.IGNORECASE,
)

# Major Indian cities with approximate centers (for fallback only)
_CITY_CENTERS = {
    "chennai": (13.08, 80.27), "mumbai": (19.08, 72.88),
    "bengaluru": (12.97, 77.59), "bangalore": (12.97, 77.59),
    "hyderabad": (17.39, 78.49), "delhi": (28.61, 77.23),
    "kolkata": (22.57, 88.36), "pune": (18.52, 73.86),
    "ahmedabad": (23.02, 72.57), "jaipur": (26.91, 75.79),
    "lucknow": (26.85, 80.95), "kochi": (9.93, 76.27),
    "coimbatore": (11.01, 76.97), "madurai": (9.92, 78.12),
    "thiruvananthapuram": (8.52, 76.94), "nagpur": (21.15, 79.09),
    "indore": (22.72, 75.86), "bhopal": (23.26, 77.41),
    "patna": (25.60, 85.10), "visakhapatnam": (17.69, 83.22),
    "surat": (21.17, 72.83), "rajkot": (22.30, 70.80),
    "amritsar": (31.63, 74.87), "chandigarh": (30.73, 76.78),
    "guwahati": (26.14, 91.74), "dehradun": (30.32, 78.03),
    "shimla": (31.10, 77.17), "srinagar": (34.08, 74.80),
    "ranchi": (23.34, 85.31), "bhubaneswar": (20.30, 85.82),
    "vijayawada": (16.51, 80.63), "guntur": (16.31, 80.44),
    "tiruchirappalli": (10.79, 78.70), "salem": (11.66, 78.15),
    "tirunelveli": (8.71, 77.76), "mangalore": (12.91, 74.86),
    "hubli": (15.36, 75.12), "belgaum": (15.85, 74.50),
    "nashik": (19.99, 73.78), "aurangabad": (19.88, 75.34),
    "kolhapur": (16.70, 74.24), "solapur": (17.66, 75.91),
    "warangal": (17.98, 79.59), "nellore": (14.44, 79.99),
    "kanpur": (26.45, 80.35), "agra": (27.18, 78.02),
    "varanasi": (25.32, 83.01), "prayagraj": (25.44, 81.85),
    "jabalpur": (23.18, 79.95), "gwalior": (26.22, 78.18),
    "udaipur": (24.58, 73.68), "jodhpur": (26.24, 73.02),
    "cuttack": (20.46, 85.88), "puri": (19.81, 85.83),
    "palakkad": (10.78, 76.65), "thrissur": (10.52, 76.21),
    "kollam": (8.89, 76.61), "alappuzha": (9.50, 76.33),
    "malappuram": (11.06, 76.08), "kozhikode": (11.26, 75.78),
    "kannur": (11.87, 75.37), "sriperumbudur": (12.97, 79.94),
    "pallavaram": (12.97, 80.15), "chrompet": (12.95, 80.14),
    "tambaram": (12.92, 80.10), "sholinganallur": (12.90, 80.23),
    "velachery": (12.98, 80.22), "adyar": (13.01, 80.25),
    "t nagar": (13.04, 80.23), "anna nagar": (13.08, 80.21),
    "koramangala": (12.94, 77.62), "whitefield": (12.97, 77.75),
    "electronic city": (12.84, 77.65), "hsr layout": (12.91, 77.64),
    "indiranagar": (12.98, 77.64), "jayanagar": (12.93, 77.59),
    "basavanagudi": (12.94, 77.57), "malleshwaram": (13.01, 77.57),
    "rajajinagar": (13.01, 77.55), "vijayanagar": (12.98, 77.53),
    "andheri": (19.12, 72.83), "bandra": (19.06, 72.84),
    "powai": (19.12, 72.90), "juhu": (19.10, 72.83),
    "worli": (19.01, 72.82), "colaba": (18.92, 72.81),
    "andheri west": (19.14, 72.83), "andheri east": (19.12, 72.87),
    "borivali": (19.23, 72.85), "malad": (19.19, 72.85),
    "thane": (19.18, 72.96), "navi mumbai": (19.03, 73.03),
    "kalyan": (19.24, 73.13), "dombivli": (19.21, 73.09),
}


def _haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))


def _extract_locality_variants(address: str) -> list[str]:
    """
    Extract locality/area names from address and generate search variants.
    E.g., "mk flats pallava garden pallavaram chennai" → ["pallavaram chennai", "pallavaram", "chennai"]
    """
    addr = address.strip()
    parts = [p.strip() for p in re.split(r'[,\s]+', addr) if p.strip()]

    # Find known city name in address
    city = None
    for c in sorted(_CITY_CENTERS.keys(), key=len, reverse=True):
        if c in addr.lower():
            city = c
            break

    # Strip building/flat names
    stripped = _BUILDING_PATTERNS.sub("", addr)
    stripped = re.sub(r'\s+', ' ', stripped).strip()

    # Extract parts that are NOT building names
    meaningful_parts = []
    for p in parts:
        if not _BUILDING_PATTERNS.match(p) and not p.isdigit():
            meaningful_parts.append(p)

    variants = []

    # 1. Try original address as-is
    variants.append(addr)

    # 2. Try stripped version (without building names)
    if stripped and stripped != addr:
        variants.append(stripped)

    # 3. Try last 3 meaningful parts (locality + city + state)
    if len(meaningful_parts) >= 3:
        variants.append(" ".join(meaningful_parts[-3:]))

    # 4. Try last 2 meaningful parts (locality + city)
    if len(meaningful_parts) >= 2:
        variants.append(" ".join(meaningful_parts[-2:]))

    # 5. Try locality name + city (if we found a city)
    if city and len(meaningful_parts) >= 2:
        # Find the part before city name
        city_idx = None
        for i, p in enumerate(meaningful_parts):
            if p.lower() == city:
                city_idx = i
                break
        if city_idx and city_idx > 0:
            locality = meaningful_parts[city_idx - 1]
            variants.append(f"{locality} {city}")

    # 6. Try just locality name (if it's not the city)
    if len(meaningful_parts) >= 2:
        for p in meaningful_parts[:-1]:
            if p.lower() != city and len(p) > 2:
                variants.append(p)
                if city:
                    variants.append(f"{p} {city}")

    # 7. If we have a city, try city + state
    if city:
        variants.append(f"{city} india")

    # Deduplicate
    seen = set()
    unique = []
    for v in variants:
        v_lower = v.lower().strip()
        if v_lower not in seen and len(v_lower) > 2:
            seen.add(v_lower)
            unique.append(v)

    return unique


def _parse_nominatim(r: dict, fallback_address: str) -> GeocodeResult:
    addr = r.get("address", {})
    return GeocodeResult(
        address=r.get("display_name", fallback_address),
        lat=float(r["lat"]),
        lon=float(r["lon"]),
        city=(
            addr.get("city") or addr.get("town") or
            addr.get("village") or addr.get("district") or
            addr.get("county") or ""
        ),
        state=addr.get("state", ""),
        country=addr.get("country", "India"),
    )


async def _nominatim_search(query: str, countrycodes: str = "in", limit: int = 5) -> list[dict]:
    """Search Nominatim with a query string."""
    params = {
        "q": query, "format": "json",
        "addressdetails": 1, "limit": limit,
    }
    if countrycodes:
        params["countrycodes"] = countrycodes

    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            resp = await client.get(NOMINATIM_SEARCH, params=params, headers=HEADERS)
            if resp.status_code == 200:
                return resp.json()
    except Exception:
        pass
    return []


def _pick_best_result(results: list[dict], original_address: str) -> dict | None:
    """Pick the most specific result from Nominatim matches."""
    if not results:
        return None

    def specificity(r):
        score = 0
        rtype = r.get("type", "")
        # Prefer specific types
        if rtype in ("house", "building", "apartments"):
            score += 100
        elif rtype in ("residential", "neighbourhood", "suburb"):
            score += 80
        elif rtype in ("road", "footway", "path"):
            score += 70
        elif rtype in ("stop", "bus_stop", "station"):
            score += 60
        elif rtype in ("city", "town", "village"):
            score += 40
        elif rtype in ("state", "country"):
            score += 10
        # Boost by importance
        score += r.get("importance", 0) * 20
        return score

    return max(results, key=specificity)


def _get_expected_localities(address: str) -> set[str]:
    """
    Extract known locality names mentioned in the original address.
    Returns set of locality names that MUST appear in the geocoded result.
    """
    addr_lower = address.lower()
    expected = set()
    for city in sorted(_CITY_CENTERS.keys(), key=len, reverse=True):
        if len(city) >= 5 and city in addr_lower:
            expected.add(city)
    return expected


def _result_matches_localities(display_name: str, expected: set[str]) -> bool:
    """
    Check if the geocoded result contains the expected locality names.
    Requires at least one NON-city locality match if expected has multiple entries.
    Returns True if expected is empty, or if result contains a specific locality.
    """
    if not expected:
        return True
    name_lower = display_name.lower()
    # If we have city AND a more specific locality, the specific locality must appear
    city_names = {"chennai", "mumbai", "bengaluru", "bangalore", "hyderabad", "delhi",
                  "kolkata", "pune", "ahmedabad", "jaipur", "lucknow", "kochi",
                  "coimbatore", "madurai", "thiruvananthapuram", "nagpur", "indore",
                  "bhopal", "patna", "visakhapatnam", "surat", "rajkot", "amritsar",
                  "chandigarh", "guwahati", "dehradun", "shimla", "srinagar",
                  "ranchi", "bhubaneswar", "vijayawada", "guntur", "tiruchirappalli",
                  "salem", "tirunelveli", "mangalore", "hubli", "belgaum", "nashik",
                  "aurangabad", "kolhapur", "solapur", "warangal", "nellore",
                  "kanpur", "agra", "varanasi", "prayagraj", "jabalpur", "gwalior",
                  "udaipur", "jodhpur", "cuttack", "puri", "palakkad", "thrissur",
                  "kollam", "alappuzha", "malappuram", "kozhikode", "kannur"}
    specific = expected - city_names
    if specific:
        return any(loc in name_lower for loc in specific)
    return any(loc in name_lower for loc in expected)


def _is_known_locality_match(display_name: str, lat: float, lon: float) -> tuple[float, float] | None:
    """
    Check if the geocoded result's display name contains a known locality
    from _CITY_CENTERS. If so, return the known coordinates for better precision.
    Returns (lat, lon) if match found, else None.
    """
    name_lower = display_name.lower()
    # Sort by length descending to match longer names first (e.g., "anna nagar" before "nagar")
    for city, (clat, clon) in sorted(_CITY_CENTERS.items(), key=lambda x: len(x[0]), reverse=True):
        if len(city) >= 5 and city in name_lower:
            # Check if the result is within 2km of known center
            dist = _haversine_km(lat, lon, clat, clon)
            if dist < 2.0:
                return (clat, clon)
    return None


async def geocode_address(address: str) -> GeocodeResult:
    """
    Precision geocoding for Indian addresses.
    Returns exact locality/street coordinates, NOT city center.
    """
    variants = _extract_locality_variants(address)
    expected_localities = _get_expected_localities(address)

    # Strategy 1: Try each variant with India filter
    for variant in variants[:5]:
        results = await _nominatim_search(variant, countrycodes="in", limit=3)
        best = _pick_best_result(results, address)
        if best:
            parsed = _parse_nominatim(best, address)
            # Skip if address mentions a known locality but result doesn't match
            if expected_localities and not _result_matches_localities(parsed.address, expected_localities):
                continue
            # Check if result matches a known locality for better precision
            known_match = _is_known_locality_match(parsed.address, parsed.lat, parsed.lon)
            if known_match:
                return GeocodeResult(
                    address=parsed.address, lat=known_match[0], lon=known_match[1],
                    city=parsed.city, state=parsed.state, country=parsed.country,
                )
            return parsed

    # Strategy 2: Try without country filter (global search)
    for variant in variants[:3]:
        results = await _nominatim_search(variant, countrycodes="", limit=3)
        best = _pick_best_result(results, address)
        if best:
            parsed = _parse_nominatim(best, address)
            if expected_localities and not _result_matches_localities(parsed.address, expected_localities):
                continue
            known_match = _is_known_locality_match(parsed.address, parsed.lat, parsed.lon)
            if known_match:
                return GeocodeResult(
                    address=parsed.address, lat=known_match[0], lon=known_match[1],
                    city=parsed.city, state=parsed.state, country=parsed.country,
                )
            return parsed

    # Strategy 3: Photon fallback
    for variant in variants[:3]:
        try:
            params = {"q": variant, "limit": 3, "lang": "en"}
            async with httpx.AsyncClient(timeout=8, follow_redirects=True) as client:
                resp = await client.get(PHOTON_SEARCH, params=params, headers=HEADERS)
                if resp.status_code == 200:
                    features = resp.json().get("features", [])
                    for f in features:
                        props = f.get("properties", {})
                        coords = f.get("geometry", {}).get("coordinates", [None, None])
                        lon, lat = coords[0], coords[1]
                        if lat and lon:
                            display_name = ", ".join(filter(None, [
                                props.get("name"), props.get("housenumber"),
                                props.get("street"),
                                props.get("city") or props.get("town"),
                                props.get("state"), props.get("country")
                            ])) or address
                            # Skip if expected locality not in result
                            if expected_localities and not _result_matches_localities(display_name, expected_localities):
                                continue
                            # Check known locality match
                            known_match = _is_known_locality_match(display_name, float(lat), float(lon))
                            if known_match:
                                return GeocodeResult(
                                    address=display_name, lat=known_match[0], lon=known_match[1],
                                    city=props.get("city") or props.get("town") or "",
                                    state=props.get("state", ""),
                                    country=props.get("country", "India"),
                                )
                            return GeocodeResult(
                                address=display_name,
                                lat=float(lat), lon=float(lon),
                                city=props.get("city") or props.get("town") or "",
                                state=props.get("state", ""),
                                country=props.get("country", "India"),
                            )
        except Exception:
            pass

    # Strategy 4: Google Geocoding (if key available)
    api_key = get_settings().google_maps_api_key
    if api_key:
        try:
            params = {"address": address, "key": api_key, "region": "in"}
            async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
                resp = await client.get(
                    "https://maps.googleapis.com/maps/api/geocode/json",
                    params=params,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("status") == "OK" and data.get("results"):
                        r = data["results"][0]
                        loc = r["geometry"]["location"]
                        addr_parts = r.get("address_components", [])
                        city = state = ""
                        for comp in addr_parts:
                            types = comp.get("types", [])
                            if "locality" in types or "administrative_area_level_2" in types:
                                city = comp.get("long_name", "")
                            if "administrative_area_level_1" in types:
                                state = comp.get("long_name", "")
                        display_addr = r.get("formatted_address", address)
                        if expected_localities and not _result_matches_localities(display_addr, expected_localities):
                            pass
                        else:
                            known_match = _is_known_locality_match(display_addr, loc["lat"], loc["lng"])
                            if known_match:
                                return GeocodeResult(
                                    address=display_addr, lat=known_match[0], lon=known_match[1],
                                    city=city, state=state, country="India",
                                )
                            return GeocodeResult(
                                address=display_addr,
                                lat=float(loc["lat"]), lon=float(loc["lng"]),
                                city=city, state=state, country="India",
                            )
        except Exception:
            pass

    # Strategy 5: City center fallback (with warning)
    addr_lower = address.lower()
    for city, (clat, clon) in _CITY_CENTERS.items():
        if city in addr_lower:
            return GeocodeResult(
                address=f"{address} (⚠️ Exact location not found — showing {city} center)",
                lat=clat, lon=clon,
                city=city.title(), state="", country="India",
            )

    raise ValueError(
        f"Could not find '{address}' on the map. Try: "
        f"(1) Remove flat/building names, keep locality + city, "
        f"(2) Use GPS coordinates (lat, lon), "
        f"or (3) Use a nearby landmark."
    )


async def reverse_geocode(lat: float, lon: float) -> GeocodeResult:
    """Reverse geocode lat/lon with Nominatim."""
    params = {"lat": lat, "lon": lon, "format": "json", "addressdetails": 1}
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            resp = await client.get(
                "https://nominatim.openstreetmap.org/reverse",
                params=params, headers=HEADERS,
            )
            if resp.status_code == 200:
                r = resp.json()
                addr = r.get("address", {})
                return GeocodeResult(
                    address=r.get("display_name", f"{lat:.4f}, {lon:.4f}"),
                    lat=lat, lon=lon,
                    city=(
                        addr.get("city") or addr.get("town") or
                        addr.get("village") or addr.get("county") or ""
                    ),
                    state=addr.get("state", ""),
                    country=addr.get("country", "India"),
                )
    except Exception:
        pass

    return GeocodeResult(
        address=f"{lat:.4f}, {lon:.4f}",
        lat=lat, lon=lon, city="", state="", country="India"
    )
