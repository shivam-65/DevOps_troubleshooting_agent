import { AlertTriangle } from 'lucide-react';

interface ErrorStateProps {
  error: string;
  onRetry?: () => void;
}

export function ErrorState({ error, onRetry }: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 gap-3">
      <AlertTriangle className="h-10 w-10 text-red-400" />
      <h3 className="text-lg font-medium text-foreground">Something went wrong</h3>
      <p className="text-sm text-muted-foreground max-w-md text-center">{error}</p>
      {onRetry && (
        <button onClick={onRetry} className="mt-2 px-4 py-2 rounded-md bg-primary text-primary-foreground text-sm font-medium hover:bg-primary/90 transition-colors">
          Try Again
        </button>
      )}
    </div>
  );
}
