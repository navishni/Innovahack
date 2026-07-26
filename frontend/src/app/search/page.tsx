"use client";

import { useState, useCallback, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useRouter } from "next/navigation";
import dynamic from "next/dynamic";
import { MapPin, Search, Loader2, X, History, Info, Sparkles, CheckCircle2 } from "lucide-react";
import Link from "next/link";
import toast from "react-hot-toast";
import { analyzeProperty, geocodeAddress } from "@/lib/api";
import { useGeoSafeStore } from "@/lib/store";
import Navbar from "@/components/Navbar";

const MapPicker = dynamic(() => import("@/components/MapPicker"), { ssr: false });

const QUICK_SEARCHES = [
  "Bandra West, Mumbai, Maharashtra",
  "Indiranagar, Bengaluru, Karnataka",
  "Civil Lines, New Delhi",
  "Alwarpet, Chennai, Tamil Nadu",
  "Salt Lake City, Kolkata, West Bengal",
  "Viman Nagar, Pune, Maharashtra",
  "Jubilee Hills, Hyderabad, Telangana",
  "Aluva, Ernakulam, Kerala",
];

const LOADING_STEPS = [
  "Geocoding address & location coordinates...",
  "Fetching elevation profile (SRTM DEM)...",
  "Querying USGS seismic hazard catalog...",
  "Analyzing coastal & cyclone exposure (IMD)...",
  "Evaluating Air Quality Index (WAQI / CPCB)...",
  "Checking groundwater table status (CGWB)...",
  "Executing Multi-Criteria Decision Analysis (MCDA)...",
  "Synthesizing AI safety explanations...",
  "Querying nearby emergency infrastructure...",
  "Finalizing risk assessment report...",
];

