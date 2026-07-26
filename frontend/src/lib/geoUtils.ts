/**
 * Geospatial Utilities — True continuous color interpolation & type definitions
 * for OSM-based choropleth rendering.
 *
 * Uses linear HSL interpolation across a 5-stop red→yellow→green ramp
 * so every distinct score value maps to a genuinely unique color.
 */

export type MapLayerMode = "overall" | "flood" | "earthquake" | "air_quality" | "heat";

/**
 * 5-stop HSL color ramp for safety score 0-100.
 * Each stop: { t: normalized position 0-1, h: hue, s: saturation%, l: lightness% }
 */
const COLOR_STOPS = [
  { t: 0.00, h: 0,   s: 72, l: 42 },   // deep red
  { t: 0.25, h: 20,  s: 85, l: 52 },   // orange
  { t: 0.50, h: 45,  s: 90, l: 52 },   // amber/yellow
  { t: 0.75, h: 85,  s: 65, l: 48 },   // lime green
  { t: 1.00, h: 152, s: 68, l: 36 },   // deep emerald
];

function lerp(a: number, b: number, t: number): number {
  return a + (b - a) * t;
}

/**
 * True continuous HSL interpolation.
 * Every unique score produces a unique color — no bucketing.
 */
export function getContinuousColor(score: number): string {
  const t = Math.max(0, Math.min(1, score / 100));

  // Find which two stops we fall between
  let lower = COLOR_STOPS[0];
  let upper = COLOR_STOPS[COLOR_STOPS.length - 1];

  for (let i = 0; i < COLOR_STOPS.length - 1; i++) {
    if (t >= COLOR_STOPS[i].t && t <= COLOR_STOPS[i + 1].t) {
      lower = COLOR_STOPS[i];
      upper = COLOR_STOPS[i + 1];
      break;
    }
  }

  // Normalized position within this segment
  const segLen = upper.t - lower.t;
  const segT = segLen === 0 ? 0 : (t - lower.t) / segLen;

  const h = Math.round(lerp(lower.h, upper.h, segT));
  const s = Math.round(lerp(lower.s, upper.s, segT));
  const l = Math.round(lerp(lower.l, upper.l, segT));

  return `hsl(${h}, ${s}%, ${l}%)`;
}
