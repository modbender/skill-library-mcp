import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, act } from '@testing-library/react';
import ImageCarousel from '../../src/components/ui/ImageCarousel';

describe('ImageCarousel', () => {
  const images = [
    { id: '1', image_url: '/img1.jpg' },
    { id: '2', image_url: '/img2.jpg' },
    { id: '3', image_url: '/img3.jpg' },
  ];

  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('renders all images', () => {
    render(<ImageCarousel images={images} />);
    expect(screen.getByRole('img', { name: /slide 1/i })).toBeInTheDocument();
    expect(screen.getByRole('img', { name: /slide 2/i })).toBeInTheDocument();
    expect(screen.getByRole('img', { name: /slide 3/i })).toBeInTheDocument();
  });

  it('auto-advances every 5 seconds', () => {
    render(<ImageCarousel images={images} />);
    const dots = screen.getAllByRole('button', { name: /go to slide \d/i });
    expect(dots[0]).toHaveAttribute('aria-current', 'true');

    act(() => {
      vi.advanceTimersByTime(5000);
    });
    expect(dots[1]).toHaveAttribute('aria-current', 'true');
  });

  it('dot indicators reflect current slide', () => {
    render(<ImageCarousel images={images} />);
    const dots = screen.getAllByRole('button', { name: /go to slide \d/i });
    expect(dots).toHaveLength(3);
  });

  it('manual navigation works', () => {
    render(<ImageCarousel images={images} />);
    const dots = screen.getAllByRole('button', { name: /go to slide \d/i });
    const nextButton = screen.getByRole('button', { name: /next/i });
    fireEvent.click(nextButton);
    expect(dots[1]).toHaveAttribute('aria-current', 'true');

    const prevButton = screen.getByRole('button', { name: /previous/i });
    fireEvent.click(prevButton);
    expect(dots[0]).toHaveAttribute('aria-current', 'true');
  });

  it('single image shows no navigation controls', () => {
    render(<ImageCarousel images={[{ id: '1', image_url: '/img1.jpg' }]} />);
    expect(screen.queryByRole('button', { name: /next/i })).not.toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /previous/i })).not.toBeInTheDocument();
  });
});
