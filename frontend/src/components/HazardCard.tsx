"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  ChevronDown, Droplets, Activity, Wind, Mountain,
  Waves, Thermometer, Layers, Factory, TrendingUp,
  AlertTriangle, CloudRain, ShieldCheck, CheckCircle2, FileText, Info
} from "lucide-react";
import { HazardScore } from "@/lib/api";

const ICON_MAP: Record<string, React.ElementType> = {
  flood_risk: Droplets,
  earthquake_risk: Activity,
  cyclone_risk: Wind,
  landslide_risk: Mountain,
  tsunami_risk: Waves,
  heat_stress: Thermometer,
  air_quality: CloudRain,
  groundwater: Droplets,
  soil_quality: Layers,
  pollution_proximity: Factory,
  climate_future: TrendingUp,
};

// Plain English labels for each hazard type
const PLAIN_LABELS: Record<string, string> = {
  flood_risk: "Flood Risk",
  earthquake_risk: "Earthquake Risk",
  cyclone_risk: "Cyclone / Storm Risk",
  landslide_risk: "Landslide Risk",
  tsunami_risk: "Tsunami Risk",
  heat_stress: "Extreme Heat",
  air_quality: "Air Quality",
  groundwater: "Water Supply",
  soil_quality: "Soil & Foundation",
  pollution_proximity: "Industrial Pollution",
  climate_future: "Future Climate Risk",
};

// Plain English one-liners explaining what the score means
const PLAIN_DESCRIPTIONS: Record<string, (level: string, score: number) => string> = {
  flood_risk: (lvl, s) => s >= 60 ? "This area is likely to flood during heavy rain. Water may enter your compound." : s >= 30 ? "Some chance of waterlogging during monsoon but usually manageable." : "Very low chance of flooding here.",
  earthquake_risk: (lvl, s) => s >= 60 ? "The ground here can shake significantly during an earthquake. Strong construction is a must." : s >= 30 ? "Mild earthquake shaking possible. Standard earthquake-safe construction is enough." : "Very stable ground — earthquakes are unlikely to cause damage here.",
  cyclone_risk: (lvl, s) => s >= 60 ? "This property is close to the coast and is in the path of cyclones. Roof and structure must be storm-proof." : s >= 30 ? "Occasionally affected by cyclone winds. Good roofing is advisable." : "This is an inland area — cyclones won't directly hit here.",
  landslide_risk: (lvl, s) => s >= 60 ? "The land slopes here. During heavy rain, mud and debris can slide downhill toward your property." : s >= 30 ? "Slightly sloped terrain — minor erosion possible but no major risk." : "Flat terrain — no risk of landslides at all.",
  tsunami_risk: (lvl, s) => s >= 60 ? "Very close to the sea and low-lying — a major ocean event could send waves to your property." : "Far enough from the coast or at sufficient elevation — tsunamis won't reach here.",
  heat_stress: (lvl, s) => s >= 60 ? "This area gets very hot. Outdoor activities are difficult in summer and cooling costs will be high." : s >= 30 ? "Moderately warm area with some heat stress in peak summer months." : "Pleasant temperatures — heat is not a major concern here.",
  air_quality: (lvl, s) => s >= 60 ? "Air quality here is poor. Breathing problems and dust pollution are common." : s >= 30 ? "Air quality is acceptable most days, but can get dusty in dry months." : "Clean air — no major pollution sources detected nearby.",
  groundwater: (lvl, s) => s >= 60 ? "Underground water is declining or contaminated. You'll likely need water treatment or rely on tankers." : s >= 30 ? "Groundwater is available but depths are increasing. Rainwater harvesting is recommended." : "Good groundwater availability in this area.",
  soil_quality: (lvl, s) => s >= 60 ? "The soil here expands and contracts with moisture. This can crack walls and foundations over time." : s >= 30 ? "Moderate soil quality — standard foundation design is adequate." : "Stable, good-quality soil — ideal for construction.",
  pollution_proximity: (lvl, s) => s >= 60 ? "Industrial factories or waste sites are nearby. There may be noise, smell, and air/water pollution." : "No major factories or dump yards detected nearby — clean environment.",
  climate_future: (lvl, s) => s >= 60 ? "By 2050, this area will be significantly hotter and wetter. Long-term liveability may reduce." : s >= 30 ? "Moderate climate change impacts expected — worth planning for." : "Relatively climate-resilient location for the long term.",
};

