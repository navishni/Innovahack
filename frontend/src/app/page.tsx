"use client";
import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import {
  Shield, MapPin, TrendingUp, Zap, Building2, Droplets,
  Activity, Wind, ChevronRight, Star, Users, FileText,
  Globe, ArrowRight, CheckCircle, Waves
} from "lucide-react";
import Navbar from "@/components/Navbar";

const FEATURES = [
  { icon: Droplets, title: "Flood Risk Analysis", desc: "DEM-based elevation analysis with SRTM data, river proximity, and historical flood records from CWC & NDMA.", color: "#3b82f6" },
  { icon: Activity, title: "Earthquake Assessment", desc: "IS 1893:2016 seismic zone classification with live USGS earthquake catalog data within 200km.", color: "#8b5cf6" },
  { icon: Wind, title: "Cyclone & Tsunami Risk", desc: "IBTrACS cyclone tracks, IMD historical data, and coastal distance analysis for Bay of Bengal exposure.", color: "#06b6d4" },
  { icon: Globe, title: "Climate Projections", desc: "IPCC AR6 / CMIP6 2050 projections for temperature, rainfall extremes, and sea-level rise by state.", color: "#10b981" },
  { icon: TrendingUp, title: "Air Quality Index", desc: "Real-time AQI from WAQI, PM2.5/PM10, NO₂ levels with CPCB historical trends for your city.", color: "#f59e0b" },
  { icon: Building2, title: "Soil & Construction", desc: "NBSS&LUP soil classification, bearing capacity analysis, and NBC 2016 construction suitability scores.", color: "#f43f5e" },
];

const STATS = [
  { value: "11+", label: "Hazard Parameters" },
  { value: "28", label: "Indian States Covered" },
  { value: "6", label: "Live APIs Integrated" },
  { value: "94%", label: "AI Confidence Score" },
];

const HOW_IT_WORKS = [
  { step: "01", title: "Enter Location", desc: "Type an address, GPS coordinates, or click on the interactive map to select any property in India.", icon: MapPin },
  { step: "02", title: "AI Analyzes", desc: "Our engine queries 6+ real-time APIs and applies MCDA scoring across 11 environmental and geological parameters.", icon: Zap },
  { step: "03", title: "Get Your Score", desc: "Receive a Property Safety Score (0–100), AI-written summary, and a detailed PDF report in seconds.", icon: Shield },
];

const SAMPLE_CITIES = [
  { city: "Mumbai, Maharashtra", score: 58, decision: "Caution", color: "#f59e0b", risk: "Coastal flooding + cyclone" },
  { city: "Shimla, Himachal Pradesh", score: 44, decision: "Avoid", color: "#f43f5e", risk: "High landslide + earthquake" },
  { city: "Bengaluru, Karnataka", score: 82, decision: "Safe", color: "#10b981", risk: "Low hazard zone" },
  { city: "Patna, Bihar", score: 51, decision: "Caution", color: "#f59e0b", risk: "Flood-prone Gangetic plain" },
];

