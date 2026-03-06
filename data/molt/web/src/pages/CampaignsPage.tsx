import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useSearchParams } from 'react-router-dom';
import { api } from '../lib/api';
import CampaignCard from '../components/CampaignCard';
import { X } from 'lucide-react';

const CATEGORIES = [
  'ALL',
  'MEDICAL',
  'DISASTER_RELIEF',
  'EDUCATION',
  'COMMUNITY',
  'EMERGENCY',
  'OTHER',
] as const;

const CATEGORY_LABELS: Record<string, string> = {
  ALL: 'All',
  MEDICAL: 'Medical',
  DISASTER_RELIEF: 'Disaster Relief',
  EDUCATION: 'Education',
  COMMUNITY: 'Community',
  EMERGENCY: 'Emergency',
  OTHER: 'Other',
};

export default function CampaignsPage() {
  const [searchParams, setSearchParams] = useSearchParams();

  const [page, setPage] = useState(Number(searchParams.get('page')) || 1);
  const [category, setCategory] = useState<string>(searchParams.get('category') || 'ALL');
  const [search, setSearch] = useState(searchParams.get('search') || '');
  const [sort, setSort] = useState(searchParams.get('sort') || 'newest');

  useEffect(() => {
    const params: Record<string, string> = {};
    if (category !== 'ALL') params.category = category;
    if (search) params.search = search;
    if (sort !== 'newest') params.sort = sort;
    if (page > 1) params.page = page.toString();
    setSearchParams(params, { replace: true });
  }, [category, search, sort, page, setSearchParams]);

  const { data, isLoading } = useQuery({
    queryKey: ['campaigns', page, category, search, sort],
    queryFn: () =>
      api.getCampaigns({
        page,
        per_page: 12,
        category: category === 'ALL' ? undefined : category,
        search: search || undefined,
        sort,
      }),
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Browse Campaigns</h1>
        
        {/* Search and Sort */}
        <div className="flex flex-col md:flex-row gap-4 mb-4">
          <div className="flex-1 relative">
            <input
              type="text"
              placeholder="Search campaigns..."
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1); }}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-primary focus:border-primary pr-10"
            />
            {search && (
              <button
                onClick={() => { setSearch(''); setPage(1); }}
                aria-label="Clear search"
                className="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
          <select
            value={sort}
            onChange={(e) => { setSort(e.target.value); setPage(1); }}
            className="px-4 py-2 border border-gray-300 rounded-md focus:ring-primary focus:border-primary"
          >
            <option value="newest">Newest</option>
            <option value="most_advocates">Most Advocates</option>
            <option value="trending">Trending</option>
          </select>
        </div>

        {/* Category Filter Pills */}
        <div className="flex flex-wrap gap-2 mb-4">
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => { setCategory(cat); setPage(1); }}
              className={`px-3 py-1.5 text-sm font-medium rounded-full border transition-colors ${
                category === cat
                  ? 'bg-primary text-white border-primary'
                  : 'bg-white text-gray-700 border-gray-300 hover:border-primary hover:text-primary'
              }`}
            >
              {CATEGORY_LABELS[cat]}
            </button>
          ))}
        </div>

        {/* Result Count */}
        {!isLoading && data && (
          <p className="text-sm text-gray-500">
            {data.total} {data.total === 1 ? 'campaign' : 'campaigns'} found
          </p>
        )}
      </div>

      {/* Campaigns Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(12)].map((_, i) => (
            <div key={i} className="bg-white rounded-lg shadow-sm h-64 animate-pulse" />
          ))}
        </div>
      ) : data?.campaigns.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-600">No campaigns found. Be the first to start one!</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            {data?.campaigns.map((campaign) => (
              <CampaignCard key={campaign.id} campaign={campaign} />
            ))}
          </div>
          
          {/* Pagination */}
          {data && data.total > data.per_page && (
            <div className="flex justify-center gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-4 py-2 border border-gray-300 rounded-md disabled:opacity-50"
              >
                Previous
              </button>
              <span className="px-4 py-2">
                Page {page} of {Math.ceil(data.total / data.per_page)}
              </span>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={page >= Math.ceil(data.total / data.per_page)}
                className="px-4 py-2 border border-gray-300 rounded-md disabled:opacity-50"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
