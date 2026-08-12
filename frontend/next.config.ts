import type { NextConfig } from "next";

// `next/image` only loads from origins explicitly allow-listed here. The
// dev default (localhost:8000) is always included; when `NEXT_PUBLIC_API_URL`
// points somewhere else (staging/production), that origin is derived from
// the env var at build time and added too, so thumbnails don't silently
// break in deployed environments.
const remotePatterns: NonNullable<NextConfig["images"]>["remotePatterns"] = [
  { protocol: "http", hostname: "localhost", port: "8000", pathname: "/api/v1/uploads/**" },
];

const apiUrl = process.env.NEXT_PUBLIC_API_URL;
if (apiUrl) {
  try {
    const parsed = new URL(apiUrl);
    if (parsed.hostname !== "localhost") {
      remotePatterns.push({
        protocol: parsed.protocol.replace(":", "") as "http" | "https",
        hostname: parsed.hostname,
        port: parsed.port || undefined,
        pathname: "/api/v1/uploads/**",
      });
    }
  } catch {
    // Invalid NEXT_PUBLIC_API_URL — fall back to the dev-only pattern above;
    // build-time env validation is out of scope for this config file.
  }
}

const nextConfig: NextConfig = {
  reactStrictMode: true,
  output: "standalone",
  experimental: {
    optimizePackageImports: ["lucide-react", "framer-motion"],
  },
  images: {
    // Thumbnails are served by the backend (a different origin in dev),
    // not bundled/optimized at build time like static assets.
    remotePatterns,
  },
};

export default nextConfig;