import { cn } from '../../utils/cn';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  className?: string;
}

export function Input({ className, ...props }: InputProps) {
  return (
    <input
      className={cn(
        'w-full mt-1 px-3 py-2 rounded-lg border border-border bg-secondary',
        'focus:outline-none focus:ring-2 focus:ring-blue-500/30',
        className
      )}
      {...props}
    />
  );
}
