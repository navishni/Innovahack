"use client";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import { Shield, FileText, Download, ArrowRight, Trash2, Clock } from "lucide-react";
import { useGeoSafeStore } from "@/lib/store";
import { generateReport } from "@/lib/api";
import toast from "react-hot-toast";
import Navbar from "@/components/Navbar";

export default function ReportsPage() {
  const { currentAnalysis } = useGeoSafeStore();
  const [savedReports, setSavedReports] = useState<any[]>([]);
  const [downloading, setDownloading] = useState<string | null>(null);

  useEffect(() => {
    // Load from localStorage
    try {
      const saved = JSON.parse(localStorage.getItem("geosafe_reports") || "[]");
      setSavedReports(saved);
    } catch { }
  }, []);

  useEffect(() => {
    if (currentAnalysis) {
      const reports = JSON.parse(localStorage.getItem("geosafe_reports") || "[]");
      const exists = reports.find((r: any) => r.id === currentAnalysis.id);
      if (!exists) {
        const updated = [{ ...currentAnalysis, saved_at: new Date().toISOString() }, ...reports].slice(0, 10);
        localStorage.setItem("geosafe_reports", JSON.stringify(updated));
        setSavedReports(updated);
      }
    }
  }, [currentAnalysis]);

  const handleDownload = async (id: string) => {
    setDownloading(id);
    try {
      const blob = await generateReport(id);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `geosafe_report_${id.slice(0, 8)}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
      toast.success("Report downloaded!");
    } catch (e: any) {
      toast.error("Report generation failed. Run analysis first.");
    } finally {
      setDownloading(null);
    }
  };

  const deleteReport = (id: string) => {
    const updated = savedReports.filter(r => r.id !== id);
    setSavedReports(updated);
    localStorage.setItem("geosafe_reports", JSON.stringify(updated));
  };

  const getDecisionColor = (score: number) =>
    score >= 75 ? "#10b981" : score >= 50 ? "#f59e0b" : "#f43f5e";

  return (
    <main className="min-h-screen bg-[#0a0f1e]">
      <Navbar />

      <div className="max-w-5xl mx-auto px-6 py-12">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="mb-10">
          <h1 className="text-4xl font-black text-white mb-2" style={{ fontFamily: 'Inter, sans-serif' }}>
            My <span className="gradient-text">Reports</span>
          </h1>
          <p className="text-slate-400">Property analyses saved in this browser session.</p>
        </motion.div>

        {savedReports.length === 0 ? (
          <div className="text-center py-32">
            <div className="w-16 h-16 rounded-2xl bg-white/5 flex items-center justify-center mx-auto mb-4">
              <FileText className="w-8 h-8 text-slate-600" />
            </div>
            <h3 className="text-slate-400 font-semibold mb-2">No reports yet</h3>
            <p className="text-slate-500 text-sm mb-6">Analyze a property to generate your first report.</p>
            <Link href="/search" className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-blue-600 text-white text-sm font-semibold hover:bg-blue-500 transition-all">
              <Shield className="w-4 h-4" /> Analyze a Property
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {savedReports.map((report, i) => {
              const color = getDecisionColor(report.safety_score);
              const decision = report.decision;
              return (
                <motion.div key={report.id}
                  initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }}
                  className="glass rounded-2xl p-6 border border-white/10 hover:border-white/20 transition-all">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-2xl font-black" style={{ color, fontFamily: 'Inter, sans-serif' }}>
                          {report.safety_score.toFixed(0)}/100
                        </span>
                        <span className="text-sm font-semibold px-2.5 py-1 rounded-full" style={{
                          background: `${color}20`, color, border: `1px solid ${color}40`
                        }}>
                          {decision === "Safe to Buy" ? "🟢" : decision === "Buy with Precautions" ? "🟡" : "🔴"} {decision}
                        </span>
                      </div>
                      <div className="text-sm text-slate-300 font-medium mb-1 truncate">{report.address}</div>
                      <div className="text-xs text-slate-500 flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {new Date(report.saved_at || report.analysis_timestamp).toLocaleString("en-IN")}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Link href={`/analysis/${report.id}`}
                        className="flex items-center gap-1.5 px-4 py-2 rounded-lg glass border border-white/10 text-xs text-white font-medium hover:bg-white/5 transition-all">
                        View <ArrowRight className="w-3 h-3" />
                      </Link>
                      <button onClick={() => handleDownload(report.id)}
                        disabled={downloading === report.id}
                        className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-blue-600/20 border border-blue-500/30 text-xs text-blue-400 font-medium hover:bg-blue-600/30 transition-all disabled:opacity-50">
                        <Download className="w-3 h-3" />
                        {downloading === report.id ? "..." : "PDF"}
                      </button>
                      <button onClick={() => deleteReport(report.id)}
                        className="p-2 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 transition-all">
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  {/* Mini hazard bars */}
                  <div className="mt-4 grid grid-cols-5 gap-2">
                    {[
                      { key: "flood_risk", label: "Flood" },
                      { key: "earthquake_risk", label: "Quake" },
                      { key: "cyclone_risk", label: "Cyclone" },
                      { key: "air_quality", label: "Air" },
                      { key: "climate_future", label: "Climate" },
                    ].map(({ key, label }) => {
                      const score = report[key]?.score ?? 0;
                      const c = score >= 70 ? "#f43f5e" : score >= 40 ? "#f59e0b" : "#10b981";
                      return (
                        <div key={key}>
                          <div className="text-xs text-slate-500 mb-1">{label}</div>
                          <div className="progress-bar">
                            <div className="progress-fill" style={{ width: `${score}%`, background: c }} />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </motion.div>
              );
            })}
          </div>
        )}
      </div>
    </main>
  );
}
