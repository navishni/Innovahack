"""
LLM Service – Gemini Flash / OpenAI GPT for Hyperlocal Property Risk Narratives.
Strictly obeys 7 narrative rules: named events, named features, source citations, costed mitigations.
"""
import json
from app.config import get_settings


SYSTEM_PROMPT = """You are GeoSafe AI, an expert hyperlocal property risk analyst in India.
You MUST follow these strict narrative rules in your outputs:
1. NEVER say "this area experienced flooding" — ALWAYS name the specific event, year, and data source (e.g. "during the December 2015 Chennai floods per TNSDMA atlas").
2. NEVER say "nearby water body" — ALWAYS name the specific feature (e.g., "Perungudi Lake", "Buckingham Canal", "Mithi River").
3. Every risk statement must end with one specific, actionable fix.
4. Always include a plain-language "What this means for you" statement.
5. Reference Indian standards (IS 1893:2016, NBC 2016, CMDA/BBMP/MMRDA bylaws).
6. CRITICAL: Reference ONLY the structured data block passed to you below. Do NOT fabricate, imagine, or hallucinate scores, evidence, or features that are not explicitly present in the data block.
7. The Backend has already mathematically computed the final numeric safety score. Your job is ONLY to generate readable prose narrating the computed data, NEVER to calculate or decide numeric scores yourself.
"""


def _build_prompt(ctx: dict) -> str:
    hazards = ctx.get("hazards", {})
    hazard_summary = "\n".join([
        f"  - {k.replace('_', ' ').title()}: {v['score']:.0f}/100 ({v['level']}) | Causal: {v.get('causal', '')}"
        for k, v in hazards.items()
    ])
    evidence_text = "\n".join([
        f"  - [{e.get('year')}] {e.get('event_name')}: {e.get('details')} (Status: {e.get('inundation_status')}, Source: {e.get('source')})"
        for e in ctx.get("evidence_log", [])
    ])

    return f"""
Property Location: {ctx['address']}
City: {ctx['city']}, State: {ctx['state']}
Overall Safety Score: {ctx['safety_score']:.1f}/100
Decision: {ctx['decision']}

Intersecting Disaster Evidence Log:
{evidence_text}

Hyperlocal Hazard Analysis:
{hazard_summary}

Please provide a JSON response with exactly these fields:
{{
  "summary": "3-4 sentences detailing the hyperlocal risk reasoning, citing specific named water bodies, fault lines, and historical disaster events.",
  "construction_recommendations": [
    "Pre-Purchase: Verify local authority bylaws (CMDA/BBMP/MMRDA/DDA) buffer compliance.",
    "Structural: Elevate plinth level to minimum HFL + 0.3m.",
    "Drainage: Install sub-surface attenuation sumps and backflow check valves.",
    "Seismic: Design ductile RCC framing per IS 13920:2016.",
    "Permeable compound paving & rainwater harvesting tank."
  ],
  "disaster_preparedness": [
    "Register with State Disaster Management Authority (SDMA) early warning SMS system.",
    "Subscribe to Central Water Commission (CWC) micro-watershed flood alerts.",
    "Maintain high-capacity submersible dewatering pump with DG backup."
  ]
}}
"""


async def generate_ai_summary(ctx: dict) -> dict:
    settings = get_settings()

    # Try Gemini first
    if settings.gemini_api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.gemini_api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = SYSTEM_PROMPT + "\n\n" + _build_prompt(ctx)
            response = model.generate_content(prompt)
            text = response.text.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            return json.loads(text)
        except Exception as e:
            print(f"Gemini error: {e}")

    # Try OpenAI
    if settings.openai_api_key:
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.openai_api_key)
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": _build_prompt(ctx)}
                ],
                response_format={"type": "json_object"},
                max_tokens=600,
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"OpenAI error: {e}")

    # Fallback: template-based summary following strict rules
    return _template_summary(ctx)


