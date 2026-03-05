// ChainSelector component - no useState needed

export type Chain = 'btc' | 'eth' | 'sol' | 'usdc_base';

interface ChainSelectorProps {
  selectedChains: Chain[];
  onChange: (chains: Chain[]) => void;
}

const chains: { value: Chain; label: string; description: string }[] = [
  { value: 'btc', label: 'Bitcoin', description: 'BTC' },
  { value: 'eth', label: 'Ethereum', description: 'ETH' },
  { value: 'sol', label: 'Solana', description: 'SOL' },
  { value: 'usdc_base', label: 'USDC (Base)', description: 'USDC on Base L2' },
];

export default function ChainSelector({ selectedChains, onChange }: ChainSelectorProps) {
  const handleToggle = (chain: Chain) => {
    if (selectedChains.includes(chain)) {
      onChange(selectedChains.filter(c => c !== chain));
    } else {
      onChange([...selectedChains, chain]);
    }
  };

  return (
    <div className="space-y-3" data-testid="chain-selector">
      <p className="text-sm text-gray-600 mb-4">
        Select which cryptocurrencies you want to accept donations in. We'll generate a dedicated
        wallet address for each selected chain.
      </p>
      <div className="grid grid-cols-2 gap-3">
        {chains.map(chain => (
          <label
            key={chain.value}
            className="flex items-center p-4 border-2 rounded-lg cursor-pointer transition-colors hover:bg-gray-50"
            style={{
              borderColor: selectedChains.includes(chain.value) ? '#3b82f6' : '#e5e7eb',
              backgroundColor: selectedChains.includes(chain.value) ? '#eff6ff' : 'white',
            }}
          >
            <input
              type="checkbox"
              checked={selectedChains.includes(chain.value)}
              onChange={() => handleToggle(chain.value)}
              className="w-4 h-4 text-primary border-gray-300 rounded focus:ring-primary mr-3"
            />
            <div className="flex-1">
              <div className="font-medium text-gray-900">{chain.label}</div>
              <div className="text-sm text-gray-500">{chain.description}</div>
            </div>
          </label>
        ))}
      </div>
    </div>
  );
}
