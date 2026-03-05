#!/bin/bash

# SaaS Landing Page Generator
# Usage: saas-landing-page "Product Name" "Description" [options]

set -e

PRODUCT="${1:-}"
DESCRIPTION="${2:-}"
TEMPLATE="${3:-modern}"
STACK="${4:-react}"
STYLE="${5:-tailwind}"
COLOR="${6:-blue}"

# Parse more options
while [[ $# -gt 6 ]]; do
    case $7 in
        --template|-t)
            TEMPLATE="$8"
            shift 2
            ;;
        --stack|-s)
            STACK="$8"
            shift 2
            ;;
        --style|-st)
            STYLE="$8"
            shift 2
            ;;
        --color|-c)
            COLOR="$8"
            shift 2
            ;;
        --output|-o)
            OUTPUT_DIR="$8"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

OUTPUT_DIR="${OUTPUT_DIR:-.}"

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [ -z "$PRODUCT" ]; then
    echo -e "${YELLOW}Usage: saas-landing-page \"Product Name\" \"Description\" [--template modern] [--stack react] [--color blue]${NC}"
    exit 1
fi

if [ -z "$DESCRIPTION" ]; then
    DESCRIPTION="An amazing product that solves your problems"
fi

# Create output directory
DIR_NAME=$(echo "$PRODUCT" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')
OUTPUT_PATH="$OUTPUT_DIR/$DIR_NAME-landing"

mkdir -p "$OUTPUT_PATH/components"
mkdir -p "$OUTPUT_PATH/assets"

echo -e "${BLUE}🚀 Generating SaaS Landing Page${NC}"
echo "Product: $PRODUCT"
echo "Template: $TEMPLATE"
echo "Stack: $STACK"
echo ""

# Generate based on stack
if [ "$STACK" = "react" ] || [ "$STACK" = "nextjs" ]; then
    cat > "$OUTPUT_PATH/App.jsx" << 'REACT_APP'
import React from 'react';
import Hero from './components/Hero';
import Features from './components/Features';
import Pricing from './components/Pricing';
import Testimonials from './components/Testimonials';
import CTA from './components/CTA';
import Footer from './components/Footer';

function App() {
  return (
    <div className="min-h-screen">
      <Hero />
      <Features />
      <Pricing />
      <Testimonials />
      <CTA />
      <Footer />
    </div>
  );
}

export default App;
REACT_APP

    cat > "$OUTPUT_PATH/components/Hero.jsx" << "HERO"
export default function Hero() {
  return (
    <section className="relative overflow-hidden py-20 lg:py-32">
      <div className="container mx-auto px-4">
        <div className="text-center max-w-4xl mx-auto">
          <h1 className="text-5xl lg:text-7xl font-bold mb-6 bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
            PRODUCT_NAME
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            DESCRIPTION
          </p>
          <div className="flex gap-4 justify-center">
            <button className="px-8 py-4 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition">
              Get Started Free
            </button>
            <button className="px-8 py-4 bg-gray-100 text-gray-700 rounded-lg font-semibold hover:bg-gray-200 transition">
              View Demo
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
HERO

    # Replace placeholders
    sed -i '' "s/PRODUCT_NAME/$PRODUCT/g" "$OUTPUT_PATH/components/Hero.jsx"
    sed -i '' "s/DESCRIPTION/$DESCRIPTION/g" "$OUTPUT_PATH/components/Hero.jsx"

    # Create index.html for Next.js
    cat > "$OUTPUT_PATH/index.html" << INDEX_HTML
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>$PRODUCT - $DESCRIPTION</title>
    <meta name="description" content="$DESCRIPTION">
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
    <div id="root"></div>
    <script src="https://unpkg.com/react@18/umd/react.development.js"></script>
    <script src="https://unpkg.com/react-dom@18/umd/react-dom.development.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <script type="text/babel">
        // React components would be compiled here
    </script>
</body>
</html>
INDEX_HTML

else
    # Plain HTML version
    cat > "$OUTPUT_PATH/index.html" << HTML
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>$PRODUCT - $DESCRIPTION</title>
    <meta name="description" content="$DESCRIPTION">
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .gradient-text {
            background: linear-gradient(to right, #2563eb, #9333ea);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
    </style>
</head>
<body>
    <!-- Hero Section -->
    <section class="py-20 lg:py-32">
        <div class="container mx-auto px-4 text-center">
            <h1 class="text-5xl lg:text-7xl font-bold mb-6 gradient-text">
                $PRODUCT
            </h1>
            <p class="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
                $DESCRIPTION
            </p>
            <div class="flex gap-4 justify-center">
                <button class="px-8 py-4 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition">
                    Get Started Free
                </button>
                <button class="px-8 py-4 bg-gray-100 text-gray-700 rounded-lg font-semibold hover:bg-gray-200 transition">
                    View Demo
                </button>
            </div>
        </div>
    </section>
    
    <!-- Features Section -->
    <section class="py-20 bg-gray-50">
        <div class="container mx-auto px-4">
            <h2 class="text-3xl font-bold text-center mb-12">Features</h2>
            <div class="grid md:grid-cols-3 gap-8">
                <div class="bg-white p-6 rounded-xl shadow-sm">
                    <div class="w-12 h-12 bg-blue-100 rounded-lg mb-4 flex items-center justify-center">
                        <span class="text-2xl">⚡</span>
                    </div>
                    <h3 class="text-xl font-semibold mb-2">Fast Performance</h3>
                    <p class="text-gray-600">Lightning fast and optimized for speed</p>
                </div>
                <div class="bg-white p-6 rounded-xl shadow-sm">
                    <div class="w-12 h-12 bg-purple-100 rounded-lg mb-4 flex items-center justify-center">
                        <span class="text-2xl">🔒</span>
                    </div>
                    <h3 class="text-xl font-semibold mb-2">Secure by Default</h3>
                    <p class="text-gray-600">Enterprise-grade security built-in</p>
                </div>
                <div class="bg-white p-6 rounded-xl shadow-sm">
                    <div class="w-12 h-12 bg-green-100 rounded-lg mb-4 flex items-center justify-center">
                        <span class="text-2xl">🎯</span>
                    </div>
                    <h3 class="text-xl font-semibold mb-2">Easy to Use</h3>
                    <p class="text-gray-600">Intuitive design for seamless experience</p>
                </div>
            </div>
        </div>
    </section>
    
    <!-- CTA Section -->
    <section class="py-20">
        <div class="container mx-auto px-4 text-center">
            <h2 class="text-3xl font-bold mb-6">Ready to get started?</h2>
            <p class="text-gray-600 mb-8">Start building amazing products today</p>
            <button class="px-8 py-4 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition">
                Start Free Trial
            </button>
        </div>
    </section>
    
    <!-- Footer -->
    <footer class="py-8 border-t">
        <div class="container mx-auto px-4 text-center text-gray-500">
            © 2026 $PRODUCT. All rights reserved.
        </div>
    </footer>
</body>
</html>
HTML
fi

# Create README
cat > "$OUTPUT_PATH/README.md" << README
# $PRODUCT Landing Page

Generated with SaaS Landing Page Generator

## Quick Start

### HTML Version
Simply open \`index.html\` in your browser.

### React/Next.js Version
\`\`\`bash
npm install
npm run dev
\`\`\`

## Customization

- Edit the content in components
- Change colors in tailwind.config.js
- Replace images in /assets

## Deployment

- Vercel: \`vercel deploy\`
- Netlify: Drag and drop build folder
- GitHub Pages: Enable in settings

## License

MIT
README

echo ""
echo -e "${GREEN}✅ Landing page generated successfully!${NC}"
echo "📁 Output: $OUTPUT_PATH"
echo ""
echo "Files created:"
ls -la "$OUTPUT_PATH"
echo ""
echo "🚀 Next steps:"
echo "1. cd $OUTPUT_PATH"
echo "2. Customize the content"
echo "3. Deploy to Vercel/Netlify"
