import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: process.env.STANDALONE_BUILD === "1" ? "standalone" : undefined,
  poweredByHeader: false,
  async rewrites() {
    const origin = process.env.API_ORIGIN ?? "http://127.0.0.1:8002";
    const parsed = new URL(origin);
    if (
      !["http:", "https:"].includes(parsed.protocol) ||
      parsed.username ||
      parsed.password ||
      parsed.search ||
      parsed.hash ||
      parsed.pathname !== "/"
    )
      throw new Error("Invalid API_ORIGIN");
    return [{ source: "/api/:path*", destination: `${origin}/api/:path*` }];
  },
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
