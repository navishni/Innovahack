import type { Metadata } from "next";
import { Inter, Outfit } from "next/font/google";
import "./globals.css";
import { Toaster } from "react-hot-toast";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const outfit = Outfit({ subsets: ["latin"], variable: "--font-outfit" });

export const metadata: Metadata = {
  title: "GeoSafe AI – India Property Safety & Risk Assessment Platform",
  description:
    "AI-powered platform to evaluate environmental safety, disaster resilience, and long-term sustainability of any property in India. Get flood, earthquake, cyclone, and climate risk scores instantly.",
  keywords:
    "property safety India, flood risk assessment, earthquake risk, cyclone risk, NDMA, GIS property analysis, real estate risk India",
  openGraph: {
    title: "GeoSafe AI – Property Safety Assessment",
    description: "Know your property's safety score before you buy.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable} ${outfit.variable}`}>
      <body className="min-h-screen bg-navy antialiased">
        <Toaster
          position="top-right"
          toastOptions={{
            style: {
              background: "#0f1730",
              color: "#e2e8f0",
              border: "1px solid rgba(255,255,255,0.1)",
              borderRadius: "10px",
              fontFamily: "Outfit, sans-serif",
            },
          }}
        />
        {children}
      </body>
    </html>
  );
}
