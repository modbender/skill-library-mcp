import { Link } from 'react-router-dom';
import type { Campaign } from '../lib/api';
import { formatCurrency, truncate, centsToDollars, cryptoToUsd } from '../lib/utils';
import Card from './ui/Card';
import Badge, { getCategoryVariant } from './ui/Badge';
import ProgressBar from './ui/ProgressBar';
import Avatar from './ui/Avatar';
import ImageCarousel from './ui/ImageCarousel';
import { TrendingUp, Users } from 'lucide-react';

interface CampaignCardProps {
  campaign: Campaign;
}

export default function CampaignCard({ campaign }: CampaignCardProps) {
  const goalInDollars = centsToDollars(campaign.goal_amount_usd);
  const progress = campaign.current_total_usd_cents
    ? centsToDollars(campaign.current_total_usd_cents)
    : cryptoToUsd(
        campaign.current_btc_satoshi || 0,
        campaign.current_eth_wei || 0,
        campaign.current_sol_lamports || 0,
        campaign.current_usdc_base || 0
      );
  const progressPercent = Math.min((progress / goalInDollars) * 100, 100);
  const isTrending = campaign.advocate_count > 5; // Simple trending logic

  return (
    <Card hover elevation="sm" className="group">
      <Link to={`/campaigns/${campaign.id}`} className="block">
        {/* Image Section with Carousel or Fallback */}
        {(campaign.images?.length || campaign.cover_image_url) ? (
          <div className="relative aspect-video w-full overflow-hidden bg-gray-200">
            <ImageCarousel
              images={campaign.images || []}
              fallbackUrl={campaign.cover_image_url}
              altPrefix={campaign.title}
              className="h-full"
            />
            {/* Gradient Overlay */}
            <div className="absolute inset-0 gradient-overlay opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none z-20" />
            
            {/* Category Badge - Positioned on Image */}
            <div className="absolute top-3 left-3 z-20 pointer-events-none">
              <Badge variant={getCategoryVariant(campaign.category)} size="sm">
                {campaign.category.replace('_', ' ')}
              </Badge>
            </div>

            {/* Trending Badge */}
            {isTrending && (
              <div className="absolute top-3 right-3 z-20 pointer-events-none">
                <Badge variant="warning" size="sm" className="flex items-center gap-1">
                  <TrendingUp className="w-3 h-3" />
                  Trending
                </Badge>
              </div>
            )}
          </div>
        ) : (
          <div className="aspect-video w-full bg-gradient-to-br from-primary-100 to-primary-200 flex items-center justify-center">
            <div className="text-primary-600 text-4xl font-bold">
              {campaign.title.charAt(0).toUpperCase()}
            </div>
          </div>
        )}

        {/* Content Section */}
        <div className="p-6">
          {/* Title */}
          <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2 group-hover:text-primary transition-colors">
            {campaign.title}
          </h3>

          {/* Description */}
          <p className="text-sm text-gray-600 mb-4 line-clamp-2 min-h-[2.5rem]">
            {truncate(campaign.description, 120)}
          </p>

          {/* Progress Section */}
          <div className="mb-4">
            <div className="flex justify-between items-center mb-2">
              <span className="text-lg font-bold text-gray-900">
                {formatCurrency(progress)}
              </span>
              <span className="text-sm text-gray-600">
                of {formatCurrency(goalInDollars)}
              </span>
            </div>
            <ProgressBar
              value={progress}
              max={goalInDollars}
              gradient
              size="md"
            />
            <p className="text-xs text-gray-500 mt-1">
              {progressPercent.toFixed(1)}% funded
            </p>
          </div>

          {/* Advocates Section */}
          <div className="flex items-center justify-between pt-4 border-t border-gray-100">
            <div className="flex items-center gap-2">
              <Users className="w-4 h-4 text-gray-400" />
              <span className="text-sm text-gray-600">
                <span className="font-semibold text-gray-900">{campaign.advocate_count}</span>{' '}
                {campaign.advocate_count === 1 ? 'agent' : 'agents'} advocating
              </span>
            </div>
            
            {/* Mock Avatar Stack - Would show top advocates */}
            {campaign.advocate_count > 0 && (
              <div className="flex -space-x-2">
                {[...Array(Math.min(campaign.advocate_count, 3))].map((_, i) => (
                  <Avatar
                    key={i}
                    size="sm"
                    name={`Agent ${i + 1}`}
                    className="border-2 border-white"
                  />
                ))}
                {campaign.advocate_count > 3 && (
                  <div className="w-8 h-8 rounded-full bg-gray-200 border-2 border-white flex items-center justify-center text-xs font-semibold text-gray-600">
                    +{campaign.advocate_count - 3}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </Link>
    </Card>
  );
}
