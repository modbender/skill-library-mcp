#!/usr/bin/env bash
set -euo pipefail

PRODUCT="${1:?Usage: generate.sh \"Product Name\" \"Tagline\" \"Description\"}"
TAGLINE="${2:?Missing tagline}"
DESC="${3:?Missing description}"
YEAR=$(date +%Y)

cat <<HTMLEOF
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${PRODUCT}</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;color:#1a1a2e;line-height:1.6}
a{text-decoration:none}
.hero{background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);color:#fff;padding:100px 20px;text-align:center}
.hero h1{font-size:clamp(2rem,5vw,3.5rem);margin-bottom:16px}
.hero p{font-size:clamp(1rem,2.5vw,1.4rem);opacity:.9;max-width:600px;margin:0 auto 32px}
.btn{display:inline-block;padding:14px 36px;border-radius:8px;font-weight:600;font-size:1.1rem;transition:transform .2s,box-shadow .2s}
.btn:hover{transform:translateY(-2px);box-shadow:0 6px 20px rgba(0,0,0,.3)}
.btn-primary{background:#e94560;color:#fff}
.btn-secondary{background:#fff;color:#302b63}
section{padding:80px 20px;max-width:1100px;margin:0 auto}
.features{text-align:center}
.features h2{font-size:2rem;margin-bottom:40px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:32px}
.card{background:#f8f9fa;border-radius:12px;padding:32px;text-align:left}
.card h3{margin-bottom:8px;color:#302b63}
.cta-banner{background:linear-gradient(135deg,#e94560,#c23152);color:#fff;text-align:center;padding:60px 20px}
.cta-banner h2{font-size:2rem;margin-bottom:16px}
footer{background:#1a1a2e;color:rgba(255,255,255,.6);text-align:center;padding:24px 20px;font-size:.9rem}
</style>
</head>
<body>
<header class="hero">
  <h1>${PRODUCT}</h1>
  <p>${TAGLINE}</p>
  <a href="#cta" class="btn btn-primary">Get Started</a>
</header>

<section class="features">
  <h2>Why ${PRODUCT}?</h2>
  <div class="grid">
    <div class="card">
      <h3>⚡ Fast</h3>
      <p>${DESC}</p>
    </div>
    <div class="card">
      <h3>🎯 Simple</h3>
      <p>Designed to be intuitive from day one. No learning curve, just results.</p>
    </div>
    <div class="card">
      <h3>🔒 Reliable</h3>
      <p>Built on solid foundations so you can focus on what matters most.</p>
    </div>
  </div>
</section>

<div class="cta-banner" id="cta">
  <h2>Ready to get started?</h2>
  <p style="margin-bottom:24px;opacity:.9">Join thousands who already use ${PRODUCT}.</p>
  <a href="#" class="btn btn-secondary">Sign Up Free</a>
</div>

<footer>
  <p>&copy; ${YEAR} ${PRODUCT}. All rights reserved.</p>
</footer>
</body>
</html>
HTMLEOF
