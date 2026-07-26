import { create } from "zustand";
import { AnalysisResult } from "./api";

interface GeoSafeState {
  currentAnalysis: AnalysisResult | null;
  comparedProperties: AnalysisResult[];
  isLoading: boolean;
  error: string | null;

  setAnalysis: (analysis: AnalysisResult) => void;
  addComparison: (analysis: AnalysisResult) => void;
  removeComparison: (id: string) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearAll: () => void;
}

export const useGeoSafeStore = create<GeoSafeState>((set) => ({
  currentAnalysis: null,
  comparedProperties: [],
  isLoading: false,
  error: null,

  setAnalysis: (analysis) => set({ currentAnalysis: analysis, error: null }),

  addComparison: (analysis) =>
    set((state) => ({
      comparedProperties: state.comparedProperties.find((p) => p.id === analysis.id)
        ? state.comparedProperties
        : [...state.comparedProperties, analysis].slice(0, 3),
    })),

  removeComparison: (id) =>
    set((state) => ({
      comparedProperties: state.comparedProperties.filter((p) => p.id !== id),
    })),

  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  clearAll: () => set({ currentAnalysis: null, comparedProperties: [], error: null }),
}));
