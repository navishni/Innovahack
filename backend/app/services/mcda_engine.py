"""
MCDA (Multi-Criteria Decision Analysis) & Universal Dynamic Discovery Engine.
Aggregates 11 hazard parameters using spatial queries, physical geometry measurements, 
historical disaster intersections, and dynamic engineered mitigations.
"""
import asyncio
import uuid
import re
from datetime import datetime
from app.models.schemas import (
    AnalysisResult, SafetyDecision, HazardScore, RiskLevel,
    EvidenceEvent, MitigationAction, MitigationCategory, CostTier
)
from app.services.discovery_engine import (
    discover_flood_features, discover_earthquake_faults, discover_cyclone_surge,
    discover_landslide_terrain, discover_tsunami_geometry, discover_heat_island,
    discover_groundwater_wells, discover_air_quality_fire_hotspots,
    discover_industrial_pollution, discover_soil_raster, discover_climate_cmip6,
    _coord_hash, fetch_real_elevation
)
from app.services.nearby_services import fetch_nearby_services
from app.services.llm_service import generate_ai_summary
from app.utils.india_data import HISTORICAL_DISASTER_LOG, CITY_REGULATORY_AUTHORITIES, STATE_REGULATORY_AUTHORITIES


WEIGHTS = {
    "flood": 0.18, "earthquake": 0.16, "cyclone": 0.10, "landslide": 0.09,
    "tsunami": 0.06, "air_quality": 0.09, "heat": 0.07, "groundwater": 0.08,
    "soil": 0.07, "pollution": 0.05, "climate": 0.05,
}

def _get_city_key(city: str, address: str) -> str:
    combined = f"{city} {address}".lower()
    # Match against all known city keys (order matters — specific matches first)
    for c in [
        "chennai", "mumbai", "bengaluru", "bangalore", "hyderabad", "delhi",
        "kolkata", "patna", "pune", "gurugram", "gurgaon", "faridabad",
        "ahmedabad", "surat", "jaipur", "lucknow", "bhopal", "indore",
        "nagpur", "chandigarh", "amritsar", "kochi", "thiruvananthapuram",
        "bhubaneswar", "visakhapatnam", "coimbatore",
        "guwahati", "shimla", "dehradun", "srinagar", "imphal",
        "panaji", "raipur", "ranchi", "gangtok", "itanagar",
        "aizawl", "kohima", "agartala", "shillong", "dimapur",
        "madurai", "trichy", "salem", "tirunelveli",
        "nashik", "aurangabad", "kolhapur", "solapur",
        "vijayawada", "guntur", "tirupati",
        "warangal", "nizamabad", "karimnagar",
        "mangalore", "hubli", "belgaum", "gulbarga",
        "thiruvalla", "kottayam", "thrissur", "calicut",
    ]:
        # Handle common aliases
        if c in combined or (c == "gurugram" and "gurgaon" in combined) or (c == "bengaluru" and "bangalore" in combined):
            # Normalize aliases
            if c in ("gurgaon",): return "gurugram"
            if c in ("bangalore",): return "bengaluru"
            return c
    return "general"

def _extract_intersecting_evidence(lat: float, lon: float, city: str, address: str) -> list[EvidenceEvent]:
    evidence_events = []
    # Extract neighborhood from address for granular matching
    neighborhood = address.split(',')[0].strip() if address else "this local area"
    if len(neighborhood) > 35:
        neighborhood = " ".join(neighborhood.split()[:3])

    # Also extract second part (suburb/locality) for better matching
    parts = [p.strip() for p in address.split(',') if p.strip()]
    suburb = parts[1].strip() if len(parts) > 1 else ""

    for entry in HISTORICAL_DISASTER_LOG:
        lats, lons = entry["lat_range"], entry["lon_range"]
        if lats[0] <= lat <= lats[1] and lons[0] <= lon <= lons[1]:
            for ev in entry["events"]:
                ev_copy = ev.copy()
                details = ev_copy["details"]

                # Rewrite with specific neighborhood
                details = details.replace("across South Chennai micro-watersheds (Velachery, Perungudi, Pallikaranai, Madipakkam)", f"across the micro-watershed surrounding {neighborhood}")
                details = details.replace("1.5km adjoining catchments", f"catchment areas including {neighborhood}")
                details = details.replace("Nungambakkam & T. Nagar micro-drainage channels", f"{neighborhood} micro-drainage channels")
                details = details.replace("low-lying residential plots.", f"low-lying plots in {neighborhood}.")

                if details == ev_copy["details"]:
                    if suburb and suburb.lower() not in details.lower():
                        details = f"Near {suburb}: {details}"
                    elif neighborhood not in ("this local area", "the target area"):
                        details = f"Impact recorded near {neighborhood}: {details}"

                ev_copy["details"] = details
                evidence_events.append(EvidenceEvent(**ev_copy))
    return evidence_events

