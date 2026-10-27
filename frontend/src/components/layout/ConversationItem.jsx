import { useEffect, useRef, useState } from "react";
import ConfirmDialog from "../common/ConfirmDialog.jsx";
import { CheckIcon, PencilIcon, TrashIcon, XIcon } from "../common/icons.jsx";

export default function ConversationItem({ conversation, active, onSelect, onRename, onDelete }) {
  const [editing, setEditing] = useState(false);
  const [title, setTitle] = useState(conversation.title);
  const [error, setError] = useState("");
  const [confirming, setConfirming] = useState(false);
  const [busy, setBusy] = useState(false);
  const inputRef = useRef(null);

  useEffect(() => {
    if (editing) inputRef.current?.select();
  }, [editing]);

  async function saveRename() {
    const next = title.trim();
    if (!next) return setError("Title cannot be empty.");
    if (next === conversation.title) return setEditing(false);
    setBusy(true);
    try {
      await onRename(conversation.id, next);
      setEditing(false);
      setError("");
    } catch (e) {
      setError(e.fieldErrors?.[0]?.message || e.message);
    } finally {
      setBusy(false);
    }
  }

  async function confirmDelete() {
    setBusy(true);
    setError("");
    try {
      await onDelete(conversation.id);
    } catch (e) {
      setError(e.message);
      setBusy(false);
    }
  }

  if (editing) {
    return (
      <div className="px-1 py-1">
        <div className="flex items-center gap-1">
          <input
            ref={inputRef}
            value={title}
            maxLength={120}
            disabled={busy}
            aria-label="Conversation title"
            onChange={(e) => setTitle(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") saveRename();
              if (e.key === "Escape") { setEditing(false); setTitle(conversation.title); setError(""); }
            }}
            className="min-w-0 flex-1 rounded-md border border-brand-300 bg-white px-2 py-1 text-sm outline-none focus:ring-2 focus:ring-brand-300"
          />
          <button onClick={saveRename} disabled={busy} aria-label="Save title" className="rounded p-1 text-brand-700 hover:bg-brand-100"><CheckIcon size={16} /></button>
          <button onClick={() => { setEditing(false); setTitle(conversation.title); setError(""); }} aria-label="Cancel rename" className="rounded p-1 text-stone-500 hover:bg-stone-200"><XIcon size={16} /></button>
        </div>
        {error && <p className="mt-1 text-xs text-red-600" role="alert">{error}</p>}
      </div>
    );
  }

  return (
    <>
      <div className={`group flex items-center rounded-lg ${active ? "bg-brand-100" : "hover:bg-stone-200/70"}`}>
        <button
          onClick={() => onSelect(conversation.id)}
          aria-current={active ? "true" : undefined}
          title={conversation.title}
          className={`min-w-0 flex-1 truncate px-3 py-2 text-left text-sm ${active ? "font-medium text-brand-900" : "text-stone-700"}`}
        >
          {conversation.title}
        </button>
        <div className="flex pr-1 opacity-100 md:opacity-0 md:group-focus-within:opacity-100 md:group-hover:opacity-100">
          <button onClick={() => { setTitle(conversation.title); setEditing(true); }} aria-label={`Rename ${conversation.title}`} className="rounded p-1.5 text-stone-500 hover:bg-white hover:text-stone-800"><PencilIcon size={15} /></button>
          <button onClick={() => setConfirming(true)} aria-label={`Delete ${conversation.title}`} className="rounded p-1.5 text-stone-500 hover:bg-white hover:text-red-600"><TrashIcon size={15} /></button>
        </div>
      </div>
      {confirming && (
        <ConfirmDialog
          title="Delete this conversation?"
          message={`"${conversation.title}" and all its messages will be permanently deleted.`}
          busy={busy}
          error={error}
          onConfirm={confirmDelete}
          onCancel={() => { setConfirming(false); setError(""); }}
        />
      )}
    </>
  );
}
