import type React from 'react';
import { cn } from '../../utils/cn';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'default' | 'elevated' | 'outlined';
  interactive?: boolean;
  as?: 'div' | 'article' | 'section';
}

const variantStyles: Record<NonNullable<CardProps['variant']>, string> = {
  default: 'bg-[var(--color-surface)] border border-[var(--color-border)] shadow-[var(--shadow-sm)]',
  elevated: 'bg-[var(--color-surface-elevated)] shadow-[var(--shadow-md)]',
  outlined: 'bg-[var(--color-surface)] border-2 border-[var(--color-border)]',
};

export function Card({
  variant = 'default',
  interactive = false,
  as: Component = 'div',
  className,
  children,
  ...props
}: CardProps) {
  return (
    <Component
      className={cn(
        'rounded-[var(--radius-lg)] overflow-hidden',
        variantStyles[variant],
        interactive &&
          'cursor-pointer transition-all duration-[var(--transition-fast)] hover:shadow-[var(--shadow-md)] hover:border-[var(--color-primary)] focus-within:ring-2 focus-within:ring-[var(--color-focus-ring)] focus-within:ring-offset-2',
        className
      )}
      {...props}
    >
      {children}
    </Component>
  );
}

export interface CardHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  as?: 'div' | 'header';
}

export function CardHeader({ as: Component = 'div', className, children, ...props }: CardHeaderProps) {
  return (
    <Component
      className={cn('px-6 py-4 border-b border-[var(--color-border-subtle)]', className)}
      {...props}
    >
      {children}
    </Component>
  );
}

export interface CardTitleProps extends React.HTMLAttributes<HTMLHeadingElement> {
  as?: 'h1' | 'h2' | 'h3' | 'h4';
}

export function CardTitle({ as: Component = 'h3', className, children, ...props }: CardTitleProps) {
  return (
    <Component
      className={cn('text-[var(--font-size-lg)] font-semibold text-[var(--color-text-primary)]', className)}
      {...props}
    >
      {children}
    </Component>
  );
}

export type CardDescriptionProps = React.HTMLAttributes<HTMLParagraphElement>

export function CardDescription({ className, children, ...props }: CardDescriptionProps) {
  return (
    <p className={cn('text-[var(--font-size-sm)] text-[var(--color-text-secondary)] mt-1', className)} {...props}>
      {children}
    </p>
  );
}

export function CardBody({ className, children, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn('px-6 py-4', className)} {...props}>
      {children}
    </div>
  );
}

export interface CardFooterProps extends React.HTMLAttributes<HTMLDivElement> {
  as?: 'div' | 'footer';
}

export function CardFooter({ as: Component = 'div', className, children, ...props }: CardFooterProps) {
  return (
    <Component
      className={cn('px-6 py-3 border-t border-[var(--color-border-subtle)] bg-[var(--color-surface-sunken)]/50', className)}
      {...props}
    >
      {children}
    </Component>
  );
}
