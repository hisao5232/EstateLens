import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactCompiler: true,
  output: 'export', // これを追加
  images: {
    unoptimized: true, // 静的エクスポート時はこれが必要
  },
};

export default nextConfig;