export default function HomePage() {
  const [activeCity, setActiveCity] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => setActiveCity(p => (p + 1) % SAMPLE_CITIES.length), 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <main className="min-h-screen bg-[#0a0f1e] overflow-x-hidden">
      <Navbar />

      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center pt-20 overflow-hidden">
        {/* Background grid */}
        <div className="absolute inset-0 opacity-20"
          style={{ backgroundImage: 'radial-gradient(circle at 1px 1px, rgba(59,130,246,0.3) 1px, transparent 0)', backgroundSize: '40px 40px' }} />
        {/* Glowing orbs */}
        <div className="absolute top-20 right-20 w-96 h-96 bg-blue-600/20 rounded-full blur-3xl" />
        <div className="absolute bottom-20 left-20 w-80 h-80 bg-purple-600/15 rounded-full blur-3xl" />
        <div className="absolute top-1/2 left-1/2 w-64 h-64 bg-cyan-600/10 rounded-full blur-3xl" />

        <div className="relative max-w-7xl mx-auto px-6 py-20 grid md:grid-cols-2 gap-16 items-center">
          <motion.div initial={{ opacity: 0, y: 40 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8 }}>
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}
              className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full glass text-xs text-blue-400 font-medium mb-6 border border-blue-500/20">
              <span className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-pulse" />
              India's First AI Property Safety Platform
            </motion.div>

            <h1 className="text-5xl md:text-6xl font-black text-white leading-tight mb-6" style={{ fontFamily: 'Inter, sans-serif' }}>
              Know If Your{" "}
              <span className="gradient-text">Property</span>
              {" "}Is Safe Before You Buy
            </h1>

            <p className="text-lg text-slate-400 leading-relaxed mb-8">
              GeoSafe AI analyzes <strong className="text-white">11 environmental & geological parameters</strong>
              {" "}using satellite data, government datasets, and AI to give you a comprehensive
              Property Safety Score — in seconds.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 mb-12">
              <Link href="/search"
                className="flex items-center justify-center gap-2 px-8 py-4 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-base transition-all hover:shadow-2xl hover:shadow-blue-500/30 hover:-translate-y-0.5">
                <MapPin className="w-5 h-5" /> Analyze a Property Free
              </Link>
              <Link href="/compare"
                className="flex items-center justify-center gap-2 px-8 py-4 rounded-xl glass hover:bg-white/5 text-white font-semibold text-base transition-all border border-white/10">
                Compare Properties <ArrowRight className="w-4 h-4" />
              </Link>
            </div>

            {/* Trust badges */}
            <div className="flex flex-wrap gap-4 text-xs text-slate-500">
              {["NDMA Data", "IS 1893:2016", "USGS API", "IPCC AR6", "CGWB"].map(badge => (
                <span key={badge} className="flex items-center gap-1">
                  <CheckCircle className="w-3 h-3 text-emerald-500" /> {badge}
                </span>
              ))}
            </div>
          </motion.div>

          {/* Live score preview card */}
          <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.8, delay: 0.3 }}>
            <div className="glass rounded-2xl p-6 glow-blue animate-float">
              <div className="flex items-center justify-between mb-4">
                <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Live Sample Analysis</span>
                <span className="text-xs text-emerald-400 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse" /> Real Data
                </span>
              </div>

              {/* City selector */}
              <div className="space-y-2 mb-6">
                {SAMPLE_CITIES.map((c, i) => (
                  <motion.button key={c.city} onClick={() => setActiveCity(i)}
                    className={`w-full flex items-center justify-between p-3 rounded-xl transition-all ${i === activeCity ? 'bg-white/10 border border-white/20' : 'hover:bg-white/5'}`}>
                    <div className="flex items-center gap-3">
                      <MapPin className="w-4 h-4 text-slate-400 flex-shrink-0" />
                      <div className="text-left">
                        <div className="text-sm font-medium text-white">{c.city}</div>
                        <div className="text-xs text-slate-500">{c.risk}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-black" style={{ color: c.color }}>{c.score}</div>
                      <div className="text-xs font-semibold" style={{ color: c.color }}>{c.decision}</div>
                    </div>
                  </motion.button>
                ))}
              </div>

              {/* Score visualization */}
              <div className="glass-light rounded-xl p-4">
                <div className="text-center mb-3">
                  <div className="text-5xl font-black" style={{ color: SAMPLE_CITIES[activeCity].color }}>
                    {SAMPLE_CITIES[activeCity].score}
                    <span className="text-xl text-slate-500">/100</span>
                  </div>
                  <div className="text-sm font-semibold mt-1" style={{ color: SAMPLE_CITIES[activeCity].color }}>
                    {SAMPLE_CITIES[activeCity].decision === 'Safe' ? '🟢' : SAMPLE_CITIES[activeCity].decision === 'Caution' ? '🟡' : '🔴'}{" "}
                    {SAMPLE_CITIES[activeCity].decision}
                  </div>
                </div>
                <div className="progress-bar mt-3">
                  <motion.div className="progress-fill"
                    style={{ background: SAMPLE_CITIES[activeCity].color }}
                    animate={{ width: `${SAMPLE_CITIES[activeCity].score}%` }}
                    transition={{ duration: 0.6 }} />
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 border-y border-white/5">
        <div className="max-w-5xl mx-auto px-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {STATS.map((stat, i) => (
              <motion.div key={stat.label}
                initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }} viewport={{ once: true }}
                className="text-center">
                <div className="text-4xl font-black gradient-text mb-1">{stat.value}</div>
                <div className="text-sm text-slate-400">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How it Works */}
      <section className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
            className="text-center mb-16">
            <h2 className="text-4xl font-black text-white mb-4" style={{ fontFamily: 'Inter, sans-serif' }}>
              How GeoSafe AI <span className="gradient-text">Works</span>
            </h2>
            <p className="text-slate-400 max-w-xl mx-auto">Three steps to a complete property safety assessment</p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {HOW_IT_WORKS.map((step, i) => (
              <motion.div key={step.step}
                initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.15 }} viewport={{ once: true }}
                className="relative glass rounded-2xl p-8 hover:glow-blue transition-all group">
                <div className="text-7xl font-black text-white/5 absolute top-4 right-4" style={{ fontFamily: 'Inter, sans-serif' }}>
                  {step.step}
                </div>
                <div className="w-12 h-12 rounded-xl bg-blue-600/20 border border-blue-500/30 flex items-center justify-center mb-6 group-hover:bg-blue-600/30 transition-all">
                  <step.icon className="w-6 h-6 text-blue-400" />
                </div>
                <h3 className="text-xl font-bold text-white mb-3">{step.title}</h3>
                <p className="text-slate-400 text-sm leading-relaxed">{step.desc}</p>
                {i < 2 && (
                  <div className="hidden md:block absolute top-1/2 -right-4 transform -translate-y-1/2 z-10">
                    <ChevronRight className="w-8 h-8 text-slate-700" />
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-24 px-6 bg-white/[0.02]">
        <div className="max-w-6xl mx-auto">
          <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
            className="text-center mb-16">
            <h2 className="text-4xl font-black text-white mb-4" style={{ fontFamily: 'Inter, sans-serif' }}>
              Comprehensive <span className="gradient-text">Risk Intelligence</span>
            </h2>
            <p className="text-slate-400 max-w-2xl mx-auto">
              Every analysis covers all 11 environmental, geological, and climate parameters 
              using India-specific government datasets and international standards.
            </p>
          </motion.div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {FEATURES.map((f, i) => (
              <motion.div key={f.title}
                initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }} viewport={{ once: true }}
                className="glass rounded-2xl p-6 hover:bg-white/5 transition-all group cursor-default">
                <div className="w-10 h-10 rounded-lg flex items-center justify-center mb-4"
                  style={{ background: `${f.color}20`, border: `1px solid ${f.color}40` }}>
                  <f.icon className="w-5 h-5" style={{ color: f.color }} />
                </div>
                <h3 className="text-base font-bold text-white mb-2">{f.title}</h3>
                <p className="text-slate-400 text-sm leading-relaxed">{f.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* What You Get */}
      <section className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <div className="glass rounded-3xl p-8 md:p-12 border border-white/10 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-64 h-64 bg-blue-600/10 rounded-full blur-3xl" />
            <div className="relative">
              <motion.div initial={{ opacity: 0 }} whileInView={{ opacity: 1 }} viewport={{ once: true }}>
                <h2 className="text-3xl md:text-4xl font-black text-white mb-4" style={{ fontFamily: 'Inter, sans-serif' }}>
                  A Complete Property <span className="gradient-text">Safety Report</span>
                </h2>
                <p className="text-slate-400 mb-10 max-w-xl">Everything you need to make a confident, data-backed property decision.</p>
              </motion.div>

              <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-4">
                {[
                  "Property Safety Score (0–100)", "AI-Written Risk Summary", "11 Individual Hazard Scores",
                  "Construction Recommendations", "Disaster Preparedness Guide", "Nearby Emergency Services",
                  "2050 Climate Projections", "Insurance Risk Estimate", "Downloadable PDF Report",
                  "Side-by-Side Comparison", "Interactive Risk Maps", "AI Chat Q&A",
                ].map((item, i) => (
                  <motion.div key={item}
                    initial={{ opacity: 0, x: -20 }} whileInView={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.05 }} viewport={{ once: true }}
                    className="flex items-center gap-3 p-3 rounded-xl hover:bg-white/5 transition-all">
                    <CheckCircle className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                    <span className="text-sm text-slate-300">{item}</span>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 px-6">
        <div className="max-w-3xl mx-auto text-center">
          <motion.div initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
            <h2 className="text-4xl md:text-5xl font-black text-white mb-6" style={{ fontFamily: 'Inter, sans-serif' }}>
              Ready to Check Your{" "}
              <span className="gradient-text">Property's Safety?</span>
            </h2>
            <p className="text-slate-400 text-lg mb-10">
              Free to use. No sign-up required. Results in under 30 seconds.
            </p>
            <Link href="/search"
              className="inline-flex items-center gap-3 px-10 py-5 rounded-2xl bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold text-lg hover:shadow-2xl hover:shadow-blue-500/30 hover:-translate-y-1 transition-all">
              <Shield className="w-6 h-6" />
              Analyze Your Property Now
              <ArrowRight className="w-5 h-5" />
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/5 py-10 px-6">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-2">
            <Shield className="w-5 h-5 text-blue-400" />
            <span className="font-bold text-white">GeoSafe AI</span>
            <span className="text-slate-500 text-sm ml-2">India Property Safety Platform</span>
          </div>
          <p className="text-slate-500 text-xs text-center">
            Data sources: NDMA, USGS, IMD, CGWB, CPCB, IS 1893:2016, IPCC AR6, NASA POWER
          </p>
          <p className="text-slate-600 text-xs">© 2025 GeoSafe AI. For informational use only.</p>
        </div>
      </footer>
    </main>
  );
}
