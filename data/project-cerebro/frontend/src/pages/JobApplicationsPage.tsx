import { useState, useEffect, useCallback } from 'react';
import { Briefcase, Plus, ExternalLink, Mail, Trash2, Clock, CheckCircle, XCircle } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Modal } from '../components/ui/Modal';
import { Input } from '../components/ui/Input';

interface JobApplication {
  id: string;
  jobId?: string;
  company: string;
  position: string;
  url?: string;
  source?: string;
  status: string;
  salary?: string;
  location?: string;
  jobType?: string;
  description?: string;
  notes?: string;
  coverLetterGenerated: boolean;
  appliedAt?: number;
  followUpAt?: number;
  followUpSentAt?: number;
  createdAt: number;
  updatedAt: number;
}

interface Stats {
  SAVED: number;
  APPLIED: number;
  FOLLOW_UP_PENDING: number;
  FOLLOW_UP_SENT: number;
  RESPONDED: number;
  INTERVIEW_SCHEDULED: number;
  INTERVIEWED: number;
  OFFER: number;
  REJECTED: number;
  WITHDRAWN: number;
}

const STATUS_COLUMNS = [
  { key: 'SAVED', label: 'Saved', color: 'bg-gray-500' },
  { key: 'APPLIED', label: 'Applied', color: 'bg-blue-500' },
  { key: 'FOLLOW_UP_PENDING', label: 'Follow-up Due', color: 'bg-yellow-500' },
  { key: 'FOLLOW_UP_SENT', label: 'Followed Up', color: 'bg-purple-500' },
  { key: 'RESPONDED', label: 'Responded', color: 'bg-cyan-500' },
  { key: 'INTERVIEW_SCHEDULED', label: 'Interview', color: 'bg-green-500' },
  { key: 'OFFER', label: 'Offer', color: 'bg-emerald-500' },
  { key: 'REJECTED', label: 'Rejected', color: 'bg-red-500' },
];