export default function SearchPage() {
  const router = useRouter();
  const { setAnalysis } = useGeoSafeStore();
  const [address, setAddress] = useState("");
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [pickedLocation, setPickedLocation] = useState<{ lat: number; lon: number; address: string } | null>(null);
  const [step, setStep] = useState<"input" | "loading" | "done">("input");
  const [progress, setProgress] = useState(0);
  const [loadingStep, setLoadingStep] = useState(0);
  const debounceRef = useRef<NodeJS.Timeout | undefined>(undefined);

  const handleAddressChange = (val: string) => {
    setAddress(val);
    clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      if (val.trim().length > 2) {
        setSuggestions(QUICK_SEARCHES.filter(s => s.toLowerCase().includes(val.toLowerCase())));
      } else {
        setSuggestions([]);
      }
    }, 200);
  };

  const handleSelectAddress = async (addr: string) => {
    setAddress(addr);
    setSuggestions([]);
    try {
      const res = await geocodeAddress(addr);
      setPickedLocation({ lat: res.lat, lon: res.lon, address: res.address });
    } catch {
      // Fallback
    }
  };

  const runAnalysis = useCallback(async (addr: string, lat?: number, lon?: number) => {
    setStep("loading");
    setProgress(5);
    setLoadingStep(0);

    let currentStep = 0;
    const interval = setInterval(() => {
      currentStep++;
      setLoadingStep(Math.min(currentStep, LOADING_STEPS.length - 1));
      setProgress(Math.min((currentStep / LOADING_STEPS.length) * 92, 92));
    }, 600);

    try {
      const result = await analyzeProperty(addr, lat, lon);
      clearInterval(interval);
      setProgress(100);
      setAnalysis(result);
      setStep("done");
      setTimeout(() => router.push(`/analysis/${result.id}`), 400);
    } catch (err: any) {
      clearInterval(interval);
      setStep("input");
      toast.error(err.message || "Analysis failed. Please try a different location.");
    }
  }, [router, setAnalysis]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const target = address.trim() || pickedLocation?.address || "";
    if (!target && !pickedLocation) {
      toast.error("Please enter an address or click a location on the map.");
      return;
    }
    runAnalysis(target, pickedLocation?.lat, pickedLocation?.lon);
  };

  const handleMapPick = (lat: number, lon: number, addr: string) => {
    setPickedLocation({ lat, lon, address: addr });
    setAddress(addr);
  };

  return (
    <div className="min-h-screen bg-[#0a0f1e] text-slate-100 flex flex-col font-sans">
      <Navbar />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8 flex flex-col lg:flex-row gap-8 mt-16">
        {/* Left Sidebar Panel */}
        <div className="lg:w-[460px] flex-shrink-0 flex flex-col gap-6">
          <motion.div initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }}>
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold mb-3">
              <Sparkles className="w-3.5 h-3.5" /> India Geocoding & Hazard Engine
            </div>
            <h1 className="text-3xl font-black text-white tracking-tight mb-2">
              Analyze Property <span className="gradient-text">Safety</span>
            </h1>
            <p className="text-slate-400 text-sm leading-relaxed">
              Search any location in India or pick coordinates directly from the map.
            </p>
          </motion.div>

          {/* Search Form */}
          <motion.form 
            onSubmit={handleSubmit}
            initial={{ opacity: 0, y: 15 }} 
            animate={{ opacity: 1, y: 0 }} 
            transition={{ delay: 0.1 }}
            className="flex flex-col gap-4"
          >
            <div className="relative">
              <div className="absolute left-4 top-4 text-slate-400 pointer-events-none">
                <MapPin className="w-5 h-5" />
              </div>
              <input
                type="text"
                value={address}
                onChange={e => handleAddressChange(e.target.value)}
                placeholder="Enter city, landmark, or full address..."
                disabled={step === "loading"}
                className="w-full bg-white/5 border border-white/10 rounded-xl pl-12 pr-10 py-3.5 text-white placeholder-slate-500 text-sm focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all"
              />
              {address && (
                <button
                  type="button"
                  onClick={() => { setAddress(""); setSuggestions([]); setPickedLocation(null); }}
                  className="absolute right-3 top-3.5 p-1 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              )}
            </div>

            {/* Suggestions Dropdown */}
            <AnimatePresence>
              {suggestions.length > 0 && (
                <motion.div
                  initial={{ opacity: 0, y: -5 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -5 }}
                  className="bg-[#0f1730] border border-white/10 rounded-xl overflow-hidden shadow-2xl"
                >
                  {suggestions.map(s => (
                    <button
                      key={s}
                      type="button"
                      onClick={() => handleSelectAddress(s)}
                      className="w-full text-left px-4 py-3 text-sm text-slate-300 hover:bg-blue-600/20 hover:text-white flex items-center gap-2.5 transition-all border-b border-white/5 last:border-0"
                    >
                      <MapPin className="w-4 h-4 text-blue-400 flex-shrink-0" />
                      <span className="truncate">{s}</span>
                    </button>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>

            {pickedLocation && (
              <div className="flex items-center gap-2 text-xs text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 rounded-lg px-3 py-2">
                <CheckCircle2 className="w-4 h-4 flex-shrink-0" />
                <span className="truncate font-medium">Selected: {pickedLocation.address}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={step === "loading"}
              className="w-full py-4 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-bold shadow-lg shadow-blue-600/25 flex items-center justify-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {step === "loading" ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Running AI Hazards Analysis...
                </>
              ) : (
                <>
                  <Search className="w-5 h-5" />
                  Analyze Property Risk
                </>
              )}
            </button>
          </motion.form>

          {/* Loading Progress State */}
          <AnimatePresence>
            {step === "loading" && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="bg-white/5 border border-blue-500/30 rounded-xl p-5 backdrop-blur-md"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-semibold text-white uppercase tracking-wider">Multi-Hazard Aggregation</span>
                  <span className="text-xs font-bold text-blue-400">{Math.round(progress)}%</span>
                </div>
                <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden mb-3">
                  <motion.div
                    className="h-full bg-gradient-to-r from-blue-500 to-purple-500"
                    animate={{ width: `${progress}%` }}
                    transition={{ duration: 0.4 }}
                  />
                </div>
                <div className="text-xs text-slate-300 flex items-center gap-2 font-medium">
                  <Loader2 className="w-3.5 h-3.5 text-blue-400 animate-spin flex-shrink-0" />
                  <span>{LOADING_STEPS[loadingStep]}</span>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Quick Examples */}
          <div className="glass rounded-xl p-5 border border-white/10">
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
              <History className="w-4 h-4 text-blue-400" />
              <span>Quick Test Cities</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {QUICK_SEARCHES.map(s => (
                <button
                  key={s}
                  type="button"
                  onClick={() => handleSelectAddress(s)}
                  className="text-xs px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-slate-300 hover:text-white hover:bg-blue-600/20 hover:border-blue-500/40 transition-all text-left"
                >
                  {s.split(",")[0]}
                </button>
              ))}
            </div>
          </div>

          {/* Info Box */}
          <div className="glass rounded-xl p-4 border border-blue-500/20 bg-blue-500/5">
            <div className="flex gap-3">
              <Info className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
              <div className="text-xs text-slate-400 leading-relaxed">
                <span className="text-white font-semibold block mb-1">India Official Datasets</span>
                Evaluates IS 1893:2016 seismic zones, NDMA flood records, CGWB groundwater atlas, 
                IMD cyclone tracks, and IPCC AR6 climate projections.
              </div>
            </div>
          </div>
        </div>

        {/* Map Right Panel */}
        <div className="flex-1 min-h-[450px] lg:min-h-[600px] rounded-2xl overflow-hidden border border-white/10 glass shadow-2xl relative">
          <MapPicker onLocationPick={handleMapPick} pickedLocation={pickedLocation} />
        </div>
      </main>
    </div>
  );
}
