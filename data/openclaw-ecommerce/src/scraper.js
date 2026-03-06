export function extractPrice(html) {
  // 1. JSON-LD
  const jsonLdMatch = html.match(/<script type="application\/ld\+json"[^>]*>([\s\S]*?)<\/script>/gi);
  if (jsonLdMatch) {
    for (const script of jsonLdMatch) {
      const jsonStr = script.replace(/<script[^>]*>|<\/script>/g, '').trim();
      try {
        const data = JSON.parse(jsonStr);
        if (data['@type'] === 'Product' && data.offers && data.offers.price) {
          return {
            price: parseFloat(data.offers.price),
            currency: data.offers.priceCurrency || 'USD'
          };
        }
      } catch (e) {}
    }
  }

  // 2. Open Graph meta
  const ogMatch = html.match(/<meta property="og:price:amount" content="([^"]+)"[^>]*>/i);
  if (ogMatch) {
    return {
      price: parseFloat(ogMatch[1]),
      currency: html.match(/<meta property="og:price:currency" content="([^"]+)"[^>]*>/i)?.[1] || 'USD'
    };
  }

  // 3. Product meta
  const productMatch = html.match(/<meta name="product:price:amount" content="([^"]+)"[^>]*>/i);
  if (productMatch) {
    return {
      price: parseFloat(productMatch[1]),
      currency: html.match(/<meta name="product:price:currency" content="([^"]+)"[^>]*>/i)?.[1] || 'USD'
    };
  }

  // 4. Fallback regex for prices like $XX.XX
  const priceMatch = html.match(/\$(\d+(?:\.\d{2})?)/);
  if (priceMatch) {
    return {
      price: parseFloat(priceMatch[1]),
      currency: 'USD'
    };
  }

  return null;
}