export function JobApplicationsPage() {
  const [applications, setApplications] = useState<JobApplication[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [draggingId, setDraggingId] = useState<string | null>(null);
  const [dragOverCol, setDragOverCol] = useState<string | null>(null);
  const [isAddOpen, setIsAddOpen] = useState(false);
  const [editingApp, setEditingApp] = useState<JobApplication | null>(null);
  const [viewMode, setViewMode] = useState<'kanban' | 'list'>('kanban');
  const [newApp, setNewApp] = useState({
    company: '',
    position: '',
    url: '',
    source: 'manual',
    salary: '',
    location: '',
    notes: '',
  });
  const [jobSearchTaskId, setJobSearchTaskId] = useState<string | null>(null);
  const [jobSearchRunning, setJobSearchRunning] = useState(false);

  const fetchApplications = useCallback(async () => {
    try {
      const [appsRes, statsRes] = await Promise.all([
        fetch('/api/job-applications'),
        fetch('/api/job-applications/stats'),
      ]);
      const appsData = await appsRes.json();
      const statsData = await statsRes.json();
      setApplications(appsData.applications || []);
      setStats(statsData.stats || null);
    } catch (e) {
      console.error('Failed to fetch job applications:', e);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchJobAutomation = useCallback(async () => {
    try {
      const res = await fetch('/api/brains/job/recurring');
      const data = await res.json();
      const jobSearchTask = (data.recurringTasks || []).find((task: any) =>
        String(task.title || '').toLowerCase().includes('job search')
      );
      setJobSearchTaskId(jobSearchTask?.id ?? null);
    } catch (e) {
      console.error('Failed to fetch job automation:', e);
    }
  }, []);

  useEffect(() => {
    fetchApplications();
    fetchJobAutomation();
  }, [fetchApplications, fetchJobAutomation]);

  const handleCreate = async () => {
    if (!newApp.company || !newApp.position) return;
    try {
      await fetch('/api/job-applications', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newApp),
      });
      setIsAddOpen(false);
      setNewApp({ company: '', position: '', url: '', source: 'manual', salary: '', location: '', notes: '' });
      fetchApplications();
    } catch (e) {
      console.error('Failed to create application:', e);
    }
  };

  const handleUpdateStatus = async (id: string, status: string) => {
    try {
      await fetch(`/api/job-applications/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status }),
      });
      fetchApplications();
    } catch (e) {
      console.error('Failed to update status:', e);
    }
  };

  // Kanban drag + drop
  const onDragStartApp = (e: React.DragEvent, app: JobApplication) => {
    setDraggingId(app.id);
    e.dataTransfer.setData('text/plain', app.id);
    e.dataTransfer.effectAllowed = 'move';
  };

  const onDragEndApp = () => {
    setDraggingId(null);
    setDragOverCol(null);
  };

  const onDragOverColumn = (e: React.DragEvent, colKey: string) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    if (dragOverCol !== colKey) setDragOverCol(colKey);
  };

  const onDropColumn = async (e: React.DragEvent, colKey: string) => {
    e.preventDefault();
    const id = e.dataTransfer.getData('text/plain') || draggingId;
    if (!id) return;

    const app = applications.find((a) => a.id === id);
    if (!app) return;

    if (app.status !== colKey) {
      await handleUpdateStatus(id, colKey);
    }

    setDragOverCol(null);
    setDraggingId(null);
  };

  const handleMarkApplied = async (id: string) => {
    try {
      await fetch(`/api/job-applications/${id}/apply`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ followUpDays: 3 }),
      });
      fetchApplications();
    } catch (e) {
      console.error('Failed to mark as applied:', e);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this application?')) return;
    try {
      await fetch(`/api/job-applications/${id}`, { method: 'DELETE' });
      fetchApplications();
    } catch (e) {
      console.error('Failed to delete:', e);
    }
  };

  const handleRunJobSearch = async () => {
    if (!jobSearchTaskId) return;
    try {
      setJobSearchRunning(true);
      await fetch(`/api/recurring/${jobSearchTaskId}/run`, { method: 'POST' });
    } catch (e) {
      console.error('Failed to run job search:', e);
    } finally {
      setJobSearchRunning(false);
    }
  };

  const getAppsByStatus = (status: string) => {
    return applications.filter((a) => a.status === status);
  };

  const formatDate = (ts?: number) => {
    if (!ts) return '-';
    return new Date(ts).toLocaleDateString();
  };

  const totalActive = stats
    ? stats.SAVED + stats.APPLIED + stats.FOLLOW_UP_PENDING + stats.FOLLOW_UP_SENT + stats.RESPONDED + stats.INTERVIEW_SCHEDULED
    : 0;

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold mb-2 flex items-center gap-3">
            <Briefcase className="w-8 h-8 text-blue-400" />
            Job Applications
          </h1>
          <p className="text-muted-foreground">Track your job search pipeline</p>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex bg-secondary rounded-lg p-1">
            <button
              onClick={() => setViewMode('kanban')}
              className={`px-3 py-1 rounded text-sm ${viewMode === 'kanban' ? 'bg-primary text-primary-foreground' : ''}`}
            >
              Kanban
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`px-3 py-1 rounded text-sm ${viewMode === 'list' ? 'bg-primary text-primary-foreground' : ''}`}
            >
              List
            </button>
          </div>
          {jobSearchTaskId && (
            <Button variant="secondary" onClick={handleRunJobSearch} disabled={jobSearchRunning}>
              <Clock className="w-4 h-4 mr-2" />
              {jobSearchRunning ? 'Running Job Search...' : 'Run Job Search'}
            </Button>
          )}
          <Button variant="primary" onClick={() => setIsAddOpen(true)}>
            <Plus className="w-4 h-4 mr-2" />
            Add Application
          </Button>
        </div>
      </header>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3">
          <Card className="p-3 text-center">
            <div className="text-2xl font-bold">{totalActive}</div>
            <div className="text-xs text-muted-foreground">Active</div>
          </Card>
          <Card className="p-3 text-center">
            <div className="text-2xl font-bold text-blue-400">{stats.APPLIED}</div>
            <div className="text-xs text-muted-foreground">Applied</div>
          </Card>
          <Card className="p-3 text-center">
            <div className="text-2xl font-bold text-yellow-400">{stats.FOLLOW_UP_PENDING}</div>
            <div className="text-xs text-muted-foreground">Need Follow-up</div>
          </Card>
          <Card className="p-3 text-center">
            <div className="text-2xl font-bold text-green-400">{stats.INTERVIEW_SCHEDULED}</div>
            <div className="text-xs text-muted-foreground">Interviews</div>
          </Card>
          <Card className="p-3 text-center">
            <div className="text-2xl font-bold text-emerald-400">{stats.OFFER}</div>
            <div className="text-xs text-muted-foreground">Offers</div>
          </Card>
          <Card className="p-3 text-center">
            <div className="text-2xl font-bold text-cyan-400">{stats.RESPONDED}</div>
            <div className="text-xs text-muted-foreground">Responses</div>
          </Card>
          <Card className="p-3 text-center">
            <div className="text-2xl font-bold text-red-400">{stats.REJECTED}</div>
            <div className="text-xs text-muted-foreground">Rejected</div>
          </Card>
          <Card className="p-3 text-center">
            <div className="text-2xl font-bold">{stats.SAVED}</div>
            <div className="text-xs text-muted-foreground">Saved</div>
          </Card>
        </div>
      )}

      {/* Main Content */}
      {loading ? (
        <div className="text-center py-12 text-muted-foreground">Loading...</div>
      ) : viewMode === 'kanban' ? (
        /* Kanban View */
        <div className="flex gap-4 overflow-x-auto pb-4">
          {STATUS_COLUMNS.map((col) => {
            const apps = getAppsByStatus(col.key);
            return (
              <div key={col.key} className="flex-shrink-0 w-72">
                <div className="flex items-center gap-2 mb-3">
                  <div className={`w-3 h-3 rounded-full ${col.color}`} />
                  <h3 className="font-medium">{col.label}</h3>
                  <Badge variant="default">{apps.length}</Badge>
                </div>
                <div
                  className={`space-y-2 rounded-xl p-1 transition-colors ${
                    dragOverCol === col.key ? 'bg-primary/10' : ''
                  }`}
                  onDragOver={(e) => onDragOverColumn(e, col.key)}
                  onDragEnter={() => setDragOverCol(col.key)}
                  onDragLeave={() => setDragOverCol((cur) => (cur === col.key ? null : cur))}
                  onDrop={(e) => onDropColumn(e, col.key)}
                >
                  {apps.map((app) => (
                    <Card
                      key={app.id}
                      draggable
                      onDragStart={(e: React.DragEvent) => onDragStartApp(e, app)}
                      onDragEnd={onDragEndApp}
                      className={`p-3 cursor-pointer hover:border-primary/50 transition-colors ${
                        draggingId === app.id ? 'opacity-60 border-primary/50' : ''
                      }`}
                      onClick={() => {
                        // Avoid opening modal if the user was dragging.
                        if (draggingId) return;
                        setEditingApp(app);
                      }}
                    >
                      <div className="font-medium truncate">{app.position}</div>
                      <div className="text-sm text-muted-foreground truncate">{app.company}</div>
                      {app.location && (
                        <div className="text-xs text-muted-foreground mt-1">{app.location}</div>
                      )}
                      {app.salary && (
                        <div className="text-xs text-green-400 mt-1">{app.salary}</div>
                      )}
                      <div className="flex items-center gap-2 mt-2">
                        {app.url && (
                          <a
                            href={app.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            onClick={(e) => e.stopPropagation()}
                            className="text-xs text-blue-400 hover:underline flex items-center gap-1"
                          >
                            <ExternalLink className="w-3 h-3" />
                            Link
                          </a>
                        )}
                        {app.source && (
                          <Badge variant="default" className="text-xs">
                            {app.source}
                          </Badge>
                        )}
                      </div>
                      {app.appliedAt && (
                        <div className="text-xs text-muted-foreground mt-2">
                          Applied: {formatDate(app.appliedAt)}
                        </div>
                      )}
                      {app.followUpAt && app.status === 'FOLLOW_UP_PENDING' && (
                        <div className="text-xs text-yellow-400 mt-1 flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          Follow up: {formatDate(app.followUpAt)}
                        </div>
                      )}
                    </Card>
                  ))}
                  {apps.length === 0 && (
                    <div className="text-center py-8 text-muted-foreground/50 text-sm">
                      No applications
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        /* List View */
        <Card>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left p-3 font-medium">Position</th>
                  <th className="text-left p-3 font-medium">Company</th>
                  <th className="text-left p-3 font-medium">Status</th>
                  <th className="text-left p-3 font-medium">Location</th>
                  <th className="text-left p-3 font-medium">Applied</th>
                  <th className="text-left p-3 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {applications.map((app) => (
                  <tr
                    key={app.id}
                    className="border-b border-border/50 hover:bg-secondary/20 cursor-pointer"
                    onClick={() => setEditingApp(app)}
                  >
                    <td className="p-3">
                      <div className="font-medium">{app.position}</div>
                      {app.salary && <div className="text-xs text-green-400">{app.salary}</div>}
                    </td>
                    <td className="p-3">{app.company}</td>
                    <td className="p-3">
                      <Badge
                        variant={
                          app.status === 'OFFER'
                            ? 'success'
                            : app.status === 'REJECTED'
                            ? 'error'
                            : 'default'
                        }
                      >
                        {app.status.replace(/_/g, ' ')}
                      </Badge>
                    </td>
                    <td className="p-3 text-sm text-muted-foreground">{app.location || '-'}</td>
                    <td className="p-3 text-sm text-muted-foreground">{formatDate(app.appliedAt)}</td>
                    <td className="p-3">
                      <div className="flex items-center gap-2">
                        {app.url && (
                          <a
                            href={app.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            onClick={(e) => e.stopPropagation()}
                          >
                            <ExternalLink className="w-4 h-4 text-blue-400" />
                          </a>
                        )}
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDelete(app.id);
                          }}
                        >
                          <Trash2 className="w-4 h-4 text-red-400" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* Add Modal */}
      <Modal isOpen={isAddOpen} onClose={() => setIsAddOpen(false)} title="Add Job Application">
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium">Company *</label>
            <Input
              value={newApp.company}
              onChange={(e) => setNewApp({ ...newApp, company: e.target.value })}
              placeholder="Company name"
            />
          </div>
          <div>
            <label className="text-sm font-medium">Position *</label>
            <Input
              value={newApp.position}
              onChange={(e) => setNewApp({ ...newApp, position: e.target.value })}
              placeholder="Job title"
            />
          </div>
          <div>
            <label className="text-sm font-medium">URL</label>
            <Input
              value={newApp.url}
              onChange={(e) => setNewApp({ ...newApp, url: e.target.value })}
              placeholder="https://..."
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium">Location</label>
              <Input
                value={newApp.location}
                onChange={(e) => setNewApp({ ...newApp, location: e.target.value })}
                placeholder="Remote, NYC, etc."
              />
            </div>
            <div>
              <label className="text-sm font-medium">Salary</label>
              <Input
                value={newApp.salary}
                onChange={(e) => setNewApp({ ...newApp, salary: e.target.value })}
                placeholder="$100k-150k"
              />
            </div>
          </div>
          <div>
            <label className="text-sm font-medium">Source</label>
            <select
              value={newApp.source}
              onChange={(e) => setNewApp({ ...newApp, source: e.target.value })}
              className="w-full mt-1 px-3 py-2 rounded-lg border border-border bg-secondary"
            >
              <option value="manual">Manual</option>
              <option value="linkedin">LinkedIn</option>
              <option value="indeed">Indeed</option>
              <option value="glassdoor">Glassdoor</option>
              <option value="wellfound">Wellfound</option>
              <option value="ziprecruiter">ZipRecruiter</option>
              <option value="referral">Referral</option>
              <option value="company_site">Company Site</option>
            </select>
          </div>
          <div>
            <label className="text-sm font-medium">Notes</label>
            <textarea
              value={newApp.notes}
              onChange={(e) => setNewApp({ ...newApp, notes: e.target.value })}
              placeholder="Any notes about the role..."
              className="w-full mt-1 px-3 py-2 rounded-lg border border-border bg-secondary min-h-[80px]"
            />
          </div>
          <div className="flex gap-2 pt-4">
            <Button variant="secondary" onClick={() => setIsAddOpen(false)} className="flex-1">
              Cancel
            </Button>
            <Button variant="primary" onClick={handleCreate} className="flex-1">
              Add
            </Button>
          </div>
        </div>
      </Modal>

      {/* Edit/View Modal */}
      {editingApp && (
        <Modal
          isOpen={!!editingApp}
          onClose={() => setEditingApp(null)}
          title={`${editingApp.position} @ ${editingApp.company}`}
        >
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Badge
                variant={
                  editingApp.status === 'OFFER'
                    ? 'success'
                    : editingApp.status === 'REJECTED'
                    ? 'error'
                    : 'default'
                }
              >
                {editingApp.status.replace(/_/g, ' ')}
              </Badge>
              {editingApp.source && (
                <Badge variant="default">{editingApp.source}</Badge>
              )}
              {editingApp.coverLetterGenerated && (
                <Badge variant="success">Cover Letter</Badge>
              )}
            </div>

            {editingApp.location && (
              <div>
                <span className="text-sm text-muted-foreground">Location:</span>{' '}
                <span>{editingApp.location}</span>
              </div>
            )}
            {editingApp.salary && (
              <div>
                <span className="text-sm text-muted-foreground">Salary:</span>{' '}
                <span className="text-green-400">{editingApp.salary}</span>
              </div>
            )}
            {editingApp.url && (
              <div>
                <a
                  href={editingApp.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-400 hover:underline flex items-center gap-1"
                >
                  <ExternalLink className="w-4 h-4" />
                  View Job Posting
                </a>
              </div>
            )}

            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-muted-foreground">Added:</span>{' '}
                {formatDate(editingApp.createdAt)}
              </div>
              {editingApp.appliedAt && (
                <div>
                  <span className="text-muted-foreground">Applied:</span>{' '}
                  {formatDate(editingApp.appliedAt)}
                </div>
              )}
              {editingApp.followUpAt && (
                <div>
                  <span className="text-muted-foreground">Follow-up:</span>{' '}
                  {formatDate(editingApp.followUpAt)}
                </div>
              )}
            </div>

            {editingApp.notes && (
              <div>
                <div className="text-sm text-muted-foreground mb-1">Notes:</div>
                <div className="p-3 bg-secondary/30 rounded-lg text-sm">{editingApp.notes}</div>
              </div>
            )}

            {/* Status Actions */}
            <div className="pt-4 border-t border-border">
              <div className="text-sm font-medium mb-3">Update Status</div>
              <div className="flex flex-wrap gap-2">
                {editingApp.status === 'SAVED' && (
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => {
                      handleMarkApplied(editingApp.id);
                      setEditingApp(null);
                    }}
                  >
                    <CheckCircle className="w-4 h-4 mr-1" />
                    Mark Applied
                  </Button>
                )}
                {editingApp.status === 'FOLLOW_UP_PENDING' && (
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={() => {
                      handleUpdateStatus(editingApp.id, 'FOLLOW_UP_SENT');
                      setEditingApp(null);
                    }}
                  >
                    <Mail className="w-4 h-4 mr-1" />
                    Mark Follow-up Sent
                  </Button>
                )}
                {['APPLIED', 'FOLLOW_UP_PENDING', 'FOLLOW_UP_SENT'].includes(editingApp.status) && (
                  <>
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => {
                        handleUpdateStatus(editingApp.id, 'RESPONDED');
                        setEditingApp(null);
                      }}
                    >
                      Got Response
                    </Button>
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => {
                        handleUpdateStatus(editingApp.id, 'INTERVIEW_SCHEDULED');
                        setEditingApp(null);
                      }}
                    >
                      Schedule Interview
                    </Button>
                  </>
                )}
                {editingApp.status === 'INTERVIEW_SCHEDULED' && (
                  <>
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => {
                        handleUpdateStatus(editingApp.id, 'INTERVIEWED');
                        setEditingApp(null);
                      }}
                    >
                      Interviewed
                    </Button>
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={() => {
                        handleUpdateStatus(editingApp.id, 'OFFER');
                        setEditingApp(null);
                      }}
                    >
                      Got Offer!
                    </Button>
                  </>
                )}
                {!['OFFER', 'REJECTED', 'WITHDRAWN'].includes(editingApp.status) && (
                  <Button
                    variant="danger"
                    size="sm"
                    onClick={() => {
                      handleUpdateStatus(editingApp.id, 'REJECTED');
                      setEditingApp(null);
                    }}
                  >
                    <XCircle className="w-4 h-4 mr-1" />
                    Rejected
                  </Button>
                )}
              </div>
            </div>

            <div className="flex gap-2 pt-4">
              <Button
                variant="danger"
                onClick={() => {
                  handleDelete(editingApp.id);
                  setEditingApp(null);
                }}
              >
                <Trash2 className="w-4 h-4 mr-1" />
                Delete
              </Button>
              <Button variant="secondary" onClick={() => setEditingApp(null)} className="flex-1">
                Close
              </Button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
