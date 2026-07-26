const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ─── TypeScript Interfaces (match backend Pydantic models exactly) ───────────

export type RiskLevel = "Very Low" | "Low" | "Moderate" | "High" | "Very High";
export type SafetyDecision = "Safe to Buy" | "Buy with Precautions" | "Avoid";
export type CostTier = "Low (<₹50k)" | "Moderate (₹50k–₹5L)" | "Major (>₹5L)";

export interface MitigationAction {
  category: "Pre-Purchase & Legal Due Diligence" | "Construction & Structural Engineering" | "Site Drainage & Landscaping" | string;
  action: string;
  cost_tier: CostTier;
  regulatory_authority?: string;
}

export interface EvidenceEvent {
  year: number;
  event_name: string;
  severity: string;
  details: string;
  inundation_status: string;
  source: string;
}

export interface HazardScore {
  score: number;
  level: RiskLevel;
  details: string;
  contributing_factors: string[];
  causal_analysis?: string;
  consequence_statement?: string;
  mitigations?: MitigationAction[];
  source_citation?: string;
  absence_signals?: string[];
}

export interface NearbyService {
  name: string;
  type: "hospital" | "fire_station" | "police" | "shelter" | string;
  distance_km: number;
  lat: number;
  lon: number;
}

export interface AnalysisResult {
  id: string;
  address: string;
  lat: number;
  lon: number;
  city: string;
  state: string;

  // Core scores
  safety_score: number;
  decision: SafetyDecision;
  confidence: number;
  climate_resilience_index: number;
  investment_risk_rating: number;
  construction_suitability: number;

  // Individual hazards
  flood_risk: HazardScore;
  earthquake_risk: HazardScore;
  cyclone_risk: HazardScore;
  landslide_risk: HazardScore;
  tsunami_risk: HazardScore;
  heat_stress: HazardScore;
  air_quality: HazardScore;
  groundwater: HazardScore;
  soil_quality: HazardScore;
  pollution_proximity: HazardScore;
  climate_future: HazardScore;

  // AI & Hyperlocal outputs
  ai_summary: string;
  what_this_means_for_you?: string;
  evidence_log?: EvidenceEvent[];
  construction_recommendations: string[];
  disaster_preparedness: string[];
  insurance_risk_estimate: string;
  long_term_sustainability: string;

  // Services & meta
  nearby_services: NearbyService[];
  analysis_timestamp: string;
  data_sources: string[];
}

export interface GeocodeResult {
  address: string;
  lat: number;
  lon: number;
  city: string;
  state: string;
  country: string;
}

// ─── API Functions ────────────────────────────────────────────────────────────

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...(options?.headers || {}) },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function analyzeProperty(
  address: string,
  lat?: number,
  lon?: number
): Promise<AnalysisResult> {
  return apiFetch<AnalysisResult>("/api/analyze", {
    method: "POST",
    body: JSON.stringify({ address, lat, lon }),
  });
}

export async function getAnalysis(id: string): Promise<AnalysisResult> {
  return apiFetch<AnalysisResult>(`/api/analyze/${id}`);
}

export async function compareProperties(
  properties: Array<{ address: string; lat?: number; lon?: number }>
): Promise<AnalysisResult[]> {
  return apiFetch<AnalysisResult[]>("/api/compare", {
    method: "POST",
    body: JSON.stringify({ properties }),
  });
}

export async function chatWithAI(
  analysisId: string,
  message: string,
  analysisContext?: Record<string, unknown>
): Promise<{ reply: string }> {
  return apiFetch<{ reply: string }>("/api/chat", {
    method: "POST",
    body: JSON.stringify({
      analysis_id: analysisId,
      message,
      analysis_context: analysisContext,
    }),
  });
}

export async function generateReport(analysisId: string): Promise<Blob> {
  const res = await fetch(`${API_BASE}/api/report/generate/${analysisId}`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Report generation failed");
  return res.blob();
}

export async function geocodeAddress(address: string): Promise<GeocodeResult> {
  return apiFetch<GeocodeResult>(
    `/api/geocode?address=${encodeURIComponent(address)}`
  );
}
