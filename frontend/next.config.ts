import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  output: "standalone",
  experimental: {
    optimizePackageImports: ["lucide-react", "framer-motion"],
  },
  images: {
    // Thumbnails are served by the backend (a different origin in dev),
    // not bundled/optimized at build time like static assets.
    remotePatterns: [
      { protocol: "http", hostname: "localhost", port: "8000", pathname: "/api/v1/uploads/**" },
    ],
  },
};

export default nextConfig;