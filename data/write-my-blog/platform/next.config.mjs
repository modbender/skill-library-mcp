/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,
    images: {
        remotePatterns: [
            { protocol: "https", hostname: "**" },
        ],
    },
    headers: async () => [
        {
            source: "/(.*)",
            headers: [
                { key: "X-Frame-Options", value: "DENY" },
                { key: "X-Content-Type-Options", value: "nosniff" },
                { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
                { key: "X-XSS-Protection", value: "1; mode=block" },
                {
                    key: "Permissions-Policy",
                    value: "camera=(), microphone=(), geolocation=()",
                },
            ],
        },
        {
            source: "/api/:path*",
            headers: [
                { key: "Cache-Control", value: "no-store, no-cache, must-revalidate" },
            ],
        },
    ],
};

export default nextConfig;
