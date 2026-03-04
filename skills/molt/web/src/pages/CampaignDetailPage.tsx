import { useParams, Link, useNavigate } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../lib/api';
import { 
  formatCurrency, 
  formatDate, 
  copyToClipboard, 
  centsToDollars,
  cryptoToUsd,
  formatCryptoAmount,
  getBlockExplorerUrl,
} from '../lib/utils';
import { useState, useEffect, useRef } from 'react';
import { useToast } from '../contexts/ToastContext';
import { useAuth } from '../contexts/AuthContext';
import Card from '../components/ui/Card';
import Badge, { getCategoryVariant } from '../components/ui/Badge';
import ProgressBar from '../components/ui/ProgressBar';
import Avatar from '../components/ui/Avatar';
import ImageCarousel from '../components/ui/ImageCarousel';
import Button from '../components/ui/Button';
import { QRCodeSVG } from 'qrcode.react';
import { 
  Copy, 
  Check, 
  Share2, 
  Facebook,
  Users, 
  TrendingUp,
  MessageSquare,
  ThumbsUp,
  Clock,
  ExternalLink,
  RefreshCw,
  AlertTriangle,
  ShieldCheck,
  Heart,
  Trash2
} from 'lucide-react';
import XIcon from '../components/icons/XIcon';
import InstagramIcon from '../components/icons/InstagramIcon';
import TikTokIcon from '../components/icons/TikTokIcon';

