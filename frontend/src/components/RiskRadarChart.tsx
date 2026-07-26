"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import {
  ResponsiveContainer, RadarChart, PolarGrid,
  PolarAngleAxis, Radar, Tooltip,
} from "recharts";
import { AnalysisResult } from "@/lib/api";

interface Props { data: AnalysisResult; }

const SHORT_LABELS: Record<string, string> = {
  flood_risk: "Flood", earthquake_risk: "Quake", cyclone_risk: "Cyclone",
  landslide_risk: "Slide", tsunami_risk: "Tsunami", heat_stress: "Heat",
  air_quality: "Air", groundwater: "Water", soil_quality: "Soil",
  pollution_proximity: "Pollution", climate_future: "Climate",
};

const HAZARD_KEYS = [
  "flood_risk", "earthquake_risk", "cyclone_risk", "landslide_risk",
  "tsunami_risk", "heat_stress", "air_quality", "groundwater",
  "soil_quality", "pollution_proximity", "climate_future",
];

export default function RiskRadarChart({ data }: Props) {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  if (!mounted) return <div className="h-full w-full shimmer rounded-xl" />;

  const chartData = HAZARD_KEYS.map((key) => {
    const hazard = (data as any)[key];
    return {
      subject: SHORT_LABELS[key] || key,
      safety: hazard ? Math.round(100 - hazard.score) : 50,
      fullMark: 100,
    };
  });

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="w-full h-full"
    >
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="70%" data={chartData}>
          <defs>
            <linearGradient id="radarGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#3b82f6" stopOpacity={0.7} />
              <stop offset="100%" stopColor="#8b5cf6" stopOpacity={0.3} />
            </linearGradient>
          </defs>
          <PolarGrid stroke="rgba(255,255,255,0.08)" />
          <PolarAngleAxis
            dataKey="subject"
            tick={{ fill: "#64748b", fontSize: 10, fontFamily: "Outfit, sans-serif" }}
          />
          <Tooltip
            contentStyle={{
              background: "rgba(10,15,30,0.95)",
              border: "1px solid rgba(255,255,255,0.1)",
              borderRadius: "10px",
              fontSize: "12px",
              color: "#e2e8f0",
            }}
            formatter={(val: any) => [`${val ?? 0}/100 (safety)`, ""]}
          />
          <Radar
            name="Safety"
            dataKey="safety"
            stroke="#3b82f6"
            strokeWidth={2}
            fill="url(#radarGrad)"
          />
        </RadarChart>
      </ResponsiveContainer>
    </motion.div>
  );
}
