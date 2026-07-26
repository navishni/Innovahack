/** @type {import('next').NextConfig} */
const nextConfig = {
  allowedDevOrigins: ['172.16.52.55'],
  turbopack: {},
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "nominatim.openstreetmap.org" },
    ],
  },
};

export default nextConfig;
