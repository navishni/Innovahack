"use client";
import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";
import { Plus, X, Search, Loader2, MapPin, TrendingUp, TrendingDown, Minus, ArrowRight } from "lucide-react";
import toast from "react-hot-toast";
import { analyzeProperty, AnalysisResult } from "@/lib/api";
import Navbar from "@/components/Navbar";

const STORAGE_KEY = "geosafe-compare-properties";

function loadProperties(): AnalysisResult[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch { return []; }
}

function saveProperties(props: AnalysisResult[]) {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(props)); } catch {}
}

const HAZARD_KEYS = [
  { key: "flood_risk", label: "Flood Risk" },
  { key: "earthquake_risk", label: "Earthquake Risk" },
  { key: "cyclone_risk", label: "Cyclone Risk" },
  { key: "landslide_risk", label: "Landslide Risk" },
  { key: "air_quality", label: "Air Quality" },
  { key: "heat_stress", label: "Heat Stress" },
  { key: "groundwater", label: "Groundwater" },
  { key: "soil_quality", label: "Soil Quality" },
  { key: "pollution_proximity", label: "Industrial Pollution" },
  { key: "climate_future", label: "Climate 2050" },
];

function ScoreBar({ score, best }: { score: number; best: boolean }) {
  const color = score >= 70 ? "#f43f5e" : score >= 40 ? "#f59e0b" : "#10b981";
  const display = typeof score === "number" ? score.toFixed(2) : "0";
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 min-w-0 progress-bar">
        <div className="progress-fill" style={{ width: `${Math.min(score, 100)}%`, background: color }} />
      </div>
      <span className="text-xs font-bold tabular-nums shrink-0 w-10 text-right" style={{ color }}>{display}</span>
      {best && <TrendingDown className="w-3 h-3 text-emerald-400 shrink-0" />}
    </div>
  );
}

