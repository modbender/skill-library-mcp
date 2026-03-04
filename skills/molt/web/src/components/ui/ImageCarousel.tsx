import { useState, useEffect, useCallback } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { cn } from '../../lib/utils';

export interface CarouselImage {
  id: string;
  image_url: string;
}

interface ImageCarouselProps {
  images: CarouselImage[];
  fallbackUrl?: string;
  altPrefix?: string;
  className?: string;
}

const AUTO_ADVANCE_MS = 5000;

export default function ImageCarousel({
  images,
  fallbackUrl,
  altPrefix = 'Slide',
  className,
}: ImageCarouselProps) {
  const [currentIndex, setCurrentIndex] = useState(0);

  const showSlides = images.length > 0 || (fallbackUrl && images.length === 0);
  const slides = images.length > 0 ? images : fallbackUrl ? [{ id: 'fallback', image_url: fallbackUrl }] : [];
  const canNavigate = slides.length > 1;

  const goToSlide = useCallback(
    (index: number) => {
      if (slides.length <= 1) return;
      setCurrentIndex((index + slides.length) % slides.length);
    },
    [slides.length]
  );

  const goNext = useCallback(() => goToSlide(currentIndex + 1), [currentIndex, goToSlide]);
  const goPrev = useCallback(() => goToSlide(currentIndex - 1), [currentIndex, goToSlide]);

  useEffect(() => {
    if (!canNavigate) return;
    const timer = setInterval(goNext, AUTO_ADVANCE_MS);
    return () => clearInterval(timer);
  }, [canNavigate, currentIndex, goNext]);

  if (!showSlides) return null;

  const apiUrl = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? 'http://localhost:8000' : '');
  const getImageUrl = (url: string) => {
    if (url.startsWith('http')) return url;
    return `${apiUrl}${url.startsWith('/') ? '' : '/'}${url}`;
  };

  return (
    <div className={cn('relative overflow-hidden rounded-xl', className)}>
      <div className="relative size-full min-h-32">
        {slides.map((img, index) => (
          <div
            key={img.id}
            className={cn(
              'absolute inset-0 transition-opacity duration-500',
              index === currentIndex ? 'opacity-100 z-10' : 'opacity-0 z-0'
            )}
            data-active={index === currentIndex}
          >
            <img
              src={getImageUrl(img.image_url)}
              alt={`${altPrefix} ${index + 1}`}
              className="w-full h-full object-cover"
            />
          </div>
        ))}
      </div>

      {canNavigate && (
        <>
          <button
            type="button"
            onClick={goPrev}
            className="absolute left-4 top-1/2 -translate-y-1/2 z-20 p-2 rounded-full bg-black/40 hover:bg-black/60 text-white transition-colors"
            aria-label="Previous slide"
          >
            <ChevronLeft className="w-6 h-6" />
          </button>
          <button
            type="button"
            onClick={goNext}
            className="absolute right-4 top-1/2 -translate-y-1/2 z-20 p-2 rounded-full bg-black/40 hover:bg-black/60 text-white transition-colors"
            aria-label="Next slide"
          >
            <ChevronRight className="w-6 h-6" />
          </button>

          <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-20 flex gap-2">
            {slides.map((_, index) => (
              <button
                key={index}
                type="button"
                onClick={() => goToSlide(index)}
                className={cn(
                  'w-2 h-2 rounded-full transition-colors',
                  index === currentIndex ? 'bg-white' : 'bg-white/50 hover:bg-white/75'
                )}
                aria-label={`Go to slide ${index + 1}`}
                aria-current={index === currentIndex ? 'true' : undefined}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
