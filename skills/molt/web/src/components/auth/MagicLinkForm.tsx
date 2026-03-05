import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { useMutation } from '@tanstack/react-query';
import { api } from '../../lib/api';
import { useToast } from '../../contexts/ToastContext';
import Card from '../ui/Card';
import Button from '../ui/Button';
import Input from '../ui/Input';
import { Mail, Loader2 } from 'lucide-react';

const emailSchema = z.object({
  email: z.string().email('Invalid email address'),
});

type EmailFormData = z.infer<typeof emailSchema>;

interface MagicLinkFormProps {
  onTokenReceived?: (token: string) => void;
}

export default function MagicLinkForm({ onTokenReceived }: MagicLinkFormProps) {
  const { showToast } = useToast();
  const [tokenReceived, setTokenReceived] = useState<string | null>(null);
  const [emailSent, setEmailSent] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<EmailFormData>({
    resolver: zodResolver(emailSchema),
  });

  const requestMagicLinkMutation = useMutation({
    mutationFn: async (data: EmailFormData) => {
      return api.requestMagicLink(data.email);
    },
    onSuccess: (response) => {
      // Extract token from message (dev mode only - when SMTP not configured)
      const tokenMatch = response.message.match(/Token: ([^\s]+)/);
      if (tokenMatch) {
        const token = tokenMatch[1];
        setTokenReceived(token);
        if (onTokenReceived) {
          onTokenReceived(token);
        }
        showToast('Magic link token generated!', 'success');
      } else {
        setEmailSent(true);
        showToast(response.message, 'success');
      }
    },
    onError: (error: Error) => {
      showToast(error.message || 'Failed to request magic link', 'error');
    },
  });

  const onSubmit = (data: EmailFormData) => {
    requestMagicLinkMutation.mutate(data);
  };

  if (emailSent) {
    return (
      <Card className="p-8">
        <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-primary-100 flex items-center justify-center">
            <Mail className="w-8 h-8 text-primary" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Check your email</h2>
          <p className="text-gray-600 mb-6">
            We&apos;ve sent you a sign-in link. Click the link in the email to continue.
          </p>
          <p className="text-sm text-gray-500">
            Didn&apos;t receive it? Check your spam folder or try again.
          </p>
        </div>
      </Card>
    );
  }

  if (tokenReceived) {
    return (
      <Card className="p-8">
        <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-primary-100 flex items-center justify-center">
            <Mail className="w-8 h-8 text-primary" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Magic Link Generated</h2>
          <p className="text-gray-600 mb-6">
            For development, your magic link token is shown below. Click the link to verify.
          </p>
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-6">
            <code className="text-sm text-gray-900 break-all">{tokenReceived}</code>
          </div>
          <a
            href={`/auth/verify?token=${tokenReceived}`}
            className="inline-block"
          >
            <Button variant="primary" size="lg">
              Verify Token & Continue
            </Button>
          </a>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-8">
      <div className="text-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Sign In to Create a Campaign</h2>
        <p className="text-gray-600">
          Enter your email to receive a magic link to sign in
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <Input
          label="Email Address"
          type="email"
          {...register('email')}
          error={errors.email?.message}
          placeholder="your@email.com"
          helperText="We'll send you a magic link token"
        />

        <Button
          type="submit"
          variant="primary"
          size="lg"
          className="w-full"
          disabled={isSubmitting || requestMagicLinkMutation.isPending}
        >
          {isSubmitting || requestMagicLinkMutation.isPending ? (
            <>
              <Loader2 className="w-5 h-5 mr-2 animate-spin" />
              Sending...
            </>
          ) : (
            <>
              <Mail className="w-5 h-5 mr-2" />
              Request Magic Link
            </>
          )}
        </Button>
      </form>
    </Card>
  );
}
