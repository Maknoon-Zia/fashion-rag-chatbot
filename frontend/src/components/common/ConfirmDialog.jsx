import { useEffect, useRef } from "react";

export default function ConfirmDialog({ title, message, confirmLabel = "Delete", busy = false, error = "", onConfirm, onCancel }) {
  const cancelRef = useRef(null);
  useEffect(() => {
    cancelRef.current?.focus();
    const onKey = (e) => e.key === "Escape" && !busy && onCancel();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [busy, onCancel]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" onMouseDown={() => !busy && onCancel()}>
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="confirm-title"
        className="w-full max-w-sm rounded-xl bg-white p-5 shadow-xl"
        onMouseDown={(e) => e.stopPropagation()}
      >
        <h2 id="confirm-title" className="text-lg font-semibold text-stone-900">{title}</h2>
        <p className="mt-2 text-sm text-stone-600">{message}</p>
        {error && <p className="mt-3 text-sm text-red-600" role="alert">{error}</p>}
        <div className="mt-5 flex justify-end gap-2">
          <button ref={cancelRef} onClick={onCancel} disabled={busy} className="rounded-lg border border-stone-300 px-4 py-2 text-sm hover:bg-stone-100 disabled:opacity-50">
            Cancel
          </button>
          <button onClick={onConfirm} disabled={busy} className="rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-60">
            {busy ? "Deleting…" : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
