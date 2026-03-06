import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import { formatCurrency, centsToDollars } from '../lib/utils';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Badge from '../components/ui/Badge';
import { ArrowLeft, Trash2, Loader2, ExternalLink } from 'lucide-react';

export default function MyCampaignsPage() {
  const { user, isAuthenticated } = useAuth();
  const { showToast } = useToast();
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);

  const { data, isLoading } = useQuery({
    queryKey: ['my-campaigns', page],
    queryFn: () => api.getMyCampaigns({ page, per_page: 10 }),
    enabled: isAuthenticated && !!user,
  });

  const deleteMutation = useMutation({
    mutationFn: (campaignId: string) => api.deleteCampaign(campaignId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-campaigns'] });
      queryClient.invalidateQueries({ queryKey: ['campaigns'] });
      showToast('Campaign deleted', 'success');
      setDeleteConfirmId(null);
    },
    onError: (error: Error) => {
      showToast(error.message || 'Failed to delete campaign', 'error');
      setDeleteConfirmId(null);
    },
  });

  if (!isAuthenticated) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-12">
        <Card className="p-8 text-center">
          <p className="text-gray-600 mb-4">Please sign in to view your campaigns.</p>
          <Button as={Link} to="/auth/login" variant="primary">
            Sign In
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <Link
        to="/campaigns"
        className="inline-flex items-center text-gray-600 hover:text-gray-900 mb-6"
      >
        <ArrowLeft className="w-4 h-4 mr-2" />
        Back to Campaigns
      </Link>

      <h1 className="text-3xl font-bold text-gray-900 mb-8">My Campaigns</h1>

      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-white rounded-xl shadow-sm h-24 animate-pulse" />
          ))}
        </div>
      ) : data?.campaigns.length === 0 ? (
        <Card className="p-12 text-center">
          <p className="text-gray-600 mb-4">You haven&apos;t created any campaigns yet.</p>
          <Button as={Link} to="/campaigns/new" variant="primary">
            Start a Campaign
          </Button>
        </Card>
      ) : (
        <div className="space-y-4">
          {data?.campaigns.map((campaign) => {
            const goalInDollars = centsToDollars(campaign.goal_amount_usd);
            const raised = campaign.current_total_usd_cents
              ? centsToDollars(campaign.current_total_usd_cents)
              : 0;
            const progressPercent = goalInDollars > 0 ? Math.min((raised / goalInDollars) * 100, 100) : 0;

            return (
              <Card key={campaign.id} className="p-6">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap mb-2">
                      <Link
                        to={`/campaigns/${campaign.id}`}
                        className="text-lg font-semibold text-gray-900 hover:text-primary"
                      >
                        {campaign.title}
                      </Link>
                      <Badge
                        variant={
                          campaign.status === 'ACTIVE'
                            ? 'success'
                            : 'default'
                        }
                        size="sm"
                      >
                        {campaign.status}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-gray-600">
                      <span>
                        {formatCurrency(raised)} of {formatCurrency(goalInDollars)}
                      </span>
                      <span>{campaign.advocate_count} advocates</span>
                    </div>
                    {campaign.status === 'ACTIVE' && (
                      <div className="mt-2 h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-primary rounded-full transition-all"
                          style={{ width: `${progressPercent}%` }}
                        />
                      </div>
                    )}
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <Button
                      as={Link}
                      to={`/campaigns/${campaign.id}`}
                      variant="outline"
                      size="sm"
                    >
                      <ExternalLink className="w-4 h-4 mr-1" />
                      View
                    </Button>
                    {campaign.status === 'ACTIVE' && (
                      <Button
                        as={Link}
                        to={`/campaigns/${campaign.id}/edit`}
                        variant="outline"
                        size="sm"
                      >
                        Edit
                      </Button>
                    )}
                    {campaign.status === 'ACTIVE' && (
                      <>
                        {deleteConfirmId === campaign.id ? (
                          <div className="flex gap-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => setDeleteConfirmId(null)}
                            >
                              Cancel
                            </Button>
                            <Button
                              variant="primary"
                              size="sm"
                              onClick={() => deleteMutation.mutate(campaign.id)}
                              disabled={deleteMutation.isPending}
                              className="bg-red-600 hover:bg-red-700 border-red-600"
                            >
                              {deleteMutation.isPending ? (
                                <Loader2 className="w-4 h-4 animate-spin" />
                              ) : (
                                'Confirm'
                              )}
                            </Button>
                          </div>
                        ) : (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setDeleteConfirmId(campaign.id)}
                            className="text-red-600 border-red-200 hover:bg-red-50"
                          >
                            <Trash2 className="w-4 h-4 mr-1" />
                            Delete
                          </Button>
                        )}
                      </>
                    )}
                  </div>
                </div>
              </Card>
            );
          })}

          {data && data.total > data.per_page && (
            <div className="flex justify-center gap-2 pt-4">
              <Button
                variant="outline"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
              >
                Previous
              </Button>
              <Button
                variant="outline"
                onClick={() => setPage((p) => p + 1)}
                disabled={page * data.per_page >= data.total}
              >
                Next
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
