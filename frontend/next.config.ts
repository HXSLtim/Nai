import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  reactStrictMode: true,
  transpilePackages: ['@mui/material', '@mui/icons-material'],
  allowedDevOrigins: ['192.168.31.101'],
};

export default nextConfig;