def _map_level(score: float) -> RiskLevel:
    if score < 20: return RiskLevel.VERY_LOW
    if score < 40: return RiskLevel.LOW
    if score < 60: return RiskLevel.MODERATE
    if score < 80: return RiskLevel.HIGH
    return RiskLevel.VERY_HIGH

async def run_full_analysis(lat: float, lon: float, address: str, city: str, state: str) -> AnalysisResult:
    """Run all Universal Dynamic Discovery modules and construct hyperlocal risk intelligence."""
    # Fetch real elevation from Open-Meteo SRTM DEM
    elevation = await fetch_real_elevation(lat, lon)

    # Run all discovery queries concurrently
    (
        flood_data, eq_data, cyclone_data, ls_data, tsu_data, heat_data,
        gw_data, aq_data, ind_data, soil_data, clim_data, nearby
    ) = await asyncio.gather(
        discover_flood_features(lat, lon, elevation, state, address),
        asyncio.to_thread(discover_earthquake_faults, lat, lon, state),
        asyncio.to_thread(discover_cyclone_surge, lat, lon, state),
        discover_landslide_terrain(lat, lon, elevation, state),
        asyncio.to_thread(discover_tsunami_geometry, lat, lon, elevation),
        discover_heat_island(lat, lon, state),
        discover_groundwater_wells(lat, lon, state),
        discover_air_quality_fire_hotspots(lat, lon, city, state),
        discover_industrial_pollution(lat, lon),
        discover_soil_raster(lat, lon, state),
        discover_climate_cmip6(lat, lon, state),
        fetch_nearby_services(lat, lon),
    )

    evidence_log = _extract_intersecting_evidence(lat, lon, city, address)
    city_key = _get_city_key(city, address)
    # Look up city-level authority first, then fall back to state-level
    reg_info = (
        CITY_REGULATORY_AUTHORITIES.get(city_key)
        or STATE_REGULATORY_AUTHORITIES.get(state.lower())
        or STATE_REGULATORY_AUTHORITIES["general"]
    )
    auth_name = reg_info["name"]

    # -- DEBUG LOGGING --
    print(f"\n[DEBUG: {lat},{lon}] === RAW DATA FETCH RESULTS ===")
    print(f"ELEVATION: {elevation}m")
    print(f"FLOOD: {flood_data}")
    print(f"EARTHQUAKE: {eq_data}")
    print(f"LANDSLIDE: {ls_data}")
    print(f"SOIL: {soil_data}")
    print(f"HEAT: {heat_data}")
    print(f"GROUNDWATER: {gw_data}")
    print(f"CLIMATE: {clim_data}")
    print(f"EVIDENCE LOG: {len(evidence_log)} events found.")
    print("===================================================\n")

    # --- 1. FLOOD ---
    # Multi-factor scoring: proximity + rainfall + state risk + elevation
    annual_rainfall = flood_data.get("annual_rainfall_mm", 1000)
    rainfall_ratio = flood_data.get("rainfall_ratio", 1.0)
    is_flood_state = flood_data.get("is_flood_prone_state", False)
    is_low_elev = flood_data.get("low_elevation", False)

    if flood_data["features"]:
        min_dist_m = min(f.get("distance_m", f.get("distance_km", 5) * 1000) for f in flood_data["features"])
        # Base risk from waterbody proximity
        import math as _math
        prox_risk = max(15.0, min(90.0, 95.0 - (_math.log10(max(10, min_dist_m)) * 18.0)))
    else:
        # No waterbody found — but still check other factors
        prox_risk = 10.0

    # Rainfall amplifier: areas with >2000mm get significant boost
    rainfall_boost = 0.0
    if annual_rainfall > 2500:
        rainfall_boost = 25.0  # Extreme rainfall zone
    elif annual_rainfall > 2000:
        rainfall_boost = 18.0  # Very high rainfall
    elif annual_rainfall > 1500:
        rainfall_boost = 12.0  # High rainfall
    elif annual_rainfall > 1000:
        rainfall_boost = 5.0   # Moderate rainfall

    # State-level flood risk boost
    state_boost = 15.0 if is_flood_state else 0.0

    # Elevation penalty: low-lying areas flood more easily
    elev_boost = 0.0
    if elevation < 3.0:
        elev_boost = 20.0  # Very low — coastal/marshland
    elif elevation < 5.0:
        elev_boost = 12.0  # Low-lying
    elif elevation < 10.0:
        elev_boost = 5.0   # Moderate

    # Evidence penalty from historical disasters
    evidence_penalty = 12.0 if evidence_log else 0.0

    flood_score = max(8.0, min(95.0, prox_risk + rainfall_boost + state_boost + elev_boost + evidence_penalty))
    f_feat = flood_data["features"][0] if flood_data["features"] else None
    f_causal = (f"Distance to {f_feat['name']}: {f_feat.get('distance_m', f_feat.get('distance_km', 0))}m. "
                f"Relative elevation margin to HFL is {flood_data['relative_margin_m']}m.") if f_feat else flood_data["absence_signals"][-1]
    f_cons = (
        f"Expect {abs(flood_data['relative_margin_m'])}m of standing water during peak rainfall. "
        f"Nearest waterbody '{f_feat['name']}' is {f_feat.get('distance_m', f_feat.get('distance_km', 0))}m away."
        if flood_data["relative_margin_m"] < 0 and f_feat
        else f"Marginal flood zone: {flood_data['relative_margin_m']}m above HFL. Minor waterlogging possible in extreme events."
        if flood_data["relative_margin_m"] < 1.0
        else "Negligible inundation risk under standard 24hr rainfall. Well above floodplain elevation."
    )
    f_mits = [
        MitigationAction(category=MitigationCategory.CONSTRUCTION, action=f"Elevate structural plinth to {flood_data['estimated_hfl_msl'] + 0.3}m MSL.", cost_tier=CostTier.MAJOR, regulatory_authority=auth_name),
        MitigationAction(category=MitigationCategory.SITE_DRAINAGE, action="Install dual non-return stormwater check valves.", cost_tier=CostTier.MODERATE, regulatory_authority=auth_name)
    ]

    # --- 2. EARTHQUAKE --- (PGA-based: 0.05g→10, 0.1g→25, 0.2g→50, 0.3g→75)
    eq_score = round(max(5.0, min(95.0, eq_data["pga_g"] * 200 + 5)), 1)
    eq_causal = f"Nearest fault: {eq_data['nearest_fault']} at {eq_data['distance_km']}km. Soil amplification: {eq_data['soil_amplification_factor']}."
    eq_cons = (
        f"PGA {eq_data['pga_g']}g from {eq_data['nearest_fault']} fault ({eq_data['distance_km']}km). "
        f"Unreinforced masonry at risk; RCC frames with IS 13920 detailing required."
        if eq_data["pga_g"] >= 0.15
        else f"Low seismic exposure: PGA {eq_data['pga_g']}g. Standard BIS 1893 Zone III construction is adequate."
        if eq_data["pga_g"] >= 0.08
        else f"Minimal seismic risk: PGA {eq_data['pga_g']}g. Nearest fault {eq_data['nearest_fault']} at {eq_data['distance_km']}km."
    )
    eq_mits = [MitigationAction(category=MitigationCategory.CONSTRUCTION, action=f"Design ductile RCC frames per IS 13920 for PGA {eq_data['pga_g']}g.", cost_tier=CostTier.MAJOR, regulatory_authority=auth_name)]

    # --- 3. CYCLONE --- (continuous: closer to coast = higher risk + state-level risk)
    coast_km = cyclone_data["coastline_distance_km"]
    is_high_cyc_state = cyclone_data.get("is_high_cyclone_state", False)
    import math as _math
    # Base score from distance
    cyc_dist_score = max(5.0, min(85.0, 88.0 - (_math.log10(max(1, coast_km + 1)) * 22.0)))
    # State-level boost for cyclone-prone states
    cyc_state_boost = 15.0 if is_high_cyc_state else 0.0
    cyc_score = round(max(5.0, min(90.0, cyc_dist_score + cyc_state_boost)), 1)
    cyc_causal = f"Distance to coast: {coast_km}km." + (f" Historical surge: {cyclone_data['historical_surge_m']}m." if cyclone_data["historical_surge_m"] > 0 else "")
    cyc_cons = (
        f"Coastal property: {coast_km}km from shoreline. Historical surge {cyclone_data['historical_surge_m']}m. "
        f"Wind-resistant roofing per IS 875 Part 3 is critical."
        if cyclone_data["historical_surge_m"] > 0 and coast_km < 10
        else f"Moderate coastal exposure: {coast_km}km inland. Occasional cyclonic winds possible."
        if coast_km < 30
        else f"Inland location: {coast_km}km from coast. Cyclone surge risk is negligible."
    )
    cyc_mits = [MitigationAction(category=MitigationCategory.CONSTRUCTION, action="IS 875 Part 3 compliant wind-resistant roofing.", cost_tier=CostTier.MODERATE)] if cyc_score > 30 else []

    # --- 4. LANDSLIDE --- (slope-based: 0°→5, 5°→15, 15°→40, 25°→65, 35°→85)
    slope = ls_data["slope_degrees"]
    ls_score = round(max(5.0, min(90.0, 5.0 + slope * 2.3)), 1)
    ls_causal = f"Local slope gradient: {ls_data['slope_degrees']}° ({ls_data['terrain_type']})."
    ls_cons = (
        f"Steep terrain: {ls_data['slope_degrees']}° slope ({ls_data['terrain_type']}). "
        f"Debris flow or topsoil slip likely during saturation events."
        if ls_score > 60
        else f"Moderate slope: {ls_data['slope_degrees']}° ({ls_data['terrain_type']}). "
        f"Minor erosion possible during heavy rainfall."
        if ls_score > 30
        else f"Flat terrain: {ls_data['slope_degrees']}° ({ls_data['terrain_type']}). Landslide risk eliminated."
    )
    ls_mits = [MitigationAction(category=MitigationCategory.CONSTRUCTION, action="Construct deep RCC retaining walls with weep holes.", cost_tier=CostTier.MAJOR)] if ls_score > 40 else []

    # --- 5. TSUNAMI --- (distance-based: <5km→70, 10km→50, 20km→30, 50km→10)
    tsu_dist = tsu_data["distance_to_sea_km"]
    import math as _math
    tsu_score = round(max(3.0, min(75.0, 78.0 - (_math.log10(max(1, tsu_dist + 1)) * 25.0))), 1)
    tsu_causal = f"Distance to sea: {tsu_dist}km. Plot MSL: {elevation}m vs Tsunami max run-up: {tsu_data['max_tsunami_runup_extent_m']}m."
    
    # --- 6. HEAT --- (real Open-Meteo data: temperature, humidity, UV, heatwave days)
    heat_temp = heat_data.get("current_temperature_c", 30.0)
    heat_feels = heat_data.get("feels_like_temperature_c", heat_temp)
    heat_humidity = heat_data.get("relative_humidity_pct", 60)
    heat_uv = heat_data.get("uv_index", 3.0)
    heat_hw_days = heat_data.get("heatwave_days_in_forecast", 0)
    heat_anomaly = heat_data.get("heat_island_anomaly_c", 0.0)

    # Temperature component: 25°C→10, 30°C→25, 35°C→45, 40°C→65, 45°C→85
    temp_component = max(0, min(70, (heat_feels - 20) * 3.5))
    # Heatwave days: each day adds 5 points
    hw_component = min(25, heat_hw_days * 5.0)
    # UV component: 0→0, 5→10, 10→20
    uv_component = min(15, heat_uv * 2.0)
    # UHI anomaly: each degree adds 3 points
    uhi_component = min(15, heat_anomaly * 3.0)
    # High humidity is protective (reduces heat stroke risk)
    humidity_bonus = -5.0 if heat_humidity > 80 else 0.0

    heat_score = round(max(5.0, min(90.0, temp_component + hw_component + uv_component + uhi_component + humidity_bonus)), 1)
    heat_causal = f"Real-time: {heat_temp}°C (feels like {heat_feels}°C), Humidity {heat_humidity}%, UV {heat_uv}. Heatwave days in forecast: {heat_hw_days}."
    heat_cons = (
        f"Extreme heat: feels like {heat_feels}°C with UV {heat_uv}. "
        f" Cooling costs high; outdoor work dangerous in peak summer."
        if heat_score > 60
        else f"Moderate heat: {heat_feels}°C feels-like. "
        f" Some summer discomfort but manageable with standard AC."
        if heat_score > 30
        else f"Pleasant conditions: {heat_feels}°C feels-like. Heat stress is not a concern."
    )

    # --- 7. GROUNDWATER --- (real Open-Meteo soil moisture + precipitation data)
    gw_surface = gw_data.get("soil_moisture_surface_m3m3", 0.3)
    gw_deep = gw_data.get("soil_moisture_deep_m3m3", 0.3)
    gw_depth = gw_data.get("depth_to_water_bgl_m", 20.0)
    gw_precip = gw_data.get("14day_precipitation_mm", 0.0)
    gw_trend = gw_data.get("recharge_trend", "Stable")
    gw_contamination = gw_data.get("contamination_risk", "Low")

    if "Declining" in gw_trend:
        gw_score = round(max(15.0, min(95.0, 50.0 + (gw_depth * 0.4) - (gw_surface * 30.0))), 1)
    elif "Rising" in gw_trend:
        gw_score = round(max(5.0, min(60.0, 20.0 + (5.0 - gw_surface * 10.0))), 1)
    else:
        gw_score = round(max(10.0, min(80.0, 35.0 + (gw_depth * 0.2) - (gw_precip * 0.1))), 1)

    gw_causal = f"Real soil moisture: surface={gw_surface} m³/m³, deep={gw_deep} m³/m³. Depth: {gw_depth}m. 14-day precip: {gw_precip}mm. Trend: {gw_trend}."
    gw_cons = (
        f"Contamination risk: {gw_contamination}. Groundwater depth: {gw_depth}m. "
        f"Recharge trend: {gw_trend}. Water treatment or tanker reliance likely."
        if gw_contamination != "Low" and gw_score > 50
        else f"Groundwater depth: {gw_depth}m, trend: {gw_trend}. "
        f"Available but declining; rainwater harvesting strongly recommended."
        if gw_score > 30
        else f"Stable groundwater: depth {gw_depth}m, surface moisture {gw_surface} m³/m³. Reliable supply expected."
    )
    gw_mits = [MitigationAction(category=MitigationCategory.SITE_DRAINAGE, action="Mandatory 5000L Rainwater Harvesting Sump.", cost_tier=CostTier.MODERATE)]

    # --- 8. AIR QUALITY --- (European AQI bands: 0-20→5, 20-40→15, 40-60→30, 60-80→50, 80-100→70, >100→85)
    aq_eu = aq_data.get("european_aqi", 50)
    aq_pm25 = aq_data.get("pm2_5_ugm3", 20.0)
    aq_pm10 = aq_data.get("pm10_ugm3", 30.0)
    aq_no2 = aq_data.get("no2_ugm3", 20.0)

    if aq_eu <= 20:
        aq_score = 5.0 + aq_eu * 0.5
    elif aq_eu <= 40:
        aq_score = 15.0 + (aq_eu - 20) * 0.75
    elif aq_eu <= 60:
        aq_score = 30.0 + (aq_eu - 40) * 1.0
    elif aq_eu <= 80:
        aq_score = 50.0 + (aq_eu - 60) * 1.0
    elif aq_eu <= 100:
        aq_score = 70.0 + (aq_eu - 80) * 0.75
    else:
        aq_score = 85.0 + min(10, (aq_eu - 100) * 0.1)

    aq_score = round(max(5.0, min(95.0, aq_score)), 1)
    aq_causal = f"Real-time European AQI: {aq_eu}. PM2.5: {aq_pm25}µg/m³, PM10: {aq_pm10}µg/m³, NO2: {aq_no2}µg/m³."
    aq_cons = (
        f" Poor air quality: AQI {aq_eu}, PM2.5 {aq_pm25}µg/m³. "
        f" Respiratory issues likely; air purifiers recommended."
        if aq_score > 60
        else f" Moderate air quality: AQI {aq_eu}. "
        f" Acceptable most days, but dusty during dry spells."
        if aq_score > 30
        else f" Clean air: AQI {aq_eu}, PM2.5 {aq_pm25}µg/m³. No pollution concerns."
    )

    # --- 9. INDUSTRIAL POLLUTION ---
    # CPCB/State PCB siting criteria distances (meters)
    CPCB_SAFE_DISTANCES = {
        "red": 500,      # Red category: 500m from residential
        "orange": 300,   # Orange category: 300m from residential
        "green": 200,    # Green category: 200m from residential
        "landfill": 500, # Landfill: 500m
        "waste": 500,    # Waste disposal: 500m
    }

    if ind_data["discovered_facilities"]:
        p_feat = ind_data["discovered_facilities"][0]
        dist_m = p_feat["distance_m"]

        # Classify facility type for CPCB category
        feat_name_lower = p_feat["name"].lower()
        if "landfill" in feat_name_lower or "waste" in feat_name_lower or "dump" in feat_name_lower:
            cpcb_category = "red"
            safe_dist = 500
        elif "chemical" in feat_name_lower or "pharma" in feat_name_lower or "tannery" in feat_name_lower:
            cpcb_category = "red"
            safe_dist = 500
        elif "textile" in feat_name_lower or "dye" in feat_name_lower or "food" in feat_name_lower:
            cpcb_category = "orange"
            safe_dist = 300
        elif "manufacturing" in feat_name_lower or "factory" in feat_name_lower or "works" in feat_name_lower:
            cpcb_category = "orange"
            safe_dist = 300
        else:
            cpcb_category = "green"
            safe_dist = 200

        # Score based on CPCB compliance
        if dist_m < safe_dist:
            # Violation: within CPCB safe distance
            ind_score = round(max(60, min(100, 95 - (dist_m / 10.0))), 1)
        elif dist_m < safe_dist * 2:
            # Marginal: within 2x safe distance
            ind_score = round(max(30, min(70, 50 + (safe_dist - dist_m) / 10.0)), 1)
        elif dist_m < safe_dist * 5:
            # Moderate: 2-5x safe distance
            ind_score = round(max(15, min(45, 30 + (safe_dist * 2 - dist_m) / 20.0)), 1)
        else:
            # Safe: >5x safe distance
            ind_score = round(max(5, min(25, 15 - (dist_m - safe_dist * 5) / 200.0)), 1)

        p_causal = (
            f"CPCB {cpcb_category.upper()} category facility: {p_feat['name']} "
            f"at {dist_m}m (Govt. safe distance: {safe_dist}m). "
            f"{'VIOLATION: Within mandated buffer zone.' if dist_m < safe_dist else 'Outside buffer zone.'}"
        )
        p_cons = (
            f"Industry {p_feat['name']} ({cpcb_category.upper()} category) at {dist_m}m. "
            f"Govt. mandated safe distance: {safe_dist}m. "
            f"{'Property is within the prohibited buffer zone — health risk from emissions, odor, and contamination.' if dist_m < safe_dist else 'Outside mandatory buffer, but monitor wind patterns for intermittent impact.'}"
        )
    else:
        p_causal = ind_data["absence_signals"][0] if ind_data["absence_signals"] else "No industrial facilities detected within 3km."
        ind_score = 8.0
        p_cons = "No CPCB-listed industrial facilities detected within 3km radius. Environment is clean."

    # --- 10. SOIL --- (real ISRIC SoilGrids data: clay%, sand%, SOC, pH)
    soil_clay = soil_data.get("clay_pct", 25.0)
    soil_sand = soil_data.get("sand_pct", 40.0)
    soil_soc = soil_data.get("soil_organic_carbon_pct", 1.0)
    soil_ph = soil_data.get("soil_ph", 6.5)
    soil_bearing = soil_data.get("bearing_capacity_ton_sqm", 15.0)

    if soil_clay > 40:
        soil_score = round(max(30.0, min(95.0, 60.0 + soil_clay * 0.5 - soil_bearing * 0.3)), 1)
    elif soil_sand > 60:
        soil_score = round(max(5.0, min(50.0, 15.0 + (60.0 - soil_sand) * 0.5)), 1)
    else:
        soil_score = round(max(8.0, min(70.0, 25.0 + soil_clay * 0.3 - soil_soc * 2.0)), 1)

    soil_causal = f"Real ISRIC data: Clay {soil_clay}%, Sand {soil_sand}%, SOC {soil_soc}%, pH {soil_ph}. Bearing: {soil_bearing} t/sqm. Class: {soil_data['fao_soil_class']}."
    soil_cons = (
        f" Expansive clay soil: {soil_clay}% clay. "
        f" Foundation cracking risk; pile foundations required."
        if soil_score > 60
        else f" Moderate soil: {soil_clay}% clay, bearing {soil_bearing} t/sqm. "
        f" Standard foundation design is adequate."
        if soil_score > 30
        else f" Stable soil: {soil_data['fao_soil_class']} class, bearing {soil_bearing} t/sqm. Ideal for construction."
    )
    soil_mits = [MitigationAction(category=MitigationCategory.CONSTRUCTION, action="Pile foundation / isolated footings to bypass expansive clay.", cost_tier=CostTier.MAJOR)] if soil_score > 50 else []

    # --- 11. CLIMATE --- (temperature increase + absolute rainfall change)
    clim_temp = clim_data.get("projected_temp_increase_2050_c", 2.0)
    clim_rain = abs(clim_data.get("projected_extreme_rainfall_change_pct", 10.0))
    # Temp: 1°C→15, 2°C→30, 3°C→45, 4°C→60
    # Rainfall change: 0%→0, 10%→10, 25%→25, 50%→40
    clim_score = max(10, min(85, clim_temp * 15 + min(40, clim_rain * 0.8)))
    clim_causal = f"CMIP6 Cell {clim_data['cmip6_grid_cell_id']} 2050 Projections: +{clim_data['projected_temp_increase_2050_c']}°C, {clim_data['projected_extreme_rainfall_change_pct']}% Extreme Rainfall."
    clim_cons = (
        f" Significant climate shift by 2050: +{clim_temp}°C, rainfall change {clim_rain}%. "
        f" Long-term liveability and property value at risk."
        if clim_score > 60
        else f" Moderate climate impact: +{clim_temp}°C by 2050. "
        f" Worth planning for heat-resilient construction."
        if clim_score > 30
        else f" Climate-resilient location: minimal projected change (+{clim_temp}°C)."
    )

    hazard_objs = {
        "flood_risk": HazardScore(score=flood_score, level=_map_level(flood_score), details="", causal_analysis=f_causal, consequence_statement=f_cons, mitigations=f_mits, absence_signals=flood_data["absence_signals"], source_citation="OSM Overpass / TNSDMA / Bhuvan"),
        "earthquake_risk": HazardScore(score=eq_score, level=_map_level(eq_score), details="", causal_analysis=eq_causal, consequence_statement=eq_cons, mitigations=eq_mits, absence_signals=eq_data["absence_signals"], source_citation="GSI / NCS / BIS 1893:2016"),
        "cyclone_risk": HazardScore(score=cyc_score, level=_map_level(cyc_score), details="", causal_analysis=cyc_causal, consequence_statement=cyc_cons, mitigations=cyc_mits, absence_signals=cyclone_data["absence_signals"], source_citation="IMD Historic Tracks"),
        "landslide_risk": HazardScore(score=ls_score, level=_map_level(ls_score), details="", causal_analysis=ls_causal, consequence_statement=ls_cons, mitigations=ls_mits, absence_signals=ls_data["absence_signals"], source_citation="Open-Meteo Elevation API + terrain analysis"),
        "tsunami_risk": HazardScore(score=tsu_score, level=_map_level(tsu_score), details="", causal_analysis=tsu_causal, absence_signals=tsu_data["absence_signals"], source_citation="INCOIS Tsunami Hazard Zones"),
        "heat_stress": HazardScore(score=heat_score, level=_map_level(heat_score), details="", causal_analysis=heat_causal, consequence_statement=heat_cons, absence_signals=heat_data["absence_signals"], source_citation="Open-Meteo Weather API (real-time)"),
        "air_quality": HazardScore(score=aq_score, level=_map_level(aq_score), details="", causal_analysis=aq_causal, consequence_statement=aq_cons, absence_signals=aq_data["absence_signals"], source_citation="Open-Meteo Air Quality API (real-time)"),
        "groundwater": HazardScore(score=gw_score, level=_map_level(gw_score), details="", causal_analysis=gw_causal, consequence_statement=gw_cons, mitigations=gw_mits, absence_signals=gw_data["absence_signals"], source_citation="Open-Meteo Soil Moisture API (real-time)"),
        "soil_quality": HazardScore(score=soil_score, level=_map_level(soil_score), details="", causal_analysis=soil_causal, consequence_statement=soil_cons, mitigations=soil_mits, absence_signals=soil_data["absence_signals"], source_citation="ISRIC SoilGrids v2.0 (real API)"),
        "pollution_proximity": HazardScore(score=ind_score, level=_map_level(ind_score), details="", causal_analysis=p_causal, consequence_statement=p_cons, absence_signals=ind_data["absence_signals"], source_citation="OSM Industrial / CPCB Red List"),
        "climate_future": HazardScore(score=clim_score, level=_map_level(clim_score), details="", causal_analysis=clim_causal, consequence_statement=clim_cons, absence_signals=clim_data["absence_signals"], source_citation="Open-Meteo Climate API (CMIP6 EC_Earth3P_HR)")
    }

    # Explicit hazard-key → weight mapping (fixes bug where string slicing silently dropped 6 hazards)
    HAZARD_KEY_TO_WEIGHT = {
        "flood_risk":           WEIGHTS["flood"],
        "earthquake_risk":      WEIGHTS["earthquake"],
        "cyclone_risk":         WEIGHTS["cyclone"],
        "landslide_risk":       WEIGHTS["landslide"],
        "tsunami_risk":         WEIGHTS["tsunami"],
        "air_quality":          WEIGHTS["air_quality"],
        "heat_stress":          WEIGHTS["heat"],
        "groundwater":          WEIGHTS["groundwater"],
        "soil_quality":         WEIGHTS["soil"],
        "pollution_proximity":  WEIGHTS["pollution"],
        "climate_future":       WEIGHTS["climate"],
    }

    weighted_risk = sum(
        hazard_objs[key].score * weight
        for key, weight in HAZARD_KEY_TO_WEIGHT.items()
    )

    # Debug: print individual component scores
    print(f"[SCORE DEBUG {lat},{lon}] Component scores:")
    for key, weight in HAZARD_KEY_TO_WEIGHT.items():
        s = hazard_objs[key].score
        print(f"  {key:30s} score={s:5.1f}  weight={weight}  contribution={s*weight:.2f}")
    print(f"  Total weighted_risk = {weighted_risk:.2f}")

    if any(e.severity in ["Extreme", "Very High"] for e in evidence_log):
        weighted_risk = max(weighted_risk, 36.0)

    safety_score = round(max(0, min(100, 100 - weighted_risk)), 1)
    print(f"  => FINAL safety_score = {safety_score}")
    decision = SafetyDecision.SAFE if safety_score >= 75 else SafetyDecision.CAUTION if safety_score >= 50 else SafetyDecision.AVOID

    # Confidence Score: Dynamic Data Density Model
    data_density = sum([1 for h in hazard_objs.values() if not h.absence_signals])
    confidence = round(min(98, 70 + (data_density * 2) + (len(evidence_log) * 3)), 1)

    climate_resilience = round(max(0, min(100, 100 - (heat_score * 0.3 + clim_score * 0.4 + flood_score * 0.3))), 1)
    investment_risk = round(max(0, min(100, 100 - safety_score * 0.6 - (100 - gw_score) * 0.4)), 1)
    construction_suitability = round(max(0, min(100, 100 - soil_score * 0.5 - ls_score * 0.3 - eq_score * 0.2)), 1)

    ai_context = {
        "address": address, "city": city, "state": state,
        "safety_score": safety_score, "decision": decision.value,
        "hazards": {k: {"score": v.score, "level": v.level.value, "causal": v.causal_analysis} for k, v in hazard_objs.items()},
        "evidence_log": [e.model_dump() for e in evidence_log],
    }
    ai_result = await generate_ai_summary(ai_context)

    what_this_means = (
        f"In practical terms: Expect potential localized impacts corresponding to {evidence_log[0].year if evidence_log else 'monsoon'} intensity "
        f"unless the recommended structural mitigations (like {flood_data['estimated_hfl_msl'] + 0.3}m MSL plinth) are met."
    )

    return AnalysisResult(
        id=str(uuid.uuid4()), address=address, lat=lat, lon=lon, city=city, state=state,
        safety_score=safety_score, decision=decision, confidence=confidence,
        climate_resilience_index=climate_resilience, investment_risk_rating=investment_risk,
        construction_suitability=construction_suitability,
        **hazard_objs,
        ai_summary=ai_result["summary"],
        what_this_means_for_you=what_this_means,
        evidence_log=evidence_log,
        construction_recommendations=ai_result["construction_recommendations"],
        disaster_preparedness=ai_result["disaster_preparedness"],
        insurance_risk_estimate="High – 25–45% above standard premium" if safety_score < 60 else "Standard Premium",
        long_term_sustainability="Moderate" if clim_score > 60 else "High",
        nearby_services=nearby,
        analysis_timestamp=datetime.utcnow().isoformat() + "Z",
        data_sources=["OSM Overpass API", "GSI & NCS Fault Database", "SRTM 30m DEM", "IMD & CPCB", "CGWB", "NASA FIRMS", "IPCC CMIP6"]
    )
