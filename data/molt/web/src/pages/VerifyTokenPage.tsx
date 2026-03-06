import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate, useLocation } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { api } from '../lib/api';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';
import { CheckCircle2, XCircle, Loader2 } from 'lucide-react';
import { Link } from 'react-router-dom';

// Simple JWT decode (just for MVP - doesn't verify signature)
function decodeJWT(token: string): { sub?: string; email?: string } | null {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (e) {
    return null;
  }
}

export default function VerifyTokenPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const location = useLocation();
  const token = searchParams.get('token');
  const { login } = useAuth();
  const { showToast } = useToast();
  const [isVerifying, setIsVerifying] = useState(false);

  const verifyMutation = useMutation({
    mutationFn: async (tokenToVerify: string) => {
      return api.verifyToken(tokenToVerify);
    },
    onSuccess: (response) => {
      if (response.success && response.access_token) {
        // Decode JWT to get user info
        const payload = decodeJWT(response.access_token);
        const userId = payload?.sub || 'unknown';
        const email = payload?.email || 'user@example.com';
        
        login(response.access_token, email, userId);
        showToast('Successfully authenticated!', 'success');
        
        // Redirect to intended destination or campaigns/new
        const from = (location.state as any)?.from?.pathname || '/campaigns/new';
        navigate(from, { replace: true });
      } else {
        showToast(response.message || 'Token verification failed', 'error');
      }
    },
    onError: (error: Error) => {
      showToast(error.message || 'Failed to verify token', 'error');
    },
  });

  useEffect(() => {
    if (token && !isVerifying) {
      setIsVerifying(true);
      verifyMutation.mutate(token);
    }
  }, [token]);

  if (!token) {
    return (
      <div className="max-w-md mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Card className="p-8">
          <div className="text-center">
            <XCircle className="w-16 h-16 mx-auto mb-4 text-error" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Invalid Token</h2>
            <p className="text-gray-600 mb-6">
              No verification token provided. Please request a new magic link.
            </p>
            <Button as={Link} to="/campaigns/new" variant="primary">
              Go to Campaign Creation
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  if (verifyMutation.isPending || isVerifying) {
    return (
      <div className="max-w-md mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Card className="p-8">
          <div className="text-center">
            <Loader2 className="w-16 h-16 mx-auto mb-4 text-primary animate-spin" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Verifying Token</h2>
            <p className="text-gray-600">Please wait while we verify your token...</p>
          </div>
        </Card>
      </div>
    );
  }

  if (verifyMutation.isError) {
    return (
      <div className="max-w-md mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Card className="p-8">
          <div className="text-center">
            <XCircle className="w-16 h-16 mx-auto mb-4 text-error" />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Verification Failed</h2>
            <p className="text-gray-600 mb-6">
              {verifyMutation.error?.message || 'The token is invalid or has expired.'}
            </p>
            <Button as={Link} to="/campaigns/new" variant="primary">
              Request New Magic Link
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-md mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <Card className="p-8">
        <div className="text-center">
          <CheckCircle2 className="w-16 h-16 mx-auto mb-4 text-success" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Verification Successful</h2>
          <p className="text-gray-600 mb-6">Redirecting...</p>
        </div>
      </Card>
    </div>
  );
}
