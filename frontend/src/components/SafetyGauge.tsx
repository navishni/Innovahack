"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";

interface Props {
  score: number;
  decision: string;
  confidence: number;
  size?: number;
}

export default function SafetyGauge({ score, decision, confidence, size = 240 }: Props) {
  const [animated, setAnimated] = useState(0);

  useEffect(() => {
    const t = setTimeout(() => setAnimated(score), 120);
    return () => clearTimeout(t);
  }, [score]);

  const color = score >= 75 ? "#10b981" : score >= 50 ? "#f59e0b" : "#f43f5e";
  const glow = score >= 75 ? "rgba(16,185,129,0.3)" : score >= 50 ? "rgba(245,158,11,0.3)" : "rgba(244,63,94,0.3)";

  const strokeWidth = size * 0.09;
  const r = (size - strokeWidth * 2) / 2;
  const cx = size / 2;
  const cy = size / 2;

  // Arc: 220 degrees (from 200° to 340° clockwise for visual gauge)
  const ARC_DEG = 240;
  const START_DEG = 150; // bottom-left start
  const toRad = (d: number) => (d * Math.PI) / 180;
  const arcLen = (ARC_DEG / 360) * 2 * Math.PI * r;
  const filledLen = (animated / 100) * arcLen;

  const pathD = (start: number, sweep: number) => {
    const s = toRad(start);
    const e = toRad(start + sweep);
    const x1 = cx + r * Math.cos(s);
    const y1 = cy + r * Math.sin(s);
    const x2 = cx + r * Math.cos(e);
    const y2 = cy + r * Math.sin(e);
    const large = sweep > 180 ? 1 : 0;
    return `M ${x1} ${y1} A ${r} ${r} 0 ${large} 1 ${x2} ${y2}`;
  };

  return (
    <div className="flex flex-col items-center">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
          {/* Track */}
          <path d={pathD(START_DEG, ARC_DEG)} fill="none" stroke="rgba(255,255,255,0.08)"
            strokeWidth={strokeWidth} strokeLinecap="round" />
          {/* Filled arc */}
          <motion.path
            d={pathD(START_DEG, ARC_DEG)}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={arcLen}
            initial={{ strokeDashoffset: arcLen }}
            animate={{ strokeDashoffset: arcLen - filledLen }}
            transition={{ duration: 1.6, ease: "easeOut" }}
            style={{ filter: `drop-shadow(0 0 8px ${glow})` }}
          />
        </svg>

        {/* Center content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.5, type: "spring" }}
            className="text-center"
          >
            <div className="font-black leading-none" style={{ fontSize: size * 0.26, color, fontFamily: "Inter, sans-serif" }}>
              {Math.round(score)}
            </div>
            <div className="text-slate-500 text-xs uppercase tracking-widest mt-1">/ 100</div>
          </motion.div>
        </div>
      </div>

      {/* Labels below gauge */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.9 }}
        className="text-center mt-1"
      >
        <div className="text-sm font-bold px-4 py-1.5 rounded-full" style={{ color, background: `${color}18`, border: `1px solid ${color}40` }}>
          {decision}
        </div>
        <div className="text-xs text-slate-500 mt-2">
          AI Confidence: <span className="text-slate-300 font-semibold">{confidence.toFixed(0)}%</span>
        </div>
      </motion.div>
    </div>
  );
}
