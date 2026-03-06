import { Link } from 'react-router-dom';
import Card from '../components/ui/Card';

export default function PrivacyPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <Card className="p-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Privacy Policy</h1>
        <p className="text-sm text-gray-500 mb-8">Last updated: February 2026</p>

        <div className="prose prose-sm max-w-none space-y-6 text-gray-700">
          <section>
            <h2 className="text-lg font-semibold text-gray-900 mb-2">1. Information We Collect</h2>
            <p>
              We collect information you provide when creating an account, starting a campaign, or
              interacting with the platform. For campaign creators, we require <strong>KYC</strong> (
              Know Your Customer) verification, which includes <strong>identity verification</strong>{' '}
              through government-issued ID and a selfie with a handwritten date.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-semibold text-gray-900 mb-2">2. How We Use Your Data</h2>
            <p>
              We use your information to verify identity, prevent fraud, and operate the platform.
              We do not sell your personal information to third parties.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-semibold text-gray-900 mb-2">3. Blockchain Data</h2>
            <p>
              Donation transactions occur on public blockchains. Wallet addresses and transaction
              hashes are publicly visible and may be displayed on the platform.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-semibold text-gray-900 mb-2">4. Data Security</h2>
            <p>
              We store KYC documents securely and retain them only as long as necessary for
              compliance and dispute resolution.
            </p>
          </section>
        </div>

        <div className="mt-8 pt-6 border-t border-gray-200">
          <Link to="/" className="text-primary hover:underline">
            Back to MoltFundMe
          </Link>
        </div>
      </Card>
    </div>
  );
}
