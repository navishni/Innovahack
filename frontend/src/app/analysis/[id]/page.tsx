"use client";

import React, { useEffect, useState } from "react";
import { getAnalysis, generateReport, AnalysisResult } from "@/lib/api";
import { useGeoSafeStore } from "@/lib/store";
import { motion } from "framer-motion";
import Link from "next/link";
import {
  Download, Building2, ShieldCheck, TrendingUp, MapPin,
  AlertCircle, Loader2, Shield, Flame, Cross, Home,
  ArrowLeft, CheckCircle, Clock, FileText, AlertTriangle, Sparkles
} from "lucide-react";
import dynamic from "next/dynamic";
import toast from "react-hot-toast";
import Navbar from "@/components/Navbar";

const AIChat = dynamic(() => import("@/components/AIChat"), { ssr: false });
const SafetyGauge = dynamic(() => import("@/components/SafetyGauge"), { ssr: false });
const RiskRadarChart = dynamic(() => import("@/components/RiskRadarChart"), { ssr: false });
const HazardCard = dynamic(() => import("@/components/HazardCard"), { ssr: false });
const PropertyMap = dynamic(() => import("@/components/PropertyMap"), { ssr: false });

export default function AnalysisDashboard({ params }: { params: Promise<{ id: string }> }) {
  const resolvedParams = React.use(params);
  const analysisId = resolvedParams.id;

  const { currentAnalysis, setAnalysis } = useGeoSafeStore();
  const [data, setData] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        if (currentAnalysis?.id === analysisId) {
          setData(currentAnalysis);
          setLoading(false);
          return;
        }

        const res = await getAnalysis(analysisId);
        setData(res);
        setAnalysis(res);
      } catch (err: any) {
        setError(err.message || "Analysis not found");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [analysisId, currentAnalysis, setAnalysis]);

  const handleDownload = async () => {
    if (!data) return;
    setDownloading(true);
    try {
      const blob = await generateReport(data.id);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `geosafe_${data.id.slice(0, 8)}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
      toast.success("Report downloaded!");
    } catch {
      toast.error("Report generation failed");
    } finally {
      setDownloading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#0a0f1e] flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 text-blue-500 animate-spin mx-auto mb-4" />
          <p className="text-slate-400">Loading hyperlocal risk dashboard...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-[#0a0f1e] flex items-center justify-center p-6">
        <div className="glass rounded-2xl p-8 max-w-md w-full text-center border border-white/10 shadow-2xl">
          <div className="w-16 h-16 rounded-full bg-rose-500/10 border border-rose-500/20 flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="w-8 h-8 text-rose-500" />
          </div>
          <h2 className="text-white font-black text-2xl mb-2">Analysis Not Found</h2>
          <p className="text-slate-400 text-sm mb-6">
            This analysis ID may have expired or is invalid. Please start a new analysis.
          </p>
          <div className="flex flex-col gap-3">
            <Link href="/search" className="w-full py-3.5 px-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl font-bold shadow-lg shadow-blue-600/25 hover:from-blue-500 hover:to-purple-500 transition-all flex items-center justify-center gap-2">
              <Shield className="w-4 h-4" /> Start New Property Analysis
            </Link>
            <Link href="/" className="w-full py-3 px-4 glass text-slate-300 rounded-xl font-semibold hover:text-white hover:bg-white/5 transition-all text-sm">
              Return to Home Page
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const decisionColor = data.safety_score >= 75 ? "#10b981" : data.safety_score >= 50 ? "#f59e0b" : "#f43f5e";
  const decisionEmoji = data.decision === "Safe to Buy" ? "🟢" : data.decision === "Buy with Precautions" ? "🟡" : "🔴";

  const hazardEntries = [
    "flood_risk", "earthquake_risk", "cyclone_risk", "landslide_risk",
    "tsunami_risk", "heat_stress", "air_quality", "groundwater",
    "soil_quality", "pollution_proximity", "climate_future"
  ].map(key => [key, (data as any)[key]]).filter(([, v]) => v);

  return (
    <div className="min-h-screen bg-[#0a0f1e] text-slate-100">
      <Navbar />

      <main className="max-w-7xl mx-auto px-6 py-10 space-y-10">
        {/* Address header */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-2 text-xs text-slate-500 mb-2">
            <MapPin className="w-3.5 h-3.5 text-blue-400" />
            <span>{data.lat.toFixed(4)}, {data.lon.toFixed(4)}</span>
            <span>·</span>
            <Clock className="w-3.5 h-3.5" />
            <span>{new Date(data.analysis_timestamp).toLocaleString("en-IN")}</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-black text-white" style={{ fontFamily: 'Inter, sans-serif' }}>
            {data.city && data.state ? `${data.city}, ${data.state}` : data.address.split(",").slice(0, 3).join(",")}
          </h1>
          <p className="text-sm text-slate-400 mt-1 truncate max-w-3xl">{data.address}</p>
        </motion.div>

        {/* HERO: Gauge + Index cards */}
        <div className="grid lg:grid-cols-3 gap-6">
          <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.1 }}
            className="glass rounded-2xl p-6 flex flex-col items-center justify-center border border-white/10"
            style={{ boxShadow: `0 0 60px ${decisionColor}20` }}>
            <SafetyGauge score={data.safety_score} decision={data.decision} confidence={data.confidence} />
            <div className="mt-4 text-sm font-semibold" style={{ color: decisionColor }}>
              {decisionEmoji} {data.decision}
            </div>
          </motion.div>

          <div className="lg:col-span-2 grid sm:grid-cols-3 gap-4">
            {[
              { label: "Climate Resilience", value: data.climate_resilience_index, icon: TrendingUp, color: "#10b981" },
              { label: "Construction Suitability", value: data.construction_suitability, icon: Building2, color: "#3b82f6" },
              { label: "Investment Risk", value: data.investment_risk_rating, icon: ShieldCheck, color: "#8b5cf6" },
            ].map((m, i) => (
              <motion.div key={m.label} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 + i * 0.08 }}
                className="glass rounded-2xl p-5 border border-white/10 relative overflow-hidden">
                <div className="absolute top-3 right-3 opacity-10">
                  <m.icon className="w-16 h-16" style={{ color: m.color }} />
                </div>
                <div className="text-xs text-slate-400 mb-2 font-medium uppercase tracking-wider">{m.label}</div>
                <div className="text-4xl font-black" style={{ color: m.color, fontFamily: 'Inter, sans-serif' }}>
                  {m.value.toFixed(0)}<span className="text-lg text-slate-500">/100</span>
                </div>
              </motion.div>
            ))}

            {/* AI Summary card */}
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}
              className="sm:col-span-3 glass rounded-2xl p-6 border border-blue-500/30 relative overflow-hidden">
              <div className="absolute left-0 top-0 bottom-0 w-1.5 bg-gradient-to-b from-blue-500 to-purple-600 rounded-l-2xl" />
              <div className="pl-3 space-y-3">
                <div className="flex items-center gap-2 text-xs text-blue-400 font-bold uppercase tracking-wider">
                  <Sparkles className="w-4 h-4" /> AI Hyperlocal Executive Reasoning
                </div>
                <p className="text-sm text-slate-200 leading-relaxed">{data.ai_summary}</p>
                
                {data.what_this_means_for_you && (
                  <div className="mt-3 p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-200 leading-relaxed font-medium">
                    <span className="font-bold text-amber-400 block mb-1">💡 What this means for you:</span>
                    {data.what_this_means_for_you}
                  </div>
                )}
              </div>
            </motion.div>
          </div>
        </div>

        {/* OSM Building Footprints Choropleth Map */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}
          className="glass rounded-2xl p-6 border border-white/10"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2 text-xl font-bold text-white" style={{ fontFamily: 'Inter, sans-serif' }}>
              <MapPin className="w-6 h-6 text-blue-400" /> Neighborhood Risk Choropleth
            </div>
            <span className="text-[10px] font-mono px-2.5 py-1 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
              Real OSM Building Footprints
            </span>
          </div>
          <PropertyMap lat={data.lat} lon={data.lon} address={data.address} safetyScore={data.safety_score} />
        </motion.div>

        {/* Localized Evidence Log */}
        {data.evidence_log && data.evidence_log.length > 0 && (
          <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
            className="glass rounded-2xl p-6 border border-white/10">
            <div className="flex items-center gap-2 text-base font-bold text-white mb-1" style={{ fontFamily: 'Inter, sans-serif' }}>
              <FileText className="w-5 h-5 text-blue-400" /> Localized Evidence Log
            </div>
            <p className="text-xs text-slate-400 mb-4">
              Chronological disaster evidence log intersecting this property's micro-watershed:
            </p>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="border-b border-white/10 text-slate-400 font-semibold bg-white/5">
                    <th className="p-3">Year</th>
                    <th className="p-3">Event Name</th>
                    <th className="p-3">Micro-Area Impact Details</th>
                    <th className="p-3">Inundation Status</th>
                    <th className="p-3">Official Source</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/5">
                  {data.evidence_log.map((ev, i) => (
                    <tr key={i} className="hover:bg-white/5 transition-colors">
                      <td className="p-3 font-bold text-blue-400">{ev.year}</td>
                      <td className="p-3 font-semibold text-white">{ev.event_name}</td>
                      <td className="p-3 text-slate-300 max-w-md leading-relaxed">{ev.details}</td>
                      <td className="p-3">
                        <span className="px-2.5 py-1 rounded-full bg-rose-500/20 text-rose-300 border border-rose-500/30 font-semibold text-[11px]">
                          {ev.inundation_status}
                        </span>
                      </td>
                      <td className="p-3 text-slate-400 italic">{ev.source}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </motion.div>
        )}

        {/* Hazards Grid + Radar Chart */}
        <div className="grid lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-4">
            <h2 className="text-xl font-bold text-white" style={{ fontFamily: 'Inter, sans-serif' }}>
              Hyperlocal Hazard Assessment
            </h2>
            <div className="grid sm:grid-cols-2 gap-4">
              {hazardEntries.map(([key, hazard], i) => (
                <motion.div key={key as string}
                  initial={{ opacity: 0, y: 15 }} whileInView={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.04 }} viewport={{ once: true }}>
                  <HazardCard type={key as string} hazard={hazard} />
                </motion.div>
              ))}
            </div>
          </div>

          <div>
            <h2 className="text-xl font-bold text-white mb-4" style={{ fontFamily: 'Inter, sans-serif' }}>Risk Profile Radar</h2>
            <div className="glass rounded-2xl p-4 border border-white/10 h-96">
              <RiskRadarChart data={data} />
            </div>
          </div>
        </div>

        {/* Recommendations */}
        <div className="grid md:grid-cols-2 gap-6">
          <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
            className="glass rounded-2xl p-6 border border-white/10">
            <h3 className="text-base font-bold text-white mb-4 flex items-center gap-2">
              <Building2 className="w-5 h-5 text-blue-400" /> Construction Recommendations
            </h3>
            <ul className="space-y-3">
              {data.construction_recommendations.map((rec, i) => (
                <li key={i} className="flex items-start gap-2.5 text-sm text-slate-300">
                  <CheckCircle className="w-4 h-4 text-blue-400 flex-shrink-0 mt-0.5" />
                  <span>{rec}</span>
                </li>
              ))}
            </ul>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
            className="glass rounded-2xl p-6 border border-white/10">
            <h3 className="text-base font-bold text-white mb-4 flex items-center gap-2">
              <Shield className="w-5 h-5 text-purple-400" /> Disaster Preparedness
            </h3>
            <ul className="space-y-3">
              {data.disaster_preparedness.map((item, i) => (
                <li key={i} className="flex items-start gap-2.5 text-sm text-slate-300">
                  <CheckCircle className="w-4 h-4 text-purple-400 flex-shrink-0 mt-0.5" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </motion.div>
        </div>

        {/* Insurance & Sustainability */}
        <div className="grid md:grid-cols-2 gap-6">
          <div className="glass rounded-2xl p-6 border border-amber-500/20 bg-amber-500/5">
            <div className="text-xs text-amber-400 uppercase tracking-wider mb-2 font-semibold">Insurance Risk Estimate</div>
            <p className="text-sm text-slate-300 leading-relaxed">{data.insurance_risk_estimate}</p>
          </div>
          <div className="glass rounded-2xl p-6 border border-emerald-500/20 bg-emerald-500/5">
            <div className="text-xs text-emerald-400 uppercase tracking-wider mb-2 font-semibold">Long-term Sustainability</div>
            <p className="text-sm text-slate-300 leading-relaxed">{data.long_term_sustainability}</p>
          </div>
        </div>

        {/* Nearby Services */}
        {data.nearby_services.length > 0 && (
          <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
            <h2 className="text-xl font-bold text-white mb-4" style={{ fontFamily: 'Inter, sans-serif' }}>Nearby Emergency Services</h2>
            <div className="grid sm:grid-cols-2 md:grid-cols-4 gap-4">
              {data.nearby_services.slice(0, 8).map((svc, i) => (
                <div key={i} className="glass rounded-xl p-4 border border-white/10 flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-white/5 flex items-center justify-center flex-shrink-0">
                    <SvcIcon type={svc.type} />
                  </div>
                  <div className="min-w-0">
                    <div className="text-sm font-medium text-white truncate">{svc.name}</div>
                    <div className="text-xs text-slate-400">{svc.distance_km.toFixed(1)} km away</div>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Data sources */}
        <div className="glass rounded-xl p-4 border border-white/5">
          <div className="text-xs text-slate-500 uppercase tracking-wider mb-2">Official Data Sources</div>
          <div className="flex flex-wrap gap-2">
            {data.data_sources.map(src => (
              <span key={src} className="text-xs px-2.5 py-1 rounded-full bg-white/5 text-slate-400 border border-white/5">{src}</span>
            ))}
          </div>
        </div>
        <div className="h-20" />
      </main>

      {data && <AIChat analysisId={data.id} analysisData={data} />}
    </div>
  );
}

function SvcIcon({ type }: { type: string }) {
  if (type === "hospital") return <Cross className="w-5 h-5 text-red-400" />;
  if (type === "fire_station") return <Flame className="w-5 h-5 text-orange-400" />;
  if (type === "police") return <Shield className="w-5 h-5 text-blue-400" />;
  return <Home className="w-5 h-5 text-emerald-400" />;
}
