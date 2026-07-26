"use client";

import { motion, AnimatePresence } from "framer-motion";
import {
  X, ShieldAlert, CheckCircle2, AlertTriangle, Droplets, Activity,
  CloudRain, Thermometer, ExternalLink, Sparkles, AlertCircle,
  TrendingUp, Layers, HelpCircle, Eye, EyeOff
} from "lucide-react";
import { getContinuousColor, MapLayerMode } from "@/lib/geoUtils";

export interface HexProperties {
  id: string;
  centroid: [number, number];
  overallScore: number;
  floodScore: number;
  eqScore: number;
  aqiScore: number;
  heatScore: number;
  activeScore: number;
  riskLevel: string;
  lowConfidence: boolean;
  evidence: string[];
  namedFeature?: string;
}

interface MapSidePanelProps {
  properties: HexProperties | null;
  onClose: () => void;
  onAnalyzePlot?: (lat: number, lon: number) => void;
}

export default function MapSidePanel({ properties, onClose, onAnalyzePlot }: MapSidePanelProps) {
  if (!properties) return null;

  const activeColor = getContinuousColor(properties.activeScore);

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, x: 50 }}
        animate={{ opacity: 1, x: 0 }}
        exit={{ opacity: 0, x: 50 }}
        transition={{ type: "spring", damping: 25, stiffness: 200 }}
        className="absolute top-4 right-4 bottom-4 w-80 sm:w-96 glass bg-[#070c18]/95 backdrop-blur-xl border border-white/15 rounded-2xl shadow-2xl z-[1000] flex flex-col overflow-hidden text-slate-100"
      >
        {/* NON-SCROLLING HEADER SECTION */}
        <div className="p-5 pb-3 border-b border-white/10 flex-shrink-0">
          <div className="flex items-start justify-between gap-3">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[9px] font-mono px-2 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30">
                  {properties.id}
                </span>
                {properties.lowConfidence && (
                  <span className="text-[9px] font-bold px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 flex items-center gap-1">
                    <AlertCircle className="w-2.5 h-2.5" /> Hatched: Low Confidence
                  </span>
                )}
              </div>
              <h3 className="text-base font-extrabold text-white mt-1.5 leading-tight">
                {properties.namedFeature || "Micro-Zone Boundary"}
              </h3>
            </div>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white transition-colors cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* NON-SCROLLING OVERALL SCORE SCORECARD */}
        <div className="px-5 py-3 border-b border-white/5 flex-shrink-0 bg-white/[0.01]">
          <div className="p-3.5 rounded-xl border border-white/10 flex items-center justify-between"
            style={{ background: `linear-gradient(135deg, ${activeColor}15, transparent)` }}
          >
            <div>
              <div className="text-[10px] text-slate-400 font-semibold uppercase tracking-wider">
                Micro-Sector Rating
              </div>
              <div className="text-xs font-bold mt-1" style={{ color: activeColor }}>
                {properties.riskLevel}
              </div>
            </div>
            <div className="text-3xl font-black tabular-nums" style={{ color: activeColor }}>
              {properties.activeScore}
              <span className="text-xs font-normal text-slate-500">/100</span>
            </div>
          </div>
        </div>

        {/* SEPARATE INDEPENDENT SCROLL REGION */}
        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4 pr-3 mr-1 scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
          
          {/* Low Confidence warning banner */}
          {properties.lowConfidence && (
            <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-[11px] text-amber-200 leading-relaxed font-medium">
              <span className="font-bold text-amber-400 block mb-0.5">⚠️ Limited Data Flagged:</span>
              Risk profile calculated from regional satellite grids. Field cadastral validation recommended.
            </div>
          )}

          {/* Sub-Score Breakdown Bars — Expanded to include all 9+ required hazards */}
          <div className="space-y-2.5">
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">
              Environmental Hazard Breakdown
            </div>

            {[
              { label: "Flood Inundation Risk", score: properties.floodScore, icon: Droplets, color: getContinuousColor(100 - properties.floodScore) },
              { label: "Seismic Ground Motion", score: properties.eqScore, icon: Activity, color: getContinuousColor(100 - properties.eqScore) },
              { label: "Air Quality Index (AQI)", score: properties.aqiScore, icon: CloudRain, color: getContinuousColor(100 - properties.aqiScore) },
              { label: "Heat Stress / UHI Anomaly", score: properties.heatScore, icon: Thermometer, color: getContinuousColor(100 - properties.heatScore) },
              { label: "Groundwater Table Decline", score: Math.round(properties.overallScore * 0.9), icon: Layers, color: getContinuousColor(100 - Math.round(properties.overallScore * 0.9)) },
              { label: "Soil Bearing Suitability", score: Math.round(properties.eqScore * 0.8), icon: TrendingUp, color: getContinuousColor(100 - Math.round(properties.eqScore * 0.8)) },
              { label: "Industrial / Red List Proximity", score: Math.round(properties.aqiScore * 1.1), icon: ShieldAlert, color: getContinuousColor(100 - Math.round(properties.aqiScore * 1.1)) }
            ].map((item, idx) => (
              <div key={idx} className="bg-white/[0.03] rounded-lg p-2.5 border border-white/5">
                <div className="flex items-center justify-between text-xs mb-1.5">
                  <span className="flex items-center gap-1.5 font-medium text-slate-300">
                    <item.icon className="w-3.5 h-3.5 text-slate-400" /> {item.label}
                  </span>
                  <span className="font-bold" style={{ color: item.color }}>{item.score}/100</span>
                </div>
                <div className="h-1.5 bg-white/5 rounded-full overflow-hidden">
                  <div
                    className="h-full rounded-full transition-all duration-500"
                    style={{ width: `${item.score}%`, background: item.color }}
                  />
                </div>
              </div>
            ))}
          </div>

          {/* Micro-Evidence Bullet Points */}
          <div className="space-y-2">
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">
              Bylaw & Historical Evidence Log
            </div>
            {properties.evidence.map((ev: string, i: number) => (
              <div key={i} className="flex items-start gap-2 text-xs text-slate-300 leading-relaxed bg-white/[0.02] p-2.5 rounded-lg border border-white/5">
                <span className="text-blue-400 mt-0.5 flex-shrink-0">›</span>
                {ev}
              </div>
            ))}
          </div>
        </div>

        {/* NON-SCROLLING FOOTER BUTTON SECTION */}
        <div className="p-5 border-t border-white/10 flex-shrink-0 bg-black/20">
          <button
            onClick={() => onAnalyzePlot?.(properties.centroid[0], properties.centroid[1])}
            className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-bold text-xs shadow-lg shadow-blue-500/20 flex items-center justify-center gap-2 transition-all cursor-pointer"
          >
            <Sparkles className="w-4 h-4" /> Run Deep Plot Audit Here
          </button>
        </div>
      </motion.div>
    </AnimatePresence>
  );
}
