import { BookIcon } from "../common/icons.jsx";

/** Collapsible list of the knowledge-base passages an answer was based on. */
export default function SourceList({ sources }) {
  if (!sources?.length) return null;
  return (
    <details className="mt-3 rounded-lg border border-stone-200 bg-stone-50 text-xs text-stone-600">
      <summary className="flex cursor-pointer select-none items-center gap-1.5 px-3 py-1.5 font-medium text-stone-700">
        <BookIcon size={14} /> Sources ({sources.length})
      </summary>
      <ol className="space-y-1 border-t border-stone-200 px-3 py-2">
        {sources.map((s, i) => (
          <li key={s.chunk_id}>
            <span className="font-medium text-stone-700">[{i + 1}]</span> {s.title} <span className="text-stone-400">›</span> {s.section}
          </li>
        ))}
      </ol>
    </details>
  );
}
