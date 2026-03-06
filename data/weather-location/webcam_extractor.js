(() => {
  const images = Array.from(document.querySelectorAll('img'));
  const candidates = images
    .map(img => ({ src: img.src, alt: img.alt }))
    .filter(img => img.src.includes('imgproxy') || img.src.includes('webcam') || img.src.includes('original.jpg'));
  return candidates.slice(0, 3);
})();
