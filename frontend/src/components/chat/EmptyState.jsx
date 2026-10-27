import { HangerIcon } from "../common/icons.jsx";

const EXAMPLES = [
  "What hijab or dupatta color goes with a black abaya?",
  "What should I wear to a job interview?",
  "How can I make three outfits from one pair of black trousers?",
  "Which fabrics are comfortable in hot, humid weather?",
  "Suggest an Eid outfit with a waistcoat for a man",
];

export default function EmptyState({ onPick, disabled }) {
  return (
    <div className="mx-auto flex max-w-xl flex-col items-center px-4 py-10 text-center">
      <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-brand-100 text-brand-700">
        <HangerIcon size={28} />
      </div>
      <h2 className="font-display text-2xl font-semibold text-stone-900">How can I help you style today?</h2>
      <p className="mt-2 text-sm text-stone-500">
        Ask about outfit coordination, colors, accessories, occasion dressing, traditional wear or reusing your wardrobe.
        Answers come from a curated fashion knowledge base, with sources.
      </p>
      <div className="mt-6 grid w-full gap-2">
        {EXAMPLES.map((p) => (
          <button
            key={p}
            onClick={() => onPick(p)}
            disabled={disabled}
            className="rounded-xl border border-stone-200 bg-white px-4 py-2.5 text-left text-sm text-stone-700 transition hover:border-brand-300 hover:bg-brand-50 disabled:opacity-50"
          >
            {p}
          </button>
        ))}
      </div>
    </div>
  );
}
