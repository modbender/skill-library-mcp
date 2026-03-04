import { useState, useRef, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate, useParams } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api, type CampaignUpdateData, type CampaignImage } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import { dollarsToCents, centsToDollars } from '../lib/utils';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Textarea from '../components/ui/Textarea';
import Select from '../components/ui/Select';
import KYCVerification from '../components/KYCVerification';
import { ArrowLeft, Loader2, ImagePlus, X } from 'lucide-react';
import { Link } from 'react-router-dom';

const campaignSchema = z.object({
  title: z.string().min(1, 'Title is required').max(100, 'Title must be 100 characters or less'),
  description: z.string().min(1, 'Description is required').max(5000, 'Description must be 5000 characters or less'),
  creator_name: z.string().min(1, 'Your name is required').max(100, 'Name must be 100 characters or less'),
  creator_story: z.string().max(2000, 'Story must be 2000 characters or less').optional().or(z.literal('')),
  category: z.enum(['MEDICAL', 'DISASTER_RELIEF', 'EDUCATION', 'COMMUNITY', 'EMERGENCY', 'OTHER']),
  goal_amount_usd: z.number().positive('Goal amount must be greater than 0'),
  cover_image_url: z.string().url('Invalid URL').optional().or(z.literal('')),
  end_date: z.string().optional(),
});

type CampaignFormData = z.infer<typeof campaignSchema>;

const categoryOptions = [
  { value: 'MEDICAL', label: 'Medical' },
  { value: 'DISASTER_RELIEF', label: 'Disaster Relief' },
  { value: 'EDUCATION', label: 'Education' },
  { value: 'COMMUNITY', label: 'Community' },
  { value: 'EMERGENCY', label: 'Emergency' },
  { value: 'OTHER', label: 'Other' },
];

