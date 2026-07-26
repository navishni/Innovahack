"""
PDF Report generation using Jinja2 + xhtml2pdf / WeasyPrint.
Renders Hyperlocal Evidence Logs, Causal Analysis, Consequence Statements, and Costed Mitigations.
"""
import os
from datetime import datetime
from jinja2 import Template
from app.models.schemas import AnalysisResult

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: 'Helvetica Neue', Arial, sans-serif; color: #1a1a2e; background: white; font-size: 13px; line-height: 1.5; }
  .cover { background: linear-gradient(135deg, #0a0f1e 0%, #1a1a4e 100%); color: white; padding: 40px 40px; }
  .cover h1 { font-size: 32px; font-weight: 800; letter-spacing: -1px; }
  .cover .subtitle { font-size: 13px; color: #94a3b8; margin-top: 6px; }
  .cover .address { font-size: 16px; color: #e2e8f0; margin-top: 16px; font-weight: 500; }
  .cover .timestamp { font-size: 11px; color: #64748b; margin-top: 8px; }
  .score-banner { background: {% if r.safety_score >= 75 %}#065f46{% elif r.safety_score >= 50 %}#78350f{% else %}#7f1d1d{% endif %}; color: white; padding: 24px 40px; display: flex; justify-content: space-between; align-items: center; }
  .score-banner .score { font-size: 64px; font-weight: 900; }
  .score-banner .decision { font-size: 20px; font-weight: 700; }
  .score-banner .confidence { font-size: 12px; opacity: 0.8; margin-top: 4px; }
  .section { padding: 24px 40px; border-bottom: 1px solid #e2e8f0; }
  .section h2 { font-size: 18px; font-weight: 700; color: #0a0f1e; margin-bottom: 14px; border-left: 4px solid #3b82f6; padding-left: 10px; }
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
  .hazard-card { background: #f8fafc; border-radius: 8px; padding: 14px; border: 1px solid #e2e8f0; margin-bottom: 12px; }
  .hazard-card .name { font-size: 13px; font-weight: 700; color: #0a0f1e; }
  .hazard-card .level { font-size: 14px; font-weight: 700; margin-top: 2px; }
  .hazard-card .causal { font-size: 11px; color: #475569; margin-top: 6px; background: #ffffff; padding: 8px; border-radius: 6px; border: 1px solid #cbd5e1; }
  .hazard-card .consequence { font-size: 11px; color: #991b1b; font-weight: 600; margin-top: 6px; }
  .very-low { color: #059669; } .low { color: #16a34a; } .moderate { color: #d97706; } .high { color: #dc2626; } .very-high { color: #991b1b; }
  .summary-box { background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 8px; padding: 16px; font-size: 13px; line-height: 1.6; color: #0c4a6e; }
  .meaning-box { background: #fefce8; border: 1px solid #fef08a; border-radius: 8px; padding: 14px; font-size: 13px; color: #713f12; font-weight: 500; margin-top: 12px; }
  .evidence-table, .mitigation-table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 12px; }
  .evidence-table th, .mitigation-table th { background: #0a0f1e; color: white; text-align: left; padding: 8px 10px; font-size: 11px; }
  .evidence-table td, .mitigation-table td { border-bottom: 1px solid #e2e8f0; padding: 8px 10px; color: #334155; }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 99px; font-size: 10px; font-weight: 600; }
  .badge-low { background: #dcfce7; color: #166534; }
  .badge-mod { background: #fef3c7; color: #92400e; }
  .badge-maj { background: #fee2e2; color: #991b1b; }
  .footer { background: #f8fafc; padding: 20px 40px; font-size: 11px; color: #94a3b8; }
  .indices-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
  .index-card { text-align: center; background: #f8fafc; border-radius: 8px; padding: 12px; border: 1px solid #e2e8f0; }
  .index-card .val { font-size: 28px; font-weight: 800; color: #0a0f1e; }
  .index-card .lbl { font-size: 10px; color: #64748b; text-transform: uppercase; margin-top: 4px; }
</style>
</head>
<body>

<div class="cover">
  <h1>🛡️ GeoSafe AI</h1>
  <div class="subtitle">Hyperlocal Property Risk Reasoning & Evidence Assessment Report</div>
  <div class="address">{{ r.address }}</div>
  <div class="timestamp">Generated: {{ timestamp }} | Report ID: {{ r.id[:8] }}</div>
</div>

<div class="score-banner">
  <div>
    <div class="decision">{{ r.decision.value }}</div>
    <div class="confidence">AI Confidence: {{ r.confidence }}%</div>
  </div>
  <div class="score">{{ r.safety_score }}<span style="font-size:20px">/100</span></div>
</div>

<div class="section">
  <h2>Key Property Indices</h2>
  <div class="indices-grid">
    <div class="index-card"><div class="val">{{ r.climate_resilience_index }}</div><div class="lbl">Climate Resilience Index</div></div>
    <div class="index-card"><div class="val">{{ r.construction_suitability }}</div><div class="lbl">Construction Suitability</div></div>
    <div class="index-card"><div class="val">{{ r.investment_risk_rating }}</div><div class="lbl">Investment Risk Rating</div></div>
  </div>
</div>

<div class="section">
  <h2>Hyperlocal AI Risk Summary</h2>
  <div class="summary-box">{{ r.ai_summary }}</div>
  {% if r.what_this_means_for_you %}
  <div class="meaning-box">
    <strong>💡 What this means for you:</strong> {{ r.what_this_means_for_you }}
  </div>
  {% endif %}
</div>

{% if r.evidence_log %}
<div class="section">
  <h2>Localized Evidence Log</h2>
  <p style="font-size:11px; color:#64748b; margin-bottom:8px;">Chronological record of historical disaster events physically intersecting this plot's micro-watershed:</p>
  <table class="evidence-table">
    <thead>
      <tr>
        <th>Year</th>
        <th>Event Name</th>
        <th>Micro-Area Impact & Details</th>
        <th>Inundation Status</th>
        <th>Official Source</th>
      </tr>
    </thead>
    <tbody>
      {% for ev in r.evidence_log %}
      <tr>
        <td><strong>{{ ev.year }}</strong></td>
        <td><strong>{{ ev.event_name }}</strong></td>
        <td>{{ ev.details }}</td>
        <td><span class="badge badge-maj">{{ ev.inundation_status }}</span></td>
        <td><small>{{ ev.source }}</small></td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% endif %}

<div class="section">
  <h2>Hyperlocal Hazard Assessment</h2>
  {% for name, hazard in hazards %}
  <div class="hazard-card">
    <div class="name">{{ name }} — <span class="level {{ hazard.level.value.lower().replace(' ', '-') }}">{{ hazard.level.value }} (Score: {{ hazard.score }}/100)</span></div>
    {% if hazard.causal_analysis %}
    <div class="causal"><strong>Causal Feature:</strong> {{ hazard.causal_analysis }}</div>
    {% endif %}
    {% if hazard.consequence_statement %}
    <div class="consequence">{{ hazard.consequence_statement }}</div>
    {% endif %}
    {% if hazard.absence_signals %}
    <div style="font-size:11px; color:#059669; margin-top:6px; background:#dcfce7; padding:8px; border-radius:6px; border:1px solid #86efac;">
      <strong>✓ Positive Safety Signals:</strong>
      <ul style="margin-left: 16px; margin-top: 4px;">
      {% for sig in hazard.absence_signals %}
        <li>{{ sig }}</li>
      {% endfor %}
      </ul>
    </div>
    {% endif %}
    <div style="font-size:11px; color:#64748b; margin-top:4px;">{{ hazard.details }}</div>
    {% if hazard.source_citation %}
    <div style="font-size:10px; color:#94a3b8; margin-top:4px;"><em>{{ hazard.source_citation }}</em></div>
    {% endif %}
  </div>
  {% endfor %}
</div>

{% if r.flood_risk.mitigations or r.earthquake_risk.mitigations %}
<div class="section">
  <h2>Actionable Costed Mitigation Plan</h2>
  <table class="mitigation-table">
    <thead>
      <tr>
        <th>Category</th>
        <th>Actionable Fix</th>
        <th>Cost Tier</th>
        <th>Regulatory Body</th>
      </tr>
    </thead>
    <tbody>
      {% for m in r.flood_risk.mitigations %}
      <tr>
        <td>{{ m.category.value }}</td>
        <td>{{ m.action }}</td>
        <td>
          {% if 'Low' in m.cost_tier.value %}<span class="badge badge-low">{{ m.cost_tier.value }}</span>
          {% elif 'Moderate' in m.cost_tier.value %}<span class="badge badge-mod">{{ m.cost_tier.value }}</span>
          {% else %}<span class="badge badge-maj">{{ m.cost_tier.value }}</span>{% endif %}
        </td>
        <td>{{ m.regulatory_authority or 'Local Body' }}</td>
      </tr>
      {% endfor %}
      {% for m in r.earthquake_risk.mitigations %}
      <tr>
        <td>{{ m.category.value }}</td>
        <td>{{ m.action }}</td>
        <td>
          {% if 'Low' in m.cost_tier.value %}<span class="badge badge-low">{{ m.cost_tier.value }}</span>
          {% elif 'Moderate' in m.cost_tier.value %}<span class="badge badge-mod">{{ m.cost_tier.value }}</span>
          {% else %}<span class="badge badge-maj">{{ m.cost_tier.value }}</span>{% endif %}
        </td>
        <td>{{ m.regulatory_authority or 'Municipal Body' }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% endif %}

<div class="section">
  <h2>Insurance & Sustainability</h2>
  <p style="font-size:13px; margin-bottom:8px;"><strong>Insurance Risk:</strong> {{ r.insurance_risk_estimate }}</p>
  <p style="font-size:13px;"><strong>Long-term Sustainability:</strong> {{ r.long_term_sustainability }}</p>
</div>

<div class="section">
  <h2>Official Data Sources</h2>
  <p style="font-size:11px; color:#64748b; line-height:1.6;">{{ r.data_sources | join(' • ') }}</p>
</div>

<div class="footer">
  <p><strong>Disclaimer:</strong> This report is generated by GeoSafe AI using spatial evidence databases, OSM Overpass, and IS/NDMA standards. It is intended as a decision-support tool. Always consult certified engineers and local planning authorities before finalizing property purchase contracts.</p>
  <p style="margin-top:6px;">© {{ year }} GeoSafe AI | India-Centric Hyperlocal Property Risk Platform</p>
</div>

</body>
</html>
"""


async def generate_pdf_report(result: AnalysisResult) -> bytes:
    """Generate a PDF report from analysis result."""
    hazards = [
        ("Flood Risk", result.flood_risk),
        ("Earthquake Risk", result.earthquake_risk),
        ("Cyclone Risk", result.cyclone_risk),
        ("Landslide Risk", result.landslide_risk),
        ("Tsunami Risk", result.tsunami_risk),
        ("Heat Stress", result.heat_stress),
        ("Air Quality", result.air_quality),
        ("Groundwater", result.groundwater),
        ("Soil Quality", result.soil_quality),
        ("Industrial Pollution", result.pollution_proximity),
        ("Climate Future (2050)", result.climate_future),
    ]

    template = Template(HTML_TEMPLATE)
    html = template.render(
        r=result,
        hazards=hazards,
        timestamp=datetime.utcnow().strftime("%d %B %Y, %H:%M UTC"),
        year=datetime.utcnow().year,
    )

    try:
        from weasyprint import HTML
        pdf_bytes = HTML(string=html).write_pdf()
        return pdf_bytes
    except ImportError:
        try:
            from io import BytesIO
            from xhtml2pdf import pisa
            result_io = BytesIO()
            pisa_status = pisa.CreatePDF(html, dest=result_io)
            if not pisa_status.err:
                return result_io.getvalue()
        except ImportError:
            pass
        return html.encode("utf-8")
