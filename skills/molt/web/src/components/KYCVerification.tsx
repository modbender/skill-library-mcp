import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api, type KYCStatus } from '../lib/api';
import { useToast } from '../contexts/ToastContext';
import Card from './ui/Card';
import Button from './ui/Button';
import { Upload, Loader2, XCircle, AlertCircle } from 'lucide-react';

interface KYCVerificationProps {
  status: KYCStatus;
}

export default function KYCVerification({ status }: KYCVerificationProps) {
  const { showToast } = useToast();
  const queryClient = useQueryClient();
  const [idPhoto, setIdPhoto] = useState<File | null>(null);
  const [selfiePhoto, setSelfiePhoto] = useState<File | null>(null);
  const [idPreview, setIdPreview] = useState<string | null>(null);
  const [selfiePreview, setSelfiePreview] = useState<string | null>(null);

  // Get today's date in readable format
  const today = new Date();
  const todayFormatted = today.toLocaleDateString('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric',
  });
  const todayShort = today.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });

  const handleIdPhotoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setIdPhoto(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setIdPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSelfiePhotoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelfiePhoto(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setSelfiePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const submitMutation = useMutation({
    mutationFn: async () => {
      if (!idPhoto || !selfiePhoto) {
        throw new Error('Please upload both photos');
      }
      return api.submitKYC(idPhoto, selfiePhoto, todayShort);
    },
    onSuccess: () => {
      showToast('KYC verification submitted successfully!', 'success');
      queryClient.invalidateQueries({ queryKey: ['kyc-status'] });
      // Reset form
      setIdPhoto(null);
      setSelfiePhoto(null);
      setIdPreview(null);
      setSelfiePreview(null);
    },
    onError: (error: Error) => {
      showToast(error.message || 'Failed to submit KYC verification', 'error');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!idPhoto || !selfiePhoto) {
      showToast('Please upload both photos', 'error');
      return;
    }
    submitMutation.mutate();
  };

  // Show pending status
  if (status.status === 'pending') {
    return (
      <div className="max-w-2xl mx-auto px-4 py-8">
        <Card className="p-8 text-center">
          <Loader2 className="w-16 h-16 mx-auto mb-4 text-primary animate-spin" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Verification Under Review</h2>
          <p className="text-gray-600">
            Your KYC verification is being reviewed. You'll be able to create campaigns once approved.
          </p>
        </Card>
      </div>
    );
  }

  // Show rejected status
  if (status.status === 'rejected') {
    return (
      <div className="max-w-2xl mx-auto px-4 py-8">
        <Card className="p-8">
          <div className="text-center mb-6">
            <XCircle className="w-16 h-16 mx-auto mb-4 text-red-500" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Verification Rejected</h2>
            {status.rejection_reason && (
              <p className="text-gray-600 mb-4">{status.rejection_reason}</p>
            )}
            {status.attempts_remaining > 0 ? (
              <p className="text-sm text-gray-500">
                You have {status.attempts_remaining} attempt{status.attempts_remaining !== 1 ? 's' : ''} remaining.
              </p>
            ) : (
              <p className="text-sm text-red-600 font-medium">
                Maximum attempts reached. Please contact support.
              </p>
            )}
          </div>
          {status.attempts_remaining > 0 && (
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Same form as below */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  1. Photo of your government-issued ID
                </label>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-primary transition-colors">
                  <input
                    type="file"
                    accept="image/jpeg,image/jpg,image/png"
                    onChange={handleIdPhotoChange}
                    className="hidden"
                    id="id-photo"
                    disabled={submitMutation.isPending}
                  />
                  <label
                    htmlFor="id-photo"
                    className="cursor-pointer flex flex-col items-center"
                  >
                    {idPreview ? (
                      <img
                        src={idPreview}
                        alt="ID preview"
                        className="max-h-48 rounded-lg mb-2"
                      />
                    ) : (
                      <>
                        <Upload className="w-12 h-12 text-gray-400 mb-2" />
                        <span className="text-sm text-gray-600">
                          Click to upload ID photo
                        </span>
                      </>
                    )}
                  </label>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  2. Selfie holding your ID + handwritten note
                </label>
                <p className="text-sm text-gray-600 mb-2">
                  Show today's date: <strong>{todayFormatted}</strong>
                </p>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-primary transition-colors">
                  <input
                    type="file"
                    accept="image/jpeg,image/jpg,image/png"
                    onChange={handleSelfiePhotoChange}
                    className="hidden"
                    id="selfie-photo"
                    disabled={submitMutation.isPending}
                  />
                  <label
                    htmlFor="selfie-photo"
                    className="cursor-pointer flex flex-col items-center"
                  >
                    {selfiePreview ? (
                      <img
                        src={selfiePreview}
                        alt="Selfie preview"
                        className="max-h-48 rounded-lg mb-2"
                      />
                    ) : (
                      <>
                        <Upload className="w-12 h-12 text-gray-400 mb-2" />
                        <span className="text-sm text-gray-600">
                          Click to upload selfie
                        </span>
                      </>
                    )}
                  </label>
                </div>
              </div>

              <Button
                type="submit"
                variant="primary"
                size="lg"
                className="w-full"
                disabled={submitMutation.isPending || !idPhoto || !selfiePhoto}
              >
                {submitMutation.isPending ? (
                  <>
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    Submitting...
                  </>
                ) : (
                  'Resubmit Verification'
                )}
              </Button>
            </form>
          )}
        </Card>
      </div>
    );
  }

  // Show upload form for "none" status
  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <Card className="p-8">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-3">Verify Your Identity</h2>
          <p className="text-gray-600">
            To create a campaign, we need to verify you're human. This helps prevent abuse and keeps MoltFundMe safe.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              1. Photo of your government-issued ID
            </label>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-primary transition-colors">
              <input
                type="file"
                accept="image/jpeg,image/jpg,image/png"
                onChange={handleIdPhotoChange}
                className="hidden"
                id="id-photo"
                disabled={submitMutation.isPending}
              />
              <label
                htmlFor="id-photo"
                className="cursor-pointer flex flex-col items-center"
              >
                {idPreview ? (
                  <img
                    src={idPreview}
                    alt="ID preview"
                    className="max-h-48 rounded-lg mb-2"
                  />
                ) : (
                  <>
                    <Upload className="w-12 h-12 text-gray-400 mb-2" />
                    <span className="text-sm text-gray-600">
                      Click to upload ID photo (JPG or PNG)
                    </span>
                    <span className="text-xs text-gray-500 mt-1">Max 10MB</span>
                  </>
                )}
              </label>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              2. Selfie holding your ID + handwritten note
            </label>
            <div className="bg-primary-50 border border-primary-200 rounded-lg p-4 mb-3">
              <div className="flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
                <div className="text-sm text-gray-700">
                  <p className="font-medium mb-1">What to include:</p>
                  <ul className="list-disc list-inside space-y-1 text-gray-600">
                    <li>Hold your ID next to your face</li>
                    <li>Write today's date on a piece of paper: <strong>{todayFormatted}</strong></li>
                    <li>Hold the paper in the photo so the date is clearly visible</li>
                  </ul>
                </div>
              </div>
            </div>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-primary transition-colors">
              <input
                type="file"
                accept="image/jpeg,image/jpg,image/png"
                onChange={handleSelfiePhotoChange}
                className="hidden"
                id="selfie-photo"
                disabled={submitMutation.isPending}
              />
              <label
                htmlFor="selfie-photo"
                className="cursor-pointer flex flex-col items-center"
              >
                {selfiePreview ? (
                  <img
                    src={selfiePreview}
                    alt="Selfie preview"
                    className="max-h-48 rounded-lg mb-2"
                  />
                ) : (
                  <>
                    <Upload className="w-12 h-12 text-gray-400 mb-2" />
                    <span className="text-sm text-gray-600">
                      Click to upload selfie (JPG or PNG)
                    </span>
                    <span className="text-xs text-gray-500 mt-1">Max 10MB</span>
                  </>
                )}
              </label>
            </div>
          </div>

          <div className="bg-gray-50 rounded-lg p-4 text-sm text-gray-600">
            <p className="font-medium mb-1">Privacy & Security:</p>
            <p>
              Your documents are stored securely and only used to verify you're a real person. 
              We never share your information with third parties.
            </p>
          </div>

          <Button
            type="submit"
            variant="primary"
            size="lg"
            className="w-full"
            disabled={submitMutation.isPending || !idPhoto || !selfiePhoto}
          >
            {submitMutation.isPending ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Submitting...
              </>
            ) : (
              'Submit Verification'
            )}
          </Button>
        </form>
      </Card>
    </div>
  );
}
