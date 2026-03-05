import type { ButtonHTMLAttributes, ReactNode } from 'react';
import { Link } from 'react-router-dom';
import { cn } from '../../lib/utils';

interface ButtonBaseProps {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

interface ButtonProps extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, 'children'>, ButtonBaseProps {
  as?: 'button';
  children: ReactNode;
  onClick?: () => void;
}

interface ButtonLinkProps extends ButtonBaseProps {
  as: typeof Link;
  to: string;
  children: ReactNode;
}

type ButtonComponentProps = ButtonProps | ButtonLinkProps;

export default function Button(props: ButtonComponentProps) {
  const { variant = 'primary', size = 'md', className, children, ...rest } = props;
  
  const baseStyles = 'inline-flex items-center justify-center font-semibold rounded-full transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';
  
  const variants = {
    primary: 'bg-[#00b964] text-white hover:bg-[#009950] focus:ring-[#00b964] shadow-lg shadow-[#00b964]/25 hover:shadow-xl hover:shadow-[#00b964]/30',
    secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-200 focus:ring-gray-500',
    outline: 'border-2 border-gray-300 text-gray-700 hover:border-gray-400 hover:bg-gray-50 focus:ring-gray-500',
    ghost: 'text-gray-700 hover:bg-gray-100 focus:ring-gray-500',
  };

  const sizes = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-5 py-2.5 text-base',
    lg: 'px-8 py-3.5 text-lg',
  };

  const classes = cn(baseStyles, variants[variant], sizes[size], className);

  if ('as' in props && props.as === Link) {
    const { as, to, ...linkProps } = props as ButtonLinkProps;
    return (
      <Link to={to} className={classes} {...(linkProps as any)}>
        {children}
      </Link>
    );
  }

  return (
    <button
      className={classes}
      {...(rest as ButtonHTMLAttributes<HTMLButtonElement>)}
    >
      {children}
    </button>
  );
}