const LEVEL_COLORS: Record<string, { badge: string; glow: string; emoji: string }> = {
  "Very Low": { badge: "text-emerald-400 bg-emerald-400/10 border-emerald-400/25", glow: "#10b981", emoji: "🟢" },
  "Low":      { badge: "text-green-400 bg-green-400/10 border-green-400/25",   glow: "#34d399", emoji: "🟢" },
  "Moderate": { badge: "text-amber-400 bg-amber-400/10 border-amber-400/25",   glow: "#f59e0b", emoji: "🟡" },
  "High":     { badge: "text-orange-400 bg-orange-400/10 border-orange-400/30",glow: "#f97316", emoji: "🔴" },
  "Very High":{ badge: "text-rose-400 bg-rose-400/10 border-rose-400/30",      glow: "#f43f5e", emoji: "🔴" },
};

const SCORE_COLOR = (score: number) => {
  if (score < 20) return "#10b981";
  if (score < 40) return "#34d399";
  if (score < 60) return "#f59e0b";
  if (score < 75) return "#f97316";
  return "#f43f5e";
};

interface HazardCardProps {
  type: string;
  hazard: HazardScore;
}

export default function HazardCard({ type, hazard }: HazardCardProps) {
  const [expanded, setExpanded] = useState(false);
  const Icon = ICON_MAP[type] || AlertTriangle;
  const levelInfo = LEVEL_COLORS[hazard.level] || { badge: "text-slate-400 bg-slate-400/10 border-slate-400/20", glow: "#94a3b8", emoji: "⚪" };
  const barColor = SCORE_COLOR(hazard.score);
  const plainLabel = PLAIN_LABELS[type] || type.split("_").map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(" ");
  const plainDesc = PLAIN_DESCRIPTIONS[type]?.(hazard.level, hazard.score) ?? hazard.details;

  return (
    <motion.div
      layout
      onClick={() => setExpanded(!expanded)}
      className="glass rounded-2xl border border-white/10 p-5 hover:border-white/20 cursor-pointer transition-all select-none"
      style={{ boxShadow: expanded ? `0 0 20px ${levelInfo.glow}18` : "none" }}
    >
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3 min-w-0">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
            style={{ background: `${levelInfo.glow}18`, border: `1px solid ${levelInfo.glow}30` }}>
            <Icon className="w-5 h-5" style={{ color: levelInfo.glow }} />
          </div>
          <div className="min-w-0">
            <div className="text-base font-bold text-white leading-tight">{plainLabel}</div>
            <div className="text-xs text-slate-500 mt-0.5 font-medium">
              {levelInfo.emoji} {hazard.level} Risk
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 flex-shrink-0 pt-0.5">
          {/* Big numeric score */}
          <div className="text-2xl font-black tabular-nums" style={{ color: barColor }}>
            {Math.round(hazard.score)}
            <span className="text-xs text-slate-500 font-normal">/100</span>
          </div>
          <motion.div animate={{ rotate: expanded ? 180 : 0 }} transition={{ duration: 0.2 }}>
            <ChevronDown className="w-4 h-4 text-slate-500" />
          </motion.div>
        </div>
      </div>

      {/* Score bar */}
      <div className="mt-3 h-2 bg-white/5 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${hazard.score}%` }}
          transition={{ duration: 0.9, ease: "easeOut" }}
          className="h-full rounded-full"
          style={{ background: `linear-gradient(90deg, ${barColor}88, ${barColor})` }}
        />
      </div>

      {/* Plain English summary — always visible */}
      <p className="mt-3 text-sm text-slate-300 leading-relaxed font-medium">
        {plainDesc}
      </p>

      {/* Impact consequence — always visible if present */}
      {hazard.consequence_statement && (() => {
        const isHigh = hazard.score >= 60;
        const isMod = hazard.score >= 30 && hazard.score < 60;
        const consStyle = isHigh
          ? "text-rose-300 bg-rose-500/10 border-rose-500/20"
          : isMod
          ? "text-amber-300 bg-amber-500/10 border-amber-500/20"
          : "text-emerald-300 bg-emerald-500/10 border-emerald-500/20";
        const consIcon = isHigh ? "text-rose-400" : isMod ? "text-amber-400" : "text-emerald-400";
        return (
          <div className={`mt-3 flex items-start gap-2 text-sm ${consStyle} border rounded-xl p-3 leading-relaxed`}>
            <AlertTriangle className={`w-4 h-4 flex-shrink-0 mt-0.5 ${consIcon}`} />
            <span>{hazard.consequence_statement}</span>
          </div>
        );
      })()}

      {/* Expandable technical details */}
      <AnimatePresence initial={false}>
        {expanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.25 }}
            className="overflow-hidden"
          >
            <div className="mt-4 pt-4 border-t border-white/5 space-y-3">
              {/* Technical causal detail */}
              {hazard.causal_analysis && (
                <div className="bg-blue-500/10 border border-blue-500/20 rounded-xl p-3">
                  <div className="flex items-center gap-1.5 text-xs text-blue-400 font-bold mb-1.5">
                    <Info className="w-3.5 h-3.5" /> Technical Detail
                  </div>
                  <p className="text-sm text-slate-300 leading-relaxed">{hazard.causal_analysis}</p>
                </div>
              )}

              {/* Positive absence signals */}
              {hazard.absence_signals && hazard.absence_signals.length > 0 && (
                <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-xl p-3 space-y-2">
                  <div className="flex items-center gap-1.5 text-sm font-bold text-emerald-400">
                    <ShieldCheck className="w-4 h-4" /> Why It's Safe Here
                  </div>
                  {hazard.absence_signals.map((sig, i) => (
                    <div key={i} className="flex items-start gap-2 text-sm text-emerald-300/90 leading-relaxed">
                      <span className="text-emerald-500 flex-shrink-0 mt-0.5">✓</span>
                      {sig}
                    </div>
                  ))}
                </div>
              )}

              {/* What to do / Mitigations */}
              {hazard.mitigations && hazard.mitigations.length > 0 && (
                <div>
                  <div className="text-sm font-bold text-white mb-2 flex items-center gap-1.5">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" /> What You Should Do
                  </div>
                  <div className="space-y-2">
                    {hazard.mitigations.map((m, i) => (
                      <div key={i} className="bg-white/5 border border-white/10 rounded-xl p-3">
                        <div className="flex items-center justify-between gap-2 mb-1.5">
                          <span className="text-xs text-slate-400 font-semibold">{m.category}</span>
                          <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
                            m.cost_tier.includes("Low") ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30" :
                            m.cost_tier.includes("Moderate") ? "bg-amber-500/20 text-amber-400 border border-amber-500/30" :
                            "bg-rose-500/20 text-rose-400 border border-rose-500/30"
                          }`}>
                            {m.cost_tier}
                          </span>
                        </div>
                        <p className="text-sm text-slate-200 leading-relaxed">{m.action}</p>
                        {m.regulatory_authority && (
                          <div className="text-xs text-slate-500 mt-1.5 flex items-center gap-1">
                            <span>📋 Approving Authority:</span>
                            <span className="text-slate-400 font-medium">{m.regulatory_authority}</span>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Source citation */}
              {hazard.source_citation && (
                <div className="text-xs text-slate-500 italic pt-1 border-t border-white/5 flex items-center gap-1.5">
                  <FileText className="w-3 h-3 text-slate-600 flex-shrink-0" />
                  Data Source: {hazard.source_citation}
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Expand hint */}
      {!expanded && (
        <div className="mt-2 text-xs text-slate-600 flex items-center gap-1">
          <ChevronDown className="w-3 h-3" /> Tap to see details & what to do
        </div>
      )}
    </motion.div>
  );
}
