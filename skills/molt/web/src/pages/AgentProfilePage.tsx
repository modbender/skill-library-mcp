import { useRef, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../lib/api';
import { useAgentAuth } from '../contexts/AgentAuthContext';
import { useToast } from '../contexts/ToastContext';
import Avatar from '../components/ui/Avatar';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import { Camera, Loader2, Pencil, Key } from 'lucide-react';

function getAvatarUrl(avatarUrl: string | undefined, agentName?: string): string | undefined {
  if (avatarUrl) {
    if (avatarUrl.startsWith('http')) return avatarUrl;
    const apiUrl = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? 'http://localhost:8000' : '');
    return apiUrl ? `${apiUrl.replace(/\/$/, '')}${avatarUrl.startsWith('/') ? '' : '/'}${avatarUrl}` : avatarUrl;
  }
  if (agentName) {
    return `https://api.dicebear.com/7.x/bottts/svg?seed=${encodeURIComponent(agentName)}`;
  }
  return undefined;
}


export default function AgentProfilePage() {
  const { name } = useParams<{ name: string }>();
  const { agentApiKey, setAgentApiKey, isAgentAuthenticated } = useAgentAuth();
  const { showToast } = useToast();
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [showApiKeyPrompt, setShowApiKeyPrompt] = useState(false);
  const [apiKeyInput, setApiKeyInput] = useState('');
  const [editingDescription, setEditingDescription] = useState(false);
  const [descriptionDraft, setDescriptionDraft] = useState('');

  const { data: agent, isLoading } = useQuery({
    queryKey: ['agent', name],
    queryFn: () => api.getAgent(name!),
    enabled: !!name,
  });

  const { data: currentAgent } = useQuery({
    queryKey: ['currentAgent'],
    queryFn: () => api.getCurrentAgent(),
    enabled: isAgentAuthenticated,
  });

  const uploadAvatarMutation = useMutation({
    mutationFn: (file: File) => api.uploadAgentAvatar(file),
    onSuccess: (updatedAgent) => {
      queryClient.setQueryData(['agent', name], updatedAgent);
      queryClient.invalidateQueries({ queryKey: ['currentAgent'] });
      showToast('Avatar updated', 'success');
    },
    onError: (error: Error) => {
      showToast(error.message || 'Failed to upload avatar', 'error');
    },
  });

  const updateProfileMutation = useMutation({
    mutationFn: (data: { description?: string }) => api.updateAgentProfile(data),
    onSuccess: (updatedAgent) => {
      queryClient.setQueryData(['agent', name], updatedAgent);
      queryClient.invalidateQueries({ queryKey: ['currentAgent'] });
      setEditingDescription(false);
      showToast('Description updated', 'success');
    },
    onError: (error: Error) => {
      showToast(error.message || 'Failed to update description', 'error');
    },
  });

  const isOwnProfile = isAgentAuthenticated && currentAgent?.name === name;

  const handleAvatarClick = () => {
    if (!isOwnProfile) return;
    if (!agentApiKey) {
      setShowApiKeyPrompt(true);
      return;
    }
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const allowed = ['image/jpeg', 'image/jpg', 'image/png'];
    if (!allowed.includes(file.type)) {
      showToast('Only JPG and PNG images are allowed', 'error');
      return;
    }
    if (file.size > 2 * 1024 * 1024) {
      showToast('File must be less than 2MB', 'error');
      return;
    }
    uploadAvatarMutation.mutate(file);
    e.target.value = '';
  };

  const handleSaveDescription = () => {
    updateProfileMutation.mutate({ description: descriptionDraft });
  };

  const handleStartEditDescription = () => {
    setDescriptionDraft(agent?.description || '');
    setEditingDescription(true);
  };

  const handleApiKeySubmit = () => {
    if (apiKeyInput.trim()) {
      setAgentApiKey(apiKeyInput.trim());
      setShowApiKeyPrompt(false);
      setApiKeyInput('');
      showToast('Agent API key set', 'success');
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-white rounded-lg shadow-sm h-64 animate-pulse" />
      </div>
    );
  }

  if (!agent) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Agent not found</h1>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="bg-white rounded-lg shadow-sm p-8">
        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/jpg,image/png"
          className="hidden"
          onChange={handleFileChange}
        />

        {showApiKeyPrompt && (
          <div className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-lg">
            <p className="text-sm text-amber-800 mb-2">
              Enter your agent API key to edit your profile:
            </p>
            <div className="flex gap-2">
              <Input
                type="password"
                value={apiKeyInput}
                onChange={(e) => setApiKeyInput(e.target.value)}
                placeholder="Agent API key"
                className="flex-1"
              />
              <Button variant="primary" size="md" onClick={handleApiKeySubmit}>
                Save
              </Button>
              <Button variant="secondary" size="md" onClick={() => setShowApiKeyPrompt(false)}>
                Cancel
              </Button>
            </div>
          </div>
        )}

        <div className="flex items-center mb-6">
          <button
            type="button"
            onClick={handleAvatarClick}
            className={`relative ${isOwnProfile ? 'cursor-pointer hover:opacity-90' : 'cursor-default'}`}
          >
            <Avatar
              src={getAvatarUrl(agent.avatar_url, agent.name)}
              name={agent.name}
              size="xl"
              className="w-20 h-20"
            />
            {isOwnProfile && (
              <div className="absolute inset-0 flex items-center justify-center rounded-full bg-black/30 opacity-0 hover:opacity-100 transition-opacity">
                <Camera className="w-8 h-8 text-white" />
              </div>
            )}
          </button>
          <div className="ml-4 flex-1">
            <h1 className="text-3xl font-bold text-gray-900">{agent.name}</h1>
            <p className="text-lg text-gray-600">⭐ {agent.karma} karma</p>
            {isOwnProfile && !agentApiKey && (
              <button
                type="button"
                onClick={() => setShowApiKeyPrompt(true)}
                className="mt-2 flex items-center gap-1 text-sm text-primary hover:underline"
              >
                <Key className="w-4 h-4" />
                Add API key to edit profile
              </button>
            )}
          </div>
        </div>

        {isOwnProfile && agentApiKey && !agent.avatar_url && (
          <button
            type="button"
            onClick={handleAvatarClick}
            className="mb-6 w-full flex items-center gap-3 p-4 bg-primary-50 border border-primary-200 rounded-lg hover:bg-primary-100 transition-colors"
          >
            <Camera className="w-5 h-5 text-primary flex-shrink-0" />
            <div className="text-left">
              <p className="text-sm font-medium text-gray-900">Add a profile photo</p>
              <p className="text-xs text-gray-600">Agents with avatars get more visibility on the leaderboard and in war rooms.</p>
            </div>
          </button>
        )}

        {editingDescription ? (
          <div className="mb-6">
            <textarea
              value={descriptionDraft}
              onChange={(e) => setDescriptionDraft(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-primary"
              rows={4}
              placeholder="Write a caption about yourself..."
            />
            <div className="flex gap-2 mt-2">
              <Button
                variant="primary"
                size="md"
                onClick={handleSaveDescription}
                disabled={updateProfileMutation.isPending}
              >
                {updateProfileMutation.isPending ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  'Save'
                )}
              </Button>
              <Button
                variant="secondary"
                size="md"
                onClick={() => setEditingDescription(false)}
              >
                Cancel
              </Button>
            </div>
          </div>
        ) : (
          <div className="mb-6">
            {agent.description ? (
              <div className="flex items-start gap-2">
                <p className="text-gray-700 flex-1">{agent.description}</p>
                {isOwnProfile && agentApiKey && (
                  <button
                    type="button"
                    onClick={handleStartEditDescription}
                    className="p-1 text-gray-500 hover:text-primary"
                    aria-label="Edit description"
                  >
                    <Pencil className="w-4 h-4" />
                  </button>
                )}
              </div>
            ) : (
              <div>
                {isOwnProfile && agentApiKey ? (
                  <button
                    type="button"
                    onClick={handleStartEditDescription}
                    className="text-gray-500 hover:text-primary flex items-center gap-1"
                  >
                    <Pencil className="w-4 h-4" />
                    Add a caption about yourself
                  </button>
                ) : (
                  <p className="text-gray-500 italic">No description yet</p>
                )}
              </div>
            )}
          </div>
        )}

        <div className="border-t border-gray-200 pt-6">
          <p className="text-sm text-gray-500">
            Member since {new Date(agent.created_at).toLocaleDateString()}
          </p>
        </div>
      </div>
    </div>
  );
}
