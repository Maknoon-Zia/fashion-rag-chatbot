import { AlertIcon, RetryIcon } from "../common/icons.jsx";

export default function ErrorBanner({ message, onRetry, retryLabel = "Retry" }) {
  if (!message) return null;
  return (
    <div className="mx-auto flex w-full max-w-3xl items-start gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800" role="alert">
      <AlertIcon size={18} className="mt-0.5 shrink-0" />
      <span className="flex-1">{message}</span>
      {onRetry && (
        <button onClick={onRetry} className="flex shrink-0 items-center gap-1 rounded-md px-2 py-0.5 font-medium text-red-700 hover:bg-red-100">
          <RetryIcon size={14} /> {retryLabel}
        </button>
      )}
    </div>
  );
}
