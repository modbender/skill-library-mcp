import { useState, useEffect } from 'react';
import { X, Copy, Check, AlertTriangle } from 'lucide-react';
import { generateWalletsForChains, type GeneratedWallet } from '../lib/wallet-generator';
import { copyToClipboard } from '../lib/utils';
import Button from './ui/Button';
import Card from './ui/Card';

interface WalletGeneratorModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (wallets: Record<string, string>) => void; // chain -> address mapping
  selectedChains: ('btc' | 'eth' | 'sol' | 'usdc_base')[];
}

const chainLabels: Record<string, string> = {
  btc: 'Bitcoin',
  eth: 'Ethereum',
  sol: 'Solana',
  usdc_base: 'USDC (Base)',
};

export default function WalletGeneratorModal({
  isOpen,
  onClose,
  onConfirm,
  selectedChains,
}: WalletGeneratorModalProps) {
  const [wallets, setWallets] = useState<GeneratedWallet[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);
  const [hasConfirmed, setHasConfirmed] = useState(false);

  useEffect(() => {
    if (isOpen && selectedChains.length > 0 && wallets.length === 0) {
      generateWallets();
    }
  }, [isOpen, selectedChains]);

  const generateWallets = async () => {
    setIsGenerating(true);
    try {
      const generated = await generateWalletsForChains(selectedChains);
      setWallets(generated);
    } catch (error) {
      console.error('Failed to generate wallets:', error);
      alert('Failed to generate wallets. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleCopy = async (phrase: string, index: number) => {
    try {
      await copyToClipboard(phrase);
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  const handleConfirm = () => {
    if (!hasConfirmed) return;
    
    // Convert wallets to address mapping (only addresses, no seed phrases)
    const addressMap: Record<string, string> = {};
    wallets.forEach(wallet => {
      addressMap[`${wallet.chain}_wallet_address`] = wallet.address;
    });
    
    onConfirm(addressMap);
    // Reset state
    setWallets([]);
    setHasConfirmed(false);
    setCopiedIndex(null);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 p-4" role="dialog" aria-modal="true" aria-labelledby="wallet-modal-title">
      <Card className="max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 id="wallet-modal-title" className="text-2xl font-bold text-gray-900">Generate Wallets</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Warning */}
        <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm font-medium text-yellow-800 mb-1">
              Save Your Recovery Phrases Securely
            </p>
            <p className="text-sm text-yellow-700">
              These recovery phrases are the only way to access your wallets. If you lose them,
              you cannot recover your funds. We never store your private keys or seed phrases.
            </p>
          </div>
        </div>

        {isGenerating ? (
          <div className="text-center py-8">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mb-4"></div>
            <p className="text-gray-600">Generating wallets...</p>
          </div>
        ) : wallets.length > 0 ? (
          <>
            <div className="space-y-4 mb-6">
              {wallets.map((wallet, index) => (
                <div
                  key={wallet.chain}
                  className="p-4 border border-gray-200 rounded-lg"
                  data-testid={`seed-phrase-display-${wallet.chain}`}
                  data-chain={wallet.chain}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium text-gray-900">
                      {chainLabels[wallet.chain]} Wallet
                    </h3>
                    <button
                      onClick={() => handleCopy(wallet.seedPhrase, index)}
                      className="flex items-center gap-1 text-sm text-gray-600 hover:text-gray-900 transition-colors"
                    >
                      {copiedIndex === index ? (
                        <>
                          <Check className="w-4 h-4" />
                          Copied
                        </>
                      ) : (
                        <>
                          <Copy className="w-4 h-4" />
                          Copy
                        </>
                      )}
                    </button>
                  </div>
                  <p className="text-xs text-gray-500 mb-2">Address: {wallet.address}</p>
                  <div className="p-3 bg-gray-50 rounded border border-gray-200">
                    <p className="text-sm font-mono text-gray-800 break-words">
                      {wallet.seedPhrase}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            <div className="mb-6">
              <label className="flex items-start gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={hasConfirmed}
                  onChange={(e) => setHasConfirmed(e.target.checked)}
                  className="mt-1 w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary"
                />
                <span className="text-sm text-gray-700">
                  I have saved my recovery phrases securely. I understand that if I lose them,
                  I cannot recover my wallets.
                </span>
              </label>
            </div>

            <div className="flex gap-3">
              <Button
                onClick={handleConfirm}
                variant="primary"
                disabled={!hasConfirmed}
                className="flex-1"
              >
                Confirm & Create Campaign
              </Button>
              <Button onClick={onClose} variant="outline">
                Cancel
              </Button>
            </div>
          </>
        ) : (
          <div className="text-center py-8">
            <p className="text-gray-600">No chains selected</p>
          </div>
        )}
      </Card>
    </div>
  );
}