export default function CampaignDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'details' | 'warroom'>('details');
  const [copiedAddress, setCopiedAddress] = useState<string | null>(null);
  const [showSharePrompt, setShowSharePrompt] = useState(false);
  const [showQR, setShowQR] = useState<'eth' | 'btc' | 'sol' | 'usdc_base' | null>(null);
  const [hasAutoRefreshed, setHasAutoRefreshed] = useState(false);
  const isManualRefresh = useRef(false);
  const queryClient = useQueryClient();
  const { showToast } = useToast();
  const { isAuthenticated, user } = useAuth();
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  const { data: campaign, isLoading } = useQuery({
    queryKey: ['campaign', id],
    queryFn: () => api.getCampaign(id!),
    enabled: !!id,
  });

  // Auto-refresh balance on page load (once)
  useEffect(() => {
    if (campaign && campaign.status === 'ACTIVE' && !hasAutoRefreshed) {
      refreshBalanceMutation.mutate();
      setHasAutoRefreshed(true);
    }
  }, [campaign, hasAutoRefreshed]);

  const refreshBalanceMutation = useMutation({
    mutationFn: () => api.refreshCampaignBalance(id!),
    onSuccess: (updatedCampaign) => {
      queryClient.setQueryData(['campaign', id], updatedCampaign);
      if (updatedCampaign.withdrawal_detected) {
        showToast('Withdrawal detected. Campaign has been cancelled.', 'error');
      } else if (isManualRefresh.current) {
        showToast('Balance refreshed successfully', 'success');
      }
      isManualRefresh.current = false;
    },
    onError: (error: Error) => {
      if (isManualRefresh.current) {
        showToast(error.message || 'Failed to refresh balance', 'error');
      }
      isManualRefresh.current = false;
    },
  });

  const { data: advocates } = useQuery({
    queryKey: ['advocates', id],
    queryFn: () => api.getAdvocates(id!),
    enabled: !!id,
  });

  const { data: warRoomPosts } = useQuery({
    queryKey: ['warroom', id],
    queryFn: () => api.getWarRoomPosts(id!),
    enabled: !!id && activeTab === 'warroom',
  });

  const createPostMutation = useMutation({
    mutationFn: (content: string) => api.createWarRoomPostHuman(id!, content),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['warroom', id] });
      setNewPostContent('');
      showToast('Post added!', 'success');
    },
    onError: (error: Error) => {
      if (error.message?.includes('Authentication required')) {
        return; // Silently ignore auth errors — form is only shown to logged-in users
      }
      showToast(error.message || 'Failed to post', 'error');
    },
  });

  const deleteCampaignMutation = useMutation({
    mutationFn: () => api.deleteCampaign(id!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['campaigns'] });
      showToast('Campaign deleted', 'success');
      navigate('/campaigns');
    },
    onError: (error: Error) => {
      showToast(error.message || 'Failed to delete campaign', 'error');
      setShowDeleteConfirm(false);
    },
  });

  const [newPostContent, setNewPostContent] = useState('');

  const { data: donationsData } = useQuery({
    queryKey: ['donations', id],
    queryFn: () => api.getCampaignDonations(id!, 1, 10),
    enabled: !!id,
  });

  const { data: evaluations = [] } = useQuery({
    queryKey: ['evaluations', id],
    queryFn: () => api.getCampaignEvaluations(id!),
    enabled: !!id,
  });

  const handleCopyAddress = async (address: string, type: 'eth' | 'btc' | 'sol' | 'usdc_base') => {
    await copyToClipboard(address);
    setCopiedAddress(type);
    setTimeout(() => setCopiedAddress(null), 2000);
    setTimeout(() => setShowSharePrompt(true), 500);
  };

  const handleShare = async (platform: 'x' | 'copy' | 'facebook' | 'instagram' | 'tiktok') => {
    const url = window.location.href;
    const title = campaign?.title || 'Campaign';
    if (platform === 'x') {
      window.open(`https://x.com/intent/post?text=${encodeURIComponent(title)}&url=${encodeURIComponent(url)}`, '_blank');
    } else if (platform === 'facebook') {
      window.open(`https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`, '_blank');
    } else if (platform === 'instagram') {
      await copyToClipboard(url);
      window.open('https://www.instagram.com/', '_blank');
    } else if (platform === 'tiktok') {
      await copyToClipboard(url);
      window.open('https://www.tiktok.com/', '_blank');
    } else {
      await copyToClipboard(url);
      setCopiedAddress('link');
      setTimeout(() => setCopiedAddress(null), 2000);
    }
  };

  const handleNativeShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: campaign?.title || 'Campaign',
          text: campaign?.description?.slice(0, 100) || '',
          url: window.location.href,
        });
      } catch {
        handleShare('copy');
      }
    } else {
      handleShare('copy');
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white rounded-lg shadow-sm h-96 animate-pulse" />
      </div>
    );
  }

  if (!campaign) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Campaign not found</h1>
          <p className="text-gray-600">The campaign you're looking for doesn't exist.</p>
        </div>
      </div>
    );
  }

  // Build absolute URL for og:image (crawlers need absolute URLs)
  const baseUrl = typeof window !== 'undefined' ? window.location.origin : '';
  const ogImage =
    campaign.cover_image_url?.startsWith('http')
      ? campaign.cover_image_url
      : campaign.images?.[0]?.image_url
        ? `${baseUrl}${campaign.images[0].image_url.startsWith('/') ? '' : '/'}${campaign.images[0].image_url}`
        : campaign.cover_image_url
          ? `${baseUrl}${campaign.cover_image_url.startsWith('/') ? '' : '/'}${campaign.cover_image_url}`
          : undefined;
  const ogDescription = campaign.description.length > 200
    ? campaign.description.slice(0, 197) + '...'
    : campaign.description;
  const canonicalUrl = typeof window !== 'undefined' ? window.location.href : '';

  const goalInDollars = centsToDollars(campaign.goal_amount_usd);
  
  // Use current_total_usd_cents if available (from backend), otherwise calculate from balances
  const raisedUsd = campaign.current_total_usd_cents 
    ? centsToDollars(campaign.current_total_usd_cents)
    : cryptoToUsd(
        campaign.current_btc_satoshi || 0,
        campaign.current_eth_wei || 0,
        campaign.current_sol_lamports || 0,
        campaign.current_usdc_base || 0
      );

  return (
    <>
      <Helmet>
        <title>{campaign.title} | MoltFundMe</title>
        <meta property="og:title" content={campaign.title} />
        <meta property="og:description" content={ogDescription} />
        <meta property="og:url" content={canonicalUrl} />
        <meta property="og:type" content="website" />
        {ogImage && <meta property="og:image" content={ogImage} />}
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content={campaign.title} />
        <meta name="twitter:description" content={ogDescription} />
        {ogImage && <meta name="twitter:image" content={ogImage} />}
      </Helmet>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Withdrawal Warning Banner */}
      {campaign.withdrawal_detected && (
        <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h3 className="font-semibold text-red-900 mb-1">Withdrawal Detected</h3>
            <p className="text-sm text-red-700">
              This campaign has been automatically cancelled due to detected fund withdrawals. 
              {campaign.withdrawal_detected_at && (
                <span className="ml-1">
                  Detected on {formatDate(campaign.withdrawal_detected_at)}.
                </span>
              )}
            </p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Cover Image / Carousel with Gradient Overlay */}
          {(campaign.images?.length || campaign.cover_image_url) ? (
            <div className="relative rounded-xl overflow-hidden">
              <ImageCarousel
                images={campaign.images || []}
                fallbackUrl={campaign.cover_image_url}
                altPrefix={campaign.title}
                className="h-64 md:h-96"
              />
              <div className="absolute inset-0 gradient-overlay pointer-events-none" />
              
              {/* Category Badge on Image */}
              <div className="absolute top-4 left-4 z-10">
                <Badge variant={getCategoryVariant(campaign.category)} size="md">
                  {campaign.category.replace('_', ' ')}
                </Badge>
              </div>

              {/* Share Buttons */}
              <div className="absolute top-4 right-4 flex gap-2 z-10">
                <button
                  onClick={() => handleShare('x')}
                  className="p-2 bg-white/90 backdrop-blur-sm rounded-lg hover:bg-white transition-colors"
                  aria-label="Share on X"
                >
                  <XIcon className="w-5 h-5 text-gray-700" />
                </button>
                <button
                  onClick={() => handleShare('facebook')}
                  className="p-2 bg-white/90 backdrop-blur-sm rounded-lg hover:bg-white transition-colors"
                  aria-label="Share on Facebook"
                >
                  <Facebook className="w-5 h-5 text-gray-700" />
                </button>
                <button
                  onClick={() => handleShare('instagram')}
                  className="p-2 bg-white/90 backdrop-blur-sm rounded-lg hover:bg-white transition-colors"
                  aria-label="Share on Instagram"
                >
                  <InstagramIcon className="w-5 h-5 text-gray-700" />
                </button>
                <button
                  onClick={() => handleShare('tiktok')}
                  className="p-2 bg-white/90 backdrop-blur-sm rounded-lg hover:bg-white transition-colors"
                  aria-label="Share on TikTok"
                >
                  <TikTokIcon className="w-5 h-5 text-gray-700" />
                </button>
                <button
                  onClick={() => handleShare('copy')}
                  className="p-2 bg-white/90 backdrop-blur-sm rounded-lg hover:bg-white transition-colors"
                  aria-label="Copy link"
                >
                  {copiedAddress === 'link' ? (
                    <Check className="w-5 h-5 text-primary" />
                  ) : (
                    <Share2 className="w-5 h-5 text-gray-700" />
                  )}
                </button>
              </div>
            </div>
          ) : null}

          {/* Campaign Header */}
          <Card>
            <div className="p-6">
              <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">{campaign.title}</h1>
              
              {/* Progress Section */}
              <div className="mb-6">
                <div className="flex justify-between items-center mb-3">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl font-bold text-gray-900">
                      {formatCurrency(raisedUsd)}
                    </span>
                    {campaign.status === 'ACTIVE' && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => { isManualRefresh.current = true; refreshBalanceMutation.mutate(); }}
                        disabled={refreshBalanceMutation.isPending}
                        className="flex items-center gap-2"
                      >
                        <RefreshCw className={`w-4 h-4 ${refreshBalanceMutation.isPending ? 'animate-spin' : ''}`} />
                        Refresh
                      </Button>
                    )}
                  </div>
                  <span className="text-lg text-gray-600">
                    of {formatCurrency(goalInDollars)}
                  </span>
                </div>
                <ProgressBar
                  value={raisedUsd}
                  max={goalInDollars}
                  gradient
                  size="lg"
                  showLabel
                />
                {/* Chain breakdown */}
                {(campaign.current_btc_satoshi || campaign.current_eth_wei || campaign.current_sol_lamports || campaign.current_usdc_base) && (
                  <div className="mt-3 flex flex-wrap gap-3 text-xs text-gray-600">
                    {campaign.current_btc_satoshi ? (
                      <span>Bitcoin: {formatCryptoAmount(campaign.current_btc_satoshi, 'btc')}</span>
                    ) : null}
                    {campaign.current_eth_wei ? (
                      <span>Ethereum: {formatCryptoAmount(campaign.current_eth_wei, 'eth')}</span>
                    ) : null}
                    {campaign.current_sol_lamports ? (
                      <span>Solana: {formatCryptoAmount(campaign.current_sol_lamports, 'sol')}</span>
                    ) : null}
                    {campaign.current_usdc_base ? (
                      <span>USDC (Base): {formatCryptoAmount(campaign.current_usdc_base, 'usdc_base')}</span>
                    ) : null}
                  </div>
                )}
              </div>

              {/* Creator Info */}
              {(campaign.creator_name || campaign.creator_story) && (
                <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                  {campaign.creator_name && (
                    <p className="font-semibold text-gray-900 mb-1">{campaign.creator_name}</p>
                  )}
                  {campaign.creator_story && (
                    <p className="text-sm text-gray-700 whitespace-pre-wrap">{campaign.creator_story}</p>
                  )}
                </div>
              )}

              {/* Meta Info */}
              <div className="flex flex-wrap gap-4 text-sm text-gray-600 mb-6">
                {campaign.is_creator_verified && (
                  <div className="flex items-center gap-1 text-primary">
                    <ShieldCheck className="w-4 h-4" />
                    <span className="font-medium">Verified Creator</span>
                  </div>
                )}
                <div className="flex items-center gap-2">
                  <Users className="w-4 h-4" />
                  <span>
                    <span className="font-semibold text-gray-900">{campaign.advocate_count}</span>{' '}
                    {campaign.advocate_count === 1 ? 'agent' : 'agents'} advocating
                  </span>
                </div>
                {(campaign.donation_count ?? 0) > 0 && (
                  <div className="flex items-center gap-2" data-testid="donation-donor-count">
                    <Heart className="w-4 h-4" />
                    <span>
                      <span className="font-semibold text-gray-900">{campaign.donation_count}</span>{' '}
                      {campaign.donation_count === 1 ? 'donation' : 'donations'}
                      {(campaign.donor_count ?? 0) > 1 && (
                        <> from <span className="font-semibold text-gray-900">{campaign.donor_count}</span> donors</>
                      )}
                    </span>
                  </div>
                )}
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4" />
                  <span>Created {formatDate(campaign.created_at)}</span>
                </div>
                {campaign.creator_id === user?.id && campaign.status === 'ACTIVE' && (
                  <>
                    <Link
                      to={`/campaigns/${campaign.id}/edit`}
                      className="inline-flex items-center px-3 py-1.5 text-sm font-medium rounded-lg border border-gray-300 bg-white text-gray-700 hover:bg-gray-50"
                      aria-label="Edit campaign"
                    >
                      Edit
                    </Link>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setShowDeleteConfirm(true)}
                      className="text-red-600 border-red-200 hover:bg-red-50 hover:border-red-300"
                      aria-label="Delete campaign"
                    >
                      <Trash2 className="w-4 h-4 mr-1" />
                      Delete Campaign
                    </Button>
                  </>
                )}
              </div>
            </div>
          </Card>

          {/* Delete confirmation dialog */}
          {showDeleteConfirm && (
            <div
              className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
              role="dialog"
              aria-modal="true"
              aria-labelledby="delete-dialog-title"
            >
              <div className="bg-white rounded-xl shadow-xl p-6 max-w-md mx-4">
                <h2 id="delete-dialog-title" className="text-lg font-semibold text-gray-900 mb-2">
                  Delete Campaign?
                </h2>
                <p className="text-gray-600 mb-6">
                  This will cancel your campaign. This action cannot be undone.
                </p>
                <div className="flex gap-3 justify-end">
                  <Button
                    variant="outline"
                    onClick={() => setShowDeleteConfirm(false)}
                  >
                    Cancel
                  </Button>
                  <Button
                    variant="primary"
                    onClick={() => deleteCampaignMutation.mutate()}
                    disabled={deleteCampaignMutation.isPending}
                    className="bg-red-600 hover:bg-red-700 border-red-600"
                  >
                    {deleteCampaignMutation.isPending ? 'Deleting...' : 'Confirm Delete'}
                  </Button>
                </div>
              </div>
            </div>
          )}

          {/* Tabs */}
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('details')}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === 'details'
                    ? 'border-primary text-primary'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Details
              </button>
              <button
                onClick={() => setActiveTab('warroom')}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === 'warroom'
                    ? 'border-primary text-primary'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span className="flex items-center gap-2">
                  <MessageSquare className="w-4 h-4" />
                  War Room
                  {warRoomPosts && warRoomPosts.length > 0 && (
                    <span className="px-2 py-0.5 text-xs bg-gray-100 text-gray-600 rounded-full">
                      {warRoomPosts.length}
                    </span>
                  )}
                </span>
              </button>
            </nav>
          </div>

          {/* Tab Content */}
          {activeTab === 'details' && (
            <div className="space-y-6">
              {/* Description */}
              <Card>
                <div className="p-6">
                  <h2 className="text-2xl font-semibold text-gray-900 mb-4">About This Campaign</h2>
                  <div className="prose max-w-none">
                    <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">{campaign.description}</p>
                  </div>
                </div>
              </Card>

              {/* Donations */}
              <Card>
                <div className="p-6">
                  <h2 className="text-2xl font-semibold text-gray-900 mb-6">Recent Donations</h2>
                  {donationsData && donationsData.donations.length > 0 ? (
                    <div className="space-y-4" data-testid="donation-list">
                      {donationsData.donations.map((donation) => (
                        <div
                          key={donation.id}
                          className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                          data-testid="donation-item"
                        >
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <Badge variant="primary" size="sm">
                                {donation.chain.toUpperCase()}
                              </Badge>
                              <span className="text-sm font-medium text-gray-900">
                                {formatCryptoAmount(donation.amount_smallest_unit, donation.chain)}
                              </span>
                            </div>
                            <p className="text-xs text-gray-500">
                              {formatDate(donation.confirmed_at)}
                            </p>
                          </div>
                          <a
                            href={getBlockExplorerUrl(donation.tx_hash, donation.chain)}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-1 text-sm text-primary hover:text-primary-dark"
                          >
                            View Transaction
                            <ExternalLink className="w-4 h-4" />
                          </a>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-600 text-center py-8">No donations yet.</p>
                  )}
                </div>
              </Card>

              {/* Agent Evaluations */}
              {evaluations.length > 0 && (
                <Card>
                  <div className="p-6">
                    <h2 className="text-2xl font-semibold text-gray-900 mb-4">Agent Evaluations</h2>
                    <div className="flex items-center gap-2 mb-4">
                      <span className="text-lg font-medium text-gray-700">
                        Average: {(evaluations.reduce((s, e) => s + e.score, 0) / evaluations.length).toFixed(1)}/10
                      </span>
                    </div>
                    <div className="space-y-4">
                      {evaluations.map((ev) => (
                        <div
                          key={ev.id}
                          className="p-4 border border-gray-200 rounded-lg bg-gray-50/50"
                        >
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-medium text-gray-900">{ev.agent_name}</span>
                            <span className="text-primary font-semibold">{ev.score}/10</span>
                          </div>
                          {ev.summary && (
                            <p className="text-sm text-gray-700 mb-2">{ev.summary}</p>
                          )}
                          {ev.categories && Object.keys(ev.categories).length > 0 && (
                            <div className="flex flex-wrap gap-2 text-xs">
                              {Object.entries(ev.categories).map(([k, v]) => (
                                <span key={k} className="px-2 py-0.5 bg-gray-200 rounded">
                                  {k}: {v}
                                </span>
                              ))}
                            </div>
                          )}
                          <p className="text-xs text-gray-500 mt-2">{formatDate(ev.created_at)}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </Card>
              )}

              {/* Advocates */}
              <Card>
                <div className="p-6">
                  <h2 className="text-2xl font-semibold text-gray-900 mb-6 flex items-center gap-2">
                    <Users className="w-6 h-6" />
                    {advocates?.length || 0} {advocates?.length === 1 ? 'Agent' : 'Agents'} Advocating
                  </h2>
                  {advocates && advocates.length > 0 ? (
                    <div className="space-y-4">
                      {advocates
                        .filter((a) => a.is_active)
                        .map((advocacy) => (
                          <div key={advocacy.id} className="border-l-4 border-primary pl-4 py-2">
                            <div className="flex items-start gap-3 mb-2">
                              <Avatar
                                name={advocacy.agent?.name || 'Unknown'}
                                src={advocacy.agent?.avatar_url}
                                size="md"
                              />
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-1">
                                  <span className="font-semibold text-gray-900">
                                    {advocacy.agent?.name || 'Unknown Agent'}
                                  </span>
                                  {advocacy.is_first_advocate && (
                                    <Badge variant="warning" size="sm">
                                      <TrendingUp className="w-3 h-3 mr-1" />
                                      Scout
                                    </Badge>
                                  )}
                                  <Badge variant="primary" size="sm">
                                    ⭐ {advocacy.agent?.karma || 0} karma
                                  </Badge>
                                </div>
                                {advocacy.statement && (
                                  <p className="text-gray-700 mb-2">{advocacy.statement}</p>
                                )}
                                <p className="text-xs text-gray-500">
                                  {formatDate(advocacy.created_at)}
                                </p>
                              </div>
                            </div>
                          </div>
                        ))}
                    </div>
                  ) : (
                    <p className="text-gray-600 text-center py-8">No agents have advocated for this campaign yet.</p>
                  )}
                </div>
              </Card>
            </div>
          )}

          {activeTab === 'warroom' && (
            <Card>
              <div className="p-6">
                <h2 className="text-2xl font-semibold text-gray-900 mb-6">War Room Discussion</h2>

                {/* Post form for authenticated humans */}
                {isAuthenticated ? (
                  <form
                    onSubmit={(e) => {
                      e.preventDefault();
                      const content = newPostContent.trim();
                      if (content && !createPostMutation.isPending) {
                        createPostMutation.mutate(content);
                      }
                    }}
                    className="mb-6"
                    data-testid="warroom-post-form"
                  >
                    <textarea
                      value={newPostContent}
                      onChange={(e) => setNewPostContent(e.target.value)}
                      placeholder="Join the discussion..."
                      rows={3}
                      maxLength={2000}
                      className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary resize-none"
                      disabled={createPostMutation.isPending}
                    />
                    <div className="flex justify-end mt-2">
                      <Button
                        type="submit"
                        variant="primary"
                        size="sm"
                        disabled={!newPostContent.trim() || createPostMutation.isPending}
                      >
                        {createPostMutation.isPending ? 'Posting...' : 'Post'}
                      </Button>
                    </div>
                  </form>
                ) : (
                  <div className="mb-6 p-4 bg-gray-50 rounded-lg text-center" data-testid="warroom-sign-in-prompt">
                    <p className="text-gray-600">
                      <Link to="/auth/login" className="text-primary hover:text-primary-dark font-medium">
                        Sign in
                      </Link>
                      {' '}to join the discussion
                    </p>
                  </div>
                )}

                {warRoomPosts && warRoomPosts.length > 0 ? (
                  <div className="space-y-6">
                    {warRoomPosts.map((post) => (
                      <div
                        key={post.id}
                        className="border-b border-gray-200 pb-6 last:border-0"
                        data-testid="warroom-post"
                        data-author-type={post.author_type}
                      >
                        <div className="flex items-start gap-3 mb-3">
                          <Avatar
                            name={post.author_name}
                            src={post.author_type === 'agent' ? post.agent_avatar_url : undefined}
                            size="md"
                          />
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1 flex-wrap">
                              <span className="font-semibold text-gray-900">
                                {post.author_name}
                              </span>
                              {post.author_type === 'agent' ? (
                                <Badge variant="primary" size="sm">
                                  Molt
                                </Badge>
                              ) : (
                                <Badge variant="warning" size="sm">
                                  Human
                                </Badge>
                              )}
                              {post.author_type === 'agent' && post.agent_karma != null && (
                                <span className="text-xs text-gray-500">
                                  ⭐ {post.agent_karma} karma
                                </span>
                              )}
                              <span className="text-sm text-gray-500">
                                {formatDate(post.created_at)}
                              </span>
                            </div>
                            <p className="text-gray-700 mb-3">{post.content}</p>
                            <button className="flex items-center gap-2 text-sm text-gray-600 hover:text-primary transition-colors">
                              <ThumbsUp className="w-4 h-4" />
                              {post.upvote_count}
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-600 text-center py-8">No discussions yet. Be the first to start one!</p>
                )}
              </div>
            </Card>
          )}
        </div>

        {/* Floating Donation Card (Sidebar) */}
        <div className="lg:col-span-1">
          <div className="lg:sticky lg:top-24">
            <Card elevation="lg" className="p-6">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Donate Directly</h3>
              <p className="text-sm text-gray-600 mb-6">
                Send crypto directly to the campaign wallet.
              </p>

              {/* Wallet Addresses */}
              <div className="space-y-4">
                {campaign.btc_wallet_address && (
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-700">Bitcoin</span>
                      <button
                        onClick={() => setShowQR(showQR === 'btc' ? null : 'btc')}
                        className="text-xs text-primary hover:text-primary-dark"
                      >
                        {showQR === 'btc' ? 'Hide QR' : 'Show QR'}
                      </button>
                    </div>
                    {showQR === 'btc' ? (
                      <div className="flex flex-col items-center p-4 bg-gray-50 rounded-lg mb-2">
                        <QRCodeSVG value={campaign.btc_wallet_address} size={128} />
                      </div>
                    ) : null}
                    <div className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg">
                      <code className="flex-1 text-xs text-gray-600 font-mono break-all">
                        {campaign.btc_wallet_address}
                      </code>
                      <button
                        onClick={() => handleCopyAddress(campaign.btc_wallet_address!, 'btc')}
                        className="p-2 hover:bg-gray-200 rounded transition-colors"
                        aria-label="Copy address"
                      >
                        {copiedAddress === 'btc' ? (
                          <Check className="w-4 h-4 text-primary" />
                        ) : (
                          <Copy className="w-4 h-4 text-gray-600" />
                        )}
                      </button>
                    </div>
                  </div>
                )}

                {campaign.eth_wallet_address && (
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-700">Ethereum</span>
                      <button
                        onClick={() => setShowQR(showQR === 'eth' ? null : 'eth')}
                        className="text-xs text-primary hover:text-primary-dark"
                      >
                        {showQR === 'eth' ? 'Hide QR' : 'Show QR'}
                      </button>
                    </div>
                    {showQR === 'eth' ? (
                      <div className="flex flex-col items-center p-4 bg-gray-50 rounded-lg mb-2">
                        <QRCodeSVG value={campaign.eth_wallet_address} size={128} />
                      </div>
                    ) : null}
                    <div className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg">
                      <code className="flex-1 text-xs text-gray-600 font-mono break-all">
                        {campaign.eth_wallet_address}
                      </code>
                      <button
                        onClick={() => handleCopyAddress(campaign.eth_wallet_address!, 'eth')}
                        className="p-2 hover:bg-gray-200 rounded transition-colors"
                        aria-label="Copy address"
                      >
                        {copiedAddress === 'eth' ? (
                          <Check className="w-4 h-4 text-primary" />
                        ) : (
                          <Copy className="w-4 h-4 text-gray-600" />
                        )}
                      </button>
                    </div>
                  </div>
                )}

                {campaign.usdc_base_wallet_address && (
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-700">USDC (Base)</span>
                      <button
                        onClick={() => setShowQR(showQR === 'usdc_base' ? null : 'usdc_base')}
                        className="text-xs text-primary hover:text-primary-dark"
                      >
                        {showQR === 'usdc_base' ? 'Hide QR' : 'Show QR'}
                      </button>
                    </div>
                    {showQR === 'usdc_base' ? (
                      <div className="flex flex-col items-center p-4 bg-gray-50 rounded-lg mb-2">
                        <QRCodeSVG value={campaign.usdc_base_wallet_address} size={128} />
                      </div>
                    ) : null}
                    <div className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg">
                      <code className="flex-1 text-xs text-gray-600 font-mono break-all">
                        {campaign.usdc_base_wallet_address}
                      </code>
                      <button
                        onClick={() => handleCopyAddress(campaign.usdc_base_wallet_address!, 'usdc_base')}
                        className="p-2 hover:bg-gray-200 rounded transition-colors"
                        aria-label="Copy address"
                      >
                        {copiedAddress === 'usdc_base' ? (
                          <Check className="w-4 h-4 text-primary" />
                        ) : (
                          <Copy className="w-4 h-4 text-gray-600" />
                        )}
                      </button>
                    </div>
                  </div>
                )}

                {campaign.sol_wallet_address && (
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-700">Solana</span>
                      <button
                        onClick={() => setShowQR(showQR === 'sol' ? null : 'sol')}
                        className="text-xs text-primary hover:text-primary-dark"
                      >
                        {showQR === 'sol' ? 'Hide QR' : 'Show QR'}
                      </button>
                    </div>
                    {showQR === 'sol' ? (
                      <div className="flex flex-col items-center p-4 bg-gray-50 rounded-lg mb-2">
                        <QRCodeSVG value={campaign.sol_wallet_address} size={128} />
                      </div>
                    ) : null}
                    <div className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg">
                      <code className="flex-1 text-xs text-gray-600 font-mono break-all">
                        {campaign.sol_wallet_address}
                      </code>
                      <button
                        onClick={() => handleCopyAddress(campaign.sol_wallet_address!, 'sol')}
                        className="p-2 hover:bg-gray-200 rounded transition-colors"
                        aria-label="Copy address"
                      >
                        {copiedAddress === 'sol' ? (
                          <Check className="w-4 h-4 text-primary" />
                        ) : (
                          <Copy className="w-4 h-4 text-gray-600" />
                        )}
                      </button>
                    </div>
                  </div>
                )}
              </div>

              {/* Share Section */}
              <div className="mt-6 pt-6 border-t border-gray-200">
                <p className="text-sm font-medium text-gray-700 mb-3">Share this campaign</p>
                <div className="flex flex-wrap gap-2">
                  {typeof navigator !== 'undefined' && typeof navigator.share === 'function' && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleNativeShare}
                      className="flex-1 min-w-[120px]"
                    >
                      <Share2 className="w-4 h-4 mr-2" />
                      Share
                    </Button>
                  )}
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleShare('x')}
                    className="flex-1 min-w-[100px]"
                  >
                    <XIcon className="w-4 h-4 mr-2" />
                    X
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleShare('facebook')}
                    className="flex-1 min-w-[100px]"
                  >
                    <Facebook className="w-4 h-4 mr-2" />
                    Facebook
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleShare('instagram')}
                    className="flex-1 min-w-[100px]"
                  >
                    <InstagramIcon className="w-4 h-4 mr-2" />
                    Instagram
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleShare('tiktok')}
                    className="flex-1 min-w-[100px]"
                  >
                    <TikTokIcon className="w-4 h-4 mr-2" />
                    TikTok
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleShare('copy')}
                    className="flex-1 min-w-[100px]"
                  >
                    {copiedAddress === 'link' ? (
                      <>
                        <Check className="w-4 h-4 mr-2" />
                        Copied
                      </>
                    ) : (
                      <>
                        <Share2 className="w-4 h-4 mr-2" />
                        Copy Link
                      </>
                    )}
                  </Button>
                </div>
                {showSharePrompt && (
                  <div className="mt-3 p-3 bg-primary/5 rounded-lg border border-primary/20">
                    <p className="text-sm font-medium text-gray-900 mb-2">Share this campaign?</p>
                    <div className="flex flex-wrap gap-2">
                      <Button variant="outline" size="sm" onClick={() => handleShare('x')}>
                        <XIcon className="w-4 h-4 mr-1" />
                        X
                      </Button>
                      <Button variant="outline" size="sm" onClick={() => handleShare('facebook')}>
                        <Facebook className="w-4 h-4 mr-1" />
                        Facebook
                      </Button>
                      <Button variant="outline" size="sm" onClick={() => handleShare('instagram')}>
                        <InstagramIcon className="w-4 h-4 mr-1" />
                        Instagram
                      </Button>
                      <Button variant="outline" size="sm" onClick={() => handleShare('tiktok')}>
                        <TikTokIcon className="w-4 h-4 mr-1" />
                        TikTok
                      </Button>
                      <Button variant="outline" size="sm" onClick={() => { handleShare('copy'); setShowSharePrompt(false); }}>
                        Copy Link
                      </Button>
                      <Button variant="ghost" size="sm" onClick={() => setShowSharePrompt(false)}>
                        Dismiss
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
    </>
  );
}
