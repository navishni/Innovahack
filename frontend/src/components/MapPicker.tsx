"use client";
import { useEffect, useRef } from "react";
import dynamic from "next/dynamic";

import "leaflet/dist/leaflet.css";

interface MapPickerProps {
  onLocationPick: (lat: number, lon: number, address: string) => void;
  pickedLocation: { lat: number; lon: number; address: string } | null;
}

// This component is only rendered client-side
export default function MapPicker({ onLocationPick, pickedLocation }: MapPickerProps) {
  const mapRef = useRef<any>(null);
  const markerRef = useRef<any>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (typeof window === "undefined") return;

    let L: any;
    let map: any;

    const init = async () => {
      L = (await import("leaflet")).default;

      // Fix default marker icons
      delete (L.Icon.Default.prototype as any)._getIconUrl;
      L.Icon.Default.mergeOptions({
        iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
        iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
        shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
      });

      if (!containerRef.current || mapRef.current) return;

      map = L.map(containerRef.current, {
        center: [20.5937, 78.9629], // India center
        zoom: 5,
        zoomControl: true,
      });

      mapRef.current = map;

      setTimeout(() => {
        if (mapRef.current) mapRef.current.invalidateSize();
      }, 250);

      // Dark tile layer
      L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com">CARTO</a>',
        maxZoom: 19,
      }).addTo(map);

      // Click handler
      map.on("click", async (e: any) => {
        const { lat, lng } = e.latlng;

        // Update or create marker
        if (markerRef.current) {
          markerRef.current.setLatLng([lat, lng]);
        } else {
          const customIcon = L.divIcon({
            html: `<div style="width:32px;height:32px;background:linear-gradient(135deg,#3b82f6,#8b5cf6);border-radius:50% 50% 50% 0;transform:rotate(-45deg);border:2px solid white;box-shadow:0 4px 16px rgba(59,130,246,0.5)"></div>`,
            className: "",
            iconSize: [32, 32],
            iconAnchor: [16, 32],
          });
          markerRef.current = L.marker([lat, lng], { icon: customIcon }).addTo(map);
        }

        // Reverse geocode
        try {
          const resp = await fetch(
            `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json`,
            { headers: { "User-Agent": "GeoSafeAI/1.0" } }
          );
          const data = await resp.json();
          const addr = data.display_name || `${lat.toFixed(4)}, ${lng.toFixed(4)}`;
          onLocationPick(lat, lng, addr);
          markerRef.current.bindPopup(`<b style="color:white">📍 Selected Location</b><br><small style="color:#94a3b8">${addr.substring(0, 60)}...</small>`).openPopup();
        } catch {
          onLocationPick(lat, lng, `${lat.toFixed(4)}, ${lng.toFixed(4)}`);
        }
      });
    };

    init();

    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
        markerRef.current = null;
      }
    };
  }, []);

  // Update marker when pickedLocation changes from address input
  useEffect(() => {
    if (!mapRef.current || !pickedLocation) return;
    const map = mapRef.current;
    map.setView([pickedLocation.lat, pickedLocation.lon], 13, { animate: true });

    import("leaflet").then((LModule) => {
      const L = LModule.default;
      if (markerRef.current) {
        markerRef.current.setLatLng([pickedLocation.lat, pickedLocation.lon]);
      } else {
        const customIcon = L.divIcon({
          html: `<div style="width:32px;height:32px;background:linear-gradient(135deg,#3b82f6,#8b5cf6);border-radius:50% 50% 50% 0;transform:rotate(-45deg);border:2px solid white;box-shadow:0 4px 16px rgba(59,130,246,0.5)"></div>`,
          className: "",
          iconSize: [32, 32],
          iconAnchor: [16, 32],
        });
        markerRef.current = L.marker([pickedLocation.lat, pickedLocation.lon], { icon: customIcon }).addTo(map);
      }
      markerRef.current.bindPopup(`<b style="color:white">📍 Selected Location</b><br><small style="color:#94a3b8">${pickedLocation.address.substring(0, 60)}...</small>`).openPopup();
    });
  }, [pickedLocation]);

  return (
    <div className="relative w-full h-full min-h-[500px]">
      <div ref={containerRef} className="w-full h-full" />
      {/* Overlay instruction */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 glass px-4 py-2 rounded-full text-xs text-slate-400 pointer-events-none z-[1000] border border-white/10">
        🖱️ Click anywhere on the map to select a property location
      </div>
    </div>
  );
}
