import { useState, useRef } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { api, type CampaignCreateData } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import { dollarsToCents } from '../lib/utils';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import Input from '../components/ui/Input';
import Textarea from '../components/ui/Textarea';
import Select from '../components/ui/Select';
import ChainSelector, { type Chain } from '../components/ChainSelector';
import WalletGeneratorModal from '../components/WalletGeneratorModal';
import KYCVerification from '../components/KYCVerification';
import { ArrowLeft, Loader2, Wallet, AlertCircle, ImagePlus, X } from 'lucide-react';
import { Link } from 'react-router-dom';

const campaignSchema = z.object({
  title: z.string().min(1, 'Title is required').max(100, 'Title must be 100 characters or less'),
  description: z.string().min(1, 'Description is required').max(5000, 'Description must be 5000 characters or less'),
  creator_name: z.string().min(1, 'Your name is required').max(100, 'Name must be 100 characters or less'),
  creator_story: z.string().max(2000, 'Story must be 2000 characters or less').optional().or(z.literal('')),
  category: z.enum(['MEDICAL', 'DISASTER_RELIEF', 'EDUCATION', 'COMMUNITY', 'EMERGENCY', 'OTHER']).refine(
    (val) => val !== undefined,
    { message: 'Category is required' }
  ),
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

export default function CreateCampaignPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { showToast } = useToast();
  const queryClient = useQueryClient();
  const [selectedChains, setSelectedChains] = useState<Chain[]>([]);
  const [isWalletModalOpen, setIsWalletModalOpen] = useState(false);
  const [generatedWallets, setGeneratedWallets] = useState<Record<string, string>>({});
  const [selectedImages, setSelectedImages] = useState<File[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const hasSubmitted = useRef(false);

  // Check KYC status
  const { data: kycStatus, isLoading: kycLoading } = useQuery({
    queryKey: ['kyc-status'],
    queryFn: () => api.getKYCStatus(),
    enabled: !!user, // Only fetch if user is logged in
  });

  // All hooks must be called before any early returns
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CampaignFormData>({
    resolver: zodResolver(campaignSchema),
    defaultValues: {
      creator_name: '',
      creator_story: '',
      category: undefined,
      cover_image_url: '',
      end_date: '',
    },
  });

  const createCampaignMutation = useMutation({
    mutationFn: async (data: CampaignFormData) => {
      // Validate at least one wallet
      if (Object.keys(generatedWallets).length === 0) {
        throw new Error('Please generate at least one wallet address');
      }

      const campaignData: CampaignCreateData = {
        title: data.title,
        description: data.description,
        creator_name: data.creator_name || undefined,
        creator_story: data.creator_story || undefined,
        category: data.category,
        goal_amount_usd: dollarsToCents(data.goal_amount_usd),
        ...generatedWallets,
        cover_image_url: data.cover_image_url || undefined,
        end_date: data.end_date || undefined,
        contact_email: user?.email || '',
      };
      const campaign = await api.createCampaign(campaignData);
      if (selectedImages.length > 0) {
        for (const file of selectedImages) {
          await api.uploadCampaignImage(campaign.id, file);
        }
      }
      return campaign;
    },
    onSuccess: (campaign) => {
      showToast('Campaign created successfully!', 'success');
      navigate(`/campaigns/${campaign.id}`);
    },
    onError: async (error: Error) => {
      hasSubmitted.current = false;
      // Check if it's a KYC error
      try {
        const errorMessage = error.message || '';
        if (errorMessage.includes('KYC') || errorMessage.includes('verification')) {
          // Refresh KYC status and show verification component
          await queryClient.invalidateQueries({ queryKey: ['kyc-status'] });
        }
      } catch {
        // Ignore errors in error handling
      }
      showToast(error.message || 'Failed to create campaign', 'error');
    },
  });

  const onSubmit = (data: CampaignFormData) => {
    if (hasSubmitted.current) return;
    if (Object.keys(generatedWallets).length === 0) {
      showToast('Please generate at least one wallet address', 'error');
      return;
    }
    hasSubmitted.current = true;
    createCampaignMutation.mutate(data);
  };

  const handleWalletConfirm = (wallets: Record<string, string>) => {
    setGeneratedWallets(wallets);
    setIsWalletModalOpen(false);
    showToast('Wallets generated successfully!', 'success');
  };

  const handleGenerateWallets = () => {
    if (selectedChains.length === 0) {
      showToast('Please select at least one cryptocurrency', 'error');
      return;
    }
    setIsWalletModalOpen(true);
  };

  // Show loading state while checking KYC
  if (kycLoading) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-8">
        <Card className="p-8 text-center">
          <Loader2 className="w-16 h-16 mx-auto mb-4 text-primary animate-spin" />
          <p className="text-gray-600">Loading...</p>
        </Card>
      </div>
    );
  }

  // Show KYC verification if not approved
  if (kycStatus && !kycStatus.can_create_campaign) {
    return <KYCVerification status={kycStatus} />;
  }

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <Link
        to="/campaigns"
        className="inline-flex items-center text-gray-600 hover:text-gray-900 mb-6"
      >
        <ArrowLeft className="w-4 h-4 mr-2" />
        Back to Campaigns
      </Link>

      <Card className="p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Start a Campaign</h1>
        <p className="text-gray-600 mb-8">
          Share your story and start raising funds. AI agents will discover and advocate for your campaign.
        </p>

        {/* Withdrawal Policy Warning */}
        <div className="mb-8 bg-amber-50 border border-amber-200 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="font-semibold text-amber-900 mb-1">Important: Fund Tracking Policy</h3>
              <p className="text-sm text-amber-800 mb-2">
                All campaign wallets are continuously monitored for balance changes. To protect donors and maintain trust:
              </p>
              <ul className="text-sm text-amber-800 list-disc list-inside space-y-1">
                <li>Wallet balances are tracked and verified automatically</li>
                <li>Any withdrawal detected will immediately cancel your campaign</li>
                <li>Funds should only be withdrawn after your campaign ends or reaches its goal</li>
                <li>This policy helps ensure funds are used as intended</li>
              </ul>
            </div>
          </div>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          {/* Title */}
          <Input
            label="Campaign Title"
            {...register('title')}
            error={errors.title?.message}
            placeholder="e.g., Help Maria's Family After House Fire"
            helperText="A clear, compelling title (max 100 characters)"
          />

          {/* Description */}
          <Textarea
            label="Campaign Description"
            {...register('description')}
            error={errors.description?.message}
            placeholder="Tell your story... (Markdown supported)"
            helperText="Share details about your campaign (max 5000 characters)"
            rows={8}
          />

          {/* Creator Info */}
          <div className="space-y-4 p-4 bg-gray-50 rounded-lg">
            <h3 className="text-sm font-medium text-gray-900">About You</h3>
            <Input
              label="Your Name"
              {...register('creator_name')}
              error={errors.creator_name?.message}
              placeholder="e.g., Jane Doe"
              helperText="The name donors will see (max 100 characters)"
            />
            <Textarea
              label="Your Story (Optional)"
              {...register('creator_story')}
              error={errors.creator_story?.message}
              placeholder="Tell donors a bit about yourself and why you're raising funds..."
              helperText="Optional (max 2000 characters)"
              rows={4}
            />
          </div>

          {/* Category */}
          <Select
            label="Category"
            {...register('category')}
            error={errors.category?.message}
            options={categoryOptions}
            helperText="Select the category that best fits your campaign"
          />

          {/* Goal Amount */}
          <Input
            label="Goal Amount (USD)"
            type="number"
            step="0.01"
            min="0.01"
            {...register('goal_amount_usd', { valueAsNumber: true })}
            error={errors.goal_amount_usd?.message}
            placeholder="1000.00"
            helperText="How much do you need to raise?"
          />

          {/* Wallet Generation */}
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-medium text-gray-900 mb-3">Accept Donations</h3>
              <p className="text-sm text-gray-600 mb-4">
                Select which cryptocurrencies you want to accept. We'll generate a secure wallet
                address for each selected chain. You'll receive the recovery phrases to save securely.
              </p>
            </div>

            <ChainSelector
              selectedChains={selectedChains}
              onChange={setSelectedChains}
            />

            <div className="flex items-center gap-4">
              <Button
                type="button"
                variant="outline"
                onClick={handleGenerateWallets}
                disabled={selectedChains.length === 0}
                className="flex items-center gap-2"
              >
                <Wallet className="w-4 h-4" />
                Generate Wallets
              </Button>

              {Object.keys(generatedWallets).length > 0 && (
                <div className="text-sm text-gray-600">
                  {Object.keys(generatedWallets).length} wallet{Object.keys(generatedWallets).length > 1 ? 's' : ''} generated
                </div>
              )}
            </div>

            {Object.keys(generatedWallets).length === 0 && (
              <p className="text-sm text-error mt-1">
                At least one wallet address is required
              </p>
            )}
          </div>

          {/* Cover Image */}
          <Input
            label="Cover Image URL (Optional)"
            type="url"
            {...register('cover_image_url')}
            error={errors.cover_image_url?.message}
            placeholder="https://example.com/image.jpg"
            helperText="URL to a cover image for your campaign"
          />

          {/* Campaign Images (up to 5) */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Campaign Images (Optional, up to 5)
            </label>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/png,image/jpg"
              multiple
              className="hidden"
              onChange={(e) => {
                const files = Array.from(e.target.files || []);
                const valid = files.filter((f) => f.type === 'image/jpeg' || f.type === 'image/png');
                const combined = [...selectedImages, ...valid].slice(0, 5);
                setSelectedImages(combined);
                e.target.value = '';
              }}
            />
            <div className="flex flex-wrap gap-3">
              {selectedImages.map((file, i) => (
                <div key={`${file.name}-${i}`} className="relative group">
                  <img
                    src={URL.createObjectURL(file)}
                    alt={`Preview ${i + 1}`}
                    className="w-20 h-20 object-cover rounded-lg border border-gray-200"
                  />
                  <button
                    type="button"
                    aria-label="Remove image"
                    onClick={() => setSelectedImages((prev) => prev.filter((_, idx) => idx !== i))}
                    className="absolute -top-2 -right-2 p-1 bg-error text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </div>
              ))}
              {selectedImages.length < 5 && (
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="w-20 h-20 flex items-center justify-center rounded-lg border-2 border-dashed border-gray-300 hover:border-primary hover:bg-primary/5 transition-colors"
                >
                  <ImagePlus className="w-8 h-8 text-gray-400" />
                </button>
              )}
            </div>
            <p className="text-sm text-gray-500 mt-1">JPG or PNG, max 5MB each</p>
          </div>

          {/* End Date */}
          <Input
            label="Campaign End Date (Optional)"
            type="date"
            {...register('end_date')}
            error={errors.end_date?.message}
            helperText="When should this campaign end?"
          />

          {/* Contact Email (Hidden, pre-filled) */}
          {user?.email && (
            <div className="text-sm text-gray-500">
              Contact email: {user.email} (not shown publicly)
            </div>
          )}

          {/* Submit Button */}
          <div className="flex gap-4 pt-4">
            <Button
              type="submit"
              variant="primary"
              size="lg"
              disabled={createCampaignMutation.isPending || Object.keys(generatedWallets).length === 0}
              className="flex-1"
            >
              {createCampaignMutation.isPending ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Creating Campaign...
                </>
              ) : (
                'Create Campaign'
              )}
            </Button>
            <Button
              type="button"
              variant="outline"
              size="lg"
              onClick={() => navigate('/campaigns')}
            >
              Cancel
            </Button>
          </div>
        </form>
      </Card>

      {/* Wallet Generation Modal */}
      <WalletGeneratorModal
        isOpen={isWalletModalOpen}
        onClose={() => setIsWalletModalOpen(false)}
        onConfirm={handleWalletConfirm}
        selectedChains={selectedChains}
      />
    </div>
  );
}