export default function EditCampaignPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const { showToast } = useToast();
  const queryClient = useQueryClient();
  const hasSubmitted = useRef(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [existingImages, setExistingImages] = useState<CampaignImage[]>([]);

  const { data: campaign, isLoading: campaignLoading } = useQuery({
    queryKey: ['campaign', id],
    queryFn: () => api.getCampaign(id!),
    enabled: !!id,
  });

  const { data: kycStatus } = useQuery({
    queryKey: ['kyc-status'],
    queryFn: () => api.getKYCStatus(),
    enabled: !!user,
  });

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<CampaignFormData>({
    resolver: zodResolver(campaignSchema),
  });

  useEffect(() => {
    if (campaign) {
      reset({
        title: campaign.title,
        description: campaign.description,
        creator_name: campaign.creator_name || '',
        creator_story: campaign.creator_story || '',
        category: campaign.category,
        goal_amount_usd: centsToDollars(campaign.goal_amount_usd),
        cover_image_url: campaign.cover_image_url || '',
        end_date: campaign.end_date ? campaign.end_date.split('T')[0] : '',
      });
    }
  }, [campaign, reset]);

  useEffect(() => {
    if (user && campaign?.creator_id && campaign.creator_id !== user.id) {
      navigate(`/campaigns/${id}`);
    }
  }, [user, campaign?.creator_id, id, navigate]);

  useEffect(() => {
    if (campaign?.images) {
      setExistingImages(campaign.images);
    }
  }, [campaign?.images]);

  const handleImageUpload = async (files: FileList | null) => {
    if (!files || !id) return;
    const validFiles = Array.from(files).filter(
      (f) => f.type === 'image/jpeg' || f.type === 'image/png'
    );
    for (const file of validFiles) {
      if (existingImages.length >= 5) break;
      try {
        const uploaded = await api.uploadCampaignImage(id, file);
        setExistingImages((prev) => [...prev, uploaded]);
        showToast('Image uploaded', 'success');
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : 'Failed to upload image';
        showToast(message, 'error');
      }
    }
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleImageDelete = async (imageId: string) => {
    if (!id) return;
    try {
      await api.deleteCampaignImage(id, imageId);
      setExistingImages((prev) => prev.filter((img) => img.id !== imageId));
      showToast('Image removed', 'success');
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Failed to remove image';
      showToast(message, 'error');
    }
  };

  const updateCampaignMutation = useMutation({
    mutationFn: async (data: CampaignFormData) => {
      const updateData: CampaignUpdateData = {
        title: data.title,
        description: data.description,
        creator_name: data.creator_name || undefined,
        creator_story: data.creator_story || undefined,
        category: data.category,
        goal_amount_usd: dollarsToCents(data.goal_amount_usd),
        cover_image_url: data.cover_image_url || undefined,
        end_date: data.end_date || undefined,
      };
      return api.updateCampaign(id!, updateData);
    },
    onSuccess: () => {
      showToast('Campaign updated successfully!', 'success');
      queryClient.invalidateQueries({ queryKey: ['campaign', id] });
      navigate(`/campaigns/${id}`);
    },
    onError: (error: Error) => {
      hasSubmitted.current = false;
      showToast(error.message || 'Failed to update campaign', 'error');
    },
  });

  const onSubmit = (data: CampaignFormData) => {
    if (hasSubmitted.current) return;
    hasSubmitted.current = true;
    updateCampaignMutation.mutate(data);
  };

  if (campaignLoading || !campaign) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-8">
        <Card className="p-8 text-center">
          <Loader2 className="w-16 h-16 mx-auto mb-4 text-primary animate-spin" />
          <p className="text-gray-600">Loading campaign...</p>
        </Card>
      </div>
    );
  }

  if (user && campaign.creator_id && campaign.creator_id !== user.id) {
    return null;
  }

  if (kycStatus && !kycStatus.can_create_campaign) {
    return <KYCVerification status={kycStatus} />;
  }

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <Link
        to={`/campaigns/${id}`}
        className="inline-flex items-center text-gray-600 hover:text-gray-900 mb-6"
      >
        <ArrowLeft className="w-4 h-4 mr-2" />
        Back to Campaign
      </Link>

      <Card className="p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Edit Campaign</h1>
        <p className="text-gray-600 mb-8">
          Update your campaign details. Wallet addresses cannot be changed here.
        </p>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <Input
            label="Campaign Title"
            {...register('title')}
            error={errors.title?.message}
            placeholder="e.g., Help Maria's Family After House Fire"
          />

          <Textarea
            label="Campaign Description"
            {...register('description')}
            error={errors.description?.message}
            placeholder="Tell your story..."
            rows={8}
          />

          <div className="space-y-4 p-4 bg-gray-50 rounded-lg">
            <h3 className="text-sm font-medium text-gray-900">About You</h3>
            <Input
              label="Your Name"
              {...register('creator_name')}
              error={errors.creator_name?.message}
              placeholder="e.g., Jane Doe"
            />
            <Textarea
              label="Your Story (Optional)"
              {...register('creator_story')}
              error={errors.creator_story?.message}
              placeholder="Tell donors a bit about yourself..."
              rows={4}
            />
          </div>

          <Select
            label="Category"
            {...register('category')}
            error={errors.category?.message}
            options={categoryOptions}
          />

          <Input
            label="Goal Amount (USD)"
            type="number"
            step="0.01"
            min="0.01"
            {...register('goal_amount_usd', { valueAsNumber: true })}
            error={errors.goal_amount_usd?.message}
            placeholder="1000.00"
          />

          <Input
            label="Cover Image URL (Optional)"
            type="url"
            {...register('cover_image_url')}
            error={errors.cover_image_url?.message}
            placeholder="https://example.com/image.jpg"
          />

          {/* Campaign Images */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Campaign Images (up to 5)
            </label>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/png,image/jpg"
              multiple
              className="hidden"
              onChange={(e) => handleImageUpload(e.target.files)}
            />
            <div className="flex flex-wrap gap-3">
              {existingImages.map((img) => (
                <div key={img.id} className="relative group">
                  <img
                    src={img.image_url}
                    alt="Campaign image"
                    className="w-20 h-20 object-cover rounded-lg border border-gray-200"
                  />
                  <button
                    type="button"
                    aria-label="Remove image"
                    onClick={() => handleImageDelete(img.id)}
                    className="absolute -top-2 -right-2 p-1 bg-error text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </div>
              ))}
              {existingImages.length < 5 && (
                <button
                  type="button"
                  aria-label="Add image"
                  onClick={() => fileInputRef.current?.click()}
                  className="w-20 h-20 flex items-center justify-center rounded-lg border-2 border-dashed border-gray-300 hover:border-primary hover:bg-primary/5 transition-colors"
                >
                  <ImagePlus className="w-8 h-8 text-gray-400" />
                </button>
              )}
            </div>
            <p className="text-sm text-gray-500 mt-1">JPG or PNG, max 5MB each</p>
          </div>

          <Input
            label="Campaign End Date (Optional)"
            type="date"
            {...register('end_date')}
            error={errors.end_date?.message}
          />

          <div className="flex gap-4 pt-4">
            <Button
              type="submit"
              variant="primary"
              size="lg"
              disabled={updateCampaignMutation.isPending}
              className="flex-1"
            >
              {updateCampaignMutation.isPending ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Saving...
                </>
              ) : (
                'Save Changes'
              )}
            </Button>
            <Button
              type="button"
              variant="outline"
              size="lg"
              onClick={() => navigate(`/campaigns/${id}`)}
            >
              Cancel
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
