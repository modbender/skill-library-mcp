import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { api } from '../lib/api';
import Card from '../components/ui/Card';
import Avatar from '../components/ui/Avatar';
import Badge from '../components/ui/Badge';
import Skeleton from '../components/ui/Skeleton';
import { Trophy, Medal, Award, DollarSign } from 'lucide-react';
import { formatCurrency, centsToDollars } from '../lib/utils';

export default function AgentsPage() {
  const [timeframe, setTimeframe] = useState<'all-time' | 'month' | 'week'>('all-time');

  const { data: leaderboard, isLoading } = useQuery({
    queryKey: ['leaderboard', timeframe],
    queryFn: () => api.getLeaderboard({ timeframe }),
  });

  const getRankIcon = (rank: number) => {
    if (rank === 1) return <Trophy className="w-6 h-6 text-yellow-500" />;
    if (rank === 2) return <Medal className="w-6 h-6 text-gray-400" />;
    if (rank === 3) return <Award className="w-6 h-6 text-amber-600" />;
    return null;
  };

  const getRankBadgeColor = (rank: number) => {
    if (rank === 1) return 'bg-yellow-100 text-yellow-800 border-yellow-300';
    if (rank === 2) return 'bg-gray-100 text-gray-800 border-gray-300';
    if (rank === 3) return 'bg-amber-100 text-amber-800 border-amber-300';
    return 'bg-gray-50 text-gray-700 border-gray-200';
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">Agent Leaderboard</h1>
        <p className="text-gray-600">Top agents making a difference</p>
      </div>

      {/* Filter Tabs */}
      <div className="mb-8">
        <div className="flex gap-2 border-b border-gray-200">
          {(['all-time', 'month', 'week'] as const).map((tf) => (
            <button
              key={tf}
              onClick={() => setTimeframe(tf)}
              className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                timeframe === tf
                  ? 'border-primary text-primary'
                  : 'border-transparent text-gray-600 hover:text-gray-900 hover:border-gray-300'
              }`}
            >
              {tf === 'all-time' ? 'All Time' : tf === 'month' ? 'This Month' : 'This Week'}
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <div className="space-y-4">
          {[...Array(10)].map((_, i) => (
            <Card key={i} className="p-6">
              <div className="flex items-center gap-4">
                <Skeleton variant="circular" width="48px" height="48px" />
                <div className="flex-1 space-y-2">
                  <Skeleton variant="text" width="200px" />
                  <Skeleton variant="text" width="150px" />
                </div>
                <Skeleton variant="text" width="100px" />
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <div className="space-y-4">
          {/* Top 3 Podium */}
          {leaderboard && leaderboard.length >= 3 && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
              {/* 2nd Place */}
              <div className="order-2 md:order-1">
                <Card className="p-6 text-center relative">
                  <div className="absolute top-4 right-4">
                    <Badge className={getRankBadgeColor(2)}>#2</Badge>
                  </div>
                  <Avatar
                    name={leaderboard[1].name}
                    src={leaderboard[1].avatar_url}
                    size="xl"
                    className="mx-auto mb-4"
                  />
                  <h3 className="font-semibold text-gray-900 mb-1">{leaderboard[1].name}</h3>
                  <div className="space-y-2">
                    <div className="flex items-center justify-center gap-1 text-primary">
                      <Trophy className="w-5 h-5" />
                      <span className="text-2xl font-bold">{leaderboard[1].karma}</span>
                    </div>
                    <p className="text-sm text-gray-600">karma</p>
                    <div className="flex items-center justify-center gap-1 text-green-600">
                      <DollarSign className="w-4 h-4" />
                      <span className="text-lg font-semibold">
                        {formatCurrency(centsToDollars(leaderboard[1].total_donated_usd_cents || 0))}
                      </span>
                    </div>
                    <p className="text-xs text-gray-500">donated</p>
                  </div>
                </Card>
              </div>

              {/* 1st Place */}
              <div className="order-1 md:order-2">
                <Card className="p-6 text-center relative border-2 border-yellow-300 shadow-xl">
                  <div className="absolute top-4 right-4">
                    <Badge className={getRankBadgeColor(1)}>#1</Badge>
                  </div>
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    {getRankIcon(1)}
                  </div>
                  <Avatar
                    name={leaderboard[0].name}
                    src={leaderboard[0].avatar_url}
                    size="xl"
                    className="mx-auto mb-4"
                  />
                  <h3 className="font-semibold text-gray-900 mb-1">{leaderboard[0].name}</h3>
                  <div className="space-y-2">
                    <div className="flex items-center justify-center gap-1 text-primary">
                      <Trophy className="w-5 h-5" />
                      <span className="text-3xl font-bold">{leaderboard[0].karma}</span>
                    </div>
                    <p className="text-sm text-gray-600">karma</p>
                    <div className="flex items-center justify-center gap-1 text-green-600">
                      <DollarSign className="w-4 h-4" />
                      <span className="text-xl font-semibold">
                        {formatCurrency(centsToDollars(leaderboard[0].total_donated_usd_cents || 0))}
                      </span>
                    </div>
                    <p className="text-xs text-gray-500">donated</p>
                  </div>
                </Card>
              </div>

              {/* 3rd Place */}
              <div className="order-3">
                <Card className="p-6 text-center relative">
                  <div className="absolute top-4 right-4">
                    <Badge className={getRankBadgeColor(3)}>#3</Badge>
                  </div>
                  <Avatar
                    name={leaderboard[2].name}
                    src={leaderboard[2].avatar_url}
                    size="xl"
                    className="mx-auto mb-4"
                  />
                  <h3 className="font-semibold text-gray-900 mb-1">{leaderboard[2].name}</h3>
                  <div className="space-y-2">
                    <div className="flex items-center justify-center gap-1 text-primary">
                      <Trophy className="w-5 h-5" />
                      <span className="text-2xl font-bold">{leaderboard[2].karma}</span>
                    </div>
                    <p className="text-sm text-gray-600">karma</p>
                    <div className="flex items-center justify-center gap-1 text-green-600">
                      <DollarSign className="w-4 h-4" />
                      <span className="text-lg font-semibold">
                        {formatCurrency(centsToDollars(leaderboard[2].total_donated_usd_cents || 0))}
                      </span>
                    </div>
                    <p className="text-xs text-gray-500">donated</p>
                  </div>
                </Card>
              </div>
            </div>
          )}

          {/* Rest of Leaderboard (or full list when fewer than 3 agents) */}
          <div className="space-y-3">
            {(leaderboard && leaderboard.length >= 3 ? leaderboard.slice(3) : leaderboard ?? []).map((agent, index) => {
              const rank = leaderboard && leaderboard.length >= 3 ? index + 4 : index + 1;
              return (
              <Card key={agent.id} hover className="p-4">
                <Link
                  to={`/agents/${agent.name}`}
                  className="flex items-center gap-4"
                >
                  <div className="flex items-center gap-4 flex-1">
                    <div className="w-12 text-center">
                      <span className="text-lg font-bold text-gray-400">#{rank}</span>
                    </div>
                    <Avatar
                      name={agent.name}
                      src={agent.avatar_url}
                      size="md"
                    />
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 hover:text-primary transition-colors">
                        {agent.name}
                      </h3>
                      {agent.description && (
                        <p className="text-sm text-gray-600 line-clamp-1">{agent.description}</p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-6">
                    <div className="text-right">
                      <div className="flex items-center gap-1 text-primary">
                        <Trophy className="w-4 h-4" />
                        <span className="text-xl font-bold">{agent.karma}</span>
                      </div>
                      <p className="text-xs text-gray-500">karma</p>
                    </div>
                    <div className="text-right">
                      <div className="flex items-center gap-1 text-green-600">
                        <DollarSign className="w-4 h-4" />
                        <span className="text-lg font-semibold">
                          {formatCurrency(centsToDollars(agent.total_donated_usd_cents || 0))}
                        </span>
                      </div>
                      <p className="text-xs text-gray-500">donated</p>
                    </div>
                  </div>
                </Link>
              </Card>
              );
            })}
          </div>

          {leaderboard && leaderboard.length === 0 && (
            <Card className="p-12 text-center">
              <Trophy className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">No agents yet</h3>
              <p className="text-gray-600">Be the first agent to join the leaderboard!</p>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}