export default function ComparePage() {
  const [properties, setProperties] = useState<AnalysisResult[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setProperties(loadProperties());
  }, []);

  const addProperty = async () => {
    if (!input.trim()) return;
    if (properties.length >= 3) { toast.error("Maximum 3 properties for comparison"); return; }
    setLoading(true);
    try {
      const result = await analyzeProperty(input);
      const updated = [...properties, result];
      setProperties(updated);
      saveProperties(updated);
      setInput("");
      toast.success("Property analyzed!");
    } catch (e: any) {
      toast.error(e.message || "Failed to analyze property");
    } finally {
      setLoading(false);
    }
  };

  const removeProperty = (id: string) => {
    const updated = properties.filter(x => x.id !== id);
    setProperties(updated);
    saveProperties(updated);
  };

  const getBestIdx = (key: string): number => {
    if (properties.length < 2) return -1;
    const scores = properties.map(p => (p as any)[key]?.score ?? 0);
    return scores.indexOf(Math.min(...scores));
  };

  const safetyBest = properties.length > 0
    ? properties.indexOf(properties.reduce((a, b) => a.safety_score > b.safety_score ? a : b))
    : -1;

  return (
    <main className="min-h-screen bg-[#0a0f1e]">
      <Navbar />

      <div className="max-w-7xl mx-auto px-6 py-12">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-10">
          <h1 className="text-4xl font-black text-white mb-2" style={{ fontFamily: 'Inter, sans-serif' }}>
            Compare <span className="gradient-text">Properties</span>
          </h1>
          <p className="text-slate-400">Add up to 3 properties to compare their safety scores side by side.</p>
        </motion.div>

        {/* Add property input */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
          className="flex gap-3 mb-10">
          <div className="relative flex-1 max-w-xl">
            <MapPin className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              value={input} onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === "Enter" && addProperty()}
              placeholder="Enter address (e.g. Bandra West, Mumbai)"
              className="w-full bg-white/5 border border-white/10 rounded-xl pl-10 pr-4 py-3.5 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-blue-500/50 transition-all"
            />
          </div>
          <button onClick={addProperty} disabled={loading || properties.length >= 3}
            className="flex items-center gap-2 px-5 py-3.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm disabled:opacity-50 transition-all">
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
            Add Property
          </button>
        </motion.div>

        {properties.length === 0 && (
          <div className="text-center py-32">
            <div className="w-16 h-16 rounded-2xl bg-white/5 flex items-center justify-center mx-auto mb-4">
              <TrendingUp className="w-8 h-8 text-slate-600" />
            </div>
            <h3 className="text-slate-400 font-semibold mb-2">No properties added yet</h3>
            <p className="text-slate-500 text-sm mb-6">Add at least 2 properties to start comparing</p>
            <div className="flex flex-wrap justify-center gap-2">
              {["Bandra West, Mumbai", "Indiranagar, Bengaluru", "Jubilee Hills, Hyderabad"].map(s => (
                <button key={s} onClick={() => setInput(s)}
                  className="text-xs px-3 py-1.5 rounded-full glass border border-white/10 text-slate-400 hover:text-white transition-all">
                  + {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {properties.length > 0 && (
          <div>
        {/* Overall score cards */}
        <div className="grid gap-4 mb-8" style={{ gridTemplateColumns: `repeat(${Math.min(properties.length, 3)}, minmax(0, 1fr))` }}>
          {properties.map((p, i) => {
            const isBest = i === safetyBest;
            const color = p.safety_score >= 75 ? "#10b981" : p.safety_score >= 50 ? "#f59e0b" : "#f43f5e";
            const decision = p.decision as string;
            return (
              <motion.div key={p.id} initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
                className={`glass rounded-2xl p-6 relative overflow-hidden ${isBest ? "border border-emerald-500/30 glow-emerald" : "border border-white/10"}`}>
                {isBest && (
                  <div className="absolute top-3 right-3 text-xs px-2 py-1 rounded-full bg-emerald-500/20 text-emerald-400 font-semibold border border-emerald-500/30">
                    ✓ Best Pick
                  </div>
                )}
                <button onClick={() => removeProperty(p.id)} className="absolute top-3 left-3 text-slate-500 hover:text-white transition-colors">
                  <X className="w-4 h-4" />
                </button>
                <div className="mt-4">
                  <div className="text-xs text-slate-500 mb-1 truncate">{p.city}, {p.state}</div>
                  <div className="text-xs text-slate-400 mb-4 truncate" title={p.address}>{p.address.substring(0, 50)}...</div>
                  <div className="text-5xl font-black mb-1 tabular-nums" style={{ color, fontFamily: 'Inter, sans-serif' }}>
                    {p.safety_score.toFixed(2)}
                    <span className="text-xl text-slate-500">/100</span>
                  </div>
                  <div className="text-sm font-semibold mb-3" style={{ color }}>
                    {decision === "Safe to Buy" ? "🟢" : decision === "Buy with Precautions" ? "🟡" : "🔴"} {decision}
                  </div>
                  <div className="text-xs text-slate-500">Confidence: {p.confidence}%</div>
                </div>
                <Link href={`/analysis/${p.id}`}
                  className="mt-4 flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300 transition-colors">
                  View Full Analysis <ArrowRight className="w-3 h-3" />
                </Link>
              </motion.div>
            );
          })}
        </div>

            {/* Detailed comparison table */}
            {properties.length >= 2 && (
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
                className="glass rounded-2xl overflow-hidden border border-white/10">
                <div className="p-6 border-b border-white/5">
                  <h2 className="text-lg font-bold text-white">Hazard Comparison</h2>
                  <p className="text-slate-400 text-sm">Lower score = safer (green = best performer)</p>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-white/5">
                        <th className="text-left p-4 text-sm text-slate-400 font-semibold">Parameter</th>
                        {properties.map(p => (
                          <th key={p.id} className="p-4 text-sm text-slate-300 font-semibold min-w-[160px]">
                            {p.city || p.address.split(",")[0]}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {HAZARD_KEYS.map(({ key, label }, ri) => {
                        const bestIdx = getBestIdx(key);
                        return (
                          <tr key={key} className={`border-b border-white/5 ${ri % 2 === 0 ? "bg-white/[0.01]" : ""}`}>
                            <td className="p-4 text-sm text-slate-300 font-medium">{label}</td>
                            {properties.map((p, pi) => {
                              const hazard = (p as any)[key];
                              return (
                                <td key={p.id} className="p-4">
                                  <ScoreBar score={hazard?.score ?? 0} best={pi === bestIdx} />
                                  <div className="text-xs text-slate-500 mt-1">{hazard?.level ?? "-"}</div>
                                </td>
                              );
                            })}
                          </tr>
                        );
                      })}

                      {/* Summary rows */}
                      {[
                        { label: "Climate Resilience", fn: (p: AnalysisResult) => ({ score: p.climate_resilience_index, invert: true }) },
                        { label: "Construction Suitability", fn: (p: AnalysisResult) => ({ score: p.construction_suitability, invert: true }) },
                      ].map(({ label, fn }) => (
                        <tr key={label} className="border-b border-white/5 bg-white/[0.02]">
                          <td className="p-4 text-sm text-white font-semibold">{label}</td>
                          {properties.map(p => {
                            const { score } = fn(p);
                            const color = score >= 70 ? "#10b981" : score >= 40 ? "#f59e0b" : "#f43f5e";
                            return (
                              <td key={p.id} className="p-4">
                                <span className="text-base font-bold tabular-nums" style={{ color }}>{score.toFixed(2)}/100</span>
                              </td>
                            );
                          })}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </motion.div>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
