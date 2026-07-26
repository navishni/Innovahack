from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class SafetyDecision(str, Enum):
    SAFE = "Safe to Buy"
    CAUTION = "Buy with Precautions"
    AVOID = "Avoid"


class RiskLevel(str, Enum):
    VERY_LOW = "Very Low"
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    VERY_HIGH = "Very High"


class CostTier(str, Enum):
    LOW = "Low (<₹50k)"
    MODERATE = "Moderate (₹50k-₹5L)"
    MAJOR = "Major (>₹5L)"


class MitigationCategory(str, Enum):
    PRE_PURCHASE = "Pre-Purchase & Legal Due Diligence"
    CONSTRUCTION = "Construction & Structural Engineering"
    SITE_DRAINAGE = "Site Drainage & Landscaping"


class MitigationAction(BaseModel):
    category: MitigationCategory
    action: str
    cost_tier: CostTier
    regulatory_authority: Optional[str] = None


class EvidenceEvent(BaseModel):
    year: int
    event_name: str
    severity: str
    details: str
    inundation_status: str  # e.g. "Coordinates Submerged", "Micro-Watershed Inundated", "Nearby Outfall Overflow"
    source: str  # e.g. "TNSDMA 2015 Flood Atlas", "NDMA Archives", "NRSC Bhuvan ISRO"


class AnalyzeRequest(BaseModel):
    address: str = Field(..., description="Property address")
    lat: Optional[float] = Field(None, description="Latitude")
    lon: Optional[float] = Field(None, description="Longitude")


class HazardScore(BaseModel):
    score: float = Field(..., ge=0, le=100, description="Risk score 0 (safe) to 100 (high risk)")
    level: RiskLevel
    details: str
    contributing_factors: List[str] = []
    
    # Hyperlocal Reasoning Upgrades
    causal_analysis: str = ""  # Specific named feature + distance + relative elevation vs HFL
    consequence_statement: str = ""  # What will physically happen at rainfall/event threshold
    mitigations: List[MitigationAction] = []  # Actionable costed plan
    source_citation: str = ""  # Explicit data source citation
    
    # Dynamic Discovery Engine Upgrades
    absence_signals: List[str] = []  # Explicit statements of absence of risk features
    confidence_score: float = 100.0  # Dynamic confidence based on data density


class NearbyService(BaseModel):
    name: str
    type: str  # hospital, fire_station, police, shelter
    distance_km: float
    lat: float
    lon: float


class AnalysisResult(BaseModel):
    id: str
    address: str
    lat: float
    lon: float
    city: str = ""
    state: str = ""

    # Core scores
    safety_score: float = Field(..., ge=0, le=100)
    decision: SafetyDecision
    confidence: float = Field(..., ge=0, le=100)
    climate_resilience_index: float = Field(..., ge=0, le=100)
    investment_risk_rating: float = Field(..., ge=0, le=100)
    construction_suitability: float = Field(..., ge=0, le=100)

    # Individual hazards
    flood_risk: HazardScore
    earthquake_risk: HazardScore
    cyclone_risk: HazardScore
    landslide_risk: HazardScore
    tsunami_risk: HazardScore
    heat_stress: HazardScore
    air_quality: HazardScore
    groundwater: HazardScore
    soil_quality: HazardScore
    pollution_proximity: HazardScore
    climate_future: HazardScore

    # AI narrative & Hyperlocal outputs
    ai_summary: str
    what_this_means_for_you: str = ""
    evidence_log: List[EvidenceEvent] = []  # Localized Evidence Log
    construction_recommendations: List[str]
    disaster_preparedness: List[str]
    insurance_risk_estimate: str
    long_term_sustainability: str

    # Services
    nearby_services: List[NearbyService] = []

    # Meta
    analysis_timestamp: str
    data_sources: List[str] = []


class CompareRequest(BaseModel):
    properties: List[AnalyzeRequest] = Field(..., min_length=2, max_length=3)


class ChatRequest(BaseModel):
    analysis_id: str
    message: str
    analysis_context: Optional[dict] = None


class ChatResponse(BaseModel):
    reply: str


class GeocodeResult(BaseModel):
    address: str
    lat: float
    lon: float
    city: str = ""
    state: str = ""
    country: str = ""
