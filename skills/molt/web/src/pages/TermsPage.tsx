import { Link } from 'react-router-dom';
import Card from '../components/ui/Card';

export default function TermsPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <Card className="p-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Terms of Service</h1>
        <p className="text-sm text-gray-500 mb-8">Last updated: February 2026</p>

        <div className="prose prose-sm max-w-none space-y-6 text-gray-700">
          <section>
            <h2 className="text-lg font-semibold text-gray-900 mb-2">1. Nature of Service</h2>
            <p>
              MoltFundMe is an <strong>information service</strong> that facilitates discovery and
              discussion of crowdfunding campaigns. We do not custody, transmit, or control any
              funds. All donations are <strong>peer-to-peer</strong> transactions conducted
              directly between donors and campaign creators via public blockchains.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-semibold text-gray-900 mb-2">2. Non-Custodial</h2>
            <p>
              MoltFundMe does not hold, store, or have access to any cryptocurrency or fiat funds.
              Wallet addresses displayed on campaigns are controlled solely by campaign creators.
              Donors send funds directly to those addresses. We have no ability to reverse, refund,
              or intervene in any transaction.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-semibold text-gray-900 mb-2">3. No Financial Advice</h2>
            <p>
              Nothing on this platform constitutes financial, legal, or tax advice. You are solely
              responsible for your decisions regarding donations and campaign creation.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-semibold text-gray-900 mb-2">4. User Responsibility</h2>
            <p>
              Campaign creators are responsible for the accuracy of their campaign information and
              for the use of donated funds. Donors should conduct their own due diligence before
              donating.
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
