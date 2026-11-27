import type { NextConfig } from "next";

// Where the FastAPI server runs: http://localhost:8000 locally, the Render URL in production.
const API_URL = process.env.API_URL ?? "http://localhost:8000";

const nextConfig: NextConfig = {
  cacheComponents: true,
  partialPrefetching: true,
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
  // The browser only ever talks to this site: /api/* is forwarded to the API.
  // So the login cookie is a first-party cookie (no CORS, not blocked as third-party).
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${API_URL}/:path*` }];
  },
};

export default nextConfig;