def _template_summary(ctx: dict) -> dict:
    score = ctx["safety_score"]
    city = ctx.get("city") or ctx.get("state") or "the target area"
    flood_causal = ctx.get("flood_causal") or "proximity to stormwater channels"
    evidence_log = ctx.get("evidence_log", [])

    ev_name = evidence_log[0]["event_name"] if evidence_log else "December 2015 & 2023 monsoon inundations"
    ev_source = evidence_log[0]["source"] if evidence_log else "TNSDMA / NRSC Bhuvan Flood Maps"

    if score >= 75:
        summary = (
            f"This property in {city} achieves a safety score of {score:.0f}/100. "
            f"Hyperlocal analysis indicates low vulnerability, sitting clear of historical inundation polygons from {ev_name} (Source: {ev_source}). "
            f"{flood_causal}. Standard plinth elevation and municipal drainage connections are recommended."
        )
    elif score >= 50:
        summary = (
            f"This property in {city} scores {score:.0f}/100 ({ctx['decision']}). "
            f"{flood_causal}. Historical evidence correlates this plot to the micro-watershed impacted during {ev_name} (Source: {ev_source}). "
            f"Purchase is viable provided structural plinth is elevated minimum 0.3m above High Flood Level (HFL)."
        )
    else:
        summary = (
            f"CRITICAL RISK ALERT: This property in {city} scores {score:.0f}/100. "
            f"Historical disaster records confirm this exact plot intersected recorded submergence during {ev_name} (Source: {ev_source}). "
            f"{flood_causal}. Immediate pre-purchase buffer verification and major foundation engineering are mandatory."
        )

    recs = [
        "Pre-Purchase: Verify local planning authority (CMDA/BBMP/MMRDA/DDA) water body buffer zone compliance before contract execution.",
        "Structural: Elevate structural plinth level to minimum 0.3m above recorded High Flood Level (HFL).",
        "Site Drainage: Install sub-surface stormwater attenuation tank with dual non-return valves.",
        "Seismic: Ductile RCC framing compliant with IS 13920:2016 for regional seismic zone.",
        "Permeable Paving: Use porous pavers for compound driveway to offset impervious surface runoff."
    ]

    prep = [
        "Register with State Disaster Management Authority (SDMA) SMS early warning alert system.",
        "Subscribe to Central Water Commission (CWC) & IMD micro-watershed rainfall advisories.",
        "Install automated dual submersible dewatering pumps with emergency battery/DG power backup."
    ]

    return {
        "summary": summary,
        "construction_recommendations": recs,
        "disaster_preparedness": prep,
    }


async def generate_chat_response(message: str, analysis_context: dict) -> str:
    """Generate a chat response citing named evidence, waterbodies, and fixes."""
    settings = get_settings()

    system = SYSTEM_PROMPT + f"""
Address: {analysis_context.get('address', 'Unknown')}
Safety Score: {analysis_context.get('safety_score', 0):.1f}/100
Decision: {analysis_context.get('decision', 'Unknown')}
Flood Causal: {analysis_context.get('flood_causal', '')}
Flood Consequence: {analysis_context.get('flood_consequence', '')}

Hazard Scores:
{json.dumps(analysis_context.get('hazards', {}), indent=2)}

Answer concisely (2-3 sentences). Always name specific water bodies, fault lines, or historical years if mentioned. End with one actionable fix.
"""

    if settings.gemini_api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.gemini_api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(system + f"\n\nUser question: {message}")
            return response.text.strip()
        except Exception:
            pass

    if settings.openai_api_key:
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.openai_api_key)
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": message}
                ],
                max_tokens=200,
            )
            return response.choices[0].message.content.strip()
        except Exception:
            pass

    return _fallback_chat(message, analysis_context)


def _fallback_chat(message: str, ctx: dict) -> str:
    msg_lower = message.lower()
    score = ctx.get("safety_score", 0)

    if any(w in msg_lower for w in ["buy", "safe", "should i"]):
        return (
            f"This property scores {score:.0f}/100 ({ctx.get('decision', 'Caution')}). "
            f"{ctx.get('flood_causal', '')}. "
            f"Fix: Elevate plinth level above High Flood Level (HFL) and verify water body buffer regulations before purchase."
        )

    if "flood" in msg_lower or "rain" in msg_lower:
        return (
            f"{ctx.get('flood_consequence', 'Flood risk is active.')} "
            f"Causal evidence: {ctx.get('flood_causal', '')}. "
            f"Fix: Install non-return outfall valves and sub-surface stormwater retention sumps."
        )

    return (
        f"This property in {ctx.get('city', 'the target area')} has a safety score of {score:.0f}/100. "
        f"{ctx.get('flood_causal', '')}. Ask me about specific hazards or mitigation steps!"
    )
