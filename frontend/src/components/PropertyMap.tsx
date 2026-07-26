"use client";

import { useEffect, useState, useCallback, useRef, useMemo } from "react";
import { MapContainer, TileLayer, Marker, Popup, GeoJSON } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { getContinuousColor, MapLayerMode } from "@/lib/geoUtils";
import MapSidePanel from "./MapSidePanel";
import { Shield, Droplets, Activity, CloudRain, Thermometer } from "lucide-react";

const iconUrl = "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png";
const iconRetinaUrl = "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png";
const shadowUrl = "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png";

const customIcon = new L.Icon({
  iconUrl, iconRetinaUrl, shadowUrl,
  iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34], shadowSize: [41, 41]
});

interface PropertyMapProps {
  lat: number;
  lon: number;
  address: string;
  safetyScore?: number;
}

interface FeatureProps {
  id: string;
  name: string;
  featureType: string;
  overallScore: number;
  floodScore: number;
  eqScore: number;
  aqiScore: number;
  heatScore: number;
  riskLevel: string;
  lowConfidence: boolean;
  evidence: string[];
  distanceFromTarget?: number;
}

export default function PropertyMap({ lat, lon, address, safetyScore = 65 }: PropertyMapProps) {
  const [activeLayer, setActiveLayer] = useState<MapLayerMode>("overall");
  const [selectedFeature, setSelectedFeature] = useState<FeatureProps | null>(null);
  const [geoData, setGeoData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    delete (L.Icon.Default.prototype as any)._getIconUrl;
  }, []);

  // Memoize address to keep dependency array stable
  const stableAddress = useMemo(() => address || "", [address]);

  // Fetch real OSM building/road GeoJSON from backend
  useEffect(() => {
    if (!lat || !lon) return;
    setLoading(true);
    setError(null);

    fetch(`http://localhost:8000/api/map-features?lat=${lat}&lon=${lon}&radius=300&safety_score=${safetyScore}&address=${encodeURIComponent(stableAddress)}`)
      .then(res => {
        if (!res.ok) throw new Error("Failed to fetch map features");
        return res.json();
      })
      .then(data => {
        // Debug: log score distribution to verify real variance
        if (data?.features?.length) {
          const scores = data.features.map((f: any) => f.properties.overallScore);
          const min = Math.min(...scores);
          const max = Math.max(...scores);
          const avg = scores.reduce((a: number, b: number) => a + b, 0) / scores.length;
          console.log(`[PropertyMap] ${scores.length} features loaded. Score range: ${min}-${max}, avg: ${avg.toFixed(1)}`);
        }
        setGeoData(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Map features fetch error:", err);
        setError("Could not load building footprints");
        setLoading(false);
      });
  }, [lat, lon, safetyScore, stableAddress]);

  if (!lat || !lon) return null;

  const getScoreForLayer = (props: any, layer: MapLayerMode): number => {
    switch (layer) {
      case "flood": return props.floodScore;
      case "earthquake": return props.eqScore;
      case "air_quality": return props.aqiScore;
      case "heat": return props.heatScore;
      default: return props.overallScore;
    }
  };

  const styleFeature = (feature: any) => {
    const props = feature.properties;
    const score = getScoreForLayer(props, activeLayer);
    const isSelected = selectedFeature?.id === props.id;
    const fillColor = getContinuousColor(score);
    const isRoad = props.featureType === "road";

    return {
      fillColor,
      fillOpacity: isSelected ? 0.72 : props.lowConfidence ? 0.22 : isRoad ? 0.55 : 0.45,
      color: isSelected ? "#38bdf8" : fillColor,
      weight: isSelected ? 3.5 : isRoad ? 2 : 1.2,
      dashArray: props.lowConfidence ? "5 5" : undefined,
    };
  };

  const onEachFeature = (feature: any, layer: L.Layer) => {
    const props = feature.properties;
    const score = getScoreForLayer(props, activeLayer);

    // Name shown on hover ONLY — no permanent labels
    const nameDisplay = props.name
      ? `<span class="font-extrabold block text-white text-[11px]">${props.name}</span>`
      : "";

    // Tooltip appears on hover — clean map at rest
    layer.bindTooltip(
      `<div class="font-sans px-2.5 py-2 text-xs text-slate-100 bg-[#070c18] border border-white/10 rounded-xl shadow-2xl min-w-[120px]">
        ${nameDisplay}
        <div class="flex items-center justify-between gap-3 mt-1">
          <span class="text-[10px] text-slate-400">Safety Score</span>
          <span class="text-[11px] font-bold" style="color: ${getContinuousColor(score)}">${score}/100</span>
        </div>
        <span class="text-[9px] text-slate-500 block mt-0.5">${props.riskLevel}</span>
      </div>`,
      {
        permanent: false,
        direction: "auto",
        opacity: 0.97,
        sticky: true,
      }
    );

    layer.on({
      click: () => {
        setSelectedFeature({
          ...props,
          activeScore: score,
        });
      },
      mouseover: (e) => {
        const l = e.target;
        if (selectedFeature?.id !== props.id) {
          l.setStyle({
            color: "#ffffff",
            weight: 3,
            fillOpacity: 0.65,
          });
          l.bringToFront();
        }
      },
      mouseout: (e) => {
        const l = e.target;
        if (selectedFeature?.id !== props.id) {
          const isRoad = props.featureType === "road";
          const fillColor = getContinuousColor(score);
          l.setStyle({
            color: fillColor,
            weight: isRoad ? 2 : 1.2,
            fillOpacity: props.lowConfidence ? 0.22 : isRoad ? 0.55 : 0.45,
          });
        }
      },
    });
  };

  const layerButtons: { mode: MapLayerMode; label: string; icon: any }[] = [
    { mode: "overall", label: "Overall", icon: Shield },
    { mode: "flood", label: "Flood", icon: Droplets },
    { mode: "earthquake", label: "Quake", icon: Activity },
    { mode: "air_quality", label: "Air", icon: CloudRain },
    { mode: "heat", label: "Heat", icon: Thermometer },
  ];

  return (
    <div className="w-full h-full min-h-[480px] rounded-2xl overflow-hidden border border-white/10 shadow-2xl relative z-0">

      {/* Layer Toggle */}
      <div className="absolute top-4 left-14 z-[500] flex items-center gap-1 bg-[#070c18]/92 backdrop-blur-xl p-1.5 rounded-xl border border-white/15 shadow-xl">
        {layerButtons.map((btn) => (
          <button
            key={btn.mode}
            onClick={() => {
              setActiveLayer(btn.mode);
              setSelectedFeature(null);
            }}
            className={`flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-[11px] font-bold transition-all cursor-pointer ${
              activeLayer === btn.mode
                ? "bg-blue-600 text-white shadow-md shadow-blue-500/30"
                : "text-slate-400 hover:text-white hover:bg-white/5"
            }`}
          >
            <btn.icon className="w-3 h-3" />
            {btn.label}
          </button>
        ))}
      </div>

      {/* Loading Overlay */}
      {loading && (
        <div className="absolute inset-0 z-[450] bg-[#070c18]/70 backdrop-blur-sm flex items-center justify-center">
          <div className="flex items-center gap-3 text-sm text-blue-400 font-semibold">
            <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
            Fetching real building footprints from OpenStreetMap...
          </div>
        </div>
      )}

      <MapContainer
        center={[lat, lon]}
        zoom={17}
        scrollWheelZoom={true}
        className="w-full h-full min-h-[480px]"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />

        {/* Real OSM Building/Road GeoJSON Layer — labels on hover only */}
        {geoData && geoData.features && geoData.features.length > 0 && (
          <GeoJSON
            key={`${activeLayer}_${selectedFeature?.id || "none"}`}
            data={geoData}
            style={styleFeature}
            onEachFeature={onEachFeature}
          />
        )}

        {/* NO permanent centroid text labels — names appear on hover tooltip only */}

        {/* Target property marker */}
        <Marker position={[lat, lon]} icon={customIcon}>
          <Popup>
            <div className="text-slate-800 font-semibold p-1">
              🎯 Target Property
              <div className="text-xs text-slate-500 font-normal mt-1 leading-tight">{address}</div>
            </div>
          </Popup>
        </Marker>
      </MapContainer>

      {/* Side Panel */}
      {selectedFeature && (
        <MapSidePanel
          properties={{
            id: selectedFeature.id,
            centroid: [lat, lon],
            overallScore: selectedFeature.overallScore,
            floodScore: selectedFeature.floodScore,
            eqScore: selectedFeature.eqScore,
            aqiScore: selectedFeature.aqiScore,
            heatScore: selectedFeature.heatScore,
            activeScore: getScoreForLayer(selectedFeature, activeLayer),
            riskLevel: selectedFeature.riskLevel,
            lowConfidence: selectedFeature.lowConfidence,
            evidence: selectedFeature.evidence,
            namedFeature: selectedFeature.name,
          }}
          onClose={() => setSelectedFeature(null)}
        />
      )}

      {/* Gradient Legend */}
      <div className="absolute bottom-4 left-4 z-[500] bg-[#070c18]/92 backdrop-blur-xl p-3 rounded-xl border border-white/15 shadow-xl text-xs w-56 space-y-1.5">
        <div className="flex items-center justify-between text-[10px] font-bold uppercase tracking-wider text-slate-400">
          <span>{activeLayer === "overall" ? "Safety" : activeLayer.replace("_", " ")} Score</span>
          <span className="text-blue-400">Hover for details</span>
        </div>
        <div className="h-2.5 rounded-full overflow-hidden w-full bg-gradient-to-r from-red-700 via-orange-500 via-amber-400 via-yellow-300 to-emerald-500 border border-white/10" />
        <div className="flex justify-between text-[10px] font-mono text-slate-500">
          <span>0</span>
          <span>25</span>
          <span>50</span>
          <span>75</span>
          <span>100</span>
        </div>
      </div>

      {/* Feature count badge */}
      {geoData && !loading && (
        <div className="absolute top-4 right-4 z-[500] bg-[#070c18]/92 backdrop-blur-xl px-3 py-1.5 rounded-xl border border-white/15 shadow-xl text-[11px] font-bold text-emerald-400">
          {geoData.features.length} real OSM features loaded
        </div>
      )}

      {/* Error fallback */}
      {error && !loading && (
        <div className="absolute top-4 right-4 z-[500] bg-rose-900/80 backdrop-blur-xl px-3 py-1.5 rounded-xl border border-rose-500/30 text-[11px] font-bold text-rose-300">
          {error}
        </div>
      )}
    </div>
  );
}
