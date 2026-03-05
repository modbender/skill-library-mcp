import { cn } from '../../utils/cn';

interface ToggleProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  disabled?: boolean;
  className?: string;
}

export function Toggle({ checked, onChange, disabled, className }: ToggleProps) {
  return (
    <button
      type="button"
      disabled={disabled}
      onClick={(e) => {
        e.stopPropagation();
        if (!disabled) onChange(!checked);
      }}
      className={cn(
        'w-11 h-6 flex items-center rounded-full p-1',
        'transition-all duration-200',
        checked ? 'bg-blue-500' : 'bg-gray-700',
        disabled && 'opacity-50 cursor-not-allowed',
        !disabled && 'hover:shadow-lg',
        className
      )}
    >
      <div
        className={cn(
          'bg-white w-4 h-4 rounded-full shadow-md',
          'transform transition-transform duration-200',
          checked ? 'translate-x-5' : 'translate-x-0'
        )}
      />
    </button>
  );
}